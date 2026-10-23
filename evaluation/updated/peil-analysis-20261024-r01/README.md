# Existing-data PEIL analyses — 24 October 2026

This package contains analysis of existing responses and saved ratings. It makes no model requests and does not change any source score or source classification. Source files remain in their original repository locations; `source-manifest.json` binds the 1,124 input files by SHA-256.

The Astra results source is the committed [results snapshot](../peil-810-astra-v3-20261018-r01-results-20261020-r01/), introduced at commit `9cecab8d4e2f5a131880e9040e7e4799c5bced4a` and merged at `72637d700910686c558831f77cf6f5d326a6c0f1`. Its publication manifest preserves the distinction between public-file hashes and hashes of the original execution records. Analysis bindings below refer to repository-relative public files.

## Cohorts remain separate

| Directory | Observations | Measures and source |
| --- | --- | --- |
| `original216/` | 18 tasks × 4 fixed models × 3 prompt variants, run 1 only | Original GPT-5.4-pro quality scores; not Astra replacements |
| `corrective162/` | 6 tasks × 3 fixed models × 3 variants × 3 runs | Astra quality scores for the separate corrective generation study |
| `historical648-reproducibility/` | 216 three-output sets, covering 648 historical responses | Saved semantic cosine similarities and original GPT-5.4-pro functional-identity Booleans |

The matched 216 responses are a run-1 subset of the 648 historical generations. They are not a second independent three-run reproducibility cohort. The 648-response Astra quality analysis is also distinct from the original 216-score analysis here. No historical and corrective observations are pooled, and neither judge is treated as ground truth.

## Quality analysis

The four ordinal measures—accuracy, formatting, fabrication avoidance and completeness—are reported separately on the original 1–5 scale, all higher being better. The original field named `fabrication` is relabelled `fabrication_avoidance` without reversing its scores.

Pairing is within task and model. For the corrective study, the three observed scores are first averaged within each task/model/variant. Overall summaries give models equal weight within a task, then give tasks equal weight. The primary contrasts are labelled PEIL minus naïve and unlabelled PEIL minus naïve; labelled minus unlabelled is separate. By-model, by-task and, for the corrective study, model/task records are included.

`original216/statistics.json` also keeps the legacy composite separate: the arithmetic mean of the four per-response ratings, with no intermediate rounding for paired comparisons. The legacy aggregate publication convention is reproduced separately: round each variant's metric mean to four decimals, average those four rounded means, then round the result to four decimals. This reproduces the stored values 4.3715 (naïve), 3.8264 (labelled) and 3.7327 (unlabelled). There is no corrective composite.

| Measure | Original labelled − naïve | Original unlabelled − naïve | Corrective labelled − naïve | Corrective unlabelled − naïve |
| --- | ---: | ---: | ---: | ---: |
| Accuracy | −1.1111 | −1.1389 | −0.0370 | −0.0370 |
| Formatting | 0.0000 | −0.1250 | 0.0000 | 0.0000 |
| Fabrication avoidance | −0.4722 | −0.6806 | +0.0185 | +0.0185 |
| Completeness | −0.5972 | −0.6111 | 0.0000 | 0.0000 |

These columns describe separate experiments. They are not estimates of an improvement caused solely by correcting inputs: the corrective models and generation conditions differ, and PEIL uses system-plus-user messages while naïve uses a user message only. Of the 162 corrective responses, 157 receive 5 on all four measures. This ceiling limits discrimination; ties are not evidence of equivalence, factual perfection or general task mastery.

### Uncertainty and repetition

The stored intervals use 10,000 whole-task resamples with NumPy PCG64, seed 20261018 for quality analyses and 20261019 for reproducibility. Variants and models stay together within each sampled task. The central 95% percentile intervals and leave-one-task-out ranges describe **task-composition sensitivity of this selected benchmark**. They are not population confidence intervals, judge calibration estimates, generation-repeat uncertainty, or significance tests. No p-values or equivalence margins are introduced.

Original-quality dispersion includes sample SD, median, quartiles, IQR and observed range. For an individual original task, four models are fixed conditions, not independent repeated experiments. `original216/composite-figure-data.json` contains each model point, the mean and min–max range. Its whiskers are not confidence intervals or repeat-run error bars.

