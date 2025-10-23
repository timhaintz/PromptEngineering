#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Optional enrichment for normalized prompt patterns using Azure OpenAI (gpt-5).
- Reads public/data/normalized-patterns.json (object with { metadata, patterns })
- For patterns with missing fields, asks the model to suggest values for:
    - template { role, context, action, format, response }
    - application (array of domain/task tags)
    - dependentLLM (only if explicitly referenced in the provided text, else null)
    - turn ("single" or "multi", only if clear)
    - usageSummary (1–2 sentences explaining how to apply the pattern in real-world use)
- Writes back the same file with merged fields plus aiAssisted metadata.
- Adds attrs.templateRawBracketed: a single-line bracketed string like
    "[Role: ..., Context: ..., Action: ..., Format: ..., Response: ...]" for export and UI display.

Usage:
  python enrich-normalized-pp.py [--model gpt-5] [--limit N]

Notes:
- Uses azure_models.get_model_client('gpt-5') from repo root. Ensure Python can import azure_models.py.
- This script is idempotent and skips fields already populated unless --force is added later.
"""
from __future__ import annotations
import os
import sys
import json
import re
import time
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple

# Ensure repo root is on PYTHONPATH so we can import azure_models.py
THIS_DIR = os.path.dirname(__file__)

# Ensure local helper modules are importable
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

try:
    from peil_prompt_reference import build_full_peil_system_prompt
except Exception as peil_err:
    print(f"ERROR: Failed to import peil_prompt_reference: {peil_err}")
    sys.exit(1)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from azure_models import get_model_client
except Exception as e:
    print(f"ERROR: Failed to import azure_models: {e}")
    sys.exit(1)

DATA_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', 'public', 'data'))
OUTPUT_FILE = os.path.join(DATA_DIR, 'normalized-patterns.json')
APPLICATION_FALLBACK_NOTE_DEFAULT = "Unable to process due to Azure's Content Management Policy."
TEMPLATE_CONTENT_FILTER_NOTE = APPLICATION_FALLBACK_NOTE_DEFAULT
TEMPLATE_NA = "N/A"
PEIL_INCOMPLETE_NOTE = "Not all information is available to run PEIL."

PEIL_REFERENCE_PROMPT = build_full_peil_system_prompt()

PEIL_GENERATOR_SYSTEM_PROMPT = dedent(
        """
        # INSTRUCTIONS
        - You are a prompt generator for the Prompt Engineering Instructional Language
            (PEIL) project.
        - Your task is to generate a single production-ready PEIL system prompt.
        - Your output is consumed by autonomous agents and viewed by humans. Return only
            the system prompt text.
        - Research summary informing this format:
                * Bomble et al. (2025) show structured, explicit prompts outperform vague
                    narratives.
                * Han, Wu, and Willard (2025) show bullet formatting improves precision,
                    recall, and F1.
        - Apply a hybrid style: deliver a short framing paragraph followed by
            rule-focused bullets as detailed in the return format guidance.
        - Anchor your output on the provided scenario persona and refer to them
            explicitly.
            - Do not mention the pattern name or refer to these instructions as a
                "pattern" or "scenario"; describe expectations directly.
        - Never prefix any sentence with label strings (for example "Role:" or
            "Provide Clear Context:").
        - Avoid labels such as "Break Down Complex Questions:", "Provide Specific
            Instructions:", "Define Conciseness:", or "Prompting Techniques From
            Research:".
        - Do not include placeholder variables or braces such as {Role}.
        - Write complete sentences.
        - Paraphrase any example content instead of quoting it verbatim.
        - Maintain an authoritative, operational tone suitable for system prompts.
        # END INSTRUCTIONS
        """
).strip()

PEIL_RETURN_FORMAT_GUIDANCE = dedent(
                """
                Return format requirements:
                        1. Write exactly two declarative sentences that frame the persona, mission,
                             and how the pattern principles support the selected scenario. Treat them
                             as one paragraph with no prefixed labels.
                        2. Insert a blank line.
                        3. Provide exactly six bullets in this order. Each bullet must be a full
                             sentence and may not start with labels such as "Role:" or "Provide
                             Clear Context:":
                                 - Context and inputs to honour. Reaffirm the signals, datasets, or
                                     stakeholders that shape the work.
                                 - Sequential breakdown of the work (use sub-bullets only when essential
                                     for clarity). Highlight the ordered steps you will follow.
                                 - Specific instructions, controls, or constraints to obey. Call out hard
                                     requirements or governance rules.
                                 - Conciseness expectations. State word, token, or formatting limits you
                                     will enforce.
                                 - Prompting techniques or reasoning methods to apply. Reference the
                                     tactics or verification loops you will use.
                                 - Desired output description referencing the scenario outcome directly.
                                     Make the deliverable explicit.
                        4. Keep the total prompt under 220 words.
                        5. Never prefix any line with the literal strings "Role:", "Provide Clear
                             Context:", "Break Down Complex Questions:", "Provide Specific
                             Instructions:", "Define Conciseness:", or "Prompting Techniques From
                             Research:".
                                6. Do not mention the pattern name or describe the guidance as a
                                    "pattern"; focus on the persona and concrete scenario details.
                """
).strip()

PEIL_HYBRID_RATIONALE = dedent(
        """
        Hybrid formatting rationale:
        - Structured, explicit prompts (Bomble et al., 2025) outperform vague or purely
            narrative instructions.
        - Bullet formatting (Han, Wu, and Willard, 2025) improves precision, recall, and
            F1 compared to plain descriptive paragraphs.
        - Combining a concise framing paragraph with explicit bullet rules balances human
            readability and LLM adherence, matching the PEIL blueprint.
        """
).strip()

PEIL_VARIABLE_GUIDE = dedent(
    """
    {Role}: This variable specifies the role of the prompt generator in the PEIL project and clarifies the responsibilities for guiding autonomous agents.
    {ProvideClearContext}: This variable ensures the model understands the surrounding environment, inputs, and stakeholders for the scenario.
    {BreakDownComplexQuestions}: This variable lists the discrete steps or sub-questions that drive a thorough line of inquiry.
    {ProvideSpecificInstructions}: This variable names the rules, controls, or constraints that must be enforced during execution.
    {DefineConciseness}: This variable sets expectations for brevity, length, or structure in the final output.
    {PromptingTechniquesFromResearch}: This variable emphasises the reasoning patterns or prompting manoeuvres to apply.
    {StateDesiredOutput}: This variable spells out the deliverable or evidence the agent must return to close the task.
    """
).strip()

BASE_SYSTEM_PROMPT = (
    "You are a careful data normalizer. Given a prompt pattern's description, examples, and current fields, "
    "infer ONLY missing or clearly improvable values. Return STRICT JSON with keys subset of {\"template\", \"application\", "
    "\"dependentLLM\", \"turn\", \"usageSummary\", \"templateRawBracketed\", \"applicationTasksString\", "
    "\"generalExplanation\", \"domainIndustryExamples\", \"peilPrompt\"}. Rules:\n"
    "- Do NOT hallucinate. If unsure, omit the key entirely.\n"
    "- dependentLLM must be null unless a specific model is explicitly referenced (e.g., GPT-3, GPT-4, Claude).\n"
    "- template: ALWAYS return an object with EXACTLY the five keys {role, context, action, format, response}. "
    "For any part that is not present in the source, set the value to 'N/A' (uppercase). Keep values concise phrases.\n"
    "- application: RETURN A SINGLE STRING containing ONE short sentence, or TWO short sentences if a second is needed for clarity. "
    "Use plain English and active voice. Keep each sentence simple (one main clause), concrete, and easy to scan. Avoid jargon, lists, parentheses, semicolons, em dashes, and placeholders. "
    "Stay grounded in the description and examples. Prefer ≤ 18 words per sentence. Do NOT return tag lists.\n"
    "- applicationTasksString: OPTIONAL. If you can confidently produce 1–8 concise tasks (prefer 8) for the pattern's media type, return a single comma+space separated string: 'task1, task2, ...'. "
    "Each task ≤5 words, DISTINCT, ACTIONABLE, and VERB-LED. Provide 3–4 cross-domain tasks AND 4–5 industry-specific tasks covering different sectors. Avoid repeating the same domain more than twice.\n"
    "- generalExplanation: 2 crisp sentences (≤22 words each) summarizing the pattern's intent, mechanics, and the user value. No fluff, no marketing tone.\n"
    "- domainIndustryExamples: OPTIONAL. Produce one object per task listed in "
    "applicationTasksString. Each object must include {task, prompt}. 'task' "
    "must EXACTLY match the provided chip text (case-sensitive). 'prompt' is "
    "1–2 grounded sentences (≤28 words each) that show how to ask the model "
    "to perform that task using the pattern's description, template, and "
    "examples. Use distinct industries whenever possible.\n"
    "- peilPrompt: OPTIONAL. Return a SINGLE STRING containing a complete system prompt "
    "built with the PEIL template. Use the hybrid format: two declarative sentences "
    "(one paragraph) that frame the persona and mission, a blank line, then six "
    "bullet sentences covering context, workflow, controls, conciseness, prompting "
    "techniques, and desired output. Bullets must not start with labels such as "
    "'Role:' or 'Provide Clear Context:'.\n"
    "Each sentence must be grounded (≤28 words) and reflect the pattern's template, "
    "application chips, and examples. Highlight the most impactful applied scenario "
    "when appropriate so downstream automation gets a concrete use case. Avoid "
    "placeholders, braces, or references to PEIL variable names.\n"
    "- turn is 'single' or 'multi' ONLY if clearly implied.\n"
    "- usageSummary: write exactly 1–2 sentences describing real-world usage without marketing tone; keep it general yet actionable; no invented claims.\n"
    "- templateRawBracketed: Return a SINGLE LINE exactly in the form [Role: <...>, Context: <...>, Action: <...>, Format: <...>, Response: <...>]. "
    "Always include all five segments in that order and use 'N/A' where a part is not present. Do NOT include newlines.\n"
)

SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "\n\n" + PEIL_REFERENCE_PROMPT

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find the first {...} block
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        snippet = m.group(0)
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None


def split_application_tasks_string(raw: Any) -> List[str]:
    """Split a comma+space separated tasks string into a list of chip texts."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    parts = [p.strip() for p in str(raw).split(',')]
    return [p for p in parts if p]


