#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Knowledge intent classification utilities."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

from azure_models import get_model_client

KNOWLEDGE_INTENT_DEFINITIONS: List[Tuple[str, str]] = [
    (
        "Refinement & Clarification",
        (
            "Human and AI already share the knowledge; prompts focus on "
            "polishing, validating, or reframing it."
        ),
    ),
    (
        "Knowledge Retrieval",
        (
            "Human lacks the knowledge while the AI can supply it directly "
            "through fact-finding or procedural recall."
        ),
    ),
    (
        "Co-Discovery & Exploration",
        (
            "Neither side starts with the answer and the prompt drives "
            "brainstorming, hypotheses, or speculative inquiry."
        ),
    ),
    (
        "AI Tutoring & Tuning",
        (
            "Human teaches or aligns the AI with their expertise, "
            "preferences, or frameworks to steer future responses."
        ),
    ),
]
KNOWLEDGE_INTENT_LABELS: List[str] = [
    name for name, _ in KNOWLEDGE_INTENT_DEFINITIONS
]

TABLE_LABEL_WIDTH = 30
TABLE_DESCRIPTION_WIDTH = 66


def _format_row(name: str, description: str) -> str:
    return (
        f"| {name:<{TABLE_LABEL_WIDTH}} | "
        f"{description:<{TABLE_DESCRIPTION_WIDTH}} |"
    )


def _build_intent_table() -> str:
    header = _format_row("Knowledge Intent", "Description")
    divider = _format_row(
        "-" * TABLE_LABEL_WIDTH,
        "-" * TABLE_DESCRIPTION_WIDTH,
    )
    rows: List[str] = [header, divider]
    for name, description in KNOWLEDGE_INTENT_DEFINITIONS:
        rows.append(_format_row(name, description))
    return "\n".join(rows)


KNOWLEDGE_INTENT_TABLE: str = _build_intent_table()

SYSTEM_PROMPT: str = dedent(
    """
    You are an expert annotator who assigns each prompt pattern to exactly one
    knowledge intent from the table below. Base the decision on the information
    provided about the pattern's purpose, guidance, and examples.
    Never invent new intent names and never return multiple intents.
    Always respond with strict JSON matching this schema:
    {"items": [{"index": 0, "knowledgeIntent": "<Knowledge Intent>"}]}
    """
).strip()


@dataclass(frozen=True)
class KnowledgeIntentRequest:
    """Classification payload for a single pattern."""

    pattern_id: Optional[str]
    name: str
    category: Optional[str]
    description: Optional[str]
    application: Optional[str]
    general_explanation: Optional[str]
    usage_summary: Optional[str]
    template: Optional[Dict[str, Any]]
    prompt_examples: Sequence[str]
    domain_industry_examples: Sequence[Dict[str, Any]]

    def cache_key(self) -> Tuple[str, str]:
        return (self.pattern_id or "", self.name or "")

    def to_payload(self) -> Dict[str, Any]:
        return {
            "patternId": self.pattern_id,
            "name": self.name,
            "category": self.category,
            "description": _clip(self.description, 900),
            "application": _clip(self.application, 320),
            "generalExplanation": _clip(self.general_explanation, 320),
            "usageSummary": _clip(self.usage_summary, 320),
            "template": _coerce_template(self.template),
            "promptExamples": _coerce_examples(self.prompt_examples, 3),
            "domainIndustryExamples": _coerce_domain_examples(
                self.domain_industry_examples,
                6,
            ),
        }


def _clip(value: Optional[str], max_chars: int) -> Optional[str]:
    if value is None:
        return None
    candidate = str(value).strip()
    if not candidate:
        return None
    if len(candidate) <= max_chars:
        return candidate
    return candidate[: max_chars - 1].rstrip() + "…"


def _coerce_examples(items: Sequence[Any], limit: int) -> List[str]:
    results: List[str] = []
    for raw in items:
        text = _clip(str(raw) if raw is not None else None, 280)
        if text:
            results.append(text)
        if len(results) >= limit:
            break
    return results


