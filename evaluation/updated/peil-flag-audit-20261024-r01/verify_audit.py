#!/usr/bin/env python3
"""Offline integrity/coverage checks for the preserved flag-evidence audit."""
from pathlib import Path
import argparse
import collections
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(root, name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts,
            'Expected repository-relative source path')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), 'Path escapes source root')
    return resolved


def rollup(statuses):
    if 'contradicted' in statuses:
        return 'contradicted'
    if all(s == 'not_verifiable' for s in statuses):
        return 'not_verifiable'
    if all(s == 'supported' for s in statuses):
        return 'supported'
    return 'partly_supported'


def verify(package):
    repo = package.parents[2]
    manifest = read_json(package / 'source-manifest.json')
    require(len({x['path'] for x in manifest['files']}) == len(manifest['files']),
            'Duplicate source manifest path')
    for record in manifest['files']:
        path = safe_relative(repo, record['path'])
        require(path.is_file() and digest(path) == record['sha256'],
                'Source hash mismatch: ' + record['path'])
        require(path.stat().st_size == record['bytes'], 'Source byte count mismatch')

    protocol = read_json(package / 'protocol.json')
    snapshot = safe_relative(repo, protocol['source_snapshot'])
    require(digest(snapshot / 'publication-index.json') == protocol['index_sha256'],
            'Snapshot index hash mismatch')
    require(digest(snapshot / 'SHA256SUMS') == protocol['manifest_sha256'],
            'Snapshot checksum manifest hash mismatch')
    sources = read_json(package / 'sources.json')['sources']
    source_ids = {s['source_id'] for s in sources}
    require(len(source_ids) == len(sources), 'Duplicate source identifier')
    require(all(s['url'].startswith('https://') for s in sources), 'Non-HTTPS evidence URL')
    cases = read_json(package / 'audit-register.json')['cases']
    require(len({c['review_id'] for c in cases}) == len(cases), 'Duplicate review identifier')
    require(len({c['job_id'] for c in cases}) == len(cases), 'Duplicate job identifier')
    statuses_allowed = set(protocol['outcomes'])
    case_outcomes, evidence_outcomes = collections.Counter(), collections.Counter()
    cohort = collections.defaultdict(lambda: {'cases': 0, 'review_reasons': 0,
                                               'outcomes': collections.Counter()})
    all_claim_ids = set()
    reason_total = 0
    corrective = []
    for case in cases:
        require(case['job_id'] == case['source']['job_id'], 'Source job mismatch')
        judgement_path = safe_relative(repo, case['public_judgement_path'])
        require(digest(judgement_path) == case['public_judgement_sha256'],
                'Judgment binding mismatch')
        judgement = read_json(judgement_path)
        require(judgement['source'] == case['source'], 'Public source identity mismatch')
        rating = judgement['original_rating_record']['rating']
        require({k: v['score'] for k, v in rating['scores'].items()} == case['original_scores'],
                'Original scores changed')
        require(case['original_flag'] is True and rating['needs_human_review'] is True,
                'Original flag changed')
        require(rating['review_reasons'] == case['review_reasons'],
                'Original review reasons changed')
        response_path = safe_relative(repo, case['source']['source_file'])
        require(digest(response_path) == case['source']['source_sha256'],
                'Response source hash mismatch')
        response = read_json(response_path)
        text = response.get('text', response.get('output'))
        require(isinstance(text, str), 'Missing response text')
        require(hashlib.sha256(text.encode('utf-8')).hexdigest() == case['response_text_sha256'],
                'Response text hash mismatch')
        audit = case['audit']
        require(audit['review_id'] == case['review_id'], 'Audit review identity mismatch')
        covered, statuses = set(), []
        require(audit['claims'], 'Empty case audit')
        for claim in audit['claims']:
            require(claim['claim_id'] not in all_claim_ids, 'Duplicate claim identifier')
            all_claim_ids.add(claim['claim_id'])
            require(claim['status'] in statuses_allowed, 'Unknown evidence status')
            require(claim['response_quote'] and claim['response_quote'] in text,
                    'Non-verbatim response excerpt: ' + claim['claim_id'])
            require(set(claim['source_ids']) <= source_ids, 'Unresolved evidence source')
            indices = claim['original_reason_indices']
            require(indices and all(isinstance(i, int) and 0 <= i < len(case['review_reasons'])
                                    for i in indices), 'Invalid review reason index')
            covered.update(indices)
            statuses.append(claim['status'])
            evidence_outcomes[claim['status']] += 1
        require(covered == set(range(len(case['review_reasons']))), 'Unaddressed review reason')
        require(rollup(statuses) == audit['overall_status'], 'Case roll-up mismatch')
        case_outcomes[audit['overall_status']] += 1
        c = cohort[case['source']['cohort']]
        c['cases'] += 1
        c['review_reasons'] += len(case['review_reasons'])
        c['outcomes'][audit['overall_status']] += 1
        reason_total += len(case['review_reasons'])
        if case['source']['cohort'] == 'corrective-six-v1':
            corrective.append(case)
    calculated = {'cases': len(cases), 'original_review_reasons': reason_total,
                  'evidence_items': len(all_claim_ids), 'sources': len(sources),
                  'case_outcomes': dict(case_outcomes),
                  'evidence_item_outcomes': dict(evidence_outcomes),
                  'by_cohort': {k: {**v, 'outcomes': dict(v['outcomes'])}
                                for k, v in cohort.items()}}
    require(calculated == read_json(package / 'summary.json'), 'Summary counts mismatch')
    require(len(cases) == 81 and reason_total == 101 and len(all_claim_ids) == 500,
            'Unexpected audit coverage')
    require(len(corrective) == 7 and
            all(c['source']['pattern_key'] == 'at_assessment_opinion_verification' and
                c['audit']['overall_status'] == 'partly_supported' for c in corrective),
            'Corrective audit disclosure mismatch')
    require(sum(all(v == 5 for v in c['original_scores'].values()) for c in corrective) == 6,
            'Corrective maximum-score disclosure mismatch')
    return {'status': 'passed', 'scope': 'Offline mechanical integrity and coverage; not independent factual adjudication',
            'source_files_verified': len(manifest['files']),
            'public_judgement_bindings_verified': len(cases),
            'public_response_bindings_verified': len(cases),
            'scores_flags_and_review_reasons_unchanged': True,
            'all_response_quotes_verbatim': True,
            'all_reason_indices_covered': True,
            'all_referenced_sources_present': True,
            'case_rollups_reproduced': True,
            'counts': calculated}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a new report without overwriting an existing file')
    args = parser.parse_args()
    result = verify(Path(__file__).resolve().parent)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