def build_user_payload(p: Dict[str, Any]) -> str:
    # Include all examples as requested; keep as-is without truncation
    examples = p.get('promptExamples', []) or []

    payload = {
        "id": p.get('id'),
        "name": p.get('name') or p.get('patternName'),
        "category": p.get('category'),
        "description": (p.get('description') or '')[:1200],
        "current": {
            "template": p.get('template') or {},
            "application": p.get('application') or [],
            "dependentLLM": p.get('dependentLLM'),
            "turn": p.get('turn'),
            "generalExplanation": p.get('generalExplanation'),
            "domainIndustryExamples": p.get('domainIndustryExamples'),
            "peilPrompt": p.get('peilPrompt'),
            "usageSummary": p.get('usageSummary'),
        },
        "applicationTasks": split_application_tasks_string(
            p.get('applicationTasksString')
        ),
        "examples": examples,
        "reference": p.get('reference') or {},
    }
    return json.dumps(payload, ensure_ascii=False)


def should_enrich(p: Dict[str, Any], fields: List[str]) -> bool:
    if not p:
        return False
    for f in fields:
        if f == 'dependentLLM' and p.get('dependentLLM', None) is None:
            return True
        if f == 'template':
            tpl = p.get('template') or {}
            if not any(tpl.get(k) for k in ['role','context','action','format','response']):
                return True
        if f == 'application' and not p.get('application'):
            return True
        if f == 'applicationTasksString' and not p.get('applicationTasksString'):
            return True
        if f == 'turn' and not p.get('turn'):
            return True
        if f == 'usageSummary' and not p.get('usageSummary'):
            return True
        if f == 'generalExplanation' and not p.get('generalExplanation'):
            return True
        if f == 'domainIndustryExamples':
            di = p.get('domainIndustryExamples')
            if not di or not isinstance(di, list):
                return True
            if isinstance(di, list) and not any(isinstance(item, dict) and item.get('task') and item.get('prompt') for item in di):
                return True
        if f == 'peilPrompt' and not p.get('peilPrompt'):
            return True
    return False


