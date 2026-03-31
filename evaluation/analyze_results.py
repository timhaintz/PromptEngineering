"""Deep analysis of Chapter 6 evaluation results."""
import json
import os
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

RESULTS_DIR = Path("evaluation/results")
SUMMARY_DIR = Path("evaluation/summary")

def load_all_judge_records():
    """Load and flatten all judge scores into records."""
    records = []
    for pattern_dir in sorted(RESULTS_DIR.iterdir()):
        if not pattern_dir.is_dir() or pattern_dir.name == "case_studies":
            continue
        for model_dir in sorted(pattern_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            judge_file = model_dir / "judge_scores.json"
            if not judge_file.exists():
                continue
            data = json.loads(judge_file.read_text(encoding="utf-8"))
            scores = data["scores"]
            variant_map = {"naive": "output_a", "peil_labelled": "output_b", "peil_unlabelled": "output_c"}
            for variant, key in variant_map.items():
                for metric in ["accuracy", "formatting", "fabrication", "completeness"]:
                    records.append({
                        "pattern": pattern_dir.name,
                        "model": model_dir.name,
                        "variant": variant,
                        "metric": metric,
                        "score": scores[key][metric]["score"],
                        "justification": scores[key][metric]["justification"],
                    })
    return records

def load_all_generation_records():
    """Load generation outputs for content analysis."""
    records = []
    for pattern_dir in sorted(RESULTS_DIR.iterdir()):
        if not pattern_dir.is_dir() or pattern_dir.name == "case_studies":
            continue
        for model_dir in sorted(pattern_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            for f in sorted(model_dir.glob("run_1_*.json")):
                if "judge" in f.name or "reproducibility" in f.name:
                    continue
                data = json.loads(f.read_text(encoding="utf-8"))
                variant = f.stem.replace("run_1_", "")
                records.append({
                    "pattern": pattern_dir.name,
                    "model": model_dir.name,
                    "variant": variant,
                    "output": data["output"],
                    "output_len": len(data["output"]),
                    "usage": data.get("usage", {}),
                })
    return records

def load_reproducibility_records():
    """Load reproducibility data."""
    records = []
    for pattern_dir in sorted(RESULTS_DIR.iterdir()):
        if not pattern_dir.is_dir() or pattern_dir.name == "case_studies":
            continue
        for model_dir in sorted(pattern_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            repro_file = model_dir / "reproducibility.json"
            if not repro_file.exists():
                continue
            data = json.loads(repro_file.read_text(encoding="utf-8"))
            for variant, vdata in data["variants"].items():
                records.append({
                    "pattern": pattern_dir.name,
                    "model": data["evaluated_model_key"],
                    "variant": variant,
                    "mean_similarity": vdata["mean_similarity"],
                    "functionally_identical": vdata["llm_assessment"]["functionally_identical"],
                })
    return records

print("=" * 80)
print("CHAPTER 6 DEEP ANALYSIS")
print("=" * 80)

judge_records = load_all_judge_records()
gen_records = load_all_generation_records()
repro_records = load_reproducibility_records()

# ─── 1. OVERALL SCORES BY VARIANT ─────────────────────────────────────
print("\n" + "=" * 80)
print("1. OVERALL SCORES BY VARIANT")
print("=" * 80)
for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
    scores = [r["score"] for r in judge_records if r["variant"] == variant]
    print(f"  {variant:20s}: mean={mean(scores):.3f}  stdev={stdev(scores):.3f}  n={len(scores)}")

# ─── 2. SCORES BY MODEL × VARIANT ────────────────────────────────────
print("\n" + "=" * 80)
print("2. SCORES BY MODEL x VARIANT (overall mean)")
print("=" * 80)
models = sorted(set(r["model"] for r in judge_records))
for model in models:
    print(f"\n  {model}:")
    for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
        scores = [r["score"] for r in judge_records if r["model"] == model and r["variant"] == variant]
        print(f"    {variant:20s}: {mean(scores):.3f}")
    # Delta
    naive_scores = [r["score"] for r in judge_records if r["model"] == model and r["variant"] == "naive"]
    peil_scores = [r["score"] for r in judge_records if r["model"] == model and r["variant"] == "peil_labelled"]
    print(f"    {'PEIL - Naive':20s}: {mean(peil_scores) - mean(naive_scores):+.3f}")

# ─── 3. SCORES BY METRIC × VARIANT ───────────────────────────────────
print("\n" + "=" * 80)
print("3. SCORES BY METRIC x VARIANT")
print("=" * 80)
for metric in ["accuracy", "formatting", "fabrication", "completeness"]:
    print(f"\n  {metric}:")
    for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
        scores = [r["score"] for r in judge_records if r["metric"] == metric and r["variant"] == variant]
        print(f"    {variant:20s}: {mean(scores):.3f}")

# ─── 4. PATTERNS WHERE PEIL WINS ─────────────────────────────────────
print("\n" + "=" * 80)
print("4. PATTERNS WHERE PEIL LABELLED BEATS NAIVE (by overall score)")
print("=" * 80)
patterns = sorted(set(r["pattern"] for r in judge_records))
peil_wins = []
peil_loses = []
for pattern in patterns:
    naive_mean = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["variant"] == "naive"])
    peil_mean = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["variant"] == "peil_labelled"])
    delta = peil_mean - naive_mean
    if delta > 0:
        peil_wins.append((pattern, delta, naive_mean, peil_mean))
    else:
        peil_loses.append((pattern, delta, naive_mean, peil_mean))

