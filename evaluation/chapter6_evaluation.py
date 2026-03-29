# ruff: noqa: E501
# flake8: noqa
# pylint: disable=line-too-long
"""CLI for the thesis Chapter 6 evaluation framework.

This script implements the quantitative and qualitative workflows described in
``thesis-chapter6-evaluation-spec.md``. It is intentionally self-contained so
that the evaluation logic, prompt definitions, judging, and aggregation live in
one place under the ``evaluation/`` subtree.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Optional

from azure.identity import (
    DefaultAzureCredential,
    InteractiveBrowserCredential,
    get_bearer_token_provider,
)
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"
SUMMARY_DIR = SCRIPT_DIR / "summary"
COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"
DEFAULT_EVALUATION_MODELS = ["gpt-4.1", "gpt-5", "grok-4-fast-reasoning", "deepseek-r1-0528"]
DEFAULT_JUDGE_MODEL = "gpt-5.4-pro"
DEFAULT_CYBER_MODEL = "gpt-5"
DEFAULT_RUNS = 3
METRICS = ("accuracy", "formatting", "fabrication", "completeness")
VARIANT_TO_OUTPUT_KEY = {
    "naive": "output_a",
    "peil_labelled": "output_b",
    "peil_unlabelled": "output_c",
}


@dataclass(frozen=True)
class PatternDefinition:
    """Represents one quantitative pattern evaluation item."""

    key: str
    logic: str
    subcategory: str
    task_title: str
    task_description: str
    naive_request: str
    task_material: str
    role: str
    context: str
    instructions: tuple[str, ...]
    technique: str
    output: str
    reference_notes: str = ""
    source_paper_id: str = ""
    source_pattern_id: str = ""
    source_paper_title: str = ""
    source_pattern_name: str = ""

    def build_prompt(self, variant: str) -> str:
        """Return the prompt text for the requested variant."""
        if variant == "naive":
            parts = [self.naive_request.strip()]
            if self.task_material.strip():
                parts.append("Task Material:\n" + self.task_material.strip())
            return "\n\n".join(parts)

        instruction_block = "\n".join(
            f"{index}. {item}" for index, item in enumerate(self.instructions, start=1)
        )

        if variant == "peil_labelled":
            parts = [
                f"Role: {self.role.strip()}",
                f"Context: {self.context.strip()}",
                f"Instructions:\n{instruction_block}",
                f"Techniques: {self.technique.strip()}",
                f"Output: {self.output.strip()}",
            ]
        elif variant == "peil_unlabelled":
            parts = [
                self.role.strip(),
                self.context.strip(),
                instruction_block,
                self.technique.strip(),
                self.output.strip(),
            ]
        else:
            raise ValueError(f"Unsupported prompt variant: {variant}")

        if self.task_material.strip():
            parts.append("Task Material:\n" + self.task_material.strip())

        return "\n\n".join(parts)

    def to_metadata(self) -> dict[str, Any]:
        """Return a JSON-serializable metadata structure."""
        metadata = asdict(self)
        metadata["instructions"] = list(self.instructions)
        return metadata


@dataclass(frozen=True)
class CyberScenario:
    """Represents one qualitative cybersecurity case study item."""

    key: str
    title: str
    taxonomy_categories: tuple[str, ...]
    analysis_focus: str
    naive_prompt: str
    task_material: str
    role: str
    context: str
    instructions: tuple[str, ...]
    technique: str
    output: str

    def build_peil_prompt(self) -> str:
        """Return the PEIL prompt for the scenario."""
        instruction_block = "\n".join(
            f"{index}. {item}" for index, item in enumerate(self.instructions, start=1)
        )
        parts = [
            f"Role: {self.role.strip()}",
            f"Context: {self.context.strip()}",
            f"Instructions:\n{instruction_block}",
            f"Techniques: {self.technique.strip()}",
            f"Output: {self.output.strip()}",
        ]
        if self.task_material.strip():
            parts.append("Task Material:\n" + self.task_material.strip())
        return "\n\n".join(parts)

    def to_metadata(self) -> dict[str, Any]:
        """Return a JSON-serializable metadata structure."""
        metadata = asdict(self)
        metadata["taxonomy_categories"] = list(self.taxonomy_categories)
        metadata["instructions"] = list(self.instructions)
        return metadata


@dataclass(frozen=True)
class ModelSpec:
    """Represents one model deployment the CLI can call."""

    key: str
    label: str
    endpoint_env: Optional[str]
    deployment_env: Optional[str]
    default_endpoint: Optional[str]
    default_deployment: str
    api_key_env: Optional[str]
    use_responses_api: bool
    supports_temperature_zero: bool
    reasoning_effort: Optional[str] = None

    def resolve_endpoint(self) -> str:
        """Resolve the model endpoint from env or defaults."""
        endpoint = os.getenv(self.endpoint_env or "", "").strip()
        if not endpoint:
            endpoint = (self.default_endpoint or "").strip()
        if not endpoint:
            raise ValueError(f"No endpoint configured for model '{self.key}'")
        return normalize_base_url(endpoint)

    def resolve_deployment(self) -> str:
        """Resolve the deployment name from env or defaults."""
        deployment = os.getenv(self.deployment_env or "", "").strip()
        if not deployment:
            deployment = self.default_deployment
        if not deployment:
            raise ValueError(f"No deployment configured for model '{self.key}'")
        return deployment

    def resolve_api_key(self) -> Optional[str]:
        """Resolve the API key if one is configured for this model."""
        if not self.api_key_env:
            return None
        value = os.getenv(self.api_key_env, "").strip()
        return value or None


@dataclass(frozen=True)
class ResolvedModel:
    """Runtime configuration for a resolved model deployment."""

    spec: ModelSpec
    base_url: str
    deployment: str
    auth_mode: str
    api_key_or_provider: Any


def now_utc_iso() -> str:
    """Return the current UTC timestamp as an ISO string."""
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    """Write a timestamped log message to stdout."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def normalize_base_url(endpoint: str) -> str:
    """Normalize a resource endpoint into an OpenAI-compatible v1 URL."""
    stripped = endpoint.strip().rstrip("/")
    stripped = stripped.replace(
        ".cognitiveservices.azure.com",
        ".openai.azure.com",
    )
    if stripped.endswith("/openai/v1"):
        return stripped + "/"
    if stripped.endswith("/openai/v1/"):
        return stripped
    return stripped + "/openai/v1/"


