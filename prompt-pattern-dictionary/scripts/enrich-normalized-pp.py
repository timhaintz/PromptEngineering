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
from typing import Any, Dict, List, Optional

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

PEIL_REFERENCE_PROMPT = build_full_peil_system_prompt()

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
    "- peilPrompt: OPTIONAL. Return a SINGLE STRING containing a complete system prompt built with the PEIL template. Format EXACTLY as seven newline-separated lines in this order:\n"
    "  Role: …\n"
    "  Provide Clear Context: …\n"
    "  Break Down Complex Questions: …\n"
    "  Provide Specific Instructions: …\n"
    "  Define Conciseness: …\n"
    "  Prompting Techniques From Research: …\n"
    "  State Desired Output: …\n"
    "Each clause must be a grounded, declarative sentence (≤28 words) that reflects the "
    "pattern's template, application chips, and examples. Highlight the single most "
    "impactful industry/domain scenario when appropriate so downstream automation gets "
    "a concrete applied use case. Avoid placeholders, braces, bullet lists, or "
    "references to the PEIL variable names themselves.\n"
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

    def normalize_peil_prompt(
        value: Any,
        tasks: Optional[List[str]] = None,
        domain_examples: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Normalize PEIL prompt into a canonical multi-line system prompt."""

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

        def clamp_clause(text: str, max_words: int = 28, max_chars: int = 220) -> str:
            cleaned = re.sub(r"\s+", " ", str(text or '')).strip().strip('"')
            cleaned = cleaned.replace('{', '').replace('}', '')
            if not cleaned:
                return ''
            words = cleaned.split()
            if len(words) > max_words:
                cleaned = ' '.join(words[:max_words]) + '…'
            if len(cleaned) > max_chars:
                cleaned = cleaned[:max_chars].rstrip() + '…'
            return cleaned

        def finalize(section_map: Dict[str, str]) -> str:
            ordered_clauses: List[tuple[str, str]] = []
            normalized_lookup: Dict[str, str] = {}
            for label, normalized_key in section_order:
                clause = clamp_clause(section_map.get(normalized_key, ''))
                if not clause:
                    return ''
                if clause[-1] not in '.!?':
                    clause += '.'
                ordered_clauses.append((label, clause))
                normalized_lookup[normalized_key] = clause

            # Derive a primary domain from domain_examples or tasks to avoid mixing domains
            def detect_domain(text: str) -> Optional[str]:
                if not text:
                    return None
                lowered = text.lower()
                domain_map = {
                    'healthcare': ['patient', 'medical', 'health', 'clinic', 'vitals', 'diagnosis', 'rx', 'ehr', 'clinical', 'medication', 'medications', 'htn', 'metformin', 'provider'],
                    'finance': ['finance', 'financial', 'ledger', 'account', 'invoice', 'debit', 'credit', 'acct', 'ar', 'ap'],
                    'insurance': ['insurance', 'claim', 'policy', 'actuarial', 'underwrite'],
                    'legal': ['contract', 'legal', 'clause', 'jurisdiction', 'obligation'],
                    'cybersecurity': ['cyber', 'security', 'firewall', 'threat', 'ip', 'incident'],
                    'supply': ['supply', 'manufactur', 'logistics', 'inventory', 'warehouse'],
                    'education': ['education', 'curriculum', 'student', 'teacher'],
                }
                for domain, keys in domain_map.items():
                    for k in keys:
                        if k in lowered:
                            return domain
                return None

            primary_domain_counts: Dict[str, int] = {}
            domain_priority = ['healthcare', 'finance', 'insurance', 'legal', 'cybersecurity', 'supply', 'education']
            if domain_examples:
                for item in domain_examples:
                    if not isinstance(item, dict):
                        continue
                    combo = f"{item.get('task','')} {item.get('prompt','')}"
                    d = detect_domain(combo)
                    if d:
                        primary_domain_counts[d] = primary_domain_counts.get(d, 0) + 1
            if tasks:
                for t in tasks:
                    d = detect_domain(t)
                    if d:
                        primary_domain_counts[d] = primary_domain_counts.get(d, 0) + 1
            for _, clause in ordered_clauses:
                d = detect_domain(clause)
                if d:
                    primary_domain_counts[d] = primary_domain_counts.get(d, 0) + 1

            primary_domain = None
            if primary_domain_counts:
                def priority_key(item: Any) -> Any:
                    domain, count = item
                    priority = domain_priority.index(domain) if domain in domain_priority else len(domain_priority)
                    return (count, -priority)

                primary_domain = max(primary_domain_counts.items(), key=priority_key)[0]

            domain_example_phrase = {
                'healthcare': 'patient record',
                'finance': 'ledger entries',
                'insurance': 'insurance claim',
                'legal': 'contract clause',
                'cybersecurity': 'firewall log',
                'supply': 'supply chain entry',
                'education': 'curriculum module',
            }
            primary_phrase = domain_example_phrase.get(primary_domain, 'domain-specific output')

            def build_example_suffix(current_clause: str) -> Optional[str]:
                """Produce a short clause to reinforce a single domain scenario without bloating the line."""

                keyword_priority = [
                    'finance', 'financial', 'account', 'ledger', 'invoice', 'audit',
                    'insurance', 'claim', 'underwrite', 'policy', 'actuarial',
                    'patient', 'clinical', 'health', 'medical', 'diagnosis',
                    'contract', 'legal', 'compliance', 'regulatory', 'governance',
                    'cyber', 'security', 'threat', 'firewall', 'incident',
                    'supply', 'manufactur', 'logistics', 'retail', 'marketing',
                    'education', 'curriculum', 'student', 'teacher',
                ]

                def score_prompt(text: str) -> int:
                    lowered = text.lower()
                    for idx, keyword in enumerate(keyword_priority):
                        if keyword in lowered:
                            return len(keyword_priority) - idx
                    return 0

                best_text = None
                best_task = None
                if domain_examples:
                    best_score = -1
                    for item in domain_examples:
                        if not isinstance(item, dict):
                            continue
                        prompt_text = clamp_clause(item.get('prompt'), max_words=36, max_chars=260)
                        if not prompt_text:
                            continue
                        task_text = str(item.get('task') or '').strip()
                        current_score = score_prompt(f"{prompt_text} {task_text}")
                        if current_score > best_score:
                            best_score = current_score
                            best_text = prompt_text
                            best_task = task_text
                    if primary_domain:
                        for item in domain_examples:
                            combo = f"{item.get('task','')} {item.get('prompt','')}"
                            if detect_domain(combo) == primary_domain:
                                prompt_text = clamp_clause(item.get('prompt'), max_words=36, max_chars=260)
                                if prompt_text:
                                    best_text = prompt_text
                                    best_task = str(item.get('task') or '').strip()
                                    break

                if not best_text and tasks:
                    best_score = -1
                    for raw_task in tasks:
                        task_text = str(raw_task or '').strip()
                        if not task_text:
                            continue
                        score = score_prompt(task_text)
                        if score > best_score:
                            best_score = score
                            best_task = task_text
                    if best_task:
                        best_text = best_task

                if not best_text:
                    return None

                cleaned_text = re.sub(r"\s{2,}", " ", best_text).strip()
                display_task = best_task or cleaned_text
                display_task = display_task.replace(':', ' ').replace('→', ' to ')
                display_task = re.sub(r"\s+", " ", display_task).strip()
                task_words = display_task.split()
                if len(task_words) > 8:
                    display_task = ' '.join(task_words[:8])
                base_phrase = primary_phrase if primary_phrase else 'domain-specific output'
                suffix_parts: List[str] = []
                suffix_parts.append(f"Focus on {base_phrase} scenarios such as {display_task}")
                tokens_found = re.findall(r"'([^']{1,60})'", cleaned_text)
                base_word_count = len((current_clause or '').split())
                token_phrase = None
                if tokens_found:
                    token_phrase = ', '.join([f"'{t}'" for t in tokens_found[:2]])
                candidate = '. '.join(suffix_parts)
                candidate_words = len(candidate.split())
                if token_phrase:
                    # Only append token language if it keeps the clause compact
                    extra = f"Highlight shorthand tokens like {token_phrase}"
                    if base_word_count + candidate_words + len(extra.split()) <= 28:
                        candidate = candidate + '. ' + extra
                candidate = clamp_clause(candidate, max_words=22, max_chars=160)
                if candidate and candidate[-1] not in '.!?':
                    candidate += '.'
                # Guard against cases where the addition would cause heavy truncation
                if base_word_count + len(candidate.split()) > 28:
                    return None
                return candidate

            example_suffix = build_example_suffix(normalized_lookup.get('statedesiredoutput', ''))
            if example_suffix and 'statedesiredoutput' in normalized_lookup:
                combined = normalized_lookup['statedesiredoutput'].rstrip('.!?') + '. ' + example_suffix
                combined = clamp_clause(combined)
                if combined and combined[-1] not in '.!?':
                    combined += '.'
                normalized_lookup['statedesiredoutput'] = combined
                for idx, (label, _) in enumerate(ordered_clauses):
                    if normalize_key(label) == 'statedesiredoutput':
                        ordered_clauses[idx] = (label, combined)
                        break

            def strip_label(label: str, clause: str) -> str:
                normalized_label = label.lower()
                lowered_clause = clause.lower()
                if lowered_clause.startswith(f"{normalized_label}: "):
                    return clause[len(label) + 2:].strip()
                if lowered_clause.startswith(f"{normalized_label} -"):
                    return clause[len(label) + 2:].strip()
                return clause.strip()

            intro_label, intro_clause = ordered_clauses[0]
            intro_text = strip_label(intro_label, intro_clause)

            bullet_lines: List[str] = []
            for label, clause in ordered_clauses[1:]:
                text = strip_label(label, clause)
                if not text:
                    continue
                bullet_lines.append(f"- {text}")

            return "\n".join([intro_text, "", *bullet_lines])

        if value is None:
            return ''

        if isinstance(value, dict):
            section_map = {
                normalize_key(k): str(v or '').strip()
                for k, v in value.items()
                if normalize_key(k)
            }
            return finalize(section_map)

        text = str(value or '').strip()
        if not text:
            return ''

        working = text.replace('\r\n', '\n')
        pattern = re.compile(
            r"(Role|Provide\s+Clear\s+Context|Break\s+Down\s+Complex\s+Questions|Provide\s+Specific\s+Instructions|Define\s+Conciseness|Prompting\s+Techniques\s+From\s+Research|State\s+Desired\s+Output)\s*[:\-]\s*(.+?)(?=(Role|Provide\s+Clear\s+Context|Break\s+Down\s+Complex\s+Questions|Provide\s+Specific\s+Instructions|Define\s+Conciseness|Prompting\s+Techniques\s+From\s+Research|State\s+Desired\s+Output)\s*[:\-]|$)",
            re.IGNORECASE | re.DOTALL,
        )

        captured: Dict[str, str] = {}
        for match in pattern.finditer(working):
            label = normalize_key(match.group(1))
            clause = match.group(2).strip()
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
                        remainder = remainder.strip()
                        if remainder:
                            captured[normalized_key] = remainder
                        break

        return finalize(captured)

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
    return 0


if __name__ == '__main__':
    sys.exit(main())
