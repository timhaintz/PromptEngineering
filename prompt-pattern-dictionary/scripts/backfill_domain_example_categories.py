#!/usr/bin/env python
"""Backfill domain industry example categories using the classifier."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    cast,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
for path in (PROJECT_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

if TYPE_CHECKING:  # pragma: no cover - import only for type checking
    from scripts.domain_example_classifier import DomainExampleClassifier


@dataclass(frozen=True)
class ExampleKey:
    """Uniquely identify a domain industry example."""

    task: str
    prompt: str

    def to_tuple(self) -> Tuple[str, str]:
        return (self.task, self.prompt)


@dataclass
class ExampleRef:
    """Pointer to the example so we can write the category back."""

    pattern_index: int
    example_index: int
    original: Dict[str, Any]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify domainIndustryExamples and backfill the category field"
            " (category, task, prompt order)."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("public/data/normalized-patterns.json"),
        help="Path to normalized patterns JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Optional output path. When omitted, the input file is updated"
            " in place unless --dry-run is set."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run classification and report results without writing changes.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of unique examples to classify (for testing).",
    )
    parser.add_argument(
        "--cache-file",
        type=Path,
        default=Path("tmp/domain_example_category_cache.json"),
        help="Optional cache file to reuse classifications across runs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reclassify examples even when a category already exists.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Dict[str, Any], path: Path) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_cache(path: Path) -> Dict[Tuple[str, str], str]:
    if not path.exists():
        return {}
    content = json.loads(path.read_text(encoding="utf-8"))
    result: Dict[Tuple[str, str], str] = {}
    if isinstance(content, list):
        entries = cast(List[Any], content)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_dict = cast(Dict[str, Any], entry)
            task = entry_dict.get("task")
            prompt = entry_dict.get("prompt")
            category = entry_dict.get("category")
            if (
                isinstance(task, str)
                and isinstance(prompt, str)
                and isinstance(category, str)
            ):
                result[(task, prompt)] = category
    return result


def save_cache(cache: Dict[Tuple[str, str], str], path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    serialised: List[Dict[str, str]] = [
        {"task": key[0], "prompt": key[1], "category": value}
        for key, value in sorted(cache.items())
    ]
    path.write_text(
        json.dumps(serialised, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_classifier_instance(
    model_name: Optional[str] = None,
) -> "DomainExampleClassifier":
    from scripts.domain_example_classifier import (
        DomainExampleClassifier as _DomainExampleClassifier,
    )

    if model_name:
        return _DomainExampleClassifier(model_name=model_name)
    return _DomainExampleClassifier()


def collect_examples(
    data: Dict[str, Any],
    force: bool,
) -> Tuple[Dict[ExampleKey, List[ExampleRef]], List[Dict[str, Any]]]:
    patterns = data.get("patterns", [])
    key_map: Dict[ExampleKey, List[ExampleRef]] = defaultdict(list)
    for pattern_index, pattern in enumerate(patterns):
        examples_raw = pattern.get("domainIndustryExamples")
        if not isinstance(examples_raw, list):
            continue
        examples_list = cast(List[Any], examples_raw)
        for example_index, raw_item in enumerate(examples_list):
            if not isinstance(raw_item, dict):
                continue
            item = cast(Dict[str, Any], raw_item)
            task = item.get("task")
            prompt = item.get("prompt")
            if not isinstance(task, str) or not isinstance(prompt, str):
                continue
            if (
                not force
                and "category" in item
                and isinstance(item["category"], str)
            ):
                continue
            key = ExampleKey(task=task.strip(), prompt=prompt.strip())
            key_map[key].append(
                ExampleRef(
                    pattern_index=pattern_index,
                    example_index=example_index,
                    original=item,
                )
            )
    return key_map, patterns


def ensure_category_first(
    example: Dict[str, Any],
    category: str,
) -> Dict[str, Any]:
    ordered: Dict[str, Any] = {"category": category}
    if "task" in example:
        ordered["task"] = example["task"]
    if "prompt" in example:
        ordered["prompt"] = example["prompt"]
    for key, value in example.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def classify_examples(
    classifier: "DomainExampleClassifier",
    keys: Iterable[ExampleKey],
    cache: Dict[Tuple[str, str], str],
) -> Dict[Tuple[str, str], str]:
    remaining: List[ExampleKey] = []
    for key in keys:
        tuple_key = key.to_tuple()
        if tuple_key not in cache:
            remaining.append(key)
    if remaining:
        pairs = [key.to_tuple() for key in remaining]
        categories = classifier.classify_examples(pairs, cache=cache)
        for pair, category in zip(pairs, categories):
            cache[pair] = category
    return cache


def update_patterns(
    patterns: List[Dict[str, Any]],
    key_map: Dict[ExampleKey, List[ExampleRef]],
    cache: Dict[Tuple[str, str], str],
) -> Counter[str]:
    counters: Counter[str] = Counter()
    for key, refs in key_map.items():
        tuple_key = key.to_tuple()
        category = cache.get(tuple_key)
        if category is None:
            raise ValueError(f"Missing category for task '{key.task}'")
        for ref in refs:
            examples = patterns[ref.pattern_index]["domainIndustryExamples"]
            original = examples[ref.example_index]
            ordered = ensure_category_first(original, category)
            examples[ref.example_index] = ordered
            counters[category] += 1
    return counters


def reorder_existing_examples(patterns: List[Dict[str, Any]]) -> int:
    """Ensure category key precedes task and prompt for labelled examples."""

    reordered = 0
    for pattern in patterns:
        examples_raw = pattern.get("domainIndustryExamples")
        if not isinstance(examples_raw, list):
            continue
        examples_list = cast(List[Any], examples_raw)
        for index, raw_item in enumerate(examples_list):
            if not isinstance(raw_item, dict):
                continue
            item = cast(Dict[str, Any], raw_item)
            category = item.get("category")
            if not isinstance(category, str):
                continue
            ordered = ensure_category_first(item, category)
            if ordered is not item:
                examples_list[index] = ordered
                reordered += 1
    return reordered


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    data = load_json(args.input)
    key_map, patterns = collect_examples(data, force=args.force)
    if not key_map:
        print("No examples required classification.")
        # Still reorder any pre-labelled examples so category appears first.
        reordered_only = reorder_existing_examples(patterns)
        if reordered_only and not args.dry_run:
            output_path = args.output or args.input
            dump_json(data, output_path)
            print(f"Reordered {reordered_only} existing examples.")
            print(f"Wrote updated data to {output_path}")
        elif reordered_only:
            print(
                f"Dry run: would reorder {reordered_only} existing examples."
            )
        else:
            print("No reorder or classification changes required.")
        return

    if args.limit is not None:
        limited_keys = list(key_map.keys())[: args.limit]
        key_map = {key: key_map[key] for key in limited_keys}

    cache = load_cache(args.cache_file) if args.cache_file else {}
    classifier = create_classifier_instance()
    cache = classify_examples(classifier, key_map.keys(), cache)
    if args.cache_file:
        save_cache(cache, args.cache_file)

    stats = update_patterns(patterns, key_map, cache)
    print("Classifications applied:")
    for category, count in stats.most_common():
        print(f"  {category}: {count}")
    print(f"Total updated examples: {sum(stats.values())}")

    reordered_existing = reorder_existing_examples(patterns)
    if reordered_existing:
        print(
            f"Reordered {reordered_existing} previously categorised examples."
        )

    if args.dry_run:
        print("Dry run: no files written.")
        return

    output_path = args.output or args.input
    dump_json(data, output_path)
    print(f"Wrote updated data to {output_path}")


if __name__ == "__main__":
    main()