def main():
    model_name = 'gpt-5'
    limit = None
    fields = [
        'template',
        'application',
        'dependentLLM',
        'turn',
        'usageSummary',
        'templateRawBracketed',
        'applicationTasksString',
        'generalExplanation',
        'domainIndustryExamples',
        'peilPrompt',
    ]
    force_all = False
    force_fields: List[str] = []
    application_fallback_note = APPLICATION_FALLBACK_NOTE_DEFAULT
    disable_fallback = False
    fill_missing_application_only = False
    selected_ids = None  # Optional set of IDs to target
    application_tasks_only = False
    force_application_tasks = False
    dry_run = False
    peil_diagnostics_enabled = False
    anchor_deterministic = False

    # Parse args
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == '--model' and i + 1 < len(args):
            model_name = args[i + 1]
            continue
        if a == '--limit' and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except Exception:
                pass
            continue
        if a in ('--fields', '--enrich-fields') and i + 1 < len(args):
            raw = args[i + 1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            allowed = {
                'template',
                'application',
                'dependentLLM',
                'turn',
                'usageSummary',
                'applicationTasksString',
                'generalExplanation',
                'domainIndustryExamples',
                'peilPrompt',
                'templateRawBracketed',
            }
            chosen = [x for x in parts if x in allowed]
            if chosen:
                fields = chosen
            continue
        if a in ('--force', '--enrich-force'):
            force_all = True
            continue
        if a in ('--force-fields', '--enrich-force-fields') and i + 1 < len(args):
            raw = args[i + 1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            allowed = {
                'template',
                'application',
                'dependentLLM',
                'turn',
                'usageSummary',
                'applicationTasksString',
                'generalExplanation',
                'domainIndustryExamples',
                'peilPrompt',
                'templateRawBracketed',
            }
            force_fields = [x for x in parts if x in allowed]
            continue
        if a in ('--application-fallback-note',) and i + 1 < len(args):
            application_fallback_note = args[i + 1]
            continue
        if a in ('--no-fallback', '--disable-fallback'):
            disable_fallback = True
            continue
        if a in ('--fill-missing-application', '--application-fill-missing-only'):
            fill_missing_application_only = True
            continue
        if a == '--applicationtasks-only':
            application_tasks_only = True
            fields = ['applicationTasksString']
            continue
        if a == '--force-applicationtasks':
            force_application_tasks = True
            if 'applicationTasksString' not in force_fields:
                force_fields.append('applicationTasksString')
            continue
        if a == '--dry-run':
            dry_run = True
            continue
        if a == '--peil-diagnostics':
            peil_diagnostics_enabled = True
            continue
        if a == '--anchor-deterministic':
            anchor_deterministic = True
            continue
        if a == '--ids' and i + 1 < len(args):
            raw = args[i + 1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            if parts:
                selected_ids = set(parts)
            continue

    if not os.path.exists(OUTPUT_FILE):
        print(f"No normalized-patterns.json found at {OUTPUT_FILE}. Nothing to enrich.")
        return 0

    data = json.load(open(OUTPUT_FILE, 'r', encoding='utf-8'))
    patterns = data.get('patterns') if isinstance(data, dict) else data
    if not isinstance(patterns, list):
        print("normalized-patterns.json has unexpected format")
        return 1

    # Fast no-AI mode: fill missing application only and exit
    if fill_missing_application_only:
        filled = 0
        for p in patterns:
            if 'application' in fields:
                app = p.get('application')
                if not app:
                    # Only fill when fallback is enabled
                    if not disable_fallback:
                        p['application'] = [application_fallback_note]
                    else:
                        # Leave as missing/empty when fallback is disabled
                        continue
                    filled += 1
        json.dump(data, open(OUTPUT_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"Filled {filled} pattern(s) with application fallback note. No AI calls performed.")
        return 0

    client = get_model_client(model_name)

    enriched_count = 0
    peil_diagnostics_records: List[Dict[str, Any]] = []
    def clamp_sentence(s: str, max_words: int = 18, max_chars: int = 160) -> str:
        words = s.split()
        if len(words) > max_words:
            s = ' '.join(words[:max_words]) + '…'
        if len(s) > max_chars:
            s = s[:max_chars].rstrip() + '…'
        return s

    def normalize_application_to_string(value: Any) -> str:
        """Convert model output (string or list) into a single crisp string of up to two sentences."""
        # Turn into a raw text
        if isinstance(value, list):
            # Join list elements with commas for better readability when input is a tag list
            raw = ', '.join([str(x).strip() for x in value if str(x).strip()])
        else:
            raw = str(value or '').strip()

        if not raw:
            return ''

        # Split into sentences and cap at two
        parts = [seg.strip() for seg in re.split(r"(?<=[.!?])\s+", raw) if seg.strip()]
        if len(parts) > 2:
            parts = parts[:2]
        # Clamp each sentence for brevity
        parts = [clamp_sentence(p) for p in parts]
        # Join back to a single string; ensure trailing punctuation
        out = ' '.join(parts).strip()
        if out and out[-1] not in '.!?':
            out += '.'
        return out

    def normalize_application_tasks(value: Any) -> str:
        """Normalize model output for applicationTasksString into a canonical comma+space separated list.
        Rules enforced:
          - 1–8 tasks (truncate beyond 8)
          - Each task <= 5 words (truncate if longer)
          - Remove empty/duplicate tasks (case-insensitive)
        Returns empty string if nothing valid remains.
        """
        if value is None:
            return ''
        if isinstance(value, dict):  # unexpected
            value = list(value.values())
        if isinstance(value, list):
            candidates = []
            for v in value:
                if isinstance(v, str):
                    candidates.extend([p.strip() for p in re.split(r",|;|\n", v) if p.strip()])
                else:
                    candidates.append(str(v).strip())
        else:
            # string or other
            candidates = [p.strip() for p in re.split(r",|;|\n", str(value)) if p.strip()]

        tasks: List[str] = []
        seen = set()
        for c in candidates:
            if not c:
                continue
            # drop surrounding quotes or numbering
            c = re.sub(r"^\d+\.|^[\-•]\s*", "", c).strip().strip('"').strip("'")
            # truncate to 5 words
            words = c.split()
            if not words:
                continue
            if len(words) > 5:
                c = ' '.join(words[:5])
            key = c.lower()
            if key in seen:
                continue
            seen.add(key)
            tasks.append(c)
            if len(tasks) >= 8:
                break
        return ', '.join(tasks)

    def normalize_general_explanation(value: Any) -> str:
        text = str(value or '').strip()
        if not text:
            return ''
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [seg.strip() for seg in raw_sentences if seg.strip()]
        if not sentences:
            return ''
        sentences = sentences[:2]
        trimmed = [
            clamp_sentence(sentence, max_words=22, max_chars=200)
            for sentence in sentences
        ]
        out = ' '.join(trimmed)
        if out and out[-1] not in '.!?':
            out += '.'
        return out

    def normalize_prompt_example(value: Any) -> str:
        text = str(value or '').strip()
        if not text:
            return ''
        text = re.sub(r"\s+", " ", text)
        sentences = [
            seg.strip()
            for seg in re.split(r"(?<=[.!?])\s+", text)
            if seg.strip()
        ]
        if not sentences:
            return ''
        sentences = sentences[:2]
        trimmed = [
            clamp_sentence(sentence, max_words=28, max_chars=220)
            for sentence in sentences
        ]
        out = ' '.join(trimmed).strip()
        if out and out[-1] not in '.!?':
            out += '.'
        return out

    def normalize_domain_examples(
        value: Any,
        expected_tasks: List[str],
    ) -> List[Dict[str, str]]:
        """Normalize domainIndustryExamples into {task, prompt} dicts."""
        if value is None:
            return []

        entries: List[Dict[str, str]] = []

        def push(task_val: str, prompt_val: str):
            task = (task_val or '').strip()
            prompt = (prompt_val or '').strip()
            if not task or not prompt:
                return
            task_words = task.split()
            if len(task_words) > 8:
                task_trunc = ' '.join(task_words[:8])
                task = task_trunc
            key = (task.lower(), prompt.lower())
            if key in seen:
                return
            seen.add(key)
            entries.append({'task': task, 'prompt': prompt})

        seen = set()

        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, dict):
                    task_source = v.get('task') or k
                    prompt_source = v.get('prompt') or v.get('example') or ''
                    push(task_source, prompt_source)
                else:
                    push(k, v)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    task_val = (
                        item.get('task')
                        or item.get('scenario')
                        or item.get('domain')
                        or ''
                    )
                    prompt_val = (
                        item.get('prompt')
                        or item.get('example')
                        or item.get('instruction')
                        or ''
                    )
                    push(task_val, prompt_val)
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    push(str(item[0]), str(item[1]))
                else:
                    parts = [
                        p.strip()
                        for p in re.split(r"\||;", str(item))
                        if p.strip()
                    ]
                    if len(parts) >= 2:
                        push(parts[0], parts[1])
        else:
            parts = [
                p.strip()
                for p in re.split(r"\n|\||;", str(value))
                if p.strip()
            ]
            if len(parts) >= 2:
                push(parts[0], parts[1])

        if not expected_tasks:
            return []

        # Build lookup keyed by lower-case task for case-insensitive matching
        lookup: Dict[str, str] = {}
        for item in entries:
            key = item['task'].lower()
            if key not in lookup:
                lookup[key] = item['prompt']
        ordered: List[Dict[str, str]] = []
        for task in expected_tasks:
            needle = task.lower()
            prompt_text = lookup.get(needle)
            if not prompt_text:
                return []
            normalized_prompt = normalize_prompt_example(prompt_text)
            if not normalized_prompt:
                return []
            ordered.append({'task': task, 'prompt': normalized_prompt})

        return ordered

    def analyze_peil_structure(text: str) -> Dict[str, int]:
        content = str(text or '').strip()
        lines = [line.rstrip() for line in content.splitlines() if line.strip()]
        bullet_count = sum(1 for line in lines if line.lstrip().startswith('- '))
        paragraphs = [para.strip() for para in content.split('\n\n') if para.strip()]
        intro_block = paragraphs[0] if paragraphs else ''
        sentences = [
            seg.strip()
            for seg in re.split(r"(?<=[.!?])\s+", intro_block)
            if seg.strip()
        ]
        word_count = len(content.split()) if content else 0
        return {
            'bullet_count': bullet_count,
            'intro_sentence_count': len(sentences),
            'word_count': word_count,
        }

    def collect_candidate_example(
        pattern_data: Dict[str, Any],
        domain_examples: Optional[List[Dict[str, Any]]],
        deterministic: bool,
    ) -> Optional[Dict[str, str]]:
        candidates: List[Dict[str, str]] = []

        def normalize_example(task_val: Any, prompt_val: Any) -> Optional[Dict[str, str]]:
            task_text = str(task_val or '').strip()
            prompt_text = str(prompt_val or '').strip()
            if not prompt_text:
                return None
            prompt_text = re.sub(r"\s+", " ", prompt_text)
            if len(prompt_text) > 400:
                prompt_text = prompt_text[:400].rstrip() + '...'
            if task_text and len(task_text) > 120:
                task_text = task_text[:120].rstrip() + '...'
            return {'task': task_text, 'prompt': prompt_text}

        for item in domain_examples or []:
            if not isinstance(item, dict):
                continue
            normalized = normalize_example(item.get('task'), item.get('prompt'))
            if normalized:
                candidates.append(normalized)

        if not candidates:
            raw_examples = pattern_data.get('promptExamples') or []
            for entry in raw_examples:
                if isinstance(entry, dict):
                    normalized = normalize_example(
                        entry.get('task') or entry.get('scenario'),
                        entry.get('prompt')
                        or entry.get('example')
                        or entry.get('text')
                        or entry.get('content'),
                    )
                else:
                    normalized = normalize_example(None, entry)
                if normalized:
                    candidates.append(normalized)

        if not candidates:
            return None

        if deterministic:
            return candidates[0]

        candidates.sort(
            key=lambda item: len(item.get('prompt', '')),
            reverse=True,
        )
        return candidates[0]

    def normalize_peil_prompt(
        value: Any,
        tasks: Optional[List[str]] = None,
        domain_examples: Optional[List[Dict[str, Any]]] = None,
        *,
        pattern: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a production PEIL prompt via the LLM or return the standard note."""

        nonlocal peil_diagnostics_records

        if client is None:
            if peil_diagnostics_enabled:
                analysis = analyze_peil_structure(PEIL_INCOMPLETE_NOTE)
                peil_diagnostics_records.append(
                    {
                        'patternId': (pattern or {}).get('id'),
                        'anchorTask': None,
                        'status': 'note',
                        'noteReason': 'missing-client',
                        'bulletCount': analysis.get('bullet_count', 0),
                        'introSentenceCount': analysis.get('intro_sentence_count', 0),
                        'wordCount': analysis.get('word_count', 0),
                        'error': 'No model client available',
                    }
                )
            return PEIL_INCOMPLETE_NOTE

        pattern_dict = pattern or {}
        pattern_id = pattern_dict.get('id')

        def sanitize(text: Any, max_chars: int = 400) -> str:
            cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
            if len(cleaned) > max_chars:
                cleaned = cleaned[:max_chars].rstrip() + '...'
            return cleaned

        section_order = [
            ("Role", "role"),
            ("Provide Clear Context", "provideclearcontext"),
            ("Break Down Complex Questions", "breakdowncomplexquestions"),
            ("Provide Specific Instructions", "providespecificinstructions"),
            ("Define Conciseness", "defineconciseness"),
            ("Prompting Techniques From Research", "promptingtechniquesfromresearch"),
            ("State Desired Output", "statedesiredoutput"),
        ]

        def normalize_key(label: str) -> str:
            return re.sub(r"[^a-z]", "", (label or '').lower())

        def parse_sections(raw: Any) -> Dict[str, str]:
            if isinstance(raw, dict):
                return {
                    normalize_key(k): sanitize(v)
                    for k, v in raw.items()
                    if normalize_key(k)
                }
            text = str(raw or '').strip()
            if not text:
                return {}
            working = text.replace('\r\n', '\n')
            pattern_matcher = re.compile(
                r"(Role|Provide\s+Clear\s+Context|Break\s+Down\s+Complex\s+Questions|Provide\s+Specific\s+Instructions|Define\s+Conciseness|Prompting\s+Techniques\s+From\s+Research|State\s+Desired\s+Output)\s*[:\-]\s*(.+?)(?=(Role|Provide\s+Clear\s+Context|Break\s+Down\s+Complex\s+Questions|Provide\s+Specific\s+Instructions|Define\s+Conciseness|Prompting\s+Techniques\s+From\s+Research|State\s+Desired\s+Output)\s*[:\-]|$)",
                re.IGNORECASE | re.DOTALL,
            )
            captured: Dict[str, str] = {}
            for match in pattern_matcher.finditer(working):
                label = normalize_key(match.group(1))
                clause = sanitize(match.group(2))
                if label and clause:
                    captured[label] = clause
            if len(captured) < len(section_order):
                for line in working.split('\n'):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    for label, normalized_key in section_order:
                        lowered = label.lower()
                        if stripped.lower().startswith(lowered):
                            remainder = stripped[len(label):]
                            if remainder and remainder[0] in ':—-–':
                                remainder = remainder[1:]
                            remainder = sanitize(remainder)
                            if remainder:
                                captured[normalized_key] = remainder
                            break
            return captured

        def limit_words(text: str, max_words: int = 28) -> str:
            words = str(text or '').split()
            if len(words) <= max_words:
                return ' '.join(words).strip()
            clipped = ' '.join(words[:max_words]).rstrip(',;:')
            return f"{clipped}..."

        def ensure_sentence(text: str, fallback: str) -> str:
            candidate = sanitize(text, 320)
            if not candidate:
                candidate = sanitize(fallback, 320)
            candidate = limit_words(candidate)
            if not candidate:
                candidate = fallback
            if candidate and candidate[-1] not in '.!?':
                candidate += '.'
            return candidate

        def first_sentence(text: Optional[str]) -> str:
            cleaned = sanitize(text, 320)
            if not cleaned:
                return ''
            segments = re.split(r"(?<=[.!?])\s+", cleaned)
            return segments[0].strip()

        def extract_persona_from_prompt(prompt_text: Optional[str]) -> Optional[str]:
            if not prompt_text:
                return None
            lowered = str(prompt_text)
            patterns = [
                r"act as (?:an?|the)\s+([^;.,]+)",
                r"adopt (?:an?|the)\s+([^;.,]+?) persona",
                r"serve as (?:an?|the)\s+([^;.,]+)",
                r"assume (?:an?|the)\s+role of\s+([^;.,]+)",
                r"play the role of (?:an?|the)\s+([^;.,]+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, lowered, re.IGNORECASE)
                if match:
                    persona_raw = match.group(1).strip()
                    if persona_raw:
                        return sanitize(persona_raw, 160)
            return None

        def build_peil_sections(
            current_map: Dict[str, str],
            template_data: Optional[Dict[str, Any]],
            example_data: Optional[Dict[str, str]],
            tasks_list: Optional[List[str]],
            pattern_meta: Dict[str, Any],
        ) -> Tuple[Dict[str, str], Dict[str, Optional[str]]]:
            template_clean = force_template_five_keys(template_data or {})
            example_task = sanitize((example_data or {}).get('task'), 160)
            example_prompt = sanitize((example_data or {}).get('prompt'), 320)
            persona_text = extract_persona_from_prompt(example_prompt)
            if not persona_text and example_task:
                persona_text = sanitize(
                    f"a specialist who can {example_task.lower()}",
                    160,
                )
            scenario_summary = first_sentence(example_prompt)
            updated = dict(current_map)

            fallback_role = "You operate as the designated domain expert."
            fallback_context = (
                "Ground decisions in the provided scenario and pattern context."
            )
            fallback_breakdown = (
                "Decompose the work into ordered steps and resolve ambiguities early."
            )
            fallback_instructions = (
                "Obey stated controls, governance rules, and stakeholder approvals."
            )
            fallback_conciseness = (
                "Keep confirmations brief and final outputs under 220 words with only"
                " essential details."
            )
            fallback_techniques = (
                "Use research-backed prompting such as Chain-of-Thought and"
                " verification checks."
            )
            fallback_output = (
                "Deliver the requested artifact with risks, decisions, and next"
                " actions highlighted."
            )

            role_candidate = ""
            template_role = template_clean.get('role')
            if persona_text and template_role and template_role.upper() != TEMPLATE_NA:
                role_candidate = (
                    f"You embody {persona_text} while fulfilling the"
                    f" {template_role} responsibilities."
                )
            elif persona_text:
                role_candidate = f"You embody {persona_text} throughout the engagement."
            elif template_role and template_role.upper() != TEMPLATE_NA:
                role_candidate = f"You operate as {template_role}."
            updated['role'] = ensure_sentence(role_candidate, fallback_role)

            context_parts: List[str] = []
            template_context = template_clean.get('context')
            if template_context and template_context.upper() != TEMPLATE_NA:
                context_parts.append(template_context)
            if example_task:
                context_parts.append(
                    f"Use the '{example_task}' scenario as the working example."
                )
            if scenario_summary:
                context_parts.append(f"Key cues: {scenario_summary}")
            context_candidate = " ".join(context_parts)
            updated['provideclearcontext'] = ensure_sentence(
                context_candidate,
                fallback_context,
            )

            breakdown_parts: List[str] = []
            template_action = template_clean.get('action')
            if template_action and template_action.upper() != TEMPLATE_NA:
                breakdown_parts.append(template_action)
            if tasks_list:
                sample_tasks = ', '.join(tasks_list[:3])
                breakdown_parts.append(f"Handle phases such as {sample_tasks}.")
            breakdown_candidate = " ".join(breakdown_parts)
            updated['breakdowncomplexquestions'] = ensure_sentence(
                breakdown_candidate,
                fallback_breakdown,
            )

            template_format = template_clean.get('format')
            instructions_candidate = ""
            if template_format and template_format.upper() != TEMPLATE_NA:
                instructions_candidate = f"Follow these controls: {template_format}"
            updated['providespecificinstructions'] = ensure_sentence(
                instructions_candidate,
                fallback_instructions,
            )

            template_response = template_clean.get('response')
            conciseness_candidate = ""
            if template_response and template_response.upper() != TEMPLATE_NA:
                conciseness_candidate = (
                    f"Keep confirmations brief and align the output with"
                    f" {template_response}."
                )
            updated['defineconciseness'] = ensure_sentence(
                conciseness_candidate,
                fallback_conciseness,
            )

            techniques_candidate = (
                "Use Chain-of-Thought reasoning, plan verification questions, and"
                " apply research-backed prompting to validate each step."
            )
            if persona_text:
                techniques_candidate += f" Maintain alignment with {persona_text}."
            updated['promptingtechniquesfromresearch'] = ensure_sentence(
                techniques_candidate,
                fallback_techniques,
            )

            desired_parts: List[str] = []
            if template_response and template_response.upper() != TEMPLATE_NA:
                desired_parts.append(f"Deliver {template_response}.")
            if example_task:
                desired_parts.append(
                    f"Tailor the result to the '{example_task}' scenario"
                    " with actionable next steps."
                )
            desired_candidate = " ".join(desired_parts)
            updated['statedesiredoutput'] = ensure_sentence(
                desired_candidate,
                fallback_output,
            )

            scenario_info = {
                'persona': persona_text,
                'task': example_task,
                'summary': scenario_summary,
            }
            return updated, scenario_info

        if isinstance(value, str):
            _ = value.strip()

        section_map = parse_sections(value)

        focus_example = collect_candidate_example(
            pattern_dict,
            domain_examples,
            anchor_deterministic,
        )

        if not focus_example:
            note_reason = 'no-anchor-example'
            if peil_diagnostics_enabled:
                analysis = analyze_peil_structure(PEIL_INCOMPLETE_NOTE)
                peil_diagnostics_records.append(
                    {
                        'patternId': pattern_id,
                        'anchorTask': None,
                        'status': 'note',
                        'noteReason': note_reason,
                        'bulletCount': analysis.get('bullet_count', 0),
                        'introSentenceCount': analysis.get('intro_sentence_count', 0),
                        'wordCount': analysis.get('word_count', 0),
                        'error': None,
                    }
                )
            return PEIL_INCOMPLETE_NOTE

        anchor_task = focus_example.get('task') or None

        section_map, scenario_info = build_peil_sections(
            section_map,
            pattern_dict.get('template') or {},
            focus_example,
            tasks,
            pattern_dict,
        )

        missing_sections = [
            key for _, key in section_order if not section_map.get(key)
        ]
        if missing_sections:
            note_reason = 'missing-derived-variables'
            if peil_diagnostics_enabled:
                analysis = analyze_peil_structure(PEIL_INCOMPLETE_NOTE)
                peil_diagnostics_records.append(
                    {
                        'patternId': pattern_id,
                        'anchorTask': anchor_task,
                        'status': 'note',
                        'noteReason': note_reason,
                        'bulletCount': analysis.get('bullet_count', 0),
                        'introSentenceCount': analysis.get('intro_sentence_count', 0),
                        'wordCount': analysis.get('word_count', 0),
                        'error': None,
                    }
                )
            return PEIL_INCOMPLETE_NOTE

        variable_lines = [
            f"- {label} => {sanitize(section_map.get(key, 'N/A'))}"
            for label, key in section_order
        ]

        task_lines = [
            f"- {sanitize(task, 120)}"
            for task in (tasks or [])
            if str(task or '').strip()
        ]

        user_sections: List[str] = []
        user_sections.append(
            dedent(
                f"""
                Pattern overview:
                - Name: {sanitize(pattern_dict.get('name') or pattern_dict.get('patternName')) or 'N/A'}
                - Category: {sanitize(pattern_dict.get('category'), 120) or 'N/A'}
                - Description: {sanitize(pattern_dict.get('description'), 600) or 'N/A'}
                """
            ).strip()
        )

        template_details: List[str] = []
        template_obj = pattern_dict.get('template') or {}
        if isinstance(template_obj, dict) and any(template_obj.values()):
            normalized_template = force_template_five_keys(template_obj)
            for key_label, value_key in [
                ('Role', 'role'),
                ('Context', 'context'),
                ('Action', 'action'),
                ('Format', 'format'),
                ('Response', 'response'),
            ]:
                clause = normalized_template.get(value_key, '')
                if clause and clause.upper() != TEMPLATE_NA:
                    template_details.append(f"- {key_label} => {sanitize(clause, 220)}")
        if template_details:
            user_sections.append("Template guidance:\n" + "\n".join(template_details))

        scenario_lines: List[str] = []
        persona_display = scenario_info.get('persona') if scenario_info else None
        if persona_display:
            scenario_lines.append(f"- Persona => {persona_display}")
        scenario_task_display = scenario_info.get('task') if scenario_info else None
        if scenario_task_display:
            scenario_lines.append(f"- Scenario task => {scenario_task_display}")
        scenario_summary_display = scenario_info.get('summary') if scenario_info else None
        if scenario_summary_display:
            scenario_lines.append(f"- Scenario cues => {scenario_summary_display}")
        if scenario_lines:
            user_sections.append("Scenario anchor:\n" + "\n".join(scenario_lines))

        user_sections.append(
            "PEIL variable guidance:\n" + "\n".join(variable_lines)
        )

        user_sections.append(PEIL_HYBRID_RATIONALE)

        if task_lines:
            user_sections.append(
                "Application tasks to reference:\n" + "\n".join(task_lines)
            )

        example_section = dedent(
            f"""
            Selected domain example (paraphrase in the final prompt):
            - Task: {focus_example.get('task') or 'N/A'}
            - Prompt summary: {focus_example.get('prompt') or 'N/A'}
            """
        ).strip()
        user_sections.append(example_section)

        user_sections.append("PEIL variable definitions:\n" + PEIL_VARIABLE_GUIDE)
        user_sections.append(PEIL_RETURN_FORMAT_GUIDANCE)

        user_prompt = "\n\n".join(section for section in user_sections if section)

        llm_response_text: Optional[str] = None
        llm_error: Optional[str] = None

        try:
            messages = [
                {"role": "system", "content": PEIL_GENERATOR_SYSTEM_PROMPT},
                {"role": "system", "content": PEIL_REFERENCE_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
            response = client.create_chat_completion(messages, stream=False)
            content: Optional[str] = None
            if hasattr(response, 'choices') and response.choices:
                content = getattr(response.choices[0].message, 'content', None)
            if not content and isinstance(response, dict):
                content = (
                    response.get('choices', [{}])[0]
                    .get('message', {})
                    .get('content')
                )
            if content:
                llm_response_text = content.strip()
        except Exception as exc:
            llm_error = str(exc)
            print(f"[{pattern_id}] WARN: PEIL generation failed: {exc}")

        if llm_response_text:
            structure = analyze_peil_structure(llm_response_text)
            if peil_diagnostics_enabled:
                peil_diagnostics_records.append(
                    {
                        'patternId': pattern_id,
                        'anchorTask': anchor_task,
                        'status': 'generated',
                        'noteReason': None,
                        'bulletCount': structure.get('bullet_count', 0),
                        'introSentenceCount': structure.get('intro_sentence_count', 0),
                        'wordCount': structure.get('word_count', 0),
                        'error': None,
                    }
                )
            return llm_response_text
        note_reason = 'model-error' if llm_error else 'no-llm-output'
        if peil_diagnostics_enabled:
            analysis = analyze_peil_structure(PEIL_INCOMPLETE_NOTE)
            peil_diagnostics_records.append(
                {
                    'patternId': pattern_id,
                    'anchorTask': anchor_task,
                    'status': 'note',
                    'noteReason': note_reason,
                    'bulletCount': analysis.get('bullet_count', 0),
                    'introSentenceCount': analysis.get('intro_sentence_count', 0),
                    'wordCount': analysis.get('word_count', 0),
                    'error': llm_error,
                }
            )
        return PEIL_INCOMPLETE_NOTE

    # Phrase diversification state (only in-memory for current run)
    generic_phrase_primary = 'clarify user intent'
    generic_alternatives = [
        'Elicit missing details',
        'Identify user goal',
        'Confirm task objective',
        'Disambiguate request scope',
        'Capture success criteria'
    ]
    generic_usage_count = 0

    def diversify_generic_tasks(task_string: str) -> str:
        """Reduce repeated generic tasks by rotating alternatives."""
        nonlocal generic_usage_count
        if not task_string:
            return task_string
        parts = [p.strip() for p in task_string.split(',')]
        changed = False
        for i, t in enumerate(parts):
            if t.lower() == generic_phrase_primary:
                if generic_usage_count >= 1:
                    alt_index = (
                        (generic_usage_count - 1) % len(generic_alternatives)
                    )
                    parts[i] = generic_alternatives[alt_index]
                    changed = True
                generic_usage_count += 1
        if changed:
            return ', '.join(parts)
        return task_string

    def _clean_cell(v: Any) -> str:
        s = str(v or '').strip()
        s = re.sub(r"\s+", " ", s)
        return s if s else TEMPLATE_NA

    def force_template_five_keys(tpl_in: Any) -> Dict[str, str]:
        tpl = tpl_in if isinstance(tpl_in, dict) else {}
        keys = ['role', 'context', 'action', 'format', 'response']
        out: Dict[str, str] = {}
        for k in keys:
            out[k] = _clean_cell(tpl.get(k, TEMPLATE_NA))
            if not out[k]:
                out[k] = TEMPLATE_NA
        return out

    def build_bracketed_from_template(tpl_dict: Dict[str, str]) -> str:
        # tpl_dict must already be normalized by force_template_five_keys
        return (
            f"[Role: {tpl_dict['role']}, Context: {tpl_dict['context']}, "
            f"Action: {tpl_dict['action']}, Format: {tpl_dict['format']}, "
            f"Response: {tpl_dict['response']}]"
        )

    def set_template_bracket_and_object(pat: Dict[str, Any], text_all: str):
        """Set template fields to a shared placeholder value."""
        normalized = force_template_five_keys({
            'role': text_all,
            'context': text_all,
            'action': text_all,
            'format': text_all,
            'response': text_all,
        })
        pat['template'] = normalized
        pat['templateRawBracketed'] = build_bracketed_from_template(normalized)

    processed_count = 0
    for p in patterns:
        if selected_ids is not None and p.get('id') not in selected_ids:
            continue
        # Decide whether to call the model.
        must_force = force_all or bool(set(force_fields) & set(fields))
        if not must_force and not should_enrich(p, fields):
            continue

        if limit is not None and processed_count >= limit:
            break
        processed_count += 1

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_payload(p)},
        ]

        try:
            pid = p.get('id')
            # Log pattern ID for tracing with API logs.
            print(f"[{pid}] REQUEST: chat.completions -> {model_name}")
            sys.stdout.flush()
            # Do not pass temperature explicitly to support models with fixed defaults.
            resp = client.create_chat_completion(messages, stream=False)
            # azure_models clients typically return OpenAI-like response
            content = None
            if hasattr(resp, 'choices') and resp.choices:
                content = getattr(resp.choices[0].message, 'content', None)
            if not content and isinstance(resp, dict):
                content = resp.get('choices', [{}])[0].get('message', {}).get('content')
            if not content:
                print(
                    f"[{pid}] RESPONSE: no content; applying fallback if enabled."
                )
                if not dry_run:
                    if 'application' in fields and not disable_fallback:
                        # Write fallback as a single string, not an array
                        p['application'] = application_fallback_note
                    if not disable_fallback:
                        # Generic failure -> set template to N/A for all five
                        set_template_bracket_and_object(p, TEMPLATE_NA)
                # Continue to next pattern without incrementing enriched_count (not AI-derived)
                continue

            obj = extract_json(content)
            if not obj or not isinstance(obj, dict):
                print(
                    f"[{pid}] RESPONSE: unparsable JSON; applying fallback if enabled."
                )
                if not dry_run:
                    if 'application' in fields and not disable_fallback:
                        # Write fallback as a single string, not an array
                        p['application'] = application_fallback_note
                    if not disable_fallback:
                        # Generic failure -> set template to N/A for all five
                        set_template_bracket_and_object(p, TEMPLATE_NA)
                continue

            updated_fields = []
            dry_run_changes: Dict[str, Any] = {}
            task_list = split_application_tasks_string(
                p.get('applicationTasksString')
            )
            domain_examples_for_peil: List[Dict[str, Any]] = []
            existing_domain_examples = p.get('domainIndustryExamples')
            if isinstance(existing_domain_examples, list):
                domain_examples_for_peil = [
                    item
                    for item in existing_domain_examples
                    if isinstance(item, dict)
                    and item.get('task')
                    and item.get('prompt')
                ]
            for key in [
                'template',
                'application',
                'dependentLLM',
                'turn',
                'usageSummary',
                'templateRawBracketed',
                'applicationTasksString',
                'generalExplanation',
                'domainIndustryExamples',
                'peilPrompt',
            ]:
                if key not in fields:
                    continue
                if (
                    key in obj
                    and obj[key] is not None
                    and obj[key] != {}
                    and obj[key] != []
                ):
                    # Normalize types and overwrite
                    updated = False
                    if key == 'application':
                        # Convert to a single string (1–2 sentences)
                        normalized_value = normalize_application_to_string(obj[key])
                        if normalized_value:
                            if dry_run:
                                dry_run_changes[key] = normalized_value
                            else:
                                p[key] = normalized_value
                            updated = True
                    elif key == 'applicationTasksString':
                        norm_tasks = normalize_application_tasks(obj[key])
                        if norm_tasks:
                            diversified = diversify_generic_tasks(norm_tasks)
                            if dry_run:
                                dry_run_changes[key] = diversified
                            else:
                                p[key] = diversified
                            updated = True
                            task_list = split_application_tasks_string(diversified)
                    elif key == 'template':
                        # Ensure exactly five keys with N/A defaults
                        normalized_tpl = force_template_five_keys(obj[key])
                        if dry_run:
                            dry_run_changes[key] = normalized_tpl
                        else:
                            p[key] = normalized_tpl
                        updated = True
                    elif key == 'templateRawBracketed':
                        # Ensure single line bracketed form; strip whitespace/newlines
                        raw = str(obj[key]).strip().replace('\n', ' ')
                        if dry_run:
                            dry_run_changes[key] = raw
                        else:
                            p['templateRawBracketed'] = raw
                        updated = True
                    elif key == 'generalExplanation':
                        summary = normalize_general_explanation(obj[key])
                        if summary:
                            if dry_run:
                                dry_run_changes[key] = summary
                            else:
                                p[key] = summary
                            updated = True
                    elif key == 'domainIndustryExamples':
                        examples_norm = normalize_domain_examples(
                            obj[key],
                            task_list,
                        )
                        if examples_norm:
                            domain_examples_for_peil = examples_norm
                            if dry_run:
                                dry_run_changes[key] = examples_norm
                            else:
                                p[key] = examples_norm
                            updated = True
                    elif key == 'peilPrompt':
                        prompt_text = normalize_peil_prompt(
                            obj[key],
                            task_list,
                            domain_examples_for_peil,
                            pattern=p,
                        )
                        if prompt_text:
                            if dry_run:
                                dry_run_changes[key] = prompt_text
                            else:
                                p[key] = prompt_text
                            updated = True
                    else:
                        # Overwrite with model output for other fields
                        if dry_run:
                            dry_run_changes[key] = obj[key]
                        else:
                            p[key] = obj[key]
                        updated = True

                    if updated:
                        updated_fields.append(key)

            # Ensure templateRawBracketed mirrors the normalized template when updated.
            if not dry_run and 'template' in updated_fields and isinstance(p.get('template'), dict):
                tpl_norm = force_template_five_keys(p.get('template'))
                p['template'] = tpl_norm
                p['templateRawBracketed'] = build_bracketed_from_template(tpl_norm)

            if dry_run and 'template' in updated_fields and 'template' in dry_run_changes:
                tpl_norm = force_template_five_keys(dry_run_changes['template'])
                dry_run_changes['template'] = tpl_norm
                dry_run_changes['templateRawBracketed'] = build_bracketed_from_template(tpl_norm)

            if updated_fields:
                updated_fields_str = ', '.join(updated_fields)
                if dry_run:
                    print(f"[{pid}] DRY RUN: would update {updated_fields_str}")
                    if dry_run_changes:
                        print(json.dumps(dry_run_changes, ensure_ascii=False, indent=2))
                else:
                    print(f"[{pid}] RESPONSE: OK; updated {updated_fields_str}")
                    p['aiAssisted'] = True
                    combined_fields = (p.get('aiAssistedFields') or []) + updated_fields
                    p['aiAssistedFields'] = sorted(list(set(combined_fields)))
                    p['aiAssistedModel'] = model_name
                    p['aiAssistedAt'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                enriched_count += 1
        except Exception as e:
            # Content filter or other failure; set application fallback note if requested
            print(f"[{p.get('id')}] ERROR: {e}")
            if not dry_run and not disable_fallback:
                # Determine if it was a content filter issue
                msg = (str(e) or '').lower()
                is_content_filter = ('content' in msg and ('policy' in msg or 'filter' in msg)) or 'content management policy' in msg
                if 'application' in fields:
                    # Use explicit content management note for application to match prior behavior
                    p['application'] = application_fallback_note if is_content_filter else p.get('application') or ''
                # For template fields, follow requested rules
                if is_content_filter:
                    set_template_bracket_and_object(p, TEMPLATE_CONTENT_FILTER_NOTE)
                else:
                    set_template_bracket_and_object(p, TEMPLATE_NA)
            continue

    if dry_run:
        print(f"Dry run complete. Would update {enriched_count} pattern(s). No files written.")
        if peil_diagnostics_enabled and peil_diagnostics_records:
            print(json.dumps(peil_diagnostics_records, ensure_ascii=False, indent=2))
        return 0

    # Final coercion pass: ensure application is ALWAYS a single string
    coerced = 0
    for p in patterns:
        if isinstance(p.get('application'), list):
            p['application'] = normalize_application_to_string(p.get('application'))
            coerced += 1

    # Write back
    json.dump(data, open(OUTPUT_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"Enrichment complete. Updated {enriched_count} pattern(s). Coerced {coerced} application field(s) to string.")
    if peil_diagnostics_enabled and peil_diagnostics_records:
        print(json.dumps(peil_diagnostics_records, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
