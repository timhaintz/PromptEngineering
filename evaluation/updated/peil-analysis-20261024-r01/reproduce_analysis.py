#!/usr/bin/env python3
"""Recompute the published summaries from existing repository data, offline.

No model client is imported. All source files and published analyses are read-only.
The optional --output writes only the verification report named by the caller.
"""
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean, median, stdev
import argparse
import hashlib
import json
import platform
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VARIANTS = ['naive', 'peil_labelled', 'peil_unlabelled']
METRICS = ['accuracy', 'formatting', 'fabrication_avoidance', 'completeness']
COMPOSITE = 'legacy_equal_weight_composite'
CHECKS = Counter()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same(actual, expected):
    if isinstance(actual, (int, float, np.number)) and not isinstance(actual, bool):
        assert abs(float(actual) - float(expected)) < 1e-11, (actual, expected)
    elif isinstance(actual, list):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected):
            same(a, b)
    elif isinstance(actual, dict):
        for k, v in actual.items():
            same(v, expected[k])
    else:
        assert actual == expected, (actual, expected)


def summary(values):
    a = np.asarray(values, dtype=float)
    q = np.quantile(a, [.25, .5, .75], method='linear')
    return dict(n=len(a), mean=float(a.mean()), sd_sample_ddof1=float(a.std(ddof=1)) if len(a) > 1 else None,
                q1=float(q[0]), median=float(q[1]), q3=float(q[2]), iqr=float(q[2] - q[0]),
                min=float(a.min()), max=float(a.max()))


def signs(values, tolerance=0):
    return dict(win=sum(x > tolerance for x in values),
                tie=sum(abs(x) <= tolerance for x in values),
                loss=sum(x < -tolerance for x in values))


def resample(values, seed):
    a = np.asarray(values, dtype=float)
    draws = np.random.default_rng(seed).integers(0, len(a), size=(10000, len(a)))
    interval = np.quantile(a[draws].mean(axis=1), [.025, .975], method='linear').tolist()
    leave_one_out = [float(np.delete(a, i).mean()) for i in range(len(a))] if len(a) > 1 else []
    return interval, leave_one_out, hashlib.sha256(draws.astype('<i8').tobytes()).hexdigest()


def select(rows, scope, scope_id):
    if scope == 'overall':
        return rows
    if scope == 'model':
        return [r for r in rows if r['model_key'] == scope_id]
    if scope == 'task':
        return [r for r in rows if r['pattern_key'] == scope_id]
    if scope == 'model_task':
        task, model = scope_id.split(' | ')
        return [r for r in rows if r['pattern_key'] == task and r['model_key'] == model]
    raise ValueError(scope)


def grouped(rows):
    d = defaultdict(list)
    for r in rows:
        d[r['pattern_key'], r['model_key'], r['variant']].append(r)
    for rs in d.values():
        rs.sort(key=lambda r: r.get('run_index', 0))
    return d


def task_differences(rows, metric, left, right, field='scores'):
    cells = grouped(rows)
    pairs, bytask = [], defaultdict(list)
    for task, model in sorted({(r['pattern_key'], r['model_key']) for r in rows}):
        a = mean(r[field][metric] for r in cells[task, model, left])
        b = mean(r[field][metric] for r in cells[task, model, right])
        difference = a - b
        pairs.append((task, model, difference))
        bytask[task].append(difference)
    return pairs, {task: mean(v) for task, v in sorted(bytask.items())}


