"""Chapter 6 PEIL trend figure (Option A2).

Reads per-pattern, per-model judge scores from
evaluation/results/<pattern>/<model>/judge_scores.json, computes the mean overall
score per (pattern, variant) across the four evaluated models, sorts patterns
by PEIL Labelled - Naive delta, and plots three lines.

Output: peil_trends.pdf (vector PDF for LaTeX).
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

SCRIPT_DIR = Path(__file__).resolve().parent
# Walk up until we find evaluation/ alongside Final/
_root = SCRIPT_DIR
while _root != _root.parent and not (_root / "evaluation" / "results").exists():
    _root = _root.parent
WORKSPACE_ROOT = _root
RESULTS_DIR = WORKSPACE_ROOT / "evaluation" / "results"
OUT_DIR = WORKSPACE_ROOT / "evaluation" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "peil_trends.pdf"

VARIANT_KEY = {
    "naive": "output_a",
    "peil_labelled": "output_b",
    "peil_unlabelled": "output_c",
}
METRICS = ["accuracy", "formatting", "fabrication", "completeness"]

PATTERN_LABELS = {
    "across_argument_debate_opening": "Debate Opening",
    "across_comparison_attendance": "Attendance",
    "across_translation_summarise_translate": "Translate & Summarise",
    "at_assessment_expert_rating": "Expert Rating",
    "at_assessment_opinion_verification": "Opinion Verification",
    "at_calculation_math_word_problems": "Math Word Problems",
    "beyond_hypothesise_theory_of_mind": "Theory of Mind",
    "beyond_logical_reasoning_premise_question": "Premise-Question",
    "beyond_simulation_change_request": "Change Request",
    "in_classification_relevancy_check": "Relevancy Class.",
    "in_error_identification_hallucination_judge": "Hallucination Eval.",
    "in_refactoring_template_filling": "Template Filling",
    "out_context_control_explicit_constraints": "Explicit Constraints",
    "out_decomposed_prompting_letter_concat": "Letter Concat.",
    "out_output_customisation_knapsack_code": "Knapsack Code",
    "over_summarisation_chain_of_density": "Chain of Density",
    "over_summarisation_text_summary": "Text Summary",
    "over_synthesis_claim_extraction": "Claim Extraction",
}

LOGIC_OF = {p: p.split("_", 1)[0].capitalize() for p in PATTERN_LABELS}
LOGIC_COLOURS = {
    "Across": "#4C72B0", "At": "#DD8452", "Beyond": "#55A467",
    "In": "#C44E52", "Out": "#8172B3", "Over": "#937860",
}


def overall_mean(scores_block: dict) -> float:
    return mean(scores_block[m]["score"] for m in METRICS)


def load_pattern_means() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for pattern_dir in sorted(RESULTS_DIR.iterdir()):
        if not pattern_dir.is_dir() or pattern_dir.name == "case_studies":
            continue
        per_variant: dict[str, list[float]] = {v: [] for v in VARIANT_KEY}
        for model_dir in sorted(pattern_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            judge_file = model_dir / "judge_scores.json"
            if not judge_file.exists():
                continue
            data = json.loads(judge_file.read_text(encoding="utf-8"))
            scores = data["scores"]
            for variant, key in VARIANT_KEY.items():
                per_variant[variant].append(overall_mean(scores[key]))
        out[pattern_dir.name] = {v: mean(vals) for v, vals in per_variant.items() if vals}
    return out


def main() -> None:
    means = load_pattern_means()
    ordered = sorted(
        means.keys(),
        key=lambda p: means[p]["peil_labelled"] - means[p]["naive"],
        reverse=True,
    )

    labels = [PATTERN_LABELS[p] for p in ordered]
    naive = [means[p]["naive"] for p in ordered]
    lab = [means[p]["peil_labelled"] for p in ordered]
    unlab = [means[p]["peil_unlabelled"] for p in ordered]
    point_colours = [LOGIC_COLOURS[LOGIC_OF[p]] for p in ordered]

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 9,
        "legend.fontsize": 8.5,
    })

    fig, ax = plt.subplots(figsize=(11, 4.6))
    x = list(range(len(ordered)))

    ax.plot(x, naive, "-", linewidth=1.6, color="#7F7F7F", label="Naive",
            marker="o", markersize=4.5, markerfacecolor="white",
            markeredgecolor="#7F7F7F", markeredgewidth=1.2, zorder=3)
    ax.plot(x, lab, "-", linewidth=1.8, color="#1F4E79", label="PEIL Labelled",
            marker="s", markersize=5, zorder=4)
    ax.plot(x, unlab, "--", linewidth=1.4, color="#5B9BD5",
            label="PEIL Unlabelled", marker="^", markersize=4.5, zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylim(1.5, 5.6)
    ax.set_yticks([2, 3, 4, 5])
    ax.set_xlim(-0.5, len(x) - 0.5)
    ax.set_ylabel("Mean overall score (1--5)")
    ax.set_xlabel(
        "Patterns, sorted by PEIL Labelled $-$ Naive delta "
        "(PEIL wins on the left)"
    )
    ax.set_title("Per-pattern mean scores across four evaluated models")
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)

    # Crossover line where PEIL Labelled drops below Naive
    for i in range(1, len(x)):
        if (lab[i - 1] - naive[i - 1]) >= 0 > (lab[i] - naive[i]):
            ax.axvline(i - 0.5, color="black", linewidth=0.7,
                       linestyle=":", alpha=0.7)
            ax.text(i - 0.5, 5.50,
                    "PEIL $\\geq$ Naive   $|$   Naive $>$ PEIL",
                    ha="center", va="top", fontsize=8.5, style="italic")
            break

    # Legend outside the plot area on the right
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5),
              frameon=True, framealpha=0.95)

    fig.tight_layout()
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