print(f"\n  PEIL wins on {len(peil_wins)}/{len(patterns)} patterns:")
for p, d, n, pe in sorted(peil_wins, key=lambda x: -x[1]):
    print(f"    {p:55s} naive={n:.2f} peil={pe:.2f} delta={d:+.2f}")
print(f"\n  PEIL loses on {len(peil_loses)}/{len(patterns)} patterns:")
for p, d, n, pe in sorted(peil_loses, key=lambda x: x[1]):
    print(f"    {p:55s} naive={n:.2f} peil={pe:.2f} delta={d:+.2f}")

# ─── 5. MODEL-SPECIFIC PEIL BENEFIT ──────────────────────────────────
print("\n" + "=" * 80)
print("5. WHICH MODEL BENEFITS MOST FROM PEIL?")
print("=" * 80)
for model in models:
    wins = 0
    total = 0
    for pattern in patterns:
        naive_mean = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["model"] == model and r["variant"] == "naive"])
        peil_mean = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["model"] == model and r["variant"] == "peil_labelled"])
        total += 1
        if peil_mean > naive_mean:
            wins += 1
    print(f"  {model:30s}: PEIL wins on {wins}/{total} patterns ({100*wins/total:.0f}%)")

# ─── 6. OUTPUT LENGTH ANALYSIS ────────────────────────────────────────
print("\n" + "=" * 80)
print("6. OUTPUT LENGTH BY VARIANT (characters)")
print("=" * 80)
for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
    lengths = [r["output_len"] for r in gen_records if r["variant"] == variant]
    print(f"  {variant:20s}: mean={mean(lengths):.0f}  min={min(lengths)}  max={max(lengths)}")

print("\n  By model:")
for model in models:
    for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
        lengths = [r["output_len"] for r in gen_records if r["variant"] == variant and r["model"] == model]
        if lengths:
            print(f"    {model:25s} {variant:20s}: mean={mean(lengths):.0f}")

# ─── 7. TOKEN USAGE ───────────────────────────────────────────────────
print("\n" + "=" * 80)
print("7. TOKEN USAGE BY VARIANT")
print("=" * 80)
for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
    input_tokens = [r["usage"].get("input_tokens", 0) or 0 for r in gen_records if r["variant"] == variant]
    output_tokens = [r["usage"].get("output_tokens", 0) or 0 for r in gen_records if r["variant"] == variant]
    print(f"  {variant:20s}: input={mean(input_tokens):.0f}  output={mean(output_tokens):.0f}  total={mean(input_tokens)+mean(output_tokens):.0f}")

# ─── 8. REPRODUCIBILITY DEEP DIVE ────────────────────────────────────
print("\n" + "=" * 80)
print("8. REPRODUCIBILITY BY MODEL x VARIANT")
print("=" * 80)
for model in models:
    print(f"\n  {model}:")
    for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
        sims = [r["mean_similarity"] for r in repro_records if r["model"] == model and r["variant"] == variant]
        idents = [r["functionally_identical"] for r in repro_records if r["model"] == model and r["variant"] == variant]
        if sims:
            print(f"    {variant:20s}: similarity={mean(sims):.4f}  identical={sum(idents)}/{len(idents)} ({100*sum(idents)/len(idents):.0f}%)")

# ─── 9. LABELLED vs UNLABELLED BY PATTERN ────────────────────────────
print("\n" + "=" * 80)
print("9. LABELLED vs UNLABELLED (where labels help most)")
print("=" * 80)
label_deltas = []
for pattern in patterns:
    labelled = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["variant"] == "peil_labelled"])
    unlabelled = mean([r["score"] for r in judge_records if r["pattern"] == pattern and r["variant"] == "peil_unlabelled"])
    label_deltas.append((pattern, labelled - unlabelled, labelled, unlabelled))

for p, d, l, u in sorted(label_deltas, key=lambda x: -x[1]):
    marker = "+" if d > 0 else "-" if d < 0 else "="
    print(f"  {marker} {p:55s} labelled={l:.2f} unlabelled={u:.2f} delta={d:+.2f}")

# ─── 10. BEST/WORST INDIVIDUAL SCORES ────────────────────────────────
print("\n" + "=" * 80)
print("10. EXTREME SCORES (perfect 5s and low 1-2s)")
print("=" * 80)
perfect = [r for r in judge_records if r["score"] == 5]
low = [r for r in judge_records if r["score"] <= 2]
print(f"\n  Perfect 5s by variant:")
for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
    count = len([r for r in perfect if r["variant"] == variant])
    print(f"    {variant:20s}: {count}")
print(f"\n  Low scores (1-2) by variant:")
for variant in ["naive", "peil_labelled", "peil_unlabelled"]:
    count = len([r for r in low if r["variant"] == variant])
    print(f"    {variant:20s}: {count}")

print(f"\n  Low scores detail (PEIL labelled):")
for r in sorted([r for r in low if r["variant"] == "peil_labelled"], key=lambda x: x["score"]):
    print(f"    score={r['score']} {r['metric']:15s} {r['model']:25s} {r['pattern'][:40]}")
    print(f"      Justification: {r['justification'][:120]}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