`corrective162/repeat-analysis.json` separately records variation across three generation runs. Matching run indices does not imply matched random seeds. Quality-score equality across runs does not establish semantic or functional identity.

### Reporting categories

`original216/category-reporting-crosswalk.json` preserves the original labels and provides a reporting-only view that retains hallucination evaluation as In / Error Identification and moves Template Filling from In to Out / Refactoring. Original data and filenames are unchanged. The adjusted view has two In tasks and four Out tasks; equal task weighting is retained.

Hypothetical reassignment of the explicit-constraints/photosynthesis task to Over, and task-withholding views, are labelled sensitivities rather than new classifications. The claim-extraction versus Synthesis interpretation remains unsettled. These views do not justify broad category-level claims. Overall, model and task estimates do not depend on those labels.

## Existing reproducibility measurements

Semantic similarity is the stored mean of the three pairwise cosine similarities in a three-run set, using the configured `text-embedding-3-large` workflow. It is not a probability or percentage of meaning preserved. The saved mean can differ slightly from the mean of the saved rounded pair scores because the original calculation used unrounded scores.

Functional identity is one saved GPT-5.4-pro Boolean for the entire three-output set. It is **not** the rule that all three cosine scores exceed 0.85. Applying that strict threshold as a diagnostic disagrees with the saved Boolean in 51 of 216 sets. Both measures remain separate and the original Booleans are preserved.

| Variant | Mean semantic cosine | Functionally identical sets |
| --- | ---: | ---: |
| Naïve | 0.948242 | 61/72 |
| PEIL labelled | 0.905748 | 54/72 |
| PEIL unlabelled | 0.898318 | 51/72 |

Full task/model comparisons and task-composition intervals are in `historical648-reproducibility/statistics.json`. A cell has three runs but only one functional judgment; its three cosine pairs share outputs and are not independent observations. The original functional judge received the variant name and fixed run order, so the assessment was not blinded to condition. No saved semantic/functional measurement for the corrective 162 is inferred from quality-score ties.

## Flags, timeout and provenance limits

The source snapshot has **810 validated ratings, 81 unresolved flags (74 historical, 7 corrective), and 811 inference attempts**. The successful authorised retry supplies the previously missing corrective rating. The original timed-out attempt remains quarantined, with unknown outcome, usage and charge. No flagged row is removed or rescored here, and no human rescoring or agreement study is claimed. See the source snapshot's [timeout and retry record](../peil-810-astra-v3-20261018-r01-results-20261020-r01/timeout-and-retry.json) and [unresolved flags](../peil-810-astra-v3-20261018-r01-results-20261020-r01/unresolved-flags.json). `corrective162/retry-sensitivity.json` preserves the 161-versus-162 comparison without imputing an original timeout score.

The original quality and reproducibility files identify task/model/variant, but do not archive complete submitted requests with bound response hashes. Current source-file identity and the saved original-score bridge are verified. These checks are not a recovered server-side receipt. Four original models and three corrective models are fixed benchmark conditions, not samples supporting general model-population claims. Earlier calibration exposure and the lack of independent human agreement limit judge comparisons.

## Reproduce the numerical checks

From the repository root, in a Python environment with the recorded NumPy version:

```sh
python -m pip install -r evaluation/updated/peil-analysis-20261024-r01/requirements.txt
python evaluation/updated/peil-analysis-20261024-r01/reproduce_analysis.py
```

The script imports no inference client and needs no credentials or network access. It verifies every source hash, reconstructs the original scores and corrective public-score bindings, and recomputes descriptive statistics, paired means, task-resampling intervals, category views, figure points, per-cell repeat variation, retry sensitivity and historical reproducibility comparisons. `verification.json` records the successful reference run. An optional `--output PATH` writes a new verification report and refuses to overwrite an existing file.

`SHA256SUMS` covers every package file except itself. `source-manifest.json` covers repository inputs separately. The numerical JSON files retain the existing analyses; this packaging step changes no score, original classification, or underlying model output.