def verify_original():
    data = load(HERE / 'original216/response-bindings.json')
    rows = data['rows']
    assert len(rows) == 216
    for r in rows:
        source = load(REPO / r['source_file'])
        old = load(REPO / r['legacy_scores_file'])
        same(source['run_index'], 1)
        for key in ['variant', 'model_key']:
            same(source[key], r[key])
        same(source['pattern']['key'], r['pattern_key'])
        same(hashlib.sha256(source['output'].encode()).hexdigest(), r['response_text_sha256'])
        scores = {m: old['scores'][r['legacy_output_slot']]['fabrication' if m == 'fabrication_avoidance' else m]['score'] for m in METRICS}
        scores[COMPOSITE] = mean(scores.values())
        same(scores, r['original_scores'])
        CHECKS['original_source_rows'] += 1
    stats = load(HERE / 'original216/statistics.json')
    for d in stats['means']:
        sub = select(rows, d['scope'], d['scope_id'])
        vals = [r['original_scores'][d['metric']] for r in sub if r['variant'] == d['variant']]
        tv = [mean(r['original_scores'][d['metric']] for r in sub if r['variant'] == d['variant'] and r['pattern_key'] == t) for t in d['task_order']]
        same(summary(vals), d['response_scores'])
        same(summary(tv), d['task_mean_scores'])
        same(tv, d['task_mean_values'])
        CHECKS['original_mean_rows'] += 1
    for d in stats['contrasts']:
        pairs, tv = task_differences(select(rows, d['scope'], d['scope_id']), d['metric'], d['left'], d['right'], 'original_scores')
        values = list(tv.values())
        same(values, d['task_mean_differences'])
        same(summary(values), d['paired_task_dispersion'])
        same(summary([p[2] for p in pairs]), d['paired_cell_dispersion'])
        same(signs(values), d['task_mean_win_tie_loss'])
        if 'task_resampling_sensitivity' in d:
            ci, loo, drawhash = resample(values, 20261018)
            expected = d['task_resampling_sensitivity']
            same(ci, expected['interval_2_5_97_5'])
            same(loo, expected['leave_one_task_out'])
            same(drawhash, expected['draw_indices_sha256'])
            CHECKS['original_sensitivity_intervals'] += 1
        CHECKS['original_contrast_rows'] += 1
    crosswalk = load(HERE / 'original216/category-reporting-crosswalk.json')
    mappings = [
        ('original_category_summaries', crosswalk['original'], []),
        ('approved_category_summaries', crosswalk['approved'], []),
        ('sensitivity_only_photosynthesis_Out_to_Over', {**crosswalk['approved'], 'out_context_control_explicit_constraints': 'Over'}, []),
        ('withhold_photosynthesis_from_Out', crosswalk['approved'], ['out_context_control_explicit_constraints']),
        ('withhold_claim_extraction_from_Over', crosswalk['approved'], ['over_synthesis_claim_extraction'])]
    for name, mapping, exclude in mappings:
        for logic, d in crosswalk[name].items():
            tasks = sorted(t for t, category in mapping.items() if category == logic and t not in exclude)
            sub = [r for r in rows if r['pattern_key'] in tasks]
            same(tasks, d['tasks'])
            for metric, variants in d['means'].items():
                for variant, expected in variants.items():
                    same(summary([r['original_scores'][metric] for r in sub if r['variant'] == variant]), expected)
                    CHECKS['category_mean_rows'] += 1
            for metric, contrasts in d['contrasts'].items():
                for name, expected in contrasts.items():
                    left, right = name.split('__minus__')
                    _, tv = task_differences(sub, metric, left, right, 'original_scores')
                    same(summary(list(tv.values())), expected['paired_task_dispersion'])
                    same(tv, expected['task_mean_differences'])
                    CHECKS['category_contrast_rows'] += 1
    fig = load(HERE / 'original216/composite-figure-data.json')
    for task in fig['rows']:
        for variant, d in task['variants'].items():
            points = {r['model_key']: r['original_scores'][COMPOSITE] for r in rows if r['pattern_key'] == task['task'] and r['variant'] == variant}
            same(points, d['model_scores'])
            same(dict(mean=mean(points.values()), min=min(points.values()), max=max(points.values())), d)
            CHECKS['figure_variant_rows'] += 1
    agg = load(REPO / 'evaluation/summary/aggregate_scores.json')['score_summary']
    for variant in VARIANTS:
        sub = [r for r in rows if r['variant'] == variant]
        means = {m: round(mean(r['original_scores'][m] for r in sub), 4) for m in METRICS}
        same(round(mean(means.values()), 4), agg[variant]['overall_mean'])
    return rows


def verify_corrective():
    rows = load(HERE / 'corrective162/response-bindings.json')['rows']
    assert len(rows) == 162
    for r in rows:
        pub = load(REPO / r['public_judgement_file'])
        source = load(REPO / r['source_file'])
        for k in ['job_id', 'source_file', 'source_sha256', 'pattern_key', 'model_key', 'variant', 'run_index']:
            same(pub['source'][k], r[k])
        same(hashlib.sha256(source['output'].encode()).hexdigest(), r['response_text_sha256'])
        rating = pub['original_rating_record']['rating']
        same({m: rating['scores'][m]['score'] for m in METRICS}, r['scores'])
        same(rating['needs_human_review'], r['needs_human_review'])
        same(pub['prior_attempt_outcome_unknown'], r['prior_attempt_outcome_unknown'])
        CHECKS['corrective_source_rows'] += 1
    assert sum(r['needs_human_review'] for r in rows) == 7
    assert sum(all(x == 5 for x in r['scores'].values()) for r in rows) == 157
    stats = load(HERE / 'corrective162/statistics.json')
    for d in stats['mean_tables']:
        sub = [r for r in select(rows, d['scope'], d['scope_id']) if r['variant'] == d['variant']]
        vals = [r['scores'][d['metric']] for r in sub]
        same(mean(vals), d['equal_cell_then_task_mean'])
        same(dict(n=len(vals), mean=mean(vals), median=median(vals), min=min(vals), max=max(vals)), d['response_distribution'])
        CHECKS['corrective_mean_rows'] += 1
    for d in stats['contrast_tables']:
        pairs, tv = task_differences(select(rows, d['scope'], d['scope_id']), d['metric'], d['left'], d['right'])
        same(mean(tv.values()), d['mean_difference'])
        same(tv, d['task_values'])
        same(signs(list(tv.values()), 1e-12), d['task_mean_win_tie_loss'])
        if 'task_resampling_sensitivity' in d:
            ci, loo, _ = resample(list(tv.values()), 20261018)
            s = d['task_resampling_sensitivity']
            same(ci, s['interval_2_5_97_5'][0])
            same(loo, [s['leave_one_task_out'][t][0] for t in sorted(tv)])
            CHECKS['corrective_sensitivity_intervals'] += 1
        CHECKS['corrective_contrast_rows'] += 1
    repeats = load(HERE / 'corrective162/repeat-analysis.json')
    cells = grouped(rows)
    for d in repeats['within_condition_cells']:
        vals = [r['scores'][d['metric']] for r in cells[d['task'], d['model'], d['variant']]]
        same(vals, d['scores'])
        same(dict(mean=mean(vals), median=median(vals), min=min(vals), max=max(vals), range=max(vals)-min(vals), sample_standard_deviation_descriptive=stdev(vals)), d)
        CHECKS['corrective_repeat_cells'] += 1
    retry = load(HERE / 'corrective162/retry-sensitivity.json')
    prior = [r for r in rows if r['job_id'] != retry['retry_job_id']]
    for d in retry['comparison_tables']:
        _, old = task_differences(select(prior, d['scope'], d['scope_id']), d['metric'], d['left'], d['right'])
        _, new = task_differences(select(rows, d['scope'], d['scope_id']), d['metric'], d['left'], d['right'])
        same(mean(old.values()), d['prior_available_case_difference'])
        same(mean(new.values()), d['final_complete_difference'])
        same(mean(new.values())-mean(old.values()), d['change'])
        CHECKS['retry_sensitivity_rows'] += 1