def _coerce_domain_examples(
    items: Sequence[Any],
    limit: int,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for entry in items:
        if not isinstance(entry, dict):
            continue
        entry_dict = cast(Dict[str, Any], entry)
        task_raw = entry_dict.get("task")
        prompt_raw = entry_dict.get("prompt")
        task = _clip(
            str(task_raw) if task_raw is not None else None,
            120,
        )
        prompt = _clip(
            str(prompt_raw) if prompt_raw is not None else None,
            320,
        )
        if not task or not prompt:
            continue
        payload = {"task": task, "prompt": prompt}
        prompt_type = entry_dict.get("promptType")
        if isinstance(prompt_type, str) and prompt_type.strip():
            prompt_type_text = _clip(prompt_type, 80)
            if prompt_type_text:
                payload["promptType"] = prompt_type_text
        results.append(payload)
        if len(results) >= limit:
            break
    return results


def _coerce_template(template: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(template, dict):
        return {}
    result: Dict[str, Any] = {}
    for key in ["role", "context", "action", "format", "response"]:
        value = template.get(key)
        text = _clip(str(value) if value is not None else None, 180)
        if text:
            result[key] = text
    return result


class KnowledgeIntentClassifier:
    """LLM-backed classifier for knowledge intent."""

    def __init__(
        self,
        model_name: str = "gpt-5",
        batch_size: int = 6,
        max_retries: int = 3,
        retry_sleep: float = 2.0,
    ) -> None:
        self.model_name = model_name
        self.batch_size = max(1, batch_size)
        self.max_retries = max(1, max_retries)
        self.retry_sleep = max(0.0, retry_sleep)
        self.client = cast(Any, get_model_client(model_name))

    def classify_requests(
        self,
        requests: Sequence[KnowledgeIntentRequest],
        cache: Optional[Dict[Tuple[str, str], str]] = None,
    ) -> List[str]:
        cache = cache if cache is not None else {}
        pending: List[Tuple[int, KnowledgeIntentRequest]] = []
        for idx, request in enumerate(requests):
            key = request.cache_key()
            if key in cache:
                continue
            pending.append((idx, request))

        if pending:
            ordered = [item for _, item in pending]
            for chunk_start in range(0, len(ordered), self.batch_size):
                chunk = ordered[chunk_start:chunk_start + self.batch_size]
                labels = self._classify_chunk(chunk)
                for req, label in zip(chunk, labels):
                    cache[req.cache_key()] = label

        results: List[str] = []
        for request in requests:
            label = cache.get(request.cache_key())
            if not label:
                raise ValueError(
                    "Missing knowledge intent label; "
                    "classification may have failed",
                )
            results.append(label)
        return results

    def _classify_chunk(
        self,
        chunk: Sequence[KnowledgeIntentRequest],
    ) -> List[str]:
        payload: List[Dict[str, Any]] = [
            {"index": idx, "pattern": item.to_payload()}
            for idx, item in enumerate(chunk)
        ]
        user_prompt = dedent(
            """
            Knowledge intent reference:
            {table}

            Review each pattern summary and return only the JSON structure
            described in the system instructions.
            Patterns:
            {entries}
            """
        ).format(
            table=KNOWLEDGE_INTENT_TABLE,
            entries=json.dumps(payload, ensure_ascii=False, indent=2),
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ]
                response: Any = self.client.create_chat_completion(
                    messages,
                    stream=False,
                )
                raw = self._extract_content(response)
                parsed = self._parse_response(raw)
                return [parsed[idx] for idx in range(len(chunk))]
            except Exception:
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.retry_sleep)
        raise RuntimeError(
            "Unexpected knowledge intent classification failure without "
            "exception"
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
        return str(content).strip()

    @staticmethod
    def _parse_response(raw: str) -> Dict[int, str]:
        data_obj = KnowledgeIntentClassifier._first_json_object(raw)
        if not isinstance(data_obj, dict) or "items" not in data_obj:
            raise ValueError("Classifier response missing 'items' array")
        data = cast(Dict[str, Any], data_obj)
        items_raw = data["items"]
        if not isinstance(items_raw, list):
            raise ValueError("Classifier items payload is not a list")
        items = cast(List[Any], items_raw)

        mapping: Dict[int, str] = {}
        for entry_raw in items:
            if not isinstance(entry_raw, dict):
                raise ValueError("Classifier item is not an object")
            entry = cast(Dict[str, Any], entry_raw)
            if "index" not in entry or "knowledgeIntent" not in entry:
                raise ValueError(
                    "Classifier entry missing index or knowledgeIntent",
                )
            idx_raw = entry.get("index")
            if idx_raw is None:
                raise ValueError("Classifier index is missing")
            try:
                idx = int(idx_raw)
            except (TypeError, ValueError) as exc:
                raise ValueError("Classifier index is not an integer") from exc
            label_value = entry.get("knowledgeIntent")
            label = str(label_value).strip()
            if label not in KNOWLEDGE_INTENT_LABELS:
                raise ValueError(
                    "Unsupported knowledge intent '"
                    f"{label}' in classifier response",
                )
            mapping[idx] = label
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
    "KNOWLEDGE_INTENT_DEFINITIONS",
    "KNOWLEDGE_INTENT_LABELS",
    "KNOWLEDGE_INTENT_TABLE",
    "KnowledgeIntentClassifier",
    "KnowledgeIntentRequest",
]
