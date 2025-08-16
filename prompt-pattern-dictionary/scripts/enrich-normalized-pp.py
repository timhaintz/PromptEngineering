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
- Writes back the same file with merged fields plus aiAssisted metadata.

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

SYSTEM_PROMPT = (
    "You are a careful data normalizer. Given a prompt pattern's description, examples, and current fields, "
    "infer ONLY missing or clearly improvable values. Return STRICT JSON with keys subset of {\"template\", \"application\", \"dependentLLM\", \"turn\"}. "
    "Rules: \n"
    "- Do NOT hallucinate. If unsure, omit the key entirely.\n"
    "- dependentLLM must be null unless a specific model is explicitly referenced (e.g., GPT-3, GPT-4, Claude).\n"
    "- template fields should be concise.\n"
    "- application: 1-5 short domain/task tags, lowercase kebab-case preferred.\n"
    "- turn is 'single' or 'multi' ONLY if clearly implied.\n"
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
    # Limit example lengths to keep tokens small
    examples = p.get('promptExamples', []) or []
    examples = [e[:800] for e in examples[:2]]

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
    return False


def main():
    model_name = 'gpt-5'
    limit = None
    fields = ['template','application','dependentLLM','turn']

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
            allowed = {'template','application','dependentLLM','turn'}
            chosen = [x for x in parts if x in allowed]
            if chosen:
                fields = chosen

    if not os.path.exists(OUTPUT_FILE):
        print(f"No normalized-patterns.json found at {OUTPUT_FILE}. Nothing to enrich.")
        return 0

    data = json.load(open(OUTPUT_FILE, 'r', encoding='utf-8'))
    patterns = data.get('patterns') if isinstance(data, dict) else data
    if not isinstance(patterns, list):
        print("normalized-patterns.json has unexpected format")
        return 1

    client = get_model_client(model_name)

    enriched_count = 0
    for p in patterns:
        if limit is not None and enriched_count >= limit:
            break
        if not should_enrich(p, fields):
            continue

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_payload(p)},
        ]

        try:
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
                print(f"[{p.get('id')}] No content in response; skipping.")
                continue

            obj = extract_json(content)
            if not obj or not isinstance(obj, dict):
                print(f"[{p.get('id')}] Could not parse JSON; skipping.")
                continue

            updated_fields = []
            for key in ['template', 'application', 'dependentLLM', 'turn']:
                if key not in fields:
                    continue
                if key in obj and obj[key] is not None and obj[key] != {} and obj[key] != []:
                    p[key] = obj[key]
                    updated_fields.append(key)

            if updated_fields:
                p['aiAssisted'] = True
                p['aiAssistedFields'] = sorted(list(set((p.get('aiAssistedFields') or []) + updated_fields)))
                p['aiAssistedModel'] = model_name
                p['aiAssistedAt'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                enriched_count += 1
        except Exception as e:
            print(f"[{p.get('id')}] Enrichment error: {e}")
            continue

    # Write back
    json.dump(data, open(OUTPUT_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"Enrichment complete. Updated {enriched_count} pattern(s).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