def verify_reproducibility():
    cells = load(HERE / 'historical648-reproducibility/cells.json')['cells']
    assert len(cells) == 216
    for c in cells:
        src = load(REPO / c['reproducibility_file'])['variants'][c['variant']]
        same(src['mean_similarity'], c['semantic_mean_cosine'])
        same(src['pairwise_similarity'], c['pairwise_cosines'])
        same(src['llm_assessment']['functionally_identical'], c['functional_llm_boolean'])
        same(all(x > .85 for x in c['pairwise_cosines'].values()), c['threshold_gt_0_85_diagnostic'])
        for r in c['source_response_bindings']:
            same(hashlib.sha256(load(REPO / r['file'])['output'].encode()).hexdigest(), r['text_sha256'])
        CHECKS['reproducibility_source_cells'] += 1
    stats = load(HERE / 'historical648-reproducibility/statistics.json')
    for d in stats['means']:
        partition = cells if d['partition'] == 'historical_all_18' else [c for c in cells if c['partition'] == d['partition']]
        vals = [c[d['metric']] for c in select(partition, d['scope'], d['scope_id']) if c['variant'] == d['variant']]
        same(dict(mean=mean(vals), min=min(vals), max=max(vals), n_cells=len(vals)), d)
        CHECKS['reproducibility_mean_rows'] += 1
    for d in stats['contrasts']:
        partition = cells if d['partition'] == 'historical_all_18' else [c for c in cells if c['partition'] == d['partition']]
        sub = select(partition, d['scope'], d['scope_id'])
        numerical = [dict(c, scores={d['metric']: float(c[d['metric']])}) for c in sub]
        _, tv = task_differences(numerical, d['metric'], d['left'], d['right'])
        same(mean(tv.values()), d['mean_difference'])
        same(tv, d['task_values'])
        if 'sensitivity' in d:
            ci, loo, _ = resample(list(tv.values()), 20261019)
            same(ci, d['sensitivity']['percentile_95_interval'])
            same(loo, list(d['sensitivity']['leave_one_task_out'].values()))
            CHECKS['reproducibility_sensitivity_intervals'] += 1
        CHECKS['reproducibility_contrast_rows'] += 1
    assert sum(c['functional_llm_boolean'] != c['threshold_gt_0_85_diagnostic'] for c in cells) == 51


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional path for a new verification report; existing files are not replaced.')
    args = parser.parse_args()
    manifest = load(HERE / 'source-manifest.json')
    for rel, expected in manifest['files'].items():
        assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
        same(sha(REPO / rel), expected)
        CHECKS['source_hashes'] += 1
    verify_original()
    verify_corrective()
    verify_reproducibility()
    # Recheck sources after computation to make the read-only contract explicit.
    assert all(sha(REPO / rel) == expected for rel, expected in manifest['files'].items())
    report = {'status': 'passed', 'python': platform.python_version(), 'numpy': np.__version__,
              'checks': dict(CHECKS), 'source_files_unchanged': True,
              'new_generation_or_judging': False,
              'scope': 'Recomputed source bindings, descriptive and paired summaries, task-resampling intervals, category views, figure points, repeat variation and retry sensitivity.'}
    output = json.dumps(report, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as f:
            f.write(output)
    print(output, end='')


if __name__ == '__main__':
    main()
