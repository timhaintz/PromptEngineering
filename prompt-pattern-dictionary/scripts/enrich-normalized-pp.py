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

SYSTEM_PROMPT = (
    "You are a careful data normalizer. Given a prompt pattern's description, examples, and current fields, "
    "infer ONLY missing or clearly improvable values. Return STRICT JSON with keys subset of {\"template\", \"application\", \"dependentLLM\", \"turn\", \"usageSummary\", \"templateRawBracketed\"}. "
    "Rules: \n"
    "- Do NOT hallucinate. If unsure, omit the key entirely.\n"
    "- dependentLLM must be null unless a specific model is explicitly referenced (e.g., GPT-3, GPT-4, Claude).\n"
    "- template: ALWAYS return an object with EXACTLY the five keys {role, context, action, format, response}. "
    "For any part that is not present in the source, set the value to 'N/A' (uppercase) — do not leave it blank. Keep values concise phrases.\n"
    "- application: RETURN A SINGLE STRING containing ONE short sentence, or TWO short sentences if a second is needed for clarity. "
    "Use plain English and active voice. Keep each sentence simple (one main clause), concrete, and easy to scan. Avoid jargon, lists, parentheses, semicolons, em dashes, and placeholders. "
    "Stay grounded in the description and examples. Prefer ≤ 18 words per sentence. Do NOT return tags.\n"
    "- turn is 'single' or 'multi' ONLY if clearly implied.\n"
    "- usageSummary: write exactly 1–2 sentences describing real-world usage without marketing tone; keep it general yet actionable; no invented claims.\n"
    "- templateRawBracketed: Return a SINGLE LINE exactly in the form [Role: <...>, Context: <...>, Action: <...>, Format: <...>, Response: <...>]. "
    "Always include all five segments in that order and use 'N/A' where a part is not present. Do NOT include newlines.\n"
)

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
        },
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
        if f == 'turn' and not p.get('turn'):
            return True
        if f == 'usageSummary' and not p.get('usageSummary'):
            return True
    return False


def main():
    model_name = 'gpt-5'
    limit = None
    fields = ['template','application','dependentLLM','turn','usageSummary','templateRawBracketed']
    force_all = False
    force_fields: List[str] = []
    application_fallback_note = APPLICATION_FALLBACK_NOTE_DEFAULT
    disable_fallback = False
    fill_missing_application_only = False
    selected_ids = None  # Optional set of IDs to target

    # Parse args
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == '--model' and i + 1 < len(args):
            model_name = args[i+1]
        if a == '--limit' and i + 1 < len(args):
            try:
                limit = int(args[i+1])
            except Exception:
                pass
        if a in ('--fields','--enrich-fields') and i + 1 < len(args):
            raw = args[i+1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            allowed = {'template','application','dependentLLM','turn','usageSummary'}
            chosen = [x for x in parts if x in allowed]
            if chosen:
                fields = chosen
        if a in ('--force','--enrich-force'):
            force_all = True
        if a in ('--force-fields','--enrich-force-fields') and i + 1 < len(args):
            raw = args[i+1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            allowed = {'template','application','dependentLLM','turn','usageSummary'}
            force_fields = [x for x in parts if x in allowed]
        if a in ('--application-fallback-note',) and i + 1 < len(args):
            # Allow overriding the fallback note text from CLI
            application_fallback_note = args[i+1]
        if a in ('--no-fallback', '--disable-fallback'):
            # Do not write any fallback message on errors or content filter blocks
            disable_fallback = True
        if a in ('--fill-missing-application', '--application-fill-missing-only'):
            # Fast, no-AI pass: only set fallback note for patterns with empty/missing application
            fill_missing_application_only = True
        if a == '--ids' and i + 1 < len(args):
            raw = args[i+1]
            parts = [x.strip() for x in raw.split(',') if x.strip()]
            if parts:
                selected_ids = set(parts)

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

    def set_template_bracket_and_object(pat: Dict[str, Any], text_for_all_fields: str):
        """Set both templateRawBracketed and template object with the provided text for all five keys."""
        normalized = force_template_five_keys({
            'role': text_for_all_fields,
            'context': text_for_all_fields,
            'action': text_for_all_fields,
            'format': text_for_all_fields,
            'response': text_for_all_fields,
        })
        pat['template'] = normalized
        pat['templateRawBracketed'] = build_bracketed_from_template(normalized)

    for p in patterns:
        if limit is not None and enriched_count >= limit:
            break
        if selected_ids is not None and p.get('id') not in selected_ids:
            continue
        # Decide whether to call model: if force_all OR force_fields intersect requested fields, always call.
        must_force = force_all or (bool(set(force_fields) & set(fields)))
        if not must_force and not should_enrich(p, fields):
            continue

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_payload(p)},
        ]

        try:
            pid = p.get('id')
            # Log the pattern ID before making the API call so it's easy to correlate with HTTP logs
            print(f"[{pid}] REQUEST: chat.completions -> {model_name}")
            sys.stdout.flush()
            # Do not pass temperature explicitly to support models that only allow default
            resp = client.create_chat_completion(messages, stream=False)
            # azure_models clients typically return OpenAI-like response
            content = None
            if hasattr(resp, 'choices') and resp.choices:
                content = getattr(resp.choices[0].message, 'content', None)
            if not content and isinstance(resp, dict):
                content = (
                    resp.get('choices', [{}])[0]
                       .get('message', {})
                       .get('content')
                )
            if not content:
                print(f"[{pid}] RESPONSE: no content; applying fallback if enabled.")
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
                print(f"[{pid}] RESPONSE: unparsable JSON; applying fallback if enabled.")
                if 'application' in fields and not disable_fallback:
                    # Write fallback as a single string, not an array
                    p['application'] = application_fallback_note
                if not disable_fallback:
                    # Generic failure -> set template to N/A for all five
                    set_template_bracket_and_object(p, TEMPLATE_NA)
                continue

            updated_fields = []
            for key in ['template', 'application', 'dependentLLM', 'turn', 'usageSummary', 'templateRawBracketed']:
                if key not in fields:
                    continue
                if key in obj and obj[key] is not None and obj[key] != {} and obj[key] != []:
                    # Normalize types and overwrite
                    if key == 'application':
                        # Convert to a single string (1–2 sentences)
                        p[key] = normalize_application_to_string(obj[key])
                    elif key == 'template':
                        # Ensure exactly five keys with N/A defaults
                        p[key] = force_template_five_keys(obj[key])
                    elif key == 'templateRawBracketed':
                        # Ensure single line bracketed form; strip whitespace/newlines
                        raw = str(obj[key]).strip().replace('\n', ' ')
                        p['templateRawBracketed'] = raw
                    else:
                        # Overwrite with model output for other fields
                        p[key] = obj[key]
                    updated_fields.append(key)

            # Ensure bracketed string exists and matches the normalized template when template was updated
            if 'template' in updated_fields and isinstance(p.get('template'), dict):
                tpl_norm = force_template_five_keys(p.get('template'))
                p['template'] = tpl_norm
                p['templateRawBracketed'] = build_bracketed_from_template(tpl_norm)

            if updated_fields:
                print(f"[{pid}] RESPONSE: OK; updated {', '.join(updated_fields)}")
                p['aiAssisted'] = True
                p['aiAssistedFields'] = sorted(list(set((p.get('aiAssistedFields') or []) + updated_fields)))
                p['aiAssistedModel'] = model_name
                p['aiAssistedAt'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                enriched_count += 1
        except Exception as e:
            # Content filter or other failure; set application fallback note if requested
            print(f"[{p.get('id')}] ERROR: {e}")
            if not disable_fallback:
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
