#!/usr/bin/env python
"""Backfill knowledge intent labels for normalized prompt patterns."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
for path in (PROJECT_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from scripts.knowledge_intent_classifier import (  # noqa: E402
    KNOWLEDGE_INTENT_LABELS,
    KnowledgeIntentClassifier,
    KnowledgeIntentRequest,
)


@dataclass(frozen=True)
class PatternRef:
    """Pointer to a pattern entry so we can write back the label."""

    index: int
    cache_key: Tuple[str, str]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify patterns with knowledge intent labels.",
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
            "Optional output path; defaults to updating the input file."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show proposed labels without writing changes.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of patterns to classify (useful for testing).",
    )
    parser.add_argument(
        "--cache-file",
        type=Path,
        default=Path("tmp/knowledge_intent_cache.json"),
        help="Cache file for knowledge intent classifications.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reclassify even when knowledgeIntent already exists.",
    )
    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help="Comma-separated list of pattern IDs to target.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5",
        help="Model name to use for classification (default: gpt-5).",
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
        for entry_raw in entries:
            if not isinstance(entry_raw, dict):
                continue
            entry = cast(Dict[str, Any], entry_raw)
            pattern_id = entry.get("patternId")
            name = entry.get("name")
            label = entry.get("knowledgeIntent")
            if (
                isinstance(name, str)
                and isinstance(label, str)
                and label in KNOWLEDGE_INTENT_LABELS
            ):
                key = (pattern_id or "", name)
                result[key] = label
    return result


def save_cache(cache: Dict[Tuple[str, str], str], path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    serialised: List[Dict[str, Optional[str]]] = []
    for key, value in sorted(
        cache.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        serialised.append(
            {
                "patternId": key[0] or None,
                "name": key[1],
                "knowledgeIntent": value,
            }
        )
    path.write_text(
        json.dumps(serialised, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalise_sequence(raw: Any) -> List[str]:
    if isinstance(raw, list):
        entries = cast(List[Any], raw)
        return [str(item).strip() for item in entries if str(item).strip()]
    if isinstance(raw, str):
        return [part.strip() for part in raw.splitlines() if part.strip()]
    return []


def normalise_domain_examples(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    results: List[Dict[str, Any]] = []
    items = cast(List[Any], raw)
    for item in items:
        if isinstance(item, dict):
            results.append(cast(Dict[str, Any], item))
    return results


def build_request(pattern: Dict[str, Any]) -> KnowledgeIntentRequest:
    pattern_id = pattern.get("id")
    name = str(pattern.get("name") or pattern.get("patternName") or "").strip()
    category = pattern.get("category")
    description = pattern.get("description")
    application = pattern.get("application")
    general_explanation = pattern.get("generalExplanation")
    usage_summary = pattern.get("usageSummary")
    prompt_examples_raw = pattern.get("promptExamples")
    domain_examples_raw = pattern.get("domainIndustryExamples")
    template_raw = pattern.get("template")
    return KnowledgeIntentRequest(
        pattern_id=pattern_id if isinstance(pattern_id, str) else None,
        name=name,
        category=str(category) if category is not None else None,
        description=str(description) if description is not None else None,
        application=str(application) if application is not None else None,
        general_explanation=(
            str(general_explanation)
            if general_explanation is not None
            else None
        ),
        usage_summary=(
            str(usage_summary) if usage_summary is not None else None
        ),
        template=cast(Dict[str, Any], template_raw)
        if isinstance(template_raw, dict)
        else None,
        prompt_examples=normalise_sequence(prompt_examples_raw),
        domain_industry_examples=normalise_domain_examples(
            domain_examples_raw
        ),
    )


def set_knowledge_intent(pattern: Dict[str, Any], label: str) -> None:
    label = label.strip()
    new_items: List[Tuple[str, Any]] = []
    inserted = False
    for key, value in pattern.items():
        if key == "knowledgeIntent":
            continue
        new_items.append((key, value))
        if key == "generalExplanation":
            new_items.append(("knowledgeIntent", label))
            inserted = True
    if not inserted:
        new_items.append(("knowledgeIntent", label))
    pattern.clear()
    pattern.update(new_items)


def collect_targets(
    patterns: List[Dict[str, Any]],
    force: bool,
    selected_ids: Optional[Iterable[str]],
) -> Tuple[List[PatternRef], List[KnowledgeIntentRequest]]:
    targets: List[PatternRef] = []
    requests: List[KnowledgeIntentRequest] = []
    selected = set(selected_ids or [])
    for index, pattern in enumerate(patterns):
        if selected and pattern.get("id") not in selected:
            continue
        existing_label = pattern.get("knowledgeIntent")
        if (
            not force
            and isinstance(existing_label, str)
            and existing_label.strip() in KNOWLEDGE_INTENT_LABELS
        ):
            continue
        request = build_request(pattern)
        if not request.name:
            continue
        targets.append(
            PatternRef(
                index=index,
                cache_key=request.cache_key(),
            )
        )
        requests.append(request)
    return targets, requests


def update_patterns(
    patterns: List[Dict[str, Any]],
    targets: List[PatternRef],
    labels: List[str],
) -> Counter[str]:
    stats: Counter[str] = Counter()
    for ref, label in zip(targets, labels):
        pattern = patterns[ref.index]
        previous = pattern.get("knowledgeIntent")
        set_knowledge_intent(pattern, label)
        stats[label] += 1
        if previous != label:
            stats["__changed__"] += 1
    return stats


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    data = load_json(args.input)
    raw_patterns = data.get("patterns")
    if not isinstance(raw_patterns, list):
        print("normalized-patterns.json has unexpected format")
        return
    pattern_entries = cast(List[Any], raw_patterns)
    patterns: List[Dict[str, Any]] = [
        cast(Dict[str, Any], item)
        for item in pattern_entries
        if isinstance(item, dict)
    ]

    selected_ids = None
    if args.ids:
        selected_ids = [
            part.strip() for part in args.ids.split(",") if part.strip()
        ]

    targets, requests = collect_targets(patterns, args.force, selected_ids)
    if not targets:
        print("No patterns required knowledge intent classification.")
        return

    if args.limit is not None:
        requests = requests[: args.limit]
        targets = targets[: len(requests)]

    cache = load_cache(args.cache_file) if args.cache_file else {}
    classifier = KnowledgeIntentClassifier(model_name=args.model)
    labels = classifier.classify_requests(requests, cache=cache)
    if args.cache_file:
        for request, label in zip(requests, labels):
            cache[request.cache_key()] = label
        save_cache(cache, args.cache_file)

    stats = update_patterns(patterns, targets, labels)

    print("Knowledge intent classifications applied:")
    for label in KNOWLEDGE_INTENT_LABELS:
        count = stats.get(label, 0)
        if count:
            print(f"  {label}: {count}")
    changed = stats.get("__changed__", 0)
    print(f"Total patterns touched: {len(targets)}")
    print(f"New or updated labels: {changed}")

    if args.dry_run:
        print("Dry run: no files written.")
        return

    output_path = args.output or args.input
    dump_json(data, output_path)
    print(f"Wrote updated data to {output_path}")


if __name__ == "__main__":
    main()
