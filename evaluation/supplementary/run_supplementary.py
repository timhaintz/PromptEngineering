# ruff: noqa: E501
# flake8: noqa
# pylint: disable=line-too-long
"""Supplementary evaluation: PEIL as system prompt for agent-oriented tasks.

This tests PEIL in its intended design context — as a system prompt that defines
agent behaviour, with task data supplied as a separate user message. This contrasts
with the main evaluation which tested PEIL as single-turn chat prompts.

6 patterns (one per taxonomy logic), 4 models, 3 variants, 3 runs each.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Re-use infrastructure from the main evaluation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from evaluation.chapter6_evaluation import (
    AzureModelRuntime,
    JUDGE_SCHEMA,
    REPRODUCIBILITY_SCHEMA,
    DEFAULT_EVALUATION_MODELS,
    DEFAULT_JUDGE_MODEL,
    METRICS,
    VARIANT_TO_OUTPUT_KEY,
    build_judge_schema,
    build_reproducibility_schema,
    cosine_similarity,
    extract_json_payload,
    log,
    now_utc_iso,
    read_json,
    write_json,
)
from itertools import combinations
from statistics import mean
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"
SUMMARY_DIR = SCRIPT_DIR / "summary"


@dataclass(frozen=True)
class AgentPattern:
    """A supplementary agent-oriented evaluation pattern."""
    key: str
    logic: str
    subcategory: str
    task_title: str
    source_paper_id: str
    source_pattern_id: str
    source_paper_title: str
    source_pattern_name: str
    # The system prompt (PEIL-structured) that defines the agent
    system_prompt_naive: str
    system_prompt_peil_labelled: str
    system_prompt_peil_unlabelled: str
    # The user message with task data (same across all 3 variants)
    user_message: str
    # For judging
    reference_notes: str = ""


def build_agent_patterns() -> list[AgentPattern]:
    """Return the 6 supplementary agent-oriented patterns."""
    return [
        # ── ACROSS: Comparison ────────────────────────────────────
        AgentPattern(
            key="agent_across_comparison_model_responses",
            logic="Across",
            subcategory="Comparison",
            task_title="Compare two model responses to the same question",
            source_paper_id="56",
            source_pattern_id="56-4-0",
            source_paper_title="Prompt Stealing Attacks Against Large Language Models",
            source_pattern_name="ChatGPT vs LLaMA",
            system_prompt_naive="You compare responses from different AI models to the same question.",
            system_prompt_peil_labelled=(
                "Role: You are a model comparison analyst who evaluates AI responses side-by-side.\n\n"
                "Context: You receive two responses to the same question from different AI models. Your evaluation must be objective, evidence-based, and practical.\n\n"
                "Instructions:\n"
                "1. Evaluate both responses on clarity, accuracy, coverage breadth, and actionable guidance.\n"
                "2. Note specific strengths and weaknesses for each response.\n"
                "3. Select the stronger response and justify your choice.\n"
                "4. Keep the comparison concise and decision-ready.\n\n"
                "Techniques: Use dimension-by-dimension comparison before drawing a final verdict.\n\n"
                "Output: Return a structured comparison with a clear verdict and justification."
            ),
            system_prompt_peil_unlabelled=(
                "You are a model comparison analyst who evaluates AI responses side-by-side.\n\n"
                "You receive two responses to the same question from different AI models. Your evaluation must be objective, evidence-based, and practical.\n\n"
                "1. Evaluate both responses on clarity, accuracy, coverage breadth, and actionable guidance.\n"
                "2. Note specific strengths and weaknesses for each response.\n"
                "3. Select the stronger response and justify your choice.\n"
                "4. Keep the comparison concise and decision-ready.\n\n"
                "Use dimension-by-dimension comparison before drawing a final verdict.\n\n"
                "Return a structured comparison with a clear verdict and justification."
            ),
            user_message=(
                "Question: Are there any good museums in Istanbul for me to visit?\n\n"
                "Response A: Istanbul has many world-class museums. The Hagia Sophia is a must-see architectural wonder that served as a cathedral and mosque. The Topkapi Palace Museum houses Ottoman artifacts and Islamic relics. The Istanbul Archaeology Museums contain over one million objects spanning multiple civilizations.\n\n"
                "Response B: Yes! Check out the Hagia Sophia, it's amazing. The Topkapi Palace is cool too. There are also some smaller galleries around Beyoglu if you like contemporary art."
            ),
            reference_notes="A strong comparison should evaluate both on clarity, depth, and actionability, noting that Response A provides more specific detail while Response B is more conversational.",
        ),
        # ── AT: Assessment / Classification ───────────────────────
        AgentPattern(
            key="agent_at_assessment_entailment",
            logic="At",
            subcategory="Assessment",
            task_title="Classify whether a hypothesis is entailed by a premise",
            source_paper_id="15",
            source_pattern_id="15-6-0",
            source_paper_title="Batch Prompting: Efficient Inference with Large Language Model APIs",
            source_pattern_name="Entailment vs. Non-Entailment",
            system_prompt_naive="You classify whether a hypothesis follows from a given premise. Answer entailment or non-entailment.",
            system_prompt_peil_labelled=(
                "Role: You are an entailment classification specialist who determines whether hypotheses are supported by premises.\n\n"
                "Context: You receive premise-hypothesis pairs and must classify each as entailment or non-entailment. Contradiction and neutral both count as non-entailment.\n\n"
                "Instructions:\n"
                "1. Read the premise carefully and identify the key claims.\n"
                "2. Read the hypothesis and determine if it is directly supported by the premise.\n"
                "3. If the premise logically entails the hypothesis, classify as entailment.\n"
                "4. If the hypothesis contradicts the premise or is not supported, classify as non-entailment.\n\n"
                "Techniques: Use evidence tracing to map each hypothesis claim to specific premise evidence before classifying.\n\n"
                "Output: Return entailment or non-entailment with a one-sentence justification."
            ),
            system_prompt_peil_unlabelled=(
                "You are an entailment classification specialist who determines whether hypotheses are supported by premises.\n\n"
                "You receive premise-hypothesis pairs and must classify each as entailment or non-entailment. Contradiction and neutral both count as non-entailment.\n\n"
                "1. Read the premise carefully and identify the key claims.\n"
                "2. Read the hypothesis and determine if it is directly supported by the premise.\n"
                "3. If the premise logically entails the hypothesis, classify as entailment.\n"
                "4. If the hypothesis contradicts the premise or is not supported, classify as non-entailment.\n\n"
                "Use evidence tracing to map each hypothesis claim to specific premise evidence before classifying.\n\n"
                "Return entailment or non-entailment with a one-sentence justification."
            ),
            user_message=(
                "Premise: Libya's case against Britain and the US concerns the dispute over their demand for extradition of Libyans charged with blowing up a Pan Am jet over Lockerbie in 1988.\n\n"
                "Hypothesis: One case involved the extradition of Libyan suspects in the Pan Am Lockerbie bombing.\n\n"
                "Is the hypothesis entailed by the premise?"
            ),
            reference_notes="Correct answer: entailment. The premise directly states the extradition dispute over Libyans charged with the Pan Am Lockerbie bombing.",
        ),
        # ── BEYOND: Deductive Reasoning ───────────────────────────
        AgentPattern(
            key="agent_beyond_deductive_reasoning",
            logic="Beyond",
            subcategory="Logical Reasoning",
            task_title="Solve a closed-ended problem with structured deductive reasoning",
            source_paper_id="13",
            source_pattern_id="13-4-0",
            source_paper_title="Prompt Programming for Large Language Models: Beyond the Few-Shot Paradigm",
            source_pattern_name="Encouraging Deductive Reasoning",
            system_prompt_naive="You solve logic problems step by step.",
            system_prompt_peil_labelled=(
                "Role: You are a deductive reasoning specialist who solves closed-ended problems with traceable logic.\n\n"
                "Context: You receive problems that have a single definitive answer. Your reasoning must be explicit, auditable, and verifiable.\n\n"
                "Instructions:\n"
                "1. Split the problem into numbered steps.\n"
                "2. State any assumptions explicitly at each step.\n"
                "3. Provide a brief justification for each intermediate conclusion.\n"
                "4. Arrive at a single definitive answer.\n\n"
                "Techniques: Use serialized deductive reasoning — solve step by step, stating assumptions and linking conclusions.\n\n"
                "Output: Return numbered reasoning steps followed by a final answer."
            ),
            system_prompt_peil_unlabelled=(
                "You are a deductive reasoning specialist who solves closed-ended problems with traceable logic.\n\n"
                "You receive problems that have a single definitive answer. Your reasoning must be explicit, auditable, and verifiable.\n\n"
                "1. Split the problem into numbered steps.\n"
                "2. State any assumptions explicitly at each step.\n"
                "3. Provide a brief justification for each intermediate conclusion.\n"
                "4. Arrive at a single definitive answer.\n\n"
                "Use serialized deductive reasoning — solve step by step, stating assumptions and linking conclusions.\n\n"
                "Return numbered reasoning steps followed by a final answer."
            ),
            user_message=(
                "A company has three departments: Engineering, Marketing, and Finance. Each department has exactly one manager. "
                "The managers are Alice, Bob, and Carol. Given the following facts:\n"
                "- Alice does not manage Engineering.\n"
                "- Bob does not manage Marketing.\n"
                "- The Finance manager has been with the company for over 10 years.\n"
                "- Carol joined the company 3 years ago.\n"
                "Who manages each department?"
            ),
            reference_notes="Carol cannot manage Finance (only 3 years). Alice doesn't manage Engineering. So Alice manages Marketing or Finance. Bob doesn't manage Marketing. If Alice manages Finance, Bob manages Engineering, Carol manages Marketing. This is consistent with all constraints.",
        ),
        # ── IN: Error Identification / Debugging ──────────────────
        AgentPattern(
            key="agent_in_error_debugging",
            logic="In",
            subcategory="Error Identification",
            task_title="Debug a runtime error from a stack trace",
            source_paper_id="69",
            source_pattern_id="69-1-2",
            source_paper_title="Automated Design of Agentic Systems",
            source_pattern_name="Self-Reflection for Runtime Errors",
            system_prompt_naive="You debug code from error messages and stack traces.",
            system_prompt_peil_labelled=(
                "Role: You are a debugging specialist who analyses runtime errors and proposes precise, testable code fixes.\n\n"
                "Context: You receive stack traces, error messages, and the relevant code. Your goal is to identify the root cause and provide a corrected implementation.\n\n"
                "Instructions:\n"
                "1. Analyse the stack trace to identify the failing line and error type.\n"
                "2. Examine the relevant code to understand the root cause.\n"
                "3. Explain why the error occurs in one clear sentence.\n"
                "4. Provide the corrected code with the fix highlighted.\n\n"
                "Techniques: Use defect isolation — trace the error from the stack trace through the code to the root cause before proposing a fix.\n\n"
                "Output: Return the root cause explanation followed by the corrected code."
            ),
            system_prompt_peil_unlabelled=(
                "You are a debugging specialist who analyses runtime errors and proposes precise, testable code fixes.\n\n"
                "You receive stack traces, error messages, and the relevant code. Your goal is to identify the root cause and provide a corrected implementation.\n\n"
                "1. Analyse the stack trace to identify the failing line and error type.\n"
                "2. Examine the relevant code to understand the root cause.\n"
                "3. Explain why the error occurs in one clear sentence.\n"
                "4. Provide the corrected code with the fix highlighted.\n\n"
                "Use defect isolation — trace the error from the stack trace through the code to the root cause before proposing a fix.\n\n"
                "Return the root cause explanation followed by the corrected code."
            ),
            user_message=(
                "Error during evaluation:\n"
                "Traceback (most recent call last):\n"
                '  File "process_orders.py", line 42, in process_batch\n'
                "    total = sum(order['amount'] for order in orders)\n"
                "TypeError: 'NoneType' object is not subscriptable\n\n"
                "Code:\n"
                "```python\n"
                "def process_batch(orders):\n"
                "    total = sum(order['amount'] for order in orders)\n"
                "    average = total / len(orders)\n"
                "    return {'total': total, 'average': average, 'count': len(orders)}\n"
                "```\n\n"
                "The function is called with a list that sometimes contains None values from a database query."
            ),
            reference_notes="Root cause: the list contains None values which can't be subscripted. Fix: filter out None values or add a guard. Also should handle empty list for division by zero.",
        ),
        # ── OUT: Structured Output / Skeleton ─────────────────────
        AgentPattern(
            key="agent_out_skeleton_outline",
            logic="Out",
            subcategory="Output Customisation",
            task_title="Generate a skeleton outline for a topic",
            source_paper_id="72",
            source_pattern_id="72-0-0",
            source_paper_title="Skeleton-of-thought: Large language models can do parallel decoding",
            source_pattern_name="Skeleton Prompt Template T s",
            system_prompt_naive="You create short outlines. Give 3 to 10 numbered points, each very short.",
            system_prompt_peil_labelled=(
                "Role: You are an organiser responsible for giving only the skeleton (not the full content) for answering questions.\n\n"
                "Context: You produce minimal outlines with 3 to 10 numbered points to guide thinking. Each point must be very short — 3 to 5 words maximum, not full sentences.\n\n"
                "Instructions:\n"
                "1. Read the user's question or topic.\n"
                "2. Identify the key aspects that should be covered.\n"
                "3. Return 3 to 10 numbered skeleton points.\n"
                "4. Keep each point to 3-5 words only — no full sentences.\n\n"
                "Techniques: Use hierarchical decomposition to identify the key structural elements before listing them.\n\n"
                "Output: Return only numbered skeleton points, 3-5 words each. No full sentences or elaboration."
            ),
            system_prompt_peil_unlabelled=(
                "You are an organiser responsible for giving only the skeleton (not the full content) for answering questions.\n\n"
                "You produce minimal outlines with 3 to 10 numbered points to guide thinking. Each point must be very short — 3 to 5 words maximum, not full sentences.\n\n"
                "1. Read the user's question or topic.\n"
                "2. Identify the key aspects that should be covered.\n"
                "3. Return 3 to 10 numbered skeleton points.\n"
                "4. Keep each point to 3-5 words only — no full sentences.\n\n"
                "Use hierarchical decomposition to identify the key structural elements before listing them.\n\n"
                "Return only numbered skeleton points, 3-5 words each. No full sentences or elaboration."
            ),
            user_message="What are the pros and cons of using microservices architecture versus a monolithic architecture for a new web application?",
            reference_notes="A strong skeleton should cover: scalability, deployment, complexity, team independence, debugging, data consistency, and infrastructure costs — each in 3-5 words only.",
        ),
        # ── OVER: Summarisation with Context ──────────────────────
        AgentPattern(
            key="agent_over_contextual_summary",
            logic="Over",
            subcategory="Summarisation",
            task_title="Analyse a topic with domain context and constraints",
            source_paper_id="34",
            source_pattern_id="34-1-3",
            source_paper_title="Prompt Engineering with ChatGPT: A Guide for Academic Writers",
            source_pattern_name="Contextual Prompt",
            system_prompt_naive="You analyse topics and provide evaluations when asked.",
            system_prompt_peil_labelled=(
                "Role: You are a domain analyst who produces grounded evaluations of effectiveness, risks, and implications.\n\n"
                "Context: You receive a topic with domain context and must produce a focused analysis. Your output informs decisions, so it must be evidence-based and actionable.\n\n"
                "Instructions:\n"
                "1. Identify the key claims or developments in the topic.\n"
                "2. Evaluate effectiveness, risks, or implications as appropriate.\n"
                "3. Note any limitations or open questions.\n"
                "4. Provide actionable recommendations where relevant.\n\n"
                "Techniques: Use structured analysis with evidence grounding — assess each dimension separately before synthesising.\n\n"
                "Output: Return a structured analysis with clear sections for findings, risks, and recommendations."
            ),
            system_prompt_peil_unlabelled=(
                "You are a domain analyst who produces grounded evaluations of effectiveness, risks, and implications.\n\n"
                "You receive a topic with domain context and must produce a focused analysis. Your output informs decisions, so it must be evidence-based and actionable.\n\n"
                "1. Identify the key claims or developments in the topic.\n"
                "2. Evaluate effectiveness, risks, or implications as appropriate.\n"
                "3. Note any limitations or open questions.\n"
                "4. Provide actionable recommendations where relevant.\n\n"
                "Use structured analysis with evidence grounding — assess each dimension separately before synthesising.\n\n"
                "Return a structured analysis with clear sections for findings, risks, and recommendations."
            ),
            user_message="Given recent studies on drug delivery systems, critically evaluate the effectiveness and safety of targeted drug delivery approaches in cancer treatment.",
            reference_notes="A strong analysis should cover nanoparticle delivery, antibody-drug conjugates, liposomal formulations, tumour targeting specificity, off-target toxicity risks, and clinical trial evidence.",
        ),
    ]


AGENT_PATTERNS = build_agent_patterns()
AGENT_PATTERN_INDEX = {p.key: p for p in AGENT_PATTERNS}


def generation_path(pattern_key: str, model_key: str, run_index: int, variant: str) -> Path:
    return RESULTS_DIR / pattern_key / model_key / f"run_{run_index}_{variant}.json"


def judge_path(pattern_key: str, model_key: str) -> Path:
    return RESULTS_DIR / pattern_key / model_key / "judge_scores.json"


def reproducibility_path(pattern_key: str, model_key: str) -> Path:
    return RESULTS_DIR / pattern_key / model_key / "reproducibility.json"


def build_messages(pattern: AgentPattern, variant: str) -> list[dict[str, str]]:
    """Build the message list for a given variant.

    Key difference from main evaluation: PEIL prompts go as system messages,
    task data goes as user message — matching PEIL's intended agent architecture.
    """
    if variant == "naive":
        return [
            {"role": "system", "content": pattern.system_prompt_naive},
            {"role": "user", "content": pattern.user_message},
        ]
    elif variant == "peil_labelled":
        return [
            {"role": "system", "content": pattern.system_prompt_peil_labelled},
            {"role": "user", "content": pattern.user_message},
        ]
    elif variant == "peil_unlabelled":
        return [
            {"role": "system", "content": pattern.system_prompt_peil_unlabelled},
            {"role": "user", "content": pattern.user_message},
        ]
    else:
        raise ValueError(f"Unknown variant: {variant}")


def generate_with_system_prompt(
    runtime: AzureModelRuntime,
    pattern: AgentPattern,
    model_key: str,
    variant: str,
    run_index: int,
    force: bool,
) -> dict[str, Any]:
    """Generate output using system + user message architecture."""
    path = generation_path(pattern.key, model_key, run_index, variant)
    if path.exists() and not force:
        return read_json(path)

    messages = build_messages(pattern, variant)
    log(f"  Generating run_{run_index}_{variant} via {model_key} (system-prompt mode)...")

    # Use the underlying client directly for system+user message control
    client, resolved = runtime.get_client(model_key)
    request: dict[str, Any] = {
        "model": resolved.deployment,
        "messages": messages,
    }
    if resolved.spec.supports_temperature_zero:
        request["temperature"] = 0.0

    last_error: Optional[Exception] = None
    for attempt in range(1, 6):
        try:
            response = client.chat.completions.create(**request)
            break
        except Exception as exc:
            last_error = exc
            error_str = str(exc).lower()
            is_rate_limit = "429" in error_str or "ratelimit" in error_str
            if attempt == 5:
                break
            wait = min(60, 2.0 * (2 ** attempt)) if is_rate_limit else 2.0 * attempt
            if is_rate_limit:
                log(f"  Rate limited, waiting {wait:.0f}s (attempt {attempt}/5)")
            time.sleep(wait)
    else:
        if last_error:
            raise last_error

    message = response.choices[0].message
    usage = getattr(response, "usage", None)

    payload = {
        "timestamp_utc": now_utc_iso(),
        "pattern_key": pattern.key,
        "logic": pattern.logic,
        "subcategory": pattern.subcategory,
        "source_paper_id": pattern.source_paper_id,
        "source_pattern_id": pattern.source_pattern_id,
        "source_paper_title": pattern.source_paper_title,
        "variant": variant,
        "run_index": run_index,
        "model_key": model_key,
        "model_deployment": resolved.deployment,
        "api": "chat.completions (system+user)",
        "auth_mode": resolved.auth_mode,
        "base_url": resolved.base_url,
        "temperature": 0.0 if resolved.spec.supports_temperature_zero else None,
        "system_prompt": messages[0]["content"],
        "user_message": messages[1]["content"],
        "output": (message.content or "").strip(),
        "reasoning_content": getattr(message, "reasoning_content", None),
        "usage": {
            "input_tokens": getattr(usage, "prompt_tokens", None),
            "output_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        } if usage else {},
    }
    write_json(path, payload)
    return read_json(path)


def build_judge_prompt(pattern: AgentPattern, outputs: dict[str, str]) -> str:
    return (
        "Role: You are an expert evaluator assessing the quality of LLM outputs for a prompt engineering research study.\n\n"
        "Context: You are comparing three outputs generated from the same task. Output A used a naive system prompt, Output B used a PEIL-structured system prompt with labels, and Output C used the same PEIL content without labels. All received the same user message. Your evaluation must be objective, consistent, and evidence-based.\n\n"
        "Instructions:\n"
        "1. Read the task description and evaluation reference carefully.\n"
        "2. Score each output independently on Output Accuracy, Formatting Consistency, Fabrication Reduction, and Task Completeness using a 1-5 scale.\n"
        "3. Provide a short evidence-based justification for each score.\n"
        "4. Do not let ordering bias your judgment.\n\n"
        "Techniques: Think step-by-step about evidence, but return only the final JSON.\n\n"
        "Output: Return JSON only.\n\n"
        f"Task: {pattern.task_title}\n"
        f"Taxonomy Logic: {pattern.logic}\n"
        f"Subcategory: {pattern.subcategory}\n"
        f"Evaluation Reference: {pattern.reference_notes}\n\n"
        f"Output A (naive system prompt):\n{outputs['naive']}\n\n"
        f"Output B (PEIL labelled system prompt):\n{outputs['peil_labelled']}\n\n"
        f"Output C (PEIL unlabelled system prompt):\n{outputs['peil_unlabelled']}"
    )


def run_supplementary(runtime: AzureModelRuntime, model_keys: list[str], judge_model_key: str, force: bool) -> None:
    """Run the supplementary agent-oriented evaluation."""
    for pattern in AGENT_PATTERNS:
        for model_key in model_keys:
            log(f"Supplementary: pattern={pattern.key} model={model_key}")

            # Generate 3 runs × 3 variants
            for run_index in range(1, 4):
                for variant in VARIANT_TO_OUTPUT_KEY:
                    generate_with_system_prompt(runtime, pattern, model_key, variant, run_index, force)

            # Judge
            jpath = judge_path(pattern.key, model_key)
            if not jpath.exists() or force:
                log(f"  Judging {model_key} outputs via {judge_model_key}...")
                outputs = {
                    v: read_json(generation_path(pattern.key, model_key, 1, v))["output"]
                    for v in VARIANT_TO_OUTPUT_KEY
                }
                max_attempts = 3
                scores = None
                for attempt in range(1, max_attempts + 1):
                    result = runtime.generate_text(judge_model_key, build_judge_prompt(pattern, outputs), json_schema=JUDGE_SCHEMA)
                    try:
                        scores = extract_json_payload(result["text"])
                        break
                    except (ValueError, json.JSONDecodeError) as exc:
                        log(f"  Judge JSON parse failed attempt {attempt}/{max_attempts} ({exc})")
                        if attempt < max_attempts:
                            time.sleep(2)
                if scores is None:
                    raise RuntimeError("Judge failed after 3 attempts")
                write_json(jpath, {
                    "timestamp_utc": now_utc_iso(),
                    "pattern_key": pattern.key,
                    "evaluated_model_key": model_key,
                    "judge_model_key": judge_model_key,
                    "scores": scores,
                })

            # Reproducibility
            rpath = reproducibility_path(pattern.key, model_key)
            if not rpath.exists() or force:
                log(f"  Computing reproducibility for {model_key}...")
                variant_results: dict[str, Any] = {}
                for variant in VARIANT_TO_OUTPUT_KEY:
                    log(f"    Reproducibility: {variant} - embedding 3 runs...")
                    outputs_list = [
                        read_json(generation_path(pattern.key, model_key, ri, variant))["output"]
                        for ri in range(1, 4)
                    ]
                    embeddings = [runtime.embed_text(text) for text in outputs_list]
                    pairwise: dict[str, float] = {}
                    sims: list[float] = []
                    for li, ri in combinations(range(3), 2):
                        s = cosine_similarity(embeddings[li], embeddings[ri])
                        pairwise[f"run_{li+1}_run_{ri+1}"] = round(s, 6)
                        sims.append(s)

                    log(f"    Reproducibility: {variant} - LLM assessment...")
                    repro_prompt = (
                        f"Compare these 3 outputs from the same model and prompt variant. Are they functionally identical?\n\n"
                        f"Run 1:\n{outputs_list[0]}\n\nRun 2:\n{outputs_list[1]}\n\nRun 3:\n{outputs_list[2]}"
                    )
                    llm_assessment = None
                    for attempt in range(1, 4):
                        lr = runtime.generate_text(judge_model_key, repro_prompt, json_schema=REPRODUCIBILITY_SCHEMA)
                        try:
                            llm_assessment = extract_json_payload(lr["text"])
                            break
                        except (ValueError, json.JSONDecodeError) as exc:
                            log(f"    Repro JSON parse failed attempt {attempt}/3 ({exc})")
                            if attempt < 3:
                                time.sleep(2)
                    if llm_assessment is None:
                        raise RuntimeError("Reproducibility assessment failed")

                    variant_results[variant] = {
                        "pairwise_similarity": pairwise,
                        "mean_similarity": round(mean(sims), 6),
                        "llm_assessment": llm_assessment,
                    }
                write_json(rpath, {
                    "timestamp_utc": now_utc_iso(),
                    "pattern_key": pattern.key,
                    "evaluated_model_key": model_key,
                    "variants": variant_results,
                })

    # Summarise
    log("Generating supplementary summary...")
    summarise_supplementary()


def summarise_supplementary() -> None:
    """Generate summary files for supplementary results."""
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for pattern in AGENT_PATTERNS:
        for model_dir in sorted((RESULTS_DIR / pattern.key).iterdir()):
            if not model_dir.is_dir():
                continue
            jf = model_dir / "judge_scores.json"
            if not jf.exists():
                continue
            data = read_json(jf)
            scores = data["scores"]
            for variant, key in VARIANT_TO_OUTPUT_KEY.items():
                for metric in METRICS:
                    records.append({
                        "pattern": pattern.key,
                        "logic": pattern.logic,
                        "model": data["evaluated_model_key"],
                        "variant": variant,
                        "metric": metric,
                        "score": scores[key][metric]["score"],
                    })

    # Overall summary
    summary: dict[str, Any] = {}
    for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
        scores = [r["score"] for r in records if r["variant"] == variant]
        by_metric = {}
        for m in METRICS:
            ms = [r["score"] for r in records if r["variant"] == variant and r["metric"] == m]
            by_metric[m] = round(mean(ms), 4) if ms else None
        summary[variant] = {
            "metrics": by_metric,
            "overall_mean": round(mean(scores), 4) if scores else None,
            "sample_count": len(scores),
        }

    def deltas(left: str, right: str) -> dict[str, Optional[float]]:
        lm = summary.get(left, {}).get("metrics", {})
        rm = summary.get(right, {}).get("metrics", {})
        d: dict[str, Optional[float]] = {}
        for m in sorted(set(lm) | set(rm)):
            if m in lm and m in rm:
                d[m] = round(rm[m] - lm[m], 4)
            else:
                d[m] = None
        lo = summary.get(left, {}).get("overall_mean")
        ro = summary.get(right, {}).get("overall_mean")
        d["overall_mean"] = round(ro - lo, 4) if lo is not None and ro is not None else None
        return d

    write_json(SUMMARY_DIR / "supplementary_aggregate.json", {
        "generated_at_utc": now_utc_iso(),
        "description": "Supplementary evaluation: PEIL as system prompt for agent-oriented tasks",
        "difference_from_main": "PEIL prompts sent as system messages with task data as separate user messages",
        "score_summary": summary,
        "peil_labelled_minus_naive": deltas("naive", "peil_labelled"),
        "peil_unlabelled_minus_naive": deltas("naive", "peil_unlabelled"),
        "labelled_minus_unlabelled": deltas("peil_unlabelled", "peil_labelled"),
    })
    log("Summary written to supplementary/summary/")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Supplementary agent-oriented evaluation")
    parser.add_argument("--models", default=",".join(DEFAULT_EVALUATION_MODELS))
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--auth-mode", default="auto")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    runtime = AzureModelRuntime(auth_mode=args.auth_mode)
    model_keys = [m.strip() for m in args.models.split(",") if m.strip()]

    try:
        run_supplementary(runtime, model_keys, args.judge_model, args.force)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
