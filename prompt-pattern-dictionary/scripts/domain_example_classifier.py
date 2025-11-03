#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Domain example categorisation utilities."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

from azure_models import get_model_client

CATEGORY_DEFINITIONS: List[Tuple[str, str]] = [
    (
        "Coding Prompt",
        "Generate, debug, or explain code and programming concepts.",
    ),
    (
        "Idea Prompt",
        "Spark new ideas, brainstorm, or explore creative directions.",
    ),
    (
        "Marketing Prompt",
        "Create campaigns, strategies, and content for promoting "
        "products/services.",
    ),
    (
        "Assistant Prompt",
        "Roleplay as a helper, coach, or advisor for specific tasks.",
    ),
    (
        "Content Creation Prompt",
        "Produce structured content like blogs, posts, books, or frameworks.",
    ),
    (
        "Health Prompt",
        "Provide general wellness, patient-care, clinical, or hospital"
        " guidance.",
    ),
    (
        "Screenwriter Prompt",
        "Develop scripts, dialogue, and cinematic storytelling.",
    ),
    (
        "Cooking Prompt",
        "Suggest recipes, meal plans, or culinary techniques.",
    ),
    (
        "Copywriting Prompt",
        "Write persuasive sales, ad, or conversion-focused text.",
    ),
    (
        "Productivity Prompt",
        "Boost efficiency with workflows, routines, or motivational "
        "systems.",
    ),
    (
        "Storytelling Prompt",
        "Craft engaging narratives, characters, and plots.",
    ),
    (
        "Travel Prompt",
        "Plan trips, itineraries, or travel recommendations.",
    ),
    (
        "Business Prompt",
        "Explore strategies, planning, and problem-solving for "
        "businesses.",
    ),
    (
        "Email Prompt",
        "Draft professional, personal, or marketing emails.",
    ),
    (
        "Education Prompt",
        "Support learning, teaching, or study frameworks.",
    ),
    (
        "Writing Prompt",
        "Inspire creative writing, essays, or stylistic exercises.",
    ),
    (
        "Design Prompt",
        "Generate visual, UI/UX, or creative design ideas.",
    ),
    (
        "Career Prompt",
        "Offer job search, resume, or career development guidance.",
    ),
    (
        "Fun Prompts",
        "Lighthearted, playful, or entertaining activities and ideas.",
    ),
]

CATEGORY_NAMES: List[str] = [name for name, _ in CATEGORY_DEFINITIONS]

TABLE_NAME_WIDTH = 22
TABLE_DESCRIPTION_WIDTH = 52


def _format_row(name: str, description: str) -> str:
    return (
        f"| {name:<{TABLE_NAME_WIDTH}} | "
        f"{description:<{TABLE_DESCRIPTION_WIDTH}} |"
    )


def _build_category_table() -> str:
    header = _format_row("Prompt Category", "Description")
    divider = _format_row(
        "-" * TABLE_NAME_WIDTH,
        "-" * TABLE_DESCRIPTION_WIDTH,
    )
    rows: List[str] = [header, divider]
    for name, description in CATEGORY_DEFINITIONS:
        rows.append(_format_row(name, description))
    return "\n".join(rows)


CATEGORY_TABLE: str = _build_category_table()

SYSTEM_PROMPT: str = dedent(
    """
    You are an expert classifier who assigns each domain example to exactly one
    category from the table below.
    Choose the single best fit based on the task focus and the intent expressed
    in the prompt.
    Never invent new labels and never return multiple categories.
    Always respond with strict JSON matching this schema:
    {"items": [{"index": 0, "promptType": "<Prompt Type Name>"}]}
    """
).strip()


@dataclass
class ClassificationRequest:
    """Single classification payload."""

    task: str
    prompt: str


