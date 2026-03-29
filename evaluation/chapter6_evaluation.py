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
    max_output_tokens: int = 1200

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
    max_output_tokens: int = 1400

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
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
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
        max_output_tokens: int,
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
                max_output_tokens,
                json_schema=json_schema,
            )
        return self._call_chat_completions(
            client,
            resolved,
            prompt,
            max_output_tokens,
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
        max_output_tokens: int,
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
            "max_output_tokens": max_output_tokens,
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
        max_output_tokens: int,
    ) -> dict[str, Any]:
        """Call the Chat Completions API and normalize the result."""
        request: dict[str, Any] = {
            "model": resolved.deployment,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_output_tokens,
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
    """Return the 18 quantitative evaluation patterns."""
    return [
        PatternDefinition(
            key="across_translation_technical_paragraph",
            logic="Across",
            subcategory="Translation",
            task_title="Translate a zero trust explainer",
            task_description="Translate the supplied English technical paragraph into Simplified Chinese while preserving security meaning and terminology.",
            naive_request="Translate this paragraph into Simplified Chinese.",
            task_material=(
                "Zero Trust architecture assumes no user or device should be trusted by default, even when it is already inside the corporate network. "
                "Every access request should be evaluated continuously using identity signals, device health, and contextual risk. "
                "This reduces lateral movement, limits blast radius, and makes multi-factor authentication and conditional access central controls rather than optional add-ons."
            ),
            role="You are a bilingual cloud security translator specializing in English and Simplified Chinese technical writing.",
            context="The translation will be used in an internal security briefing for engineers in Beijing. Preserve technical accuracy, established security terminology, and product-neutral phrasing.",
            instructions=(
                "Translate the full paragraph into Simplified Chinese.",
                "Preserve terms such as Zero Trust, lateral movement, multi-factor authentication, and conditional access accurately.",
                "Keep the tone professional and concise.",
                "Do not add explanations, examples, or extra facts.",
            ),
            technique="Use step-by-step semantic preservation so that each sentence keeps the same technical meaning as the source.",
            output="Return only the final Simplified Chinese translation as two short paragraphs.",
            reference_notes="The translation should preserve the named security concepts and should not introduce new recommendations or examples.",
            max_output_tokens=700,
        ),
        PatternDefinition(
            key="across_argument_mfa_policy",
            logic="Across",
            subcategory="Argument",
            task_title="Argue for or against universal MFA",
            task_description="Develop a balanced argument about whether organizations should require multi-factor authentication for all employee access, including low-risk internal tools.",
            naive_request="Argue for and against requiring MFA for every employee system, even low-risk internal tools, and give a recommendation.",
            task_material="Audience: security leadership preparing a policy recommendation for the next governance meeting.",
            role="You are a senior security strategist writing policy advice for a security steering committee.",
            context="The committee cares about risk reduction, productivity, implementation cost, and user adoption. The response should acknowledge real tradeoffs instead of giving a one-sided answer.",
            instructions=(
                "Present the strongest argument in favor of universal MFA.",
                "Present the strongest argument against universal MFA for low-risk tools.",
                "Compare the tradeoffs across security, usability, and operating cost.",
                "Finish with a clear recommendation and a short rationale.",
            ),
            technique="Use dialectical reasoning: build the best case for each side before forming the final recommendation.",
            output="Return a structured memo with sections titled Position For, Position Against, Tradeoff Assessment, and Recommendation. Keep it under 450 words.",
            reference_notes="A strong answer should address both security benefit and user friction rather than treating MFA as cost-free.",
        ),
        PatternDefinition(
            key="across_comparison_serverless_platforms",
            logic="Across",
            subcategory="Comparison",
            task_title="Compare Azure Functions and AWS Lambda",
            task_description="Compare Azure Functions and AWS Lambda for an enterprise event-driven processing workload.",
            naive_request="Compare Azure Functions and AWS Lambda for an enterprise event-driven workload.",
            task_material=(
                "Workload assumptions: bursty API traffic, scheduled jobs, queue-triggered background processing, enterprise identity requirements, and a moderate operations team."
            ),
            role="You are a cloud architecture advisor helping an enterprise choose a serverless platform.",
            context="The decision will be used by an architecture review board that wants a practical comparison rather than marketing language.",
            instructions=(
                "Compare both services on scaling behavior, developer experience, observability, identity and access control, and operational overhead.",
                "Note the most relevant strengths and limitations for each platform.",
                "Call out one scenario where Azure Functions is a better fit and one where AWS Lambda is a better fit.",
                "Avoid absolute claims that ignore context.",
            ),
            technique="Use dimension-by-dimension comparison before drawing scenario-based conclusions.",
            output="Return a concise comparison table followed by a short recommendation paragraph.",
            reference_notes="The answer should compare both services across multiple dimensions and avoid framing one platform as universally superior.",
            max_output_tokens=900,
        ),
        PatternDefinition(
            key="at_assessment_code_review",
            logic="At",
            subcategory="Assessment",
            task_title="Assess a Python upload handler",
            task_description="Evaluate the supplied Python code for security and maintainability issues.",
            naive_request="Evaluate this Python code and tell me what is wrong with it.",
            task_material=(
                "```python\n"
                "import os\n"
                "from flask import request\n\n"
                "UPLOAD_DIR = '/tmp/uploads'\n\n"
                "def save_file():\n"
                "    file = request.files['file']\n"
                "    target = os.path.join(UPLOAD_DIR, file.filename)\n"
                "    file.save(target)\n"
                "    return {'path': target, 'status': 'saved'}\n"
                "```"
            ),
            role="You are a senior application security reviewer.",
            context="The code is part of an internal web application that accepts user-supplied files. The team wants a practical review that prioritizes important defects.",
            instructions=(
                "Assess the code for security, reliability, and maintainability concerns.",
                "Rank the issues by severity.",
                "Explain why each issue matters in one sentence.",
                "Suggest concrete fixes for the top findings.",
            ),
            technique="Use rubric-based assessment: identify finding, severity, rationale, and remediation for each issue.",
            output="Return a short assessment report with sections Summary, Findings, and Recommended Fixes.",
            reference_notes="High-value findings include path traversal risk from filename handling, missing validation, and hard-coded filesystem assumptions.",
        ),
        PatternDefinition(
            key="at_calculation_incident_hours",
            logic="At",
            subcategory="Calculation",
            task_title="Calculate analyst effort from phishing clicks",
            task_description="Solve the multi-step incident response calculation and provide the final number of analyst hours.",
            naive_request="Solve this calculation and show the answer.",
            task_material=(
                "Campaign A targeted 24 mailboxes and one-third of recipients clicked the link.\n"
                "Campaign B targeted 18 mailboxes and 5 recipients clicked the link.\n"
                "Campaign C targeted 30 mailboxes and 20% of recipients clicked the link.\n"
                "If each clicked user requires 45 minutes of analyst response time, how many total analyst hours are required?"
            ),
            role="You are a careful quantitative incident response analyst.",
            context="The result will be used in an after-action report, so arithmetic accuracy matters more than writing style.",
            instructions=(
                "Compute the number of clicked users for each campaign.",
                "Sum the total number of clicked users.",
                "Convert the total response time from minutes into hours.",
                "Provide the final answer clearly.",
            ),
            technique="Use explicit step-by-step arithmetic and verify the final unit conversion.",
            output="Return the working and end with a line that states the final analyst hours required.",
            reference_notes="Correct calculation: 8 + 5 + 6 = 19 clicked users, 19 * 45 = 855 minutes, 855 / 60 = 14.25 hours.",
            max_output_tokens=600,
        ),
        PatternDefinition(
            key="at_assessment_fact_claims",
            logic="At",
            subcategory="Assessment",
            task_title="Assess timeline-based claims",
            task_description="Assess whether each claim is supported, contradicted, or not supported by the incident timeline.",
            naive_request="Read the timeline and assess each claim.",
            task_material=(
                "Incident timeline:\n"
                "- 08:00 UTC: Security team applied an emergency VPN configuration change.\n"
                "- 09:15 UTC: Monitoring detected repeated failed logins from a foreign IP range.\n"
                "- 09:40 UTC: The privileged admin account was locked.\n"
                "- 10:10 UTC: Data transfer spikes were observed from the finance file share.\n"
                "- 10:30 UTC: The finance file share was isolated from the network.\n\n"
                "Claims:\n"
                "A. The privileged admin account was locked before suspicious login activity was detected.\n"
                "B. Potential data exfiltration indicators appeared before the finance file share was isolated.\n"
                "C. The timeline proves that the VPN configuration change caused the incident."
            ),
            role="You are an evidence-driven incident reviewer.",
            context="The goal is to distinguish what the timeline directly supports from what it merely suggests.",
            instructions=(
                "Label each claim as Supported, Contradicted, or Insufficient Evidence.",
                "Explain the label with direct reference to the timeline.",
                "Avoid causal conclusions that the timeline does not prove.",
                "Keep the reasoning concise.",
            ),
            technique="Use evidence tracing: map each claim to the exact timeline entries that support or weaken it.",
            output="Return a short table with columns Claim, Verdict, and Justification.",
            reference_notes="Expected verdicts: A Contradicted, B Supported, C Insufficient Evidence.",
            max_output_tokens=700,
        ),
        PatternDefinition(
            key="beyond_logical_reasoning_shift_puzzle",
            logic="Beyond",
            subcategory="Logical Reasoning",
            task_title="Solve an analyst shift puzzle",
            task_description="Solve the logic puzzle and identify the shift and queue assignment for each analyst.",
            naive_request="Solve this logic puzzle.",
            task_material=(
                "Three analysts - Priya, Mateo, and Lin - each worked one shift (morning, afternoon, overnight) and each owned one queue (phishing, ransomware, insider-risk).\n"
                "Clues:\n"
                "1. Priya did not work the overnight shift.\n"
                "2. Mateo handled the phishing queue.\n"
                "3. The ransomware analyst worked the afternoon shift.\n"
                "4. Lin did not work the afternoon shift.\n"
                "5. The insider-risk analyst worked later than Priya.\n"
                "Determine the shift and queue for each analyst."
            ),
            role="You are a precise logical reasoning specialist.",
            context="The answer should show disciplined elimination rather than a guess.",
            instructions=(
                "Work through the clues systematically.",
                "Eliminate impossible assignments before making conclusions.",
                "State the final shift and queue for each analyst.",
                "Keep the final answer unambiguous.",
            ),
            technique="Use step-by-step deductive elimination and verify that the final assignment satisfies all clues.",
            output="Return a brief reasoning trace followed by a final answer list for Priya, Mateo, and Lin.",
            reference_notes="Correct solution: Priya worked afternoon and handled ransomware, Mateo worked morning and handled phishing, Lin worked overnight and handled insider-risk.",
            max_output_tokens=800,
        ),
        PatternDefinition(
            key="beyond_hypothesis_generation_login_spikes",
            logic="Beyond",
            subcategory="Hypothesis",
            task_title="Generate hypotheses from suspicious login data",
            task_description="Generate plausible hypotheses that explain the observed authentication spike pattern.",
            naive_request="Look at this data and generate hypotheses about what might be happening.",
            task_material=(
                "Observed data over four days:\n"
                "- Day 1: 120 failed VPN logins, mostly from one country, normal MFA challenge rate.\n"
                "- Day 2: 430 failed VPN logins, spread across six countries, elevated MFA challenge failures.\n"
                "- Day 3: 410 failed VPN logins, mostly targeting finance and HR users, several successful password resets.\n"
                "- Day 4: 95 failed VPN logins, but help desk tickets about lockouts doubled compared with baseline."
            ),
            role="You are a threat hunting analyst developing working hypotheses from incomplete evidence.",
            context="The team needs plausible explanations to guide investigation, not a claim of certainty.",
            instructions=(
                "Generate at least three distinct hypotheses that explain the pattern.",
                "For each hypothesis, cite the observations that support it.",
                "List one piece of additional evidence that would help confirm or reject each hypothesis.",
                "Rank the hypotheses from most to least plausible.",
            ),
            technique="Use abductive reasoning: infer the most plausible explanations from the observed evidence while explicitly noting uncertainty.",
            output="Return a ranked list of hypotheses with supporting signals and next-check evidence.",
            reference_notes="Strong hypotheses could include password spraying, coordinated credential stuffing, or a help-desk abuse component. The answer should not claim certainty.",
            max_output_tokens=1000,
        ),
        PatternDefinition(
            key="beyond_simulation_rate_limiting",
            logic="Beyond",
            subcategory="Simulation",
            task_title="Simulate a rate-limiting rollout",
            task_description="Simulate the likely operational effects of introducing IP-based rate limiting on a login endpoint over one week.",
            naive_request="Simulate what happens if we add IP-based rate limiting to our login endpoint next week.",
            task_material=(
                "System context:\n"
                "- Current state: no IP-based rate limiting.\n"
                "- Baseline: 12,000 legitimate login attempts per day and 2,500 malicious attempts per day.\n"
                "- Planned change: block any IP that exceeds 10 failed logins in 5 minutes for 30 minutes.\n"
                "- Constraint: the service supports global customers who may share NAT gateways."
            ),
            role="You are a reliability-minded security engineer modeling operational change.",
            context="The simulation should be realistic and should include both security benefits and unintended side effects.",
            instructions=(
                "Describe the most likely day-by-day effects during the first week after rollout.",
                "Identify both expected benefits and plausible false-positive impacts.",
                "Note any assumptions that the simulation relies on.",
                "End with two mitigation suggestions for the most important downside risks.",
            ),
            technique="Use scenario simulation with explicit assumptions and first-order operational consequences.",
            output="Return a seven-day simulation log followed by a short conclusion.",
            reference_notes="The response should mention both attacker suppression and possible false positives from shared IP space or support ticket volume.",
            max_output_tokens=1200,
        ),
        PatternDefinition(
            key="in_error_identification_python_handler",
            logic="In",
            subcategory="Error Identification",
            task_title="Find bugs in a database handler",
            task_description="Identify the defects and security issues in the provided code snippet.",
            naive_request="Find the bugs in this code.",
            task_material=(
                "```python\n"
                "import sqlite3\n\n"
                "def get_user(username):\n"
                "    connection = sqlite3.connect('users.db')\n"
                "    cursor = connection.cursor()\n"
                "    cursor.execute(f\"SELECT * FROM users WHERE username = '{username}'\")\n"
                "    user = cursor.fetchone()\n"
                "    return user\n"
                "```"
            ),
            role="You are a senior Python security reviewer.",
            context="The goal is to surface concrete implementation problems, especially issues that could lead to compromise or unstable behavior.",
            instructions=(
                "Identify the most important defects in the code.",
                "Explain why each defect is dangerous or incorrect.",
                "State how to fix each defect.",
                "Prioritize issues that materially affect correctness or security.",
            ),
            technique="Use defect isolation: inspect input handling, query construction, resource lifecycle, and error handling separately.",
            output="Return a numbered list of findings ordered by severity.",
            reference_notes="High-value findings include SQL injection, unclosed database connection, and lack of exception handling.",
            max_output_tokens=800,
        ),
        PatternDefinition(
            key="in_categorisation_alert_triage",
            logic="In",
            subcategory="Categorising",
            task_title="Categorize security alerts",
            task_description="Categorize each alert into the most appropriate response bucket.",
            naive_request="Categorize these alerts.",
            task_material=(
                "Categories: Phishing, Malware, Misconfiguration, Benign.\n\n"
                "Alerts:\n"
                "1. Multiple users report a cloned login page hosted on a lookalike domain.\n"
                "2. Endpoint telemetry shows a scheduled task launching an encoded PowerShell command.\n"
                "3. A storage account is publicly readable because anonymous blob access was enabled.\n"
                "4. The nightly vulnerability scan generated an informational message for a test subnet that is intentionally internet-exposed.\n"
                "5. Mail gateway logs show a wave of messages with malicious attachment hashes already blocked at delivery.\n"
                "6. Defender reports a signed but known-bad ransomware loader dropped into the temp directory."
            ),
            role="You are a SOC triage analyst standardizing alert handling.",
            context="The triage categories are used for queue routing, so each label should map cleanly to the dominant issue.",
            instructions=(
                "Assign exactly one category to each alert.",
                "Explain the label in one short sentence.",
                "Prefer the category that best reflects the operational response path.",
                "Do not invent extra categories.",
            ),
            technique="Use criteria-based categorization: identify the dominant incident type and choose the closest operational bucket.",
            output="Return a table with Alert Number, Category, and Justification.",
            reference_notes="Expected dominant labels: 1 Phishing, 2 Malware, 3 Misconfiguration, 4 Benign, 5 Phishing, 6 Malware.",
            max_output_tokens=900,
        ),
        PatternDefinition(
            key="in_refactoring_http_service",
            logic="In",
            subcategory="Refactoring",
            task_title="Refactor mixed business and transport logic",
            task_description="Refactor the code so that business logic is separated from the HTTP client dependency.",
            naive_request="Refactor this code so it is cleaner.",
            task_material=(
                "```python\n"
                "import requests\n\n"
                "class BusinessLogic:\n"
                "    def get(self, url):\n"
                "        return requests.get(url)\n\n"
                "    def post(self, url, data):\n"
                "        return requests.post(url, data=data)\n\n"
                "    def fetch_data(self, url):\n"
                "        response = self.get(url)\n"
                "        return response.json()\n\n"
                "    def send_data(self, url, data):\n"
                "        response = self.post(url, data)\n"
                "        return response.status_code\n"
                "```"
            ),
            role="You are a software architect focused on maintainable Python design.",
            context="The team wants to make the business logic testable and replaceable without locking itself to a specific HTTP library.",
            instructions=(
                "Separate the business logic from the third-party HTTP dependency.",
                "Introduce a clear abstraction boundary.",
                "Keep the example concise but runnable in principle.",
                "Explain the new structure briefly after the code.",
            ),
            technique="Use interface extraction and dependency inversion to decouple the service logic from the transport implementation.",
            output="Return the refactored Python code followed by a brief explanation of the new design.",
            reference_notes="A strong answer introduces an adapter or client abstraction rather than leaving requests calls inside the business class.",
            max_output_tokens=1200,
        ),
        PatternDefinition(
            key="out_output_customisation_incident_json",
            logic="Out",
            subcategory="Output Customisation",
            task_title="Format incident facts as JSON",
            task_description="Transform the supplied incident facts into a constrained JSON object.",
            naive_request="Turn these incident facts into JSON.",
            task_material=(
                "Incident facts:\n"
                "- Incident ID: IR-2026-041\n"
                "- Severity: High\n"
                "- Initial vector: credential phishing\n"
                "- Affected assets: finance-share, dc-02\n"
                "- Confirmed actions: malicious inbox rules, suspicious SMB transfer\n"
                "- Current status: contained\n"
                "- Next owner: incident-response\n"
                "- Evidence gaps: exact exfiltrated files unknown"
            ),
            role="You are an operations analyst normalizing incident data for downstream tooling.",
            context="The JSON will be consumed by another service, so structural consistency matters more than prose quality.",
            instructions=(
                "Represent the incident as valid JSON.",
                "Use the keys incident_id, severity, initial_vector, affected_assets, confirmed_actions, current_status, next_owner, and evidence_gaps.",
                "Render arrays where multiple values are present.",
                "Do not add fields that were not requested.",
            ),
            technique="Use schema-constrained formatting and preserve source facts without embellishment.",
            output="Return only valid JSON with the requested keys.",
            reference_notes="The answer should be valid JSON and should not wrap the object in Markdown or add commentary.",
            max_output_tokens=500,
        ),
        PatternDefinition(
            key="out_decomposed_prompting_migration_plan",
            logic="Out",
            subcategory="Decomposed Prompting",
            task_title="Break down a migration task",
            task_description="Break down the cloud migration problem into a practical sequence of smaller work items.",
            naive_request="Break down this migration task into steps.",
            task_material=(
                "Task: Migrate a Flask monolith that currently runs on a single VM to Azure App Service with Azure Database for PostgreSQL, "
                "GitHub Actions deployment automation, and managed identity for secrets access. The team has two engineers and four weeks."
            ),
            role="You are a delivery-focused cloud migration planner.",
            context="The audience is a small engineering team that needs a plan they can execute, review, and track.",
            instructions=(
                "Decompose the work into a sequence of smaller tasks.",
                "Group tasks into phases with clear dependencies.",
                "Call out the riskiest work items and validation checkpoints.",
                "Keep the plan realistic for a two-engineer team over four weeks.",
            ),
            technique="Use decomposition by phase, dependency, and validation checkpoint.",
            output="Return a phased migration plan with numbered tasks and a short risk section.",
            reference_notes="A strong answer should not present the migration as a single flat checklist. It should stage foundation, app changes, deployment, and validation.",
            max_output_tokens=1000,
        ),
        PatternDefinition(
            key="out_context_control_privacy_review",
            logic="Out",
            subcategory="Context Control",
            task_title="Analyze only privacy risks",
            task_description="Analyze the supplied application design only from the perspective of privacy risk.",
            naive_request="Review this application design and tell me the risks.",
            task_material=(
                "Application design summary:\n"
                "A mobile wellness app collects mood journal entries, approximate location, wearable heart-rate data, and optional voice notes. "
                "The company stores raw data for five years to support product analytics and model training. Data is shared with a third-party transcription service and a marketing analytics vendor."
            ),
            role="You are a privacy engineering reviewer.",
            context="The requester only wants privacy implications. Security, performance, UX, and growth considerations are out of scope unless they directly change privacy exposure.",
            instructions=(
                "Assess the design only for privacy risks.",
                "Focus on data minimization, retention, third-party sharing, and user consent.",
                "Explicitly avoid unrelated concerns such as performance or feature velocity.",
                "Suggest the most important privacy mitigations.",
            ),
            technique="Use scoped analysis with strict boundary control so the answer stays inside the requested domain.",
            output="Return a privacy-only review with sections Risks and Recommended Mitigations.",
            reference_notes="Answers that drift into general app security or product strategy should be scored lower on task completeness and formatting discipline.",
            max_output_tokens=900,
        ),
        PatternDefinition(
            key="over_summarisation_policy_update",
            logic="Over",
            subcategory="Summarisation",
            task_title="Summarize a security policy update",
            task_description="Summarize the supplied policy text for an executive audience.",
            naive_request="Summarize this policy update for executives.",
            task_material=(
                "Policy update text:\n"
                "Beginning in Q3, all privileged administrative actions must be performed through managed workstations enrolled in endpoint compliance monitoring. "
                "Break-glass accounts remain permitted, but their passwords must be stored in the enterprise vault, checked every 30 days, and tested quarterly in a monitored exercise. "
                "Remote privileged access from unmanaged personal devices is prohibited. Logging requirements are expanding to include session recording for domain administration, cloud control plane changes, and production database access. "
                "Business units that cannot meet the standard by the deadline must submit a compensating control plan signed by both the business owner and the CISO delegate. "
                "The intent of the update is to reduce credential theft impact, improve auditability, and make exception handling visible instead of informal."
            ),
            role="You are an executive communications analyst.",
            context="Executives want the essence of the change, the operational implications, and the reason it matters. They do not want the full policy wording.",
            instructions=(
                "Identify the core change in plain language.",
                "Highlight the most important operational implications.",
                "Explain why the policy change matters.",
                "Keep the summary concise and executive-friendly.",
            ),
            technique="Use hierarchical summarization: capture the central message first, then distill only the most decision-relevant details.",
            output="Return an executive summary in 3 to 5 bullet points.",
            reference_notes="Strong answers should mention managed workstations, break-glass controls, logging expansion, and formal exception handling without reproducing the full source text.",
            max_output_tokens=700,
        ),
        PatternDefinition(
            key="over_synthesis_multi_source_recommendation",
            logic="Over",
            subcategory="Synthesis",
            task_title="Synthesize three source excerpts",
            task_description="Synthesize the supplied source excerpts into one coherent recommendation.",
            naive_request="Read these excerpts and synthesize them into a recommendation.",
            task_material=(
                "Source A: The phishing simulation program improved reporting rates from 11% to 36% over two quarters, but repeat clickers remained concentrated in three business units.\n\n"
                "Source B: SOC analysts report that most real email incidents still arrive through third-party file sharing notifications and business collaboration platforms rather than traditional email attachments.\n\n"
                "Source C: Budget for security awareness is flat next quarter, so any new intervention should target the highest-risk groups and channels rather than broad training refresh for the whole company."
            ),
            role="You are a security program analyst preparing a recommendation for leadership.",
            context="Leadership wants one actionable recommendation that integrates the data, the operational reality, and the budget constraint.",
            instructions=(
                "Identify the main signal from each source.",
                "Combine the sources into one coherent interpretation.",
                "Recommend a practical next step that fits the budget constraint.",
                "Explain why the recommendation follows from the combined evidence.",
            ),
            technique="Use cross-source synthesis: extract the key signal from each source and combine them into one decision-oriented conclusion.",
            output="Return a short recommendation memo with sections Integrated Finding and Recommended Action.",
            reference_notes="A strong synthesis should recommend targeted interventions for high-risk units and modern collaboration-based phishing channels rather than broad untargeted training.",
            max_output_tokens=850,
        ),
        PatternDefinition(
            key="over_dense_summarisation_incident_digest",
            logic="Over",
            subcategory="Summarisation",
            task_title="Create a dense incident digest",
            task_description="Condense the incident narrative into a dense summary that preserves named entities, key events, and quantitative details.",
            naive_request="Write a dense summary of this incident.",
            task_material=(
                "Incident narrative:\n"
                "On 14 March 2026, Fabrikam's incident response team investigated unauthorized activity linked to a compromised vendor account used by Northwind Logistics. "
                "The first confirmed signal appeared at 02:14 UTC when Microsoft Defender for Endpoint flagged an encoded PowerShell child process on workstation FIN-WS-17. "
                "By 02:26 UTC, the attacker had authenticated to the finance file share using the vendor account and copied 184 files totaling 1.8 GB. "
                "At 02:31 UTC, a newly created inbox rule redirected payment confirmation emails for three finance users. The team disabled the vendor account at 02:36 UTC, isolated FIN-WS-17 at 02:41 UTC, and blocked the attacker IP range at 02:48 UTC. "
                "Later review showed that 27 of the copied files contained sensitive invoice data, while no evidence showed destructive malware or domain-wide privilege escalation."
            ),
            role="You are a crisis communications analyst producing a high-density operations digest.",
            context="The digest is for incident leaders who want maximum information value in minimal space without losing crucial named entities or quantitative facts.",
            instructions=(
                "Preserve the named organizations, assets, timestamps, and quantitative details.",
                "Condense the narrative aggressively without losing material facts.",
                "Do not add interpretation beyond the provided facts.",
                "Keep the final digest under 120 words.",
            ),
            technique="Use dense summarization: compress phrasing while preserving entities, chronology, and numerical details.",
            output="Return one paragraph under 120 words.",
            reference_notes="A strong answer should retain Fabrikam, Northwind Logistics, FIN-WS-17, core timestamps, file counts, and the lack of destructive malware or privilege escalation.",
            max_output_tokens=500,
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
        pattern.max_output_tokens,
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
    judge_result = runtime.generate_text(
        judge_model_key,
        build_judge_prompt(pattern, outputs),
        2000,
        json_schema=JUDGE_SCHEMA,
    )
    scores = extract_json_payload(judge_result["text"])
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
        llm_result = runtime.generate_text(
            judge_model_key,
            build_reproducibility_prompt(pattern, variant, outputs),
            1200,
            json_schema=REPRODUCIBILITY_SCHEMA,
        )
        variant_results[variant] = {
            "pairwise_similarity": pairwise,
            "mean_similarity": round(mean(similarities), 6),
            "llm_assessment": extract_json_payload(llm_result["text"]),
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
            response_data = runtime.generate_text(model_key, prompt, scenario.max_output_tokens)
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
                    response = runtime.generate_text(model_key, "Reply with OK.", 64)
                    model_report["probe"] = {
                        "status": "ok",
                        "output_preview": response["text"][:120],
                        "usage": response.get("usage", {}),
                    }
                else:
                    response = runtime.generate_text(model_key, "Reply with OK.", 64)
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