def safe_float(value: Any) -> Optional[float]:
    """Convert values to float when possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity for two vectors."""
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def ensure_parent(path: Path) -> None:
    """Create the parent directory for a file path."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with stable formatting."""
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def strip_code_fences(text: str) -> str:
    """Remove Markdown code fences from model output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()


def extract_json_payload(text: str) -> Any:
    """Parse JSON from plain text or fenced output."""
    cleaned = strip_code_fences(text)
    if not cleaned:
        raise ValueError("Empty response text — no JSON payload to extract")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in response text: {cleaned[:200]}")
        return json.loads(match.group(0))


def comma_separated_list(raw: Optional[str]) -> list[str]:
    """Parse a comma-separated CLI option."""
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_model_registry() -> dict[str, ModelSpec]:
    """Return the known model registry for the evaluation workflow."""
    return {
        "gpt-4.1": ModelSpec(
            key="gpt-4.1",
            label="GPT-4.1",
            endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
            deployment_env="AZUREVSEASTUS2_OPENAI_GPT41_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVSEASTUS2_OPENAI_KEY",
            use_responses_api=True,
            supports_temperature_zero=True,
        ),
        "gpt-5": ModelSpec(
            key="gpt-5",
            label="GPT-5.2",
            endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
            deployment_env="AZUREVSEASTUS2_OPENAI_GPT52_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVSEASTUS2_OPENAI_KEY",
            use_responses_api=True,
            supports_temperature_zero=False,
            reasoning_effort="medium",
        ),
        "grok-4-fast-reasoning": ModelSpec(
            key="grok-4-fast-reasoning",
            label="Grok-4-fast-reasoning",
            endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
            deployment_env="AZUREVSEASTUS2_GROK4_FAST_REASONING_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVSEASTUS2_OPENAI_KEY",
            use_responses_api=False,
            supports_temperature_zero=True,
        ),
        "deepseek-r1-0528": ModelSpec(
            key="deepseek-r1-0528",
            label="DeepSeek-R1-0528",
            endpoint_env="AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT",
            deployment_env="AZUREVS_DEEPSEEK_R1_0528_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVS_OPENAI_GPT45PREVIEW_KEY",
            use_responses_api=False,
            supports_temperature_zero=True,
        ),
        "deepseek-v3.2": ModelSpec(
            key="deepseek-v3.2",
            label="DeepSeek-V3.2",
            endpoint_env="AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT",
            deployment_env="AZUREVS_DEEPSEEK_V32_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVS_OPENAI_GPT45PREVIEW_KEY",
            use_responses_api=False,
            supports_temperature_zero=True,
        ),
        "gpt-5.4-pro": ModelSpec(
            key="gpt-5.4-pro",
            label="GPT-5.4-pro",
            endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
            deployment_env="AZUREVSEASTUS2_OPENAI_GPT54PRO_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVSEASTUS2_OPENAI_KEY",
            use_responses_api=True,
            supports_temperature_zero=False,
            reasoning_effort="medium",
        ),
        "embedding-3": ModelSpec(
            key="embedding-3",
            label="text-embedding-3-large",
            endpoint_env="AZUREVS_OPENAI_ENDPOINT",
            deployment_env="AZUREVS_OPENAI_EMBEDDING3_MODEL",
            default_endpoint=None,
            default_deployment="",
            api_key_env="AZUREVS_OPENAI_KEY",
            use_responses_api=False,
            supports_temperature_zero=False,
        ),
    }


MODEL_REGISTRY = build_model_registry()


class AzureModelRuntime:
    """Creates cached OpenAI clients for Azure-hosted model deployments."""

    def __init__(self, auth_mode: str) -> None:
        self.auth_mode = auth_mode
        self._client_cache: dict[tuple[str, str], OpenAI] = {}
        self._resolved_cache: dict[str, ResolvedModel] = {}
        self._credential: Optional[DefaultAzureCredential] = None

    def resolve_model(self, model_key: str) -> ResolvedModel:
        """Resolve one model into a runtime configuration."""
        if model_key in self._resolved_cache:
            return self._resolved_cache[model_key]

        if model_key not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model key: {model_key}")

        spec = MODEL_REGISTRY[model_key]
        api_key = spec.resolve_api_key()

        if self.auth_mode == "api_key":
            if not api_key:
                raise ValueError(f"Model '{model_key}' requires an API key for auth_mode=api_key")
            auth_mode = "api_key"
            credential = api_key
        elif self.auth_mode == "entra":
            auth_mode = "entra"
            credential = self._get_token_provider()
        else:
            if api_key:
                auth_mode = "api_key"
                credential = api_key
            else:
                auth_mode = "entra"
                credential = self._get_token_provider()

        resolved = ResolvedModel(
            spec=spec,
            base_url=spec.resolve_endpoint(),
            deployment=spec.resolve_deployment(),
            auth_mode=auth_mode,
            api_key_or_provider=credential,
        )
        self._resolved_cache[model_key] = resolved
        return resolved

    def get_client(self, model_key: str) -> tuple[OpenAI, ResolvedModel]:
        """Return a cached OpenAI client and its resolved model config."""
        resolved = self.resolve_model(model_key)
        cache_key = (resolved.base_url, resolved.auth_mode)
        if cache_key not in self._client_cache:
            self._client_cache[cache_key] = OpenAI(
                base_url=resolved.base_url,
                api_key=resolved.api_key_or_provider,
            )
        return self._client_cache[cache_key], resolved

    def generate_text(
        self,
        model_key: str,
        prompt: str,
        *,
        json_schema: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Call a model and return normalized output data."""
        client, resolved = self.get_client(model_key)
        spec = resolved.spec
        if spec.use_responses_api:
            return self._call_responses_api(
                client,
                resolved,
                prompt,
                json_schema=json_schema,
            )
        return self._call_chat_completions(
            client,
            resolved,
            prompt,
        )

    def embed_text(self, text: str) -> list[float]:
        """Create an embedding using the configured text-embedding deployment."""
        client, resolved = self.get_client("embedding-3")
        response = self._with_retries(
            lambda: client.embeddings.create(
                model=resolved.deployment,
                input=text,
            )
        )
        return list(response.data[0].embedding)

    def _get_token_provider(self) -> Any:
        """Return a bearer token provider for Azure auth."""
        if self._credential is None:
            tenant_id = os.getenv("AZURE_TENANT_ID", "").strip() or None
            if tenant_id:
                self._credential = DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    interactive_browser_tenant_id=tenant_id,
                )
            else:
                # Use InteractiveBrowserCredential so the user can pick
                # the right tenant when multiple are available.
                self._credential = InteractiveBrowserCredential()
        return get_bearer_token_provider(self._credential, COGNITIVE_SCOPE)

    def _with_retries(self, operation: Any, attempts: int = 3, delay_seconds: float = 2.0) -> Any:
        """Run an API operation with simple retry behavior."""
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                return operation()
            except Exception as exc:  # pragma: no cover - defensive network path
                last_error = exc
                if attempt == attempts:
                    break
                time.sleep(delay_seconds * attempt)
        if last_error is None:
            raise RuntimeError("Operation failed without raising an exception")
        raise last_error

    def _call_responses_api(
        self,
        client: OpenAI,
        resolved: ResolvedModel,
        prompt: str,
        *,
        json_schema: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Call the Responses API and normalize the result."""
        request: dict[str, Any] = {
            "model": resolved.deployment,
            "input": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        if resolved.spec.reasoning_effort:
            request["reasoning"] = {"effort": resolved.spec.reasoning_effort, "summary": "auto"}
        if resolved.spec.supports_temperature_zero:
            request["temperature"] = 0.0
        if json_schema is not None:
            request["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": json_schema["name"],
                    "schema": json_schema["schema"],
                    "strict": True,
                }
            }

        try:
            response = self._with_retries(lambda: client.responses.create(**request))
        except Exception:
            if json_schema is None:
                raise
            fallback_request = dict(request)
            fallback_request.pop("text", None)
            fallback_request["input"] = [
                {
                    "role": "user",
                    "content": prompt
                    + "\n\nReturn valid JSON only. Do not wrap the JSON in Markdown fences.",
                }
            ]
            response = self._with_retries(lambda: client.responses.create(**fallback_request))

        output_text = getattr(response, "output_text", "") or self._extract_response_output(response)
        usage = self._extract_response_usage(response)
        return {
            "text": output_text.strip(),
            "reasoning_content": None,
            "response_id": getattr(response, "id", None),
            "usage": usage,
            "auth_mode": resolved.auth_mode,
            "api": "responses",
            "model": resolved.deployment,
            "base_url": resolved.base_url,
            "temperature": 0.0 if resolved.spec.supports_temperature_zero else None,
        }

    def _call_chat_completions(
        self,
        client: OpenAI,
        resolved: ResolvedModel,
        prompt: str,
    ) -> dict[str, Any]:
        """Call the Chat Completions API and normalize the result."""
        request: dict[str, Any] = {
            "model": resolved.deployment,
            "messages": [{"role": "user", "content": prompt}],
        }
        if resolved.spec.supports_temperature_zero:
            request["temperature"] = 0.0

        response = self._with_retries(lambda: client.chat.completions.create(**request))
        message = response.choices[0].message
        usage = self._extract_chat_usage(response)
        return {
            "text": (message.content or "").strip(),
            "reasoning_content": getattr(message, "reasoning_content", None),
            "response_id": getattr(response, "id", None),
            "usage": usage,
            "auth_mode": resolved.auth_mode,
            "api": "chat.completions",
            "model": resolved.deployment,
            "base_url": resolved.base_url,
            "temperature": 0.0 if resolved.spec.supports_temperature_zero else None,
        }

    @staticmethod
    def _extract_response_output(response: Any) -> str:
        """Extract output text from a Responses API object."""
        outputs: list[str] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for content_item in getattr(item, "content", []) or []:
                    if getattr(content_item, "type", None) == "output_text":
                        outputs.append(getattr(content_item, "text", ""))
        return "\n".join(part for part in outputs if part)

    @staticmethod
    def _extract_response_usage(response: Any) -> dict[str, Optional[float]]:
        """Extract usage fields from a Responses API object."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
        input_tokens = safe_float(getattr(usage, "input_tokens", None))
        output_tokens = safe_float(getattr(usage, "output_tokens", None))
        total_tokens = safe_float(getattr(usage, "total_tokens", None))
        if total_tokens is None and input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    @staticmethod
    def _extract_chat_usage(response: Any) -> dict[str, Optional[float]]:
        """Extract usage fields from a Chat Completions object."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
        input_tokens = safe_float(getattr(usage, "prompt_tokens", None))
        output_tokens = safe_float(getattr(usage, "completion_tokens", None))
        total_tokens = safe_float(getattr(usage, "total_tokens", None))
        if total_tokens is None and input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }


def build_quantitative_patterns() -> list[PatternDefinition]:
    """Return the 18 quantitative evaluation patterns grounded in promptpatterns.json research papers."""
    return [
        # ── ACROSS LOGIC (3 patterns) ──────────────────────────────────────
        PatternDefinition(
            key="across_argument_debate_opening",
            logic="Across",
            subcategory="Argument",
            task_title="Write a debate opening statement",
            task_description="Write a concise opening argument for a structured online debate on whether remote work improves employee productivity.",
            naive_request='Pretend to be engaging in an online debate on the topic of "Remote work improves employee productivity". You have been randomly assigned to argue in favour of the proposition. Please write your Opening argument. You should not exceed 4 sentences. Important: Do not start with greetings or address the opponent first.',
            task_material="",
            role="You are an online debater specialising in workplace policy who constructs concise, evidence-grounded opening statements.",
            context="You are defending the proposition that remote work improves employee productivity in a structured text-based debate. Your audience includes neutral judges evaluating clarity, evidence, and persuasiveness.",
            instructions=(
                "State your position clearly in the first sentence.",
                "Provide two supporting points with brief evidence or reasoning.",
                "Close with a forward-looking statement that frames the rest of the debate.",
                "Do not exceed four sentences. Do not use greetings or address the opponent.",
            ),
            technique="Use dialectical reasoning to present a clear thesis with supporting evidence before concluding.",
            output="Return a 2-4 sentence opening argument with no greetings.",
            reference_notes="A strong answer states a clear position, provides evidence-backed reasoning, and stays under four sentences without greetings.",
            source_paper_id="62",
            source_pattern_id="62-0-0",
            source_paper_title="On the Conversational Persuasiveness of Large Language Models: A Randomized Controlled Trial",
            source_pattern_name="Opening",
        ),
        PatternDefinition(
            key="across_comparison_attendance",
            logic="Across",
            subcategory="Comparison",
            task_title="Compare two numeric values and select the larger",
            task_description="Given two attendance figures from different rounds, determine which round had the higher attendance.",
            naive_request="Q: What was the attendance when round was SF 2nd Leg? A: 34,669\nQ: What was the attendance when round was QFR? A: 33,861\nWhich round had a higher attendance?",
            task_material="",
            role="You are a data comparison analyst who extracts numeric values, normalises formatting, and identifies the larger value.",
            context="You are comparing attendance figures from two sporting event rounds. The figures may include thousands separators that must be handled correctly.",
            instructions=(
                "Extract the numeric attendance value for each round.",
                "Handle thousands separators (commas) correctly during comparison.",
                "State which round has the higher attendance.",
                "Provide the numeric values to justify the comparison.",
            ),
            technique="Use step-by-step numeric extraction and comparison before stating the result.",
            output="Return the round name with the higher attendance and both numeric values.",
            reference_notes="Correct answer: SF 2nd Leg (34,669 > 33,861).",
            source_paper_id="20",
            source_pattern_id="20-2-0",
            source_paper_title="Successive Prompting for Decomposing Complex Questions",
            source_pattern_name="What round had a higher attendance: SF 2nd Leg or QFR?",
        ),
        PatternDefinition(
            key="across_translation_summarise_translate",
            logic="Across",
            subcategory="Translation",
            task_title="Summarise a text and translate to French",
            task_description="Produce a concise English summary of the provided text and then translate that summary into French.",
            naive_request="Summarize the following text, then translate the summary to French.\n\nText: Cloud computing has transformed how organisations deploy and manage infrastructure. By shifting from on-premises servers to elastic cloud services, businesses reduce capital expenditure and gain the ability to scale resources on demand. However, this shift introduces new challenges around data sovereignty, vendor lock-in, and shared responsibility for security. Organisations must carefully evaluate provider SLAs, data residency requirements, and exit strategies before committing to a cloud-first approach.",
            task_material="Cloud computing has transformed how organisations deploy and manage infrastructure. By shifting from on-premises servers to elastic cloud services, businesses reduce capital expenditure and gain the ability to scale resources on demand. However, this shift introduces new challenges around data sovereignty, vendor lock-in, and shared responsibility for security. Organisations must carefully evaluate provider SLAs, data residency requirements, and exit strategies before committing to a cloud-first approach.",
            role="You are a bilingual technical writer who produces concise summaries and accurate French translations.",
            context="The summary will be shared with both English-speaking and French-speaking stakeholders. Preserve technical accuracy and flag any ambiguous idioms.",
            instructions=(
                "Summarise the text in 2-3 concise English sentences.",
                "Translate the summary into French, preserving tone and terminology.",
                "Flag any idiomatic expressions that may not translate directly.",
                "Do not add information beyond what the source text contains.",
            ),
            technique="Use hierarchical summarisation first, then apply careful bilingual translation preserving key technical terms.",
            output="Return two sections: English Summary and French Translation.",
            reference_notes="A strong answer produces a faithful summary and an accurate French translation without adding new claims.",
            source_paper_id="30",
            source_pattern_id="30-6-0",
            source_paper_title="Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing",
            source_pattern_name="Summarization and Translation",
        ),
        # ── AT LOGIC (3 patterns) ─────────────────────────────────────────
        PatternDefinition(
            key="at_assessment_expert_rating",
            logic="At",
            subcategory="Assessment",
            task_title="Rate platforms using weighted criteria",
            task_description="As an expert in online learning, weight evaluation criteria and rate six communication platforms.",
            naive_request="As an expert in the field of online learning, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task is to weight the criteria.",
            task_material="Criteria: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, user experiences.\nPlatforms: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, FaceTime.\nScale: Very Low, Low, Medium Low, Medium, Medium High, High, Very High.",
            role="You are an expert in online learning and educational technology evaluation.",
            context="You are providing a structured assessment for a university selecting a communication platform. The evaluation must be transparent, consistent, and justifiable to stakeholders.",
            instructions=(
                "First, assign and justify weights for each of the seven criteria.",
                "Then rate each of the six platforms on every criterion using the provided scale.",
                "Present the results in a clear table format.",
                "Note any significant strengths or limitations for each platform.",
            ),
            technique="Use rubric-based assessment with explicit criteria weighting before applying ratings systematically.",
            output="Return a criteria weighting table followed by a platform rating matrix.",
            reference_notes="A strong answer provides justified weights and consistent ratings across all platforms and criteria.",
            source_paper_id="3",
            source_pattern_id="3-0-0",
            source_paper_title="A Novel Framework leveraging Prompt Engineering and the Grey-Based Approach",
            source_pattern_name="Expert",
        ),
        PatternDefinition(
            key="at_calculation_math_word_problems",
            logic="At",
            subcategory="Calculation",
            task_title="Solve a multi-step math word problem",
            task_description="Solve the word problem using step-by-step arithmetic and provide the final answer.",
            naive_request="Q: There were nine computers in the server room. Five more computers were installed each day, from Monday to Thursday. How many computers are now in the server room?",
            task_material="",
            role="You are a careful arithmetic problem solver who shows all working.",
            context="The result will be used in an operational report, so arithmetic accuracy is more important than prose quality.",
            instructions=(
                "Identify the starting quantity.",
                "Calculate the total additions over the specified period.",
                "Sum the starting quantity and additions.",
                "State the final answer clearly on a separate line.",
            ),
            technique="Use explicit step-by-step arithmetic and verify the final answer with a re-check.",
            output="Return the working steps and end with: The answer is [number].",
            reference_notes="Correct calculation: 9 + (5 * 4) = 9 + 20 = 29. The answer is 29.",
            source_paper_id="31",
            source_pattern_id="31-0-0",
            source_paper_title="Chain-of-thought prompting elicits reasoning in large language models",
            source_pattern_name="Math Word Problems",
        ),
        PatternDefinition(
            key="at_assessment_opinion_verification",
            logic="At",
            subcategory="Assessment",
            task_title="Verify the truth of a factual claim",
            task_description="Assess whether the provided statement is true, providing a verdict with reasoning and uncertainty.",
            naive_request="As a rational being who believes in scientific knowledge, do you think the following statement is true?\nThe Great Wall of China is visible from space with the naked eye.",
            task_material="",
            role="You are a fact-verification specialist who separates evidence-based claims from common misconceptions.",
            context="The user needs a clear, defensible verdict to inform a decision. Distinguish facts from opinions, flag missing context, and cite sources or explain limitations.",
            instructions=(
                "State whether the claim is true, false, or uncertain.",
                "Provide the key evidence or reasoning behind the verdict.",
                "Note any nuance, context-dependence, or common misconceptions.",
                "Keep the response concise and decision-ready.",
            ),
            technique="Use evidence tracing and chain-of-verification to check the claim against established knowledge before stating a verdict.",
            output="Return a clear verdict (True / False / Uncertain) followed by a brief justification.",
            reference_notes="The claim is false. The Great Wall is generally not visible from low Earth orbit with the naked eye, contrary to popular myth.",
            source_paper_id="37",
            source_pattern_id="37-0-0",
            source_paper_title="Reliability Check: An Analysis of GPT-3's Response to Sensitive Topics and Prompt Wording",
            source_pattern_name="Opinion Verification",
        ),
        # ── BEYOND LOGIC (3 patterns) ─────────────────────────────────────
        PatternDefinition(
            key="beyond_logical_reasoning_premise_question",
            logic="Beyond",
            subcategory="Logical Reasoning",
            task_title="Reason step-by-step from premises to conclusion",
            task_description="Apply premise-to-question reasoning to determine whether a conclusion follows from the given premises.",
            naive_request="Premise 1: All managers in the company have completed leadership training.\nPremise 2: Sarah is a manager in the company.\nPremise 3: The leadership training includes a module on conflict resolution.\nConclusion: Sarah has completed a module on conflict resolution.\nDoes the conclusion follow from the premises?",
            task_material="",
            role="You are a logical reasoning specialist who validates conclusions through disciplined premise analysis.",
            context="The analysis will be used to assess whether a policy conclusion is logically sound. The answer should show structured reasoning, not just a yes/no verdict.",
            instructions=(
                "List the premises explicitly.",
                "Turn each premise into a question to identify alternatives.",
                "Reason step by step using both lists, tracking branches.",
                "State whether the conclusion follows and explain why.",
            ),
            technique="Use premise-question reasoning: convert premises to questions, explore alternatives, and reason through branches before concluding.",
            output="Return the listed premises, the derived questions, the step-by-step reasoning, and a final verdict.",
            reference_notes="The conclusion follows: Sarah is a manager (P2), all managers completed training (P1), training includes conflict resolution (P3), therefore Sarah completed a conflict resolution module.",
            source_paper_id="33",
            source_pattern_id="33-1-1",
            source_paper_title="Humans in Humans Out: On GPT Converging Toward CommonSense in both Success and Failure",
            source_pattern_name="Premise-Question Reasoning",
        ),
        PatternDefinition(
            key="beyond_hypothesise_theory_of_mind",
            logic="Beyond",
            subcategory="Hypothesise",
            task_title="Infer a person's beliefs from a scenario",
            task_description="Read the scenario and answer where the unaware person will look for the moved item.",
            naive_request="We will read about a scenario, and then have a question and answer session about it.\n--\nScenario:\nAlice and Bob have a shared Dropbox folder.\nAlice puts a file called 'photo.png' inside /shared_folder/photos.\nBob notices Alice put the file there, and moves the file to /shared_folder/photos/family without telling Alice.\n--\nQ: After the file is moved, where does Alice think the file is?",
            task_material="",
            role="You are a theory-of-mind analyst who infers what a person believes based on what they know and do not know.",
            context="This tests the ability to distinguish between what is objectively true and what a specific person believes based on their limited knowledge.",
            instructions=(
                "Identify what Alice knows and does not know.",
                "Identify what Bob did and whether Alice is aware of it.",
                "Reason about Alice's belief state based on her information.",
                "State where Alice thinks the file is and explain why.",
            ),
            technique="Use perspective-taking: separate objective facts from each person's knowledge state before answering.",
            output="State where Alice thinks the file is and explain the reasoning based on her knowledge.",
            reference_notes="Alice thinks the file is in /shared_folder/photos because she put it there and was not told about the move.",
            source_paper_id="32",
            source_pattern_id="32-26-0",
            source_paper_title="Sparks of artificial general intelligence: Early experiments with GPT-4",
            source_pattern_name="Understanding beliefs",
        ),
        PatternDefinition(
            key="beyond_simulation_change_request",
            logic="Beyond",
            subcategory="Simulation",
            task_title="Simulate a system change and assess impact",
            task_description="Simulate adding a new mandatory field to an API and list the affected components.",
            naive_request="My software system uses an OpenAPI specification for a user registration service with endpoints POST /users and GET /users/{id}. I want you to simulate a change where a new mandatory field 'phone_number' needs to be added to the user registration. List which functions and which files will need to be modified.",
            task_material="System: A REST API for user registration built with Python/FastAPI.\nEndpoints: POST /users (create user), GET /users/{id} (retrieve user).\nCurrent fields: name, email, password.\nProposed change: Add mandatory 'phone_number' field.",
            role="You are a software architect who simulates proposed system changes and identifies affected components.",
            context="The team needs to understand the blast radius of this change before implementation. The assessment will inform sprint planning and test coverage.",
            instructions=(
                "List the components affected by adding the mandatory field.",
                "For each affected component, describe the required modification.",
                "Identify any risks or side effects of the change.",
                "Suggest the order of implementation and testing.",
            ),
            technique="Use impact analysis simulation: trace the new field through all layers (API spec, validation, storage, tests) to identify every affected component.",
            output="Return a structured impact analysis with affected files, required changes, risks, and implementation order.",
            reference_notes="A strong answer should identify changes in the API schema, request validation, database model, serialisation, tests, and documentation.",
            source_paper_id="1",
            source_pattern_id="1-0-2",
            source_paper_title="ChatGPT Prompt Patterns for Improving Code Quality, Refactoring, Requirements Elicitation, and Software Design",
            source_pattern_name="Change Request Simulation",
        ),
        # ── IN LOGIC (3 patterns) ─────────────────────────────────────────
        PatternDefinition(
            key="in_error_identification_hallucination_judge",
            logic="In",
            subcategory="Error Identification",
            task_title="Judge whether an answer contains hallucination",
            task_description="Given a question, an answer, and related knowledge, determine if the answer contains non-factual or hallucinated information.",
            naive_request='I want you to act as an answer judge. Given a question and an answer, your objective is to determine if the provided answer contains non-factual or hallucinated information. You SHOULD give your judgement based on the following hallucination types and the world knowledge.\n\nQuestion: What is the capital of Australia?\nAnswer: The capital of Australia is Sydney, which was chosen as the capital when the country was federated in 1901.\nKnowledge: The capital of Australia is Canberra. It was chosen as a compromise between Sydney and Melbourne, with the capital officially moving to Canberra in 1927.',
            task_material="Question: What is the capital of Australia?\nAnswer: The capital of Australia is Sydney, which was chosen as the capital when the country was federated in 1901.\nKnowledge: The capital of Australia is Canberra. It was chosen as a compromise between Sydney and Melbourne, with the capital officially moving to Canberra in 1927.",
            role="You are a hallucination detection judge who identifies factual contradictions, fabrications, and unsupported claims in model outputs.",
            context="You are evaluating an LLM answer against verified knowledge to detect hallucination. Your judgment must distinguish between factual errors, context misunderstanding, and fabricated details.",
            instructions=(
                "Compare the answer against the provided knowledge.",
                "Identify any factual contradictions between the answer and the knowledge.",
                "Check whether any claims in the answer are fabricated or unsupported.",
                "State your verdict: Hallucinated or Not Hallucinated, with specific evidence.",
            ),
            technique="Use chain-of-verification: compare each claim in the answer against the knowledge base systematically before judging.",
            output="Return a verdict (Hallucinated / Not Hallucinated) with specific evidence of any errors found.",
            reference_notes="The answer is hallucinated: it states Sydney is the capital (incorrect, it is Canberra) and gives a wrong date for the capital decision.",
            source_paper_id="8",
            source_pattern_id="8-0-0",
            source_paper_title="HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models",
            source_pattern_name="Hallucination Evaluation",
        ),
        PatternDefinition(
            key="in_classification_relevancy_check",
            logic="In",
            subcategory="Categorising",
            task_title="Classify whether a sentence contains a specific property with data",
            task_description="Determine whether the provided sentence is relevant for further analysis by checking if it contains the specified property with a numeric value and units.",
            naive_request="Is the following sentence relevant for further analysis? Does it contain the data for the property in question (value and units)?\n\nProperty: tensile strength\nSentence: The measured tensile strength of the sample was 450 MPa at room temperature.",
            task_material="Property: tensile strength\nSentence: The measured tensile strength of the sample was 450 MPa at room temperature.",
            role="You are a data extraction specialist who triages sentences for relevance to a specified material property.",
            context="This classification step filters sentences from research papers before detailed data extraction. Only sentences containing the target property with numeric values and units should pass.",
            instructions=(
                "Check if the sentence mentions the specified property.",
                "Check if the sentence contains a numeric value with units for that property.",
                "State whether the sentence is relevant (Yes) or not (No).",
                "Briefly explain why.",
            ),
            technique="Use criteria-based classification: check each required element (property mention, numeric value, units) before deciding relevance.",
            output="Return Yes or No followed by a brief justification.",
            reference_notes="Yes: the sentence mentions tensile strength (the target property) with a value of 450 and units of MPa.",
            source_paper_id="18",
            source_pattern_id="18-0-0",
            source_paper_title="Extracting Accurate Materials Data from Research Papers with Conversational Language Models and Prompt Engineering",
            source_pattern_name="Initial relevancy prompt",
        ),
        PatternDefinition(
            key="in_refactoring_template_filling",
            logic="In",
            subcategory="Refactoring",
            task_title="Fill placeholders in a provided template",
            task_description="Given a template with marked placeholders, fill each placeholder while preserving the template formatting.",
            naive_request="I am going to provide a template for your output. Everything in all caps is a placeholder. Any time that you generate text, try to fit it into one of the placeholders that I list. Please preserve the formatting and overall template that I provide at https://myapi.com/NAME/profile/JOB",
            task_material="Template: https://myapi.com/NAME/profile/JOB\nPlaceholder NAME: a realistic full name\nPlaceholder JOB: a realistic job title",
            role="You are a template-filling assistant who populates marked placeholders while preserving all surrounding formatting.",
            context="The output will be consumed by an automated system, so structural consistency is critical. Only replace the explicit placeholders.",
            instructions=(
                "Identify all placeholders (text in ALL CAPS) in the template.",
                "Replace each placeholder with appropriate content.",
                "Preserve all non-placeholder text and formatting exactly.",
                "If a placeholder cannot be filled, flag it rather than guessing.",
            ),
            technique="Use schema-constrained formatting: identify each placeholder, substitute content, and verify the output preserves the original structure.",
            output="Return the filled template with placeholders replaced and all other text preserved.",
            reference_notes="A strong answer replaces NAME and JOB with realistic values while keeping the URL structure intact.",
            source_paper_id="0",
            source_pattern_id="0-1-4",
            source_paper_title="A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT",
            source_pattern_name="Template",
        ),
        # ── OUT LOGIC (3 patterns) ────────────────────────────────────────
        PatternDefinition(
            key="out_output_customisation_knapsack_code",
            logic="Out",
            subcategory="Output Customisation",
            task_title="Generate Python code to solve a knapsack problem",
            task_description="Generate executable Python code that solves the 0/1 knapsack problem optimally for the given items and prints the chosen items with totals.",
            naive_request="Generate a code to solve this problem for Google Colab. Use the following items for the code: Item 1: Value - 8, Weight - 3 kg; Item 2: Value - 6, Weight - 2 kg; Item 3: Value - 10, Weight - 5 kg; Item 4: Value - 3, Weight - 1 kg; Item 5: Value - 7, Weight - 4 kg. Maximum weight capacity: 10 kg.",
            task_material="Items: (Value=8, Weight=3kg), (Value=6, Weight=2kg), (Value=10, Weight=5kg), (Value=3, Weight=1kg), (Value=7, Weight=4kg). Maximum weight: 10 kg.",
            role="You are a Python developer who writes clean, optimised code for combinatorial optimisation problems.",
            context="The code will run in a Colab notebook. It must solve the 0/1 knapsack optimally and print the selected items with their values, weights, and totals.",
            instructions=(
                "Implement the 0/1 knapsack algorithm in Python.",
                "Use the provided items and maximum weight capacity.",
                "Print the selected items with their values and weights.",
                "Print the total value and total weight of the solution.",
            ),
            technique="Use structured chain-of-thought for algorithm design: define the problem, implement the solution, and verify with a clear printout.",
            output="Return executable Python code with clear output showing selected items and totals.",
            reference_notes="Optimal solution: Items 1, 2, 4, 5 (or equivalent) with maximum total value within 10 kg weight limit.",
            source_paper_id="50",
            source_pattern_id="50-1-1",
            source_paper_title="Prompt Engineering: a methodology for optimizing interactions with AI-Language Models in the field of engineering",
            source_pattern_name="Code Generation for Optimization Problem",
        ),
        PatternDefinition(
            key="out_decomposed_prompting_letter_concat",
            logic="Out",
            subcategory="Decomposed Prompting",
            task_title="Decompose a string manipulation task into sub-steps",
            task_description="Break down the task of extracting and concatenating the first letter of each word into explicit, numbered sub-questions with intermediate results.",
            naive_request='Concatenate the first letter of every word in "Jack Ryan" using spaces.',
            task_material="",
            role="You are a task decomposition specialist who breaks complex operations into numbered sub-questions with bracketed operations.",
            context="This tests the ability to decompose a string manipulation task into verifiable intermediate steps rather than jumping to the answer.",
            instructions=(
                "Split the input into individual words.",
                "Extract the first letter of each word.",
                "Concatenate the extracted letters using spaces.",
                "Present each step as a numbered sub-question with its result.",
            ),
            technique="Use decomposed prompting: break the task into ordered sub-questions with bracketed operations ([split], [str_pos], [merge]) and numbered outputs.",
            output="Return the decomposed steps in QC/Q1/Q2/Q3 format with intermediate results, ending with the final answer.",
            reference_notes='Correct decomposition: split into ["Jack", "Ryan"], extract first letters ["J", "R"], merge with spaces to get "J R".',
            source_paper_id="6",
            source_pattern_id="6-0-0",
            source_paper_title="Decomposed Prompting: A Modular Approach for Solving Complex Tasks",
            source_pattern_name="Decomposed Prompt",
        ),
        PatternDefinition(
            key="out_context_control_explicit_constraints",
            logic="Out",
            subcategory="Context Control",
            task_title="Summarise a topic within explicit constraints",
            task_description="Summarise the main points of photosynthesis in exactly three sentences.",
            naive_request="Summarize the main points of photosynthesis in three sentences.",
            task_material="",
            role="You are a science communicator who produces constrained, accurate summaries.",
            context="The summary must meet an exact sentence count constraint. Accuracy and completeness within the constraint are both important.",
            instructions=(
                "Cover the key aspects of photosynthesis: inputs, process, and outputs.",
                "Use exactly three sentences — no more, no fewer.",
                "Ensure scientific accuracy in all statements.",
                "Keep the language accessible to a general audience.",
            ),
            technique="Use explicit constraint adherence: plan the three sentences to cover inputs, process, and outputs before writing.",
            output="Return exactly three sentences summarising photosynthesis.",
            reference_notes="A strong answer covers light energy, carbon dioxide and water as inputs, the conversion process in chloroplasts, and glucose and oxygen as outputs — all in exactly three sentences.",
            source_paper_id="46",
            source_pattern_id="46-0-1",
            source_paper_title="Prompt Engineering for ChatGPT - A Quick Guide To Techniques, Tips, and Best Practices",
            source_pattern_name="Using explicit constraints",
        ),
        # ── OVER LOGIC (3 patterns) ───────────────────────────────────────
        PatternDefinition(
            key="over_summarisation_chain_of_density",
            logic="Over",
            subcategory="Summarisation",
            task_title="Generate entity-dense iterative summaries",
            task_description="Generate five increasingly entity-dense summaries of the provided article, each the same length, progressively adding missing salient entities.",
            naive_request='Article: Cloud computing has transformed how organisations deploy and manage infrastructure. By shifting from on-premises servers to elastic cloud services, businesses reduce capital expenditure and gain the ability to scale resources on demand. Major providers including Amazon Web Services, Microsoft Azure, and Google Cloud Platform compete on pricing, global reach, and managed service breadth. However, this shift introduces challenges around data sovereignty, vendor lock-in, and shared responsibility for security. The 2023 Flexera State of the Cloud report found that 65 percent of enterprise workloads now run in public cloud environments, up from 50 percent in 2020. Organisations must carefully evaluate provider SLAs, data residency requirements, and exit strategies before committing.\n\nYou will generate increasingly concise, entity-dense summaries of the above Article.\nRepeat the following 2 steps 5 times.\nStep 1. Identify 1-3 informative Entities from the Article which are missing from the previously generated summary.\nStep 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.\nA Missing Entity is:\n- Relevant to the main story,\n- Specific yet concise (5 words or fewer),\n- Novel (not in the previous summary),\n- Faithful (present in the Article),\n- Anywhere (can be located anywhere in the Article).\nReturn a JSON list of 5 dictionaries with keys "Missing_Entities" and "Denser_Summary".',
            task_material="Cloud computing has transformed how organisations deploy and manage infrastructure. By shifting from on-premises servers to elastic cloud services, businesses reduce capital expenditure and gain the ability to scale resources on demand. Major providers including Amazon Web Services, Microsoft Azure, and Google Cloud Platform compete on pricing, global reach, and managed service breadth. However, this shift introduces challenges around data sovereignty, vendor lock-in, and shared responsibility for security. The 2023 Flexera State of the Cloud report found that 65 percent of enterprise workloads now run in public cloud environments, up from 50 percent in 2020. Organisations must carefully evaluate provider SLAs, data residency requirements, and exit strategies before committing.",
            role="You are a summarisation specialist who produces iteratively denser summaries that preserve entities and key details.",
            context="The output will be used to evaluate how well models handle progressive entity-dense summarisation. Each summary must be the same length as the previous one but contain more salient entities.",
            instructions=(
                "Start with a broad entity-sparse summary of the article.",
                "Identify 1-3 informative missing entities from the article for each iteration.",
                "Rewrite the summary at the same length, incorporating the new entities by compressing language.",
                "Never drop entities from previous summaries. Repeat for 5 iterations total.",
            ),
            technique="Use chain-of-density summarisation: iteratively compress language to add entities without increasing length.",
            output='Return a JSON list of 5 dictionaries, each with keys "Missing_Entities" and "Denser_Summary".',
            reference_notes="Key entities to incorporate: AWS/Azure/GCP, Flexera report, 65 percent, data sovereignty, vendor lock-in, SLAs.",
            source_paper_id="38",
            source_pattern_id="38-0-0",
            source_paper_title="From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting",
            source_pattern_name="Initial Entity-Sparse Summary",
        ),
        PatternDefinition(
            key="over_synthesis_claim_extraction",
            logic="Over",
            subcategory="Synthesis",
            task_title="Extract atomic claims from a book summary",
            task_description="Break a summary into self-contained atomic claims that can each be independently verified against the source text.",
            naive_request='You are trying to verify the faithfulness of statements made in a given summary of a book against the actual text of the book. To do so, you first need to break the summary into a set of "atomic claims", each of which will then be passed to a human who will verify its faithfulness. Each claim should be self-contained with all the necessary context. Each claim should contain no more than two sentences. Each individual claim should be on its own line prefixed by a "- ".\n\nSummary: In the novel, detective Maria Santos investigates a series of disappearances in the coastal town of Porto Azul during the summer of 2019. She discovers that the missing persons were all members of a local sailing club and had recently voted to sell the club\'s historic waterfront property to a development company. Her investigation reveals that the club\'s treasurer, Carlos Mendez, orchestrated the disappearances to prevent the sale and preserve the property for personal financial gain.',
            task_material='Summary: In the novel, detective Maria Santos investigates a series of disappearances in the coastal town of Porto Azul during the summer of 2019. She discovers that the missing persons were all members of a local sailing club and had recently voted to sell the club\'s historic waterfront property to a development company. Her investigation reveals that the club\'s treasurer, Carlos Mendez, orchestrated the disappearances to prevent the sale and preserve the property for personal financial gain.',
            role="You are a claim extraction specialist who decomposes summaries into independently verifiable atomic statements.",
            context="Each extracted claim will be passed to a human fact-checker who will verify it against the source text. Claims must be self-contained so the checker does not need additional context.",
            instructions=(
                "Break the summary into atomic, self-contained claims.",
                "Each claim must include sufficient context to be verified independently.",
                "Limit each claim to no more than two sentences.",
                "Prefix each claim with a dash and put each on its own line.",
            ),
            technique="Use structured decomposition: parse the summary sentence by sentence and extract each discrete factual assertion as a standalone claim.",
            output="Return a list of atomic claims, each prefixed with a dash on its own line.",
            reference_notes="Should extract claims about: Maria Santos as detective, Porto Azul as setting, summer 2019 timing, sailing club membership, vote to sell property, development company, Carlos Mendez as treasurer, his motive.",
            source_paper_id="63",
            source_pattern_id="63-0-0",
            source_paper_title="FABLES: Evaluating faithfulness and content selection in book-length summarization",
            source_pattern_name="Claim Extraction",
        ),
        PatternDefinition(
            key="over_summarisation_text_summary",
            logic="Over",
            subcategory="Summarisation",
            task_title="Summarise a research paper on climate change",
            task_description="Produce a concise, neutral summary of the provided text highlighting main arguments, key findings, and conclusions.",
            naive_request="Please provide a summary of the main arguments and findings presented in the following article on the effects of climate change on ocean ecosystems.",
            task_material="Rising ocean temperatures and acidification are fundamentally altering marine ecosystems worldwide. Research published between 2020 and 2025 shows that coral bleaching events have increased in frequency by 40 percent compared to the previous decade. Species migration patterns are shifting poleward at an average rate of 70 kilometres per decade, disrupting established food webs. The IPCC Sixth Assessment Report projects that even under moderate emissions scenarios, 70 to 90 percent of tropical coral reefs face severe degradation by 2050. Meanwhile, ocean deoxygenation is creating expanding dead zones, particularly in the Eastern Pacific and Bay of Bengal. Adaptation strategies including marine protected areas, assisted migration, and blue carbon restoration show promise but face significant scaling challenges. The economic impact on fisheries-dependent communities is estimated at $10 billion annually by 2030.",
            role="You are an executive communications analyst who produces neutral, concise research summaries.",
            context="The summary will be used to brief decision-makers who need the key findings without the full article. Neutrality and accuracy are more important than brevity.",
            instructions=(
                "Identify the main arguments presented in the text.",
                "Highlight the key quantitative findings.",
                "Note the conclusions and any implications or limitations.",
                "Keep the summary concise and maintain a neutral tone.",
            ),
            technique="Use hierarchical summarisation: capture the central thesis first, then distil the most important supporting evidence.",
            output="Return a concise summary of 3-5 sentences covering arguments, findings, and conclusions.",
            reference_notes="Key findings to include: 40% increase in bleaching, 70km/decade species migration, 70-90% coral degradation by 2050, expanding dead zones, $10B annual fisheries impact.",
            source_paper_id="71",
            source_pattern_id="71-25-0",
            source_paper_title="ChatGPT for higher education and professional development: A guide to conversational AI",
            source_pattern_name="Text Summarization",
        ),
    ]


def build_cybersecurity_scenarios() -> list[CyberScenario]:
    """Return the three qualitative cybersecurity case studies."""
    return [
        CyberScenario(
            key="threat_intelligence_analysis",
            title="Threat Intelligence Analysis",
            taxonomy_categories=("In Logic -> Error Identification",),
            analysis_focus="Identify indicators of compromise and explain what improved in the PEIL version.",
            naive_prompt="Look at these logs and tell me if there are any threats.",
            task_material=(
                "Network log excerpts:\n"
                "2026-03-14T01:22:11Z src=185.77.12.44 dst=vpn-gateway action=failed-login user=jsmith\n"
                "2026-03-14T01:22:18Z src=185.77.12.44 dst=vpn-gateway action=failed-login user=finance-admin\n"
                "2026-03-14T01:23:04Z src=185.77.12.44 dst=vpn-gateway action=success-login user=finance-admin\n"
                "2026-03-14T01:27:41Z src=185.77.12.44 dst=fs-fin-01 action=smb-read path=/invoices/Q1\n"
                "2026-03-14T01:28:55Z src=185.77.12.44 dst=mail-01 action=inbox-rule-create user=finance-admin rule='forward all external'\n"
                "2026-03-14T01:31:14Z src=185.77.12.44 dst=fs-fin-01 action=smb-write path=/tools/7z.exe\n"
            ),
            role="You are a senior cybersecurity threat analyst.",
            context="You are reviewing raw event data to identify likely indicators of compromise for an internal incident triage call.",
            instructions=(
                "Identify the most important indicators of compromise from the logs.",
                "Explain what each indicator suggests about attacker behavior.",
                "Distinguish clearly between evidence and inference.",
                "Finish with the top three immediate investigation actions.",
            ),
            technique="Use step-by-step evidence analysis and avoid claiming certainty where the logs only suggest intent.",
            output="Present the result as a short incident triage brief with sections Indicators, Assessment, and Immediate Actions.",
        ),
        CyberScenario(
            key="secure_code_generation",
            title="Secure Code Generation",
            taxonomy_categories=(
                "Across Logic -> Cross Boundary",
                "Out Logic -> Output Customisation",
            ),
            analysis_focus="Compare how much safer and more explicit the PEIL-generated code is.",
            naive_prompt="Write a Python login function.",
            task_material="Requirement: generate a Python function that handles user authentication with proper input validation.",
            role="You are a security engineer implementing authentication code for a production web service.",
            context="The code should reflect OWASP-aligned defensive practices suitable for a real engineering review, not just a toy example.",
            instructions=(
                "Generate a Python example that validates input safely and avoids insecure shortcuts.",
                "Include password verification via a secure hash comparison placeholder rather than plain-text checking.",
                "Note the main security controls in concise comments.",
                "Do not include hard-coded credentials or insecure storage patterns.",
            ),
            technique="Use adversarial thinking by considering how an attacker would exploit weak input handling, credential storage, and error messages.",
            output="Return documented Python code followed by a short note listing the applied security controls.",
        ),
        CyberScenario(
            key="incident_report_generation",
            title="Incident Report Generation",
            taxonomy_categories=("Over Logic -> Synthesis", "Out Logic -> Output Customisation"),
            analysis_focus="Compare the structure, completeness, and professionalism of the resulting report.",
            naive_prompt="Write an incident report about this security event.",
            task_material=(
                "Raw event data:\n"
                "- Date: 21 March 2026\n"
                "- Business unit: Finance\n"
                "- Trigger: suspicious payment confirmation forwarding rule\n"
                "- Initial access: compromised third-party vendor account\n"
                "- Affected systems: Exchange Online, finance-share\n"
                "- Confirmed impact: 27 invoice files accessed, mail forwarding rule created\n"
                "- Containment: vendor account disabled, forwarding rule removed, file share isolated\n"
                "- Open question: whether any invoices were exfiltrated externally"
            ),
            role="You are an incident response lead drafting a formal cybersecurity incident report.",
            context="The report will be sent to management and auditors, so it must be structured, factual, and suitable for formal review.",
            instructions=(
                "Write the report with standard sections for Summary, Timeline, Impact, Containment, and Open Questions.",
                "Use only the facts provided and distinguish unknowns from confirmed facts.",
                "Keep the tone formal and professional.",
                "Highlight the remaining uncertainty around possible exfiltration.",
            ),
            technique="Use structured synthesis to combine the raw facts into a formal document while preserving evidentiary discipline.",
            output="Return a formal incident report with the requested section headings.",
        ),
    ]


PATTERNS = build_quantitative_patterns()
PATTERN_INDEX = {pattern.key: pattern for pattern in PATTERNS}
CYBER_SCENARIOS = build_cybersecurity_scenarios()
CYBER_SCENARIO_INDEX = {scenario.key: scenario for scenario in CYBER_SCENARIOS}


def build_judge_schema() -> dict[str, Any]:
    """Return the JSON schema for judge output."""
    metric_schema = {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "minimum": 1, "maximum": 5},
            "justification": {"type": "string"},
        },
        "required": ["score", "justification"],
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "properties": {
            "accuracy": metric_schema,
            "formatting": metric_schema,
            "fabrication": metric_schema,
            "completeness": metric_schema,
        },
        "required": ["accuracy", "formatting", "fabrication", "completeness"],
        "additionalProperties": False,
    }
    return {
        "name": "judge_scores",
        "schema": {
            "type": "object",
            "properties": {
                "output_a": output_schema,
                "output_b": output_schema,
                "output_c": output_schema,
            },
            "required": ["output_a", "output_b", "output_c"],
            "additionalProperties": False,
        },
    }


def build_reproducibility_schema() -> dict[str, Any]:
    """Return the JSON schema for LLM-based reproducibility assessment."""
    return {
        "name": "reproducibility_assessment",
        "schema": {
            "type": "object",
            "properties": {
                "functionally_identical": {"type": "boolean"},
                "justification": {"type": "string"},
                "material_differences": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["functionally_identical", "justification", "material_differences"],
            "additionalProperties": False,
        },
    }


JUDGE_SCHEMA = build_judge_schema()
REPRODUCIBILITY_SCHEMA = build_reproducibility_schema()


def quantitative_model_path(pattern_key: str, model_key: str) -> Path:
    """Return the output directory for one quantitative pattern/model pair."""
    return RESULTS_DIR / pattern_key / model_key


def case_study_model_path(scenario_key: str, model_key: str) -> Path:
    """Return the output directory for one qualitative scenario/model pair."""
    return RESULTS_DIR / "case_studies" / scenario_key / model_key


def generation_path(pattern_key: str, model_key: str, run_index: int, variant: str) -> Path:
    """Return the path for one generation artifact."""
    return quantitative_model_path(pattern_key, model_key) / f"run_{run_index}_{variant}.json"


def judge_path(pattern_key: str, model_key: str) -> Path:
    """Return the path for the judge output."""
    return quantitative_model_path(pattern_key, model_key) / "judge_scores.json"


def reproducibility_path(pattern_key: str, model_key: str) -> Path:
    """Return the path for reproducibility output."""
    return quantitative_model_path(pattern_key, model_key) / "reproducibility.json"


def scenario_output_path(scenario_key: str, model_key: str, variant: str) -> Path:
    """Return the path for one qualitative artifact."""
    return case_study_model_path(scenario_key, model_key) / f"{variant}.json"


def build_quantitative_prompt_metadata(pattern: PatternDefinition, variant: str) -> dict[str, Any]:
    """Return prompt metadata for generation files."""
    return {
        "pattern": pattern.to_metadata(),
        "variant": variant,
        "prompt": pattern.build_prompt(variant),
    }


def save_generation_artifact(
    path: Path,
    *,
    pattern: PatternDefinition,
    variant: str,
    run_index: int,
    model_key: str,
    response_data: dict[str, Any],
) -> None:
    """Persist one generation artifact."""
    payload = {
        "timestamp_utc": now_utc_iso(),
        "pattern": pattern.to_metadata(),
        "variant": variant,
        "run_index": run_index,
        "model_key": model_key,
        "model_deployment": response_data["model"],
        "api": response_data["api"],
        "auth_mode": response_data["auth_mode"],
        "base_url": response_data["base_url"],
        "temperature": response_data["temperature"],
        "prompt": pattern.build_prompt(variant),
        "output": response_data["text"],
        "reasoning_content": response_data.get("reasoning_content"),
        "response_id": response_data.get("response_id"),
        "usage": response_data.get("usage", {}),
    }
    write_json(path, payload)


def generate_quantitative_artifact(
    runtime: AzureModelRuntime,
    pattern: PatternDefinition,
    model_key: str,
    variant: str,
    run_index: int,
    force: bool,
) -> dict[str, Any]:
    """Generate or load one quantitative artifact."""
    path = generation_path(pattern.key, model_key, run_index, variant)
    if path.exists() and not force:
        return read_json(path)

    response_data = runtime.generate_text(
        model_key,
        pattern.build_prompt(variant),
    )
    save_generation_artifact(
        path,
        pattern=pattern,
        variant=variant,
        run_index=run_index,
        model_key=model_key,
        response_data=response_data,
    )
    return read_json(path)


def build_judge_prompt(pattern: PatternDefinition, outputs: dict[str, str]) -> str:
    """Return the judge prompt for one pattern."""
    return (
        "Role: You are an expert evaluator assessing the quality of LLM outputs for a prompt engineering research study.\n\n"
        "Context: You are comparing three outputs generated from the same task: Output A from a naive prompt, Output B from a PEIL-structured prompt with labels, and Output C from the same PEIL content without labels. Your evaluation must be objective, consistent, and evidence-based.\n\n"
        "Instructions:\n"
        "1. Read the task description and evaluation reference carefully.\n"
        "2. Score each output independently on Output Accuracy, Formatting Consistency, Fabrication Reduction, and Task Completeness using the 1-5 rubric implied by the study.\n"
        "3. Provide a short evidence-based justification for each score.\n"
        "4. Do not let ordering bias your judgment.\n\n"
        "Techniques: Think step-by-step about evidence, but return only the final JSON.\n\n"
        "Output: Return JSON only.\n\n"
        f"Task Title: {pattern.task_title}\n"
        f"Task Description: {pattern.task_description}\n"
        f"Taxonomy Logic: {pattern.logic}\n"
        f"Subcategory: {pattern.subcategory}\n"
        f"Evaluation Reference: {pattern.reference_notes or 'No extra reference provided.'}\n\n"
        f"Output A (naive):\n{outputs['naive']}\n\n"
        f"Output B (PEIL labelled):\n{outputs['peil_labelled']}\n\n"
        f"Output C (PEIL unlabelled):\n{outputs['peil_unlabelled']}"
    )


def judge_pattern_outputs(
    runtime: AzureModelRuntime,
    pattern: PatternDefinition,
    model_key: str,
    judge_model_key: str,
    force: bool,
) -> dict[str, Any]:
    """Judge the first-run outputs for one quantitative pattern/model pair."""
    path = judge_path(pattern.key, model_key)
    if path.exists() and not force:
        return read_json(path)

    outputs = {
        variant: read_json(generation_path(pattern.key, model_key, 1, variant))["output"]
        for variant in VARIANT_TO_OUTPUT_KEY
    }
    max_judge_attempts = 3
    scores = None
    last_error = None
    for attempt in range(1, max_judge_attempts + 1):
        judge_result = runtime.generate_text(
            judge_model_key,
            build_judge_prompt(pattern, outputs),
            json_schema=JUDGE_SCHEMA,
        )
        try:
            scores = extract_json_payload(judge_result["text"])
            break
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            log(f"  Judge JSON parse failed attempt {attempt}/{max_judge_attempts} ({exc})")
            if attempt < max_judge_attempts:
                time.sleep(2)
    if scores is None:
        raise RuntimeError(f"Judge failed after {max_judge_attempts} attempts: {last_error}")
    payload = {
        "timestamp_utc": now_utc_iso(),
        "pattern": pattern.to_metadata(),
        "evaluated_model_key": model_key,
        "judge_model_key": judge_model_key,
        "judge_model_deployment": judge_result["model"],
        "api": judge_result["api"],
        "auth_mode": judge_result["auth_mode"],
        "response_id": judge_result.get("response_id"),
        "usage": judge_result.get("usage", {}),
        "scores": scores,
    }
    write_json(path, payload)
    return payload


def build_reproducibility_prompt(pattern: PatternDefinition, variant: str, outputs: list[str]) -> str:
    """Return the prompt used to assess functional identity across runs."""
    variant_label = {
        "naive": "naive",
        "peil_labelled": "PEIL labelled",
        "peil_unlabelled": "PEIL unlabelled",
    }[variant]
    return (
        "Role: You are an expert evaluator assessing reproducibility across repeated model runs.\n\n"
        "Context: You are comparing three outputs generated by the same model from the same prompt variant. Minor wording differences should count as reproducible if the outputs are functionally equivalent.\n\n"
        "Instructions:\n"
        "1. Compare the outputs for meaning, structure, and whether they satisfy the same task in materially the same way.\n"
        "2. Decide whether the outputs are functionally identical for research purposes.\n"
        "3. Briefly explain the decision and list any material differences.\n\n"
        "Techniques: Reason carefully, but return only the final JSON.\n\n"
        f"Task: {pattern.task_title}\n"
        f"Variant: {variant_label}\n"
        f"Evaluation Reference: {pattern.reference_notes or 'No extra reference provided.'}\n\n"
        f"Run 1:\n{outputs[0]}\n\n"
        f"Run 2:\n{outputs[1]}\n\n"
        f"Run 3:\n{outputs[2]}"
    )


def compute_reproducibility(
    runtime: AzureModelRuntime,
    pattern: PatternDefinition,
    model_key: str,
    judge_model_key: str,
    force: bool,
) -> dict[str, Any]:
    """Compute pairwise semantic similarity plus LLM reproducibility judgment."""
    path = reproducibility_path(pattern.key, model_key)
    if path.exists() and not force:
        return read_json(path)

    variant_results: dict[str, Any] = {}
    for variant in VARIANT_TO_OUTPUT_KEY:
        run_artifacts = [
            read_json(generation_path(pattern.key, model_key, run_index, variant))
            for run_index in range(1, DEFAULT_RUNS + 1)
        ]
        outputs = [artifact["output"] for artifact in run_artifacts]
        embeddings = [runtime.embed_text(text) for text in outputs]
        pairwise: dict[str, float] = {}
        similarities: list[float] = []
        for left_index, right_index in combinations(range(DEFAULT_RUNS), 2):
            score = cosine_similarity(embeddings[left_index], embeddings[right_index])
            key = f"run_{left_index + 1}_run_{right_index + 1}"
            pairwise[key] = round(score, 6)
            similarities.append(score)
        max_repro_attempts = 3
        llm_assessment = None
        last_error = None
        for attempt in range(1, max_repro_attempts + 1):
            llm_result = runtime.generate_text(
                judge_model_key,
                build_reproducibility_prompt(pattern, variant, outputs),
                json_schema=REPRODUCIBILITY_SCHEMA,
            )
            try:
                llm_assessment = extract_json_payload(llm_result["text"])
                break
            except (ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                log(f"  Reproducibility JSON parse failed attempt {attempt}/{max_repro_attempts} ({exc})")
                if attempt < max_repro_attempts:
                    time.sleep(2)
        if llm_assessment is None:
            raise RuntimeError(f"Reproducibility assessment failed after {max_repro_attempts} attempts: {last_error}")
        variant_results[variant] = {
            "pairwise_similarity": pairwise,
            "mean_similarity": round(mean(similarities), 6),
            "llm_assessment": llm_assessment,
            "judge_usage": llm_result.get("usage", {}),
        }

    payload = {
        "timestamp_utc": now_utc_iso(),
        "pattern": pattern.to_metadata(),
        "evaluated_model_key": model_key,
        "judge_model_key": judge_model_key,
        "variants": variant_results,
    }
    write_json(path, payload)
    return payload


def run_quantitative(
    runtime: AzureModelRuntime,
    *,
    model_keys: list[str],
    judge_model_key: str,
    pattern_keys: list[str],
    runs: int,
    force: bool,
) -> None:
    """Execute the quantitative evaluation workflow."""
    if runs != DEFAULT_RUNS:
        raise ValueError("This implementation currently expects exactly 3 runs for reproducibility.")

    for pattern_key in pattern_keys:
        pattern = PATTERN_INDEX[pattern_key]
        for model_key in model_keys:
            log(f"Quantitative: pattern={pattern.key} model={model_key}")
            for run_index in range(1, runs + 1):
                for variant in VARIANT_TO_OUTPUT_KEY:
                    generate_quantitative_artifact(
                        runtime,
                        pattern,
                        model_key,
                        variant,
                        run_index,
                        force,
                    )
            judge_pattern_outputs(runtime, pattern, model_key, judge_model_key, force)
            compute_reproducibility(runtime, pattern, model_key, judge_model_key, force)


def save_case_study_artifact(
    path: Path,
    *,
    scenario: CyberScenario,
    variant: str,
    model_key: str,
    prompt: str,
    response_data: dict[str, Any],
) -> None:
    """Persist one qualitative case study artifact."""
    payload = {
        "timestamp_utc": now_utc_iso(),
        "scenario": scenario.to_metadata(),
        "variant": variant,
        "model_key": model_key,
        "model_deployment": response_data["model"],
        "api": response_data["api"],
        "auth_mode": response_data["auth_mode"],
        "base_url": response_data["base_url"],
        "temperature": response_data["temperature"],
        "prompt": prompt,
        "output": response_data["text"],
        "reasoning_content": response_data.get("reasoning_content"),
        "response_id": response_data.get("response_id"),
        "usage": response_data.get("usage", {}),
    }
    write_json(path, payload)


def run_case_studies(
    runtime: AzureModelRuntime,
    *,
    model_key: str,
    scenario_keys: list[str],
    force: bool,
) -> None:
    """Execute the qualitative cybersecurity scenarios."""
    for scenario_key in scenario_keys:
        scenario = CYBER_SCENARIO_INDEX[scenario_key]
        log(f"Case study: scenario={scenario.key} model={model_key}")
        prompt_map = {
            "naive": scenario.naive_prompt + "\n\nTask Material:\n" + scenario.task_material,
            "peil": scenario.build_peil_prompt(),
        }
        for variant, prompt in prompt_map.items():
            path = scenario_output_path(scenario.key, model_key, variant)
            if path.exists() and not force:
                continue
            response_data = runtime.generate_text(model_key, prompt)
            save_case_study_artifact(
                path,
                scenario=scenario,
                variant=variant,
                model_key=model_key,
                prompt=prompt,
                response_data=response_data,
            )


def collect_judge_records() -> list[dict[str, Any]]:
    """Flatten all quantitative judge files into a record list."""
    records: list[dict[str, Any]] = []
    for pattern in PATTERNS:
        pattern_root = RESULTS_DIR / pattern.key
        if not pattern_root.exists():
            continue
        for model_dir in sorted(path for path in pattern_root.iterdir() if path.is_dir()):
            judge_file = model_dir / "judge_scores.json"
            if not judge_file.exists():
                continue
            payload = read_json(judge_file)
            scores = payload["scores"]
            for variant, output_key in VARIANT_TO_OUTPUT_KEY.items():
                for metric in METRICS:
                    score_block = scores[output_key][metric]
                    records.append(
                        {
                            "pattern_key": pattern.key,
                            "logic": pattern.logic,
                            "subcategory": pattern.subcategory,
                            "model_key": payload["evaluated_model_key"],
                            "variant": variant,
                            "metric": metric,
                            "score": score_block["score"],
                            "justification": score_block["justification"],
                        }
                    )
    return records


def collect_reproducibility_records() -> list[dict[str, Any]]:
    """Flatten reproducibility files into a record list."""
    records: list[dict[str, Any]] = []
    for pattern in PATTERNS:
        pattern_root = RESULTS_DIR / pattern.key
        if not pattern_root.exists():
            continue
        for model_dir in sorted(path for path in pattern_root.iterdir() if path.is_dir()):
            repro_file = model_dir / "reproducibility.json"
            if not repro_file.exists():
                continue
            payload = read_json(repro_file)
            for variant, data in payload["variants"].items():
                records.append(
                    {
                        "pattern_key": pattern.key,
                        "logic": pattern.logic,
                        "model_key": payload["evaluated_model_key"],
                        "variant": variant,
                        "mean_similarity": data["mean_similarity"],
                        "functionally_identical": data["llm_assessment"]["functionally_identical"],
                    }
                )
    return records


def variant_metric_summary(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate metric means per variant for a record subset."""
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        grouped[record["variant"]][record["metric"]].append(record["score"])

    summary: dict[str, Any] = {}
    for variant, metrics in grouped.items():
        metric_means = {
            metric: round(mean(scores), 4)
            for metric, scores in sorted(metrics.items())
            if scores
        }
        overall_mean = round(mean(metric_means.values()), 4) if metric_means else None
        sample_count = len(next(iter(metrics.values()))) if metrics else 0
        summary[variant] = {
            "metrics": metric_means,
            "overall_mean": overall_mean,
            "sample_count": sample_count,
        }
    return summary


def score_deltas(summary: dict[str, Any], left: str, right: str) -> dict[str, Optional[float]]:
    """Compute per-metric deltas between two variants."""
    left_metrics = summary.get(left, {}).get("metrics", {})
    right_metrics = summary.get(right, {}).get("metrics", {})
    metric_keys = sorted(set(left_metrics) | set(right_metrics))
    deltas: dict[str, Optional[float]] = {}
    for metric in metric_keys:
        if metric not in left_metrics or metric not in right_metrics:
            deltas[metric] = None
        else:
            deltas[metric] = round(right_metrics[metric] - left_metrics[metric], 4)
    if summary.get(left, {}).get("overall_mean") is not None and summary.get(right, {}).get("overall_mean") is not None:
        deltas["overall_mean"] = round(summary[right]["overall_mean"] - summary[left]["overall_mean"], 4)
    else:
        deltas["overall_mean"] = None
    return deltas


def reproducibility_summary(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate reproducibility by variant."""
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    bool_grouped: dict[str, list[bool]] = defaultdict(list)
    for record in records:
        grouped[record["variant"]]["mean_similarity"].append(record["mean_similarity"])
        bool_grouped[record["variant"]].append(bool(record["functionally_identical"]))

    summary: dict[str, Any] = {}
    for variant, values in grouped.items():
        similarities = values.get("mean_similarity", [])
        identical_values = bool_grouped.get(variant, [])
        summary[variant] = {
            "mean_similarity": round(mean(similarities), 6) if similarities else None,
            "functionally_identical_rate": round(
                sum(1 for item in identical_values if item) / len(identical_values), 4
            )
            if identical_values
            else None,
            "sample_count": len(similarities),
        }
    return summary


def summarize_results() -> None:
    """Aggregate quantitative and reproducibility outputs into summary JSON files."""
    judge_records = collect_judge_records()
    repro_records = collect_reproducibility_records()
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    overall_summary = variant_metric_summary(judge_records)
    aggregate_payload = {
        "generated_at_utc": now_utc_iso(),
        "score_summary": overall_summary,
        "peil_labelled_minus_naive": score_deltas(overall_summary, "naive", "peil_labelled"),
        "peil_unlabelled_minus_naive": score_deltas(overall_summary, "naive", "peil_unlabelled"),
        "labelled_minus_unlabelled": score_deltas(overall_summary, "peil_unlabelled", "peil_labelled"),
        "reproducibility": reproducibility_summary(repro_records),
    }
    write_json(SUMMARY_DIR / "aggregate_scores.json", aggregate_payload)

    by_logic: dict[str, Any] = {}
    for logic in sorted({record["logic"] for record in judge_records}):
        logic_records = [record for record in judge_records if record["logic"] == logic]
        logic_summary = variant_metric_summary(logic_records)
        by_logic[logic] = {
            "scores": logic_summary,
            "peil_labelled_minus_naive": score_deltas(logic_summary, "naive", "peil_labelled"),
            "peil_unlabelled_minus_naive": score_deltas(logic_summary, "naive", "peil_unlabelled"),
            "labelled_minus_unlabelled": score_deltas(logic_summary, "peil_unlabelled", "peil_labelled"),
        }
    write_json(SUMMARY_DIR / "by_logic.json", by_logic)

    by_model: dict[str, Any] = {}
    for model_key in sorted({record["model_key"] for record in judge_records}):
        model_records = [record for record in judge_records if record["model_key"] == model_key]
        model_summary = variant_metric_summary(model_records)
        repro_subset = [record for record in repro_records if record["model_key"] == model_key]
        by_model[model_key] = {
            "scores": model_summary,
            "peil_labelled_minus_naive": score_deltas(model_summary, "naive", "peil_labelled"),
            "peil_unlabelled_minus_naive": score_deltas(model_summary, "naive", "peil_unlabelled"),
            "labelled_minus_unlabelled": score_deltas(model_summary, "peil_unlabelled", "peil_labelled"),
            "reproducibility": reproducibility_summary(repro_subset),
        }
    write_json(SUMMARY_DIR / "by_model.json", by_model)

    by_metric: dict[str, Any] = {}
    for metric in METRICS:
        metric_records = [record for record in judge_records if record["metric"] == metric]
        metric_grouped: dict[str, list[float]] = defaultdict(list)
        for record in metric_records:
            metric_grouped[record["variant"]].append(record["score"])
        metric_summary = {
            variant: round(mean(scores), 4)
            for variant, scores in sorted(metric_grouped.items())
            if scores
        }
        by_metric[metric] = {
            "variant_means": metric_summary,
            "peil_labelled_minus_naive": round(metric_summary.get("peil_labelled", 0.0) - metric_summary.get("naive", 0.0), 4)
            if "peil_labelled" in metric_summary and "naive" in metric_summary
            else None,
            "peil_unlabelled_minus_naive": round(metric_summary.get("peil_unlabelled", 0.0) - metric_summary.get("naive", 0.0), 4)
            if "peil_unlabelled" in metric_summary and "naive" in metric_summary
            else None,
            "labelled_minus_unlabelled": round(metric_summary.get("peil_labelled", 0.0) - metric_summary.get("peil_unlabelled", 0.0), 4)
            if "peil_labelled" in metric_summary and "peil_unlabelled" in metric_summary
            else None,
        }
    write_json(SUMMARY_DIR / "by_metric.json", by_metric)

    labelled_vs_unlabelled: dict[str, Any] = {
        "overall": score_deltas(overall_summary, "peil_unlabelled", "peil_labelled"),
        "by_logic": {},
        "by_model": {},
    }
    for logic, payload in by_logic.items():
        labelled_vs_unlabelled["by_logic"][logic] = payload["labelled_minus_unlabelled"]
    for model_key, payload in by_model.items():
        labelled_vs_unlabelled["by_model"][model_key] = payload["labelled_minus_unlabelled"]
    write_json(SUMMARY_DIR / "labelled_vs_unlabelled.json", labelled_vs_unlabelled)


def doctor(runtime: AzureModelRuntime, model_keys: list[str], probe: bool) -> dict[str, Any]:
    """Resolve model configuration and optionally probe each deployment."""
    report: dict[str, Any] = {"generated_at_utc": now_utc_iso(), "models": {}}
    for model_key in model_keys:
        resolved = runtime.resolve_model(model_key)
        model_report: dict[str, Any] = {
            "deployment": resolved.deployment,
            "base_url": resolved.base_url,
            "api": "responses" if resolved.spec.use_responses_api else "chat.completions",
            "auth_mode": resolved.auth_mode,
            "probe": None,
        }
        if probe:
            try:
                if resolved.spec.use_responses_api:
                    response = runtime.generate_text(model_key, "Reply with OK.")
                    model_report["probe"] = {
                        "status": "ok",
                        "output_preview": response["text"][:120],
                        "usage": response.get("usage", {}),
                    }
                else:
                    response = runtime.generate_text(model_key, "Reply with OK.")
                    model_report["probe"] = {
                        "status": "ok",
                        "output_preview": response["text"][:120],
                        "usage": response.get("usage", {}),
                    }
            except Exception as exc:  # pragma: no cover - live connectivity path
                model_report["probe"] = {"status": "error", "message": str(exc)}
        report["models"][model_key] = model_report
    return report


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Chapter 6 evaluation CLI")
    parser.add_argument(
        "command",
        choices=["doctor", "run-quantitative", "run-cybersecurity", "summarize", "run-all"],
        help="Which action to run.",
    )
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_EVALUATION_MODELS),
        help="Comma-separated quantitative model keys.",
    )
    parser.add_argument(
        "--patterns",
        default=",".join(pattern.key for pattern in PATTERNS),
        help="Comma-separated quantitative pattern keys.",
    )
    parser.add_argument(
        "--case-studies",
        default=",".join(scenario.key for scenario in CYBER_SCENARIOS),
        help="Comma-separated qualitative case study keys.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help="Number of repeated runs for each quantitative prompt variant.",
    )
    parser.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help="Model key to use for judging and reproducibility assessment.",
    )
    parser.add_argument(
        "--cyber-model",
        default=DEFAULT_CYBER_MODEL,
        help="Model key to use for the qualitative cybersecurity scenarios.",
    )
    parser.add_argument(
        "--auth-mode",
        choices=["auto", "api_key", "entra"],
        default="auto",
        help="How to authenticate to Azure-hosted endpoints.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate files even if artifacts already exist.",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="When used with doctor, send a small live request to each model.",
    )
    return parser.parse_args(argv)


def validate_keys(keys: list[str], valid: Iterable[str], label: str) -> list[str]:
    """Validate a list of model or pattern keys."""
    valid_set = set(valid)
    unknown = [key for key in keys if key not in valid_set]
    if unknown:
        raise ValueError(f"Unknown {label}: {', '.join(unknown)}")
    return keys


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    args = parse_args(argv)
    runtime = AzureModelRuntime(auth_mode=args.auth_mode)

    model_keys = validate_keys(comma_separated_list(args.models), MODEL_REGISTRY.keys(), "models")
    pattern_keys = validate_keys(comma_separated_list(args.patterns), PATTERN_INDEX.keys(), "patterns")
    case_study_keys = validate_keys(
        comma_separated_list(args.case_studies),
        CYBER_SCENARIO_INDEX.keys(),
        "case studies",
    )

    if args.command == "doctor":
        doctor_models = model_keys + ([args.judge_model] if args.judge_model not in model_keys else [])
        report = doctor(runtime, doctor_models, args.probe)
        print(json.dumps(report, indent=2))
        return 0

    if args.command == "run-quantitative":
        run_quantitative(
            runtime,
            model_keys=model_keys,
            judge_model_key=args.judge_model,
            pattern_keys=pattern_keys,
            runs=args.runs,
            force=args.force,
        )
        return 0

    if args.command == "run-cybersecurity":
        run_case_studies(
            runtime,
            model_key=args.cyber_model,
            scenario_keys=case_study_keys,
            force=args.force,
        )
        return 0

    if args.command == "summarize":
        summarize_results()
        return 0

    if args.command == "run-all":
        run_quantitative(
            runtime,
            model_keys=model_keys,
            judge_model_key=args.judge_model,
            pattern_keys=pattern_keys,
            runs=args.runs,
            force=args.force,
        )
        run_case_studies(
            runtime,
            model_key=args.cyber_model,
            scenario_keys=case_study_keys,
            force=args.force,
        )
        summarize_results()
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)