class DomainExampleClassifier:
    """LLM-backed classifier for domain examples."""

    def __init__(
        self,
        model_name: str = "gpt-5",
        batch_size: int = 8,
        max_retries: int = 3,
        retry_sleep: float = 2.0,
    ) -> None:
        self.model_name = model_name
        self.batch_size = max(1, batch_size)
        self.max_retries = max(1, max_retries)
        self.retry_sleep = max(0.0, retry_sleep)
        self.client = get_model_client(model_name)

    def classify_examples(
        self,
        examples: Sequence[Tuple[str, str]],
        cache: Optional[Dict[Tuple[str, str], str]] = None,
    ) -> List[str]:
        """Classify examples, respecting and updating the supplied cache."""

        cache = cache if cache is not None else {}
        pending: List[Tuple[int, ClassificationRequest]] = []
        for idx, (task, prompt) in enumerate(examples):
            key = (task, prompt)
            if key in cache:
                continue
            pending.append(
                (
                    idx,
                    ClassificationRequest(task=task, prompt=prompt),
                )
            )

        if pending:
            ordered = [item for _, item in pending]
            for chunk_start in range(0, len(ordered), self.batch_size):
                chunk = ordered[chunk_start: chunk_start + self.batch_size]
                chunk_categories = self._classify_chunk(chunk)
                for req, category in zip(chunk, chunk_categories):
                    cache[(req.task, req.prompt)] = category

        results: List[str] = []
        for task, prompt in examples:
            category = cache.get((task, prompt))
            if not category:
                raise ValueError(
                    "Missing category for an example; classification may have"
                    " failed",
                )
            results.append(category)
        return results

    def _classify_chunk(
        self,
        chunk: Sequence[ClassificationRequest],
    ) -> List[str]:
        payload: List[Dict[str, Any]] = [
            {"index": idx, "task": item.task, "prompt": item.prompt}
            for idx, item in enumerate(chunk)
        ]
        user_prompt = dedent(
            """
            Category reference:
            {table}

            Classify each entry and return only the JSON structure described in
            the system instructions.
            Entries:
            {entries}
            """
        ).format(
            table=CATEGORY_TABLE,
            entries=json.dumps(payload, ensure_ascii=False, indent=2),
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ]
                client: Any = self.client
                response: Any = client.create_chat_completion(
                    messages,
                    stream=False,
                )
                raw = self._extract_content(response)
                parsed = self._parse_response(raw)
                ordered = [parsed[idx] for idx in range(len(chunk))]
                return ordered
            except Exception:
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.retry_sleep)
        raise RuntimeError(
            "Unexpected classification failure without exception",
        )

    @staticmethod
    def _extract_content(response: Any) -> str:
        content: Optional[str] = None
        if hasattr(response, "choices") and getattr(response, "choices"):
            content = getattr(response.choices[0].message, "content", None)
        if not content and isinstance(response, dict):
            response_dict = cast(Dict[str, Any], response)
            choices = cast(
                List[Dict[str, Any]],
                response_dict.get("choices", []),
            )
            if choices:
                message = cast(
                    Dict[str, Any],
                    choices[0].get("message", {}),
                )
                content = cast(Optional[str], message.get("content"))
        if not content:
            raise ValueError("Model returned no content")
        content_str = str(content)
        return content_str.strip()

    @staticmethod
    def _parse_response(raw: str) -> Dict[int, str]:
        data_obj = DomainExampleClassifier._first_json_object(raw)
        if not isinstance(data_obj, dict) or "items" not in data_obj:
            raise ValueError("Classifier response missing 'items' array")
        data = cast(Dict[str, Any], data_obj)
        items_raw = data["items"]
        if not isinstance(items_raw, list):
            raise ValueError("Classifier items payload is not a list")
        items_list = cast(List[Any], items_raw)

        mapping: Dict[int, str] = {}
        for entry in items_list:
            if not isinstance(entry, dict):
                raise ValueError("Classifier item is not an object")
            if "index" not in entry or "promptType" not in entry:
                raise ValueError(
                    "Classifier entry missing index or promptType",
                )
            entry_dict = cast(Dict[str, Any], entry)
            try:
                idx = int(entry_dict["index"])
            except (TypeError, ValueError) as exc:
                raise ValueError("Classifier index is not an integer") from exc
            category = str(entry_dict["promptType"]).strip()
            if category not in CATEGORY_NAMES:
                raise ValueError(
                    f"Unsupported category '{category}' in classifier"
                    " response",
                )
            mapping[idx] = category
        return mapping

    @staticmethod
    def _first_json_object(text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                raise
            return json.loads(match.group(0))


__all__ = [
    "CATEGORY_DEFINITIONS",
    "CATEGORY_NAMES",
    "CATEGORY_TABLE",
    "ClassificationRequest",
    "DomainExampleClassifier",
]
