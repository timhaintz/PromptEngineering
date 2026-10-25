# Flagged-claim evidence audit — publication projection, 24 October 2026

This package preserves the existing **20 October 2026** factual-claim and source-attribution audit of 81 flagged responses. It adds no generation, judging, rescoring or classification changes. Evidence statuses are separate annotations: **partial support does not clear a flag**, and even a supported checked assertion does not validate a whole response.

The audit is linked to the committed [810-rating snapshot](../peil-810-astra-v3-20261018-r01-results-20261020-r01/), introduced at `9cecab8d4e2f5a131880e9040e7e4799c5bced4a` and merged at `72637d700910686c558831f77cf6f5d326a6c0f1`. Every case retains its public source-response and judgment paths, SHA-256 bindings, original scores, flag and review reasons. Full responses and original judge rationales remain in those source files. This package contains the exact checked response excerpts, audit findings, references and limits.

## Cohorts and outcome meanings

| Cohort | Flagged responses | Original review reasons | Supported | Partly supported | Contradicted | Not verifiable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Historical, within 648 responses | 74 | 94 | 3 | 51 | 16 | 4 |
| Corrective, within 162 responses | 7 | 7 | 0 | 7 | 0 | 0 |

The matched 216 responses are nested within the historical 648, not an independent third cohort. The table describes the **checked claims** in a flag-selected subset, not model accuracy or whole-response truth. All 101 original review reasons are covered by 500 evidence items using 57 source records. Audit coverage is complete; factual verification and flag resolution are not.

All seven corrective cases concern opinion verification (`at_assessment_opinion_verification`) and have a `partly_supported` audit roll-up. Six retain four maximum quality scores; one retains accuracy 4 and 5 on the other measures. The checked citations or attributions have supported elements alongside unresolved qualifications. This does not establish a corrective PEIL factuality advantage or justify changing any quality score.

- `supported`: inspected evidence supports the specific checked assertion within its recorded limits.
- `partly_supported`: some content is supported, but a qualification or unresolved part remains.
- `contradicted`: at least one checked assertion has direct contrary evidence; other assertions in that response may still be correct.
- `not_verifiable`: available sources did not establish the assertion or its provenance; this is not proof of fabrication.

The stored case rule gives a contradicted item priority; otherwise all not-verifiable items produce not-verifiable, all supported items produce supported, and mixed/qualified support produces partly-supported. Per-claim findings and limitations take precedence over a short roll-up. No roll-up is a new quality rating.

## Files

| File | Content |
| --- | --- |
| `audit-register.json` | 81 case records and all 500 original claim findings, with public response/rating bindings |
| `sources.json` | 57 source records, URLs, dates, evidence excerpts, locators where recorded and retrieval/version limitations |
| `protocol.json` | Preserved scientific scope, selection, evidence hierarchy, timing, partial masking and outcome semantics; publication projection notes |
| `limitations.json` | Global and issue-specific interpretation limits |
| `summary.json` | Descriptive counts, including separate historical/corrective counts |
| `source-manifest.json` | Exact SHA-256 bindings for repository-relative public inputs |
| `verification.json` | Mechanical integrity and coverage check result, not independent validation of factual interpretations |
| `verify_audit.py` | Offline, standard-library verifier against the committed public responses and ratings |
| `SHA256SUMS` | SHA-256 hashes for every package file except this checksum file itself |

Source IDs on each evidence item resolve into `sources.json`. Primary research, original authors and official agencies/vendors are preferred; retained secondary sources are labelled with their limits. Some findings use a shared source record (for example REM001) to describe multiple related assertions. Read the evidence summaries and qualifiers alongside the exact response excerpts.

## Scientific limits and preserved records

This is a post hoc, AI-assisted audit, not a preregistered systematic review, independent human validation or another LLM quality-judging run. Casebooks omitted scores and condition metadata, but previous context and response content limit blinding. No interrater reliability estimate is available. Neither the original judge nor this audit is ground truth.

Only the claims implicated by the selected review reasons were checked. The other 729 responses, and unflagged claims inside flagged responses, were not comprehensively fact-checked. Repeated claims, shared sources and compound assertions are not independent statistical observations. Counts must not be turned into population error rates or used to compare prompt-variant accuracy.

The audit used later external sources unavailable to the models during generation. It checks evidence after the event; it does not compare tool-enabled generation with model-only generation. Present vendor documentation is not proof of historical features, deployment suitability or compliance. Unlocated sources are not automatically fabricated, and source dates and limitations remain material.

The source snapshot retains **810 valid ratings from 811 attempts and 81 unresolved flags**. A separately authorised retry supplies the missing corrective rating. The original timeout remains quarantined with unknown outcome, usage and charge; the retry did not recover its result. See the existing [timeout and retry record](../peil-810-astra-v3-20261018-r01-results-20261020-r01/timeout-and-retry.json) and [flag register](../peil-810-astra-v3-20261018-r01-results-20261020-r01/unresolved-flags.json). This package does not edit either.

The separate [numerical analysis package](../peil-analysis-20261024-r01/) reports original quality, original reproducibility and corrective quality outcomes without substituting these audit annotations for scores.

## Verify locally

From the repository root:

```sh
python evaluation/updated/peil-flag-audit-20261024-r01/verify_audit.py
```

The verifier requires only Python's standard library. It makes no network or model requests, reads no credentials, changes no source records, checks all source hashes and public rating bindings, verifies every quotation against its response, and recomputes coverage and outcome counts. An optional `--output PATH` saves a new report and refuses to overwrite an existing file. Passing these checks establishes preservation and consistency, not the scientific correctness of every evidence interpretation. Sources were checked during the original audit; this publication step does not assert a fresh retrieval of those websites.
