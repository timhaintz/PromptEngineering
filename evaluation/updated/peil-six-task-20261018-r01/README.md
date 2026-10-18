# Corrected six-task cohort: peil-six-task-20261018-r01

**Generation is complete: 162 responses. Full-study judging has not started.**

The six original task instances are preserved. Their original instance data is
now supplied to every prompt variant. The original structured instructions are
retained. Sol, Luna and Grok-4.7 each produced three repeats of the naive, PEIL
labelled and PEIL unlabelled variants: 6 × 3 × 3 × 3 = 162 responses.

## Where the results are

```
generations/<task>/<model>/run_<repeat>_<variant>.json
```

Each JSON contains the exact request/messages, response text in `output`,
generator/settings, task/variant/repeat, usage and provenance. Read
[`run-summary.json`](run-summary.json) for completion counts and model-version
observations. These files contain answers, not scores. No main-study ratings
exist yet.

Historical responses and original ratings remain in
[`evaluation/results/`](../../results/). They have not been overwritten.

## Frozen implementation and publication provenance

- Generation implementation: `59d7aa17059b7533874fd6624a73b6fb2e94b93a`.
- Prepared generation tag: `experiments/peil-six-task-20261018-r01-prepared`.
- Implementation merge: `a5996df063c27b9daf81f010024d693c527815a0` (PR #44).
- [`generation-manifest.json`](generation-manifest.json) is the original
  pre-collection manifest, copied unchanged.
- [`publication-index.json`](publication-index.json) connects each public file
  to the preserved original file/artifact hashes and unchanged response hash.
- `SHA256SUMS` records the published preparation files. Verify from this run
  directory with `shasum -a 256 -c SHA256SUMS`.

The public files are explicitly identified publication copies. The original
resource URL, provider response/request identifiers and full raw provider
envelope are omitted; the unmodified originals remain in the private run
archive. Exact prompt messages, request payloads, response text, normalized and
provider usage, requested settings and returned model identifiers are preserved.
Public artifact hashes are recomputed after this metadata removal. Original
hashes are retained; they are not represented as hashes of the altered files.

## Prepared judging plan

[`judging/plan.json`](judging/plan.json) contains **810** requests: all **648**
historical responses plus the **162** corrected responses, under the same
`single-response-judge-v3` protocol, Astra judge and maximum reasoning. It fixes
the exact response membership, references, four anchored metrics, JSON schema,
source hashes and deterministic request ordering.

Paths in the plan are **repository-relative**. Any future invocation must run
from the repository root with this exact source tree. The plan's
`ready_for_execution` field means its structural/reference checks passed. It is
not execution authorization and does not certify current cloud state.

Judging is not authorised by preparation of these files. Before an explicitly
authorised run, recheck Astra's live deployment/version/upgrade policy and
configuration, and record the observation alongside the frozen plan. The last
recorded observation is version `2026-09-03` with automatic default-version
upgrades enabled; see
[`judging/judge-deployment-record.json`](judging/judge-deployment-record.json).
Recheck after each bounded batch. Stop on a detected change. No cloud setting
was changed while preparing this bundle.

## Analysis and human review

[`judging/analysis-and-review-rules.json`](judging/analysis-and-review-rules.json)
fixes the rules before full-study scoring:

- Compare each PEIL variant with naive within the same corrected task and model.
  Report all four metrics separately and all 24 primary model/contrast/metric
  summaries, with equal task weights and every task-level effect visible.
- Treat the six task instances as the task units. Three repeats describe within-
  cell variation; they do not create independent task samples. Use descriptive
  distributions, leave-one-task-out ranges and task-resampling sensitivity;
  no confirmatory significance tests or primary composite score are specified.
- Keep the 648 historical and 162 corrected responses separate. Use the
  [`216-response bridge`](judging/historical-score-bridge.json) to compare old
  and new scoring of identical original run-1 texts. Do not pool legacy and
  revised scores or attribute all scoring changes to the new judge alone.
- Review **108** preselected responses: 54 corrected (one from each
  task/model/variant cell) and 54 historical (one from each task/variant cell).
  Selection is deterministic, balanced by repeat, and excludes the twelve
  previously used calibration sources. Selection seed, nonce and counts are in
  [`human-review-selection.json`](judging/human-review-selection.json).
- A named human should score the
  [`masked packet`](judging/human-review-packet.json) before seeing Astra scores
  or coordinator identities. Save assessments separately; preserve this blank
  frozen template. The coordinator mapping is retained separately. Response
  wording may still reveal condition/model, so this is partial masking.
- Review all flags, reference conflicts and the predeclared CAL-06/07/08/12
  boundaries separately. The human base sample is not chosen from model flags.
  Resolve substantial disagreements explicitly and preserve original Astra
  ratings; do not selectively replace scores to create a mixed primary dataset.

Reviewer identities are not yet assigned. Human review and unresolved-reference
resolution are required before final performance claims. Stable task IDs govern
primary analysis; taxonomy decisions remain separate and are needed before
category-level claims.

The 12-case calibration passed its declared hard checks, but it was diagnostic,
AI-assisted and reused observed cases. It is not independent human validation.
Four boundary cases were not flagged by Astra. CAL-08 retains a grounding
limitation: the judge receives intended references and an input-status flag,
not the full submitted prompt. A separate human grounding pass must preserve
that distinction. See [`calibration-record.json`](judging/calibration-record.json).

## Test evidence

[`validation-summary.json`](validation-summary.json) records the preparation
checks and the previously recorded **69 local focused test passes** (14
transport, 11 corrective-runner, 44 judging). The retained local evidence is a
summary, not a standalone pytest stdout/JUnit report. Test source files are code;
running them does not automatically commit a test report.

The five CI jobs passed in
[GitHub Actions run 39093325940](https://github.com/timhaintz/PromptEngineering/actions/runs/39093325940).
Their detailed logs belong to that Actions run, not to the Git tree. The current
CI Python allowlist differs from the three focused evaluation test files; the
69 focused passes were local.

## Interpretation and preservation

Input restoration, contemporary generators and system/user message placement
change together. This cohort does not isolate the causal effect of any one
change. Astra shares the OpenAI family with Sol and Luna; model settings do not
equalise reasoning compute. Six corrected tasks do not cover all six taxonomy
categories, and results do not automatically generalise beyond these instances.

This dated plan follows exposure to historical results, calibration and
corrective generation. It precedes full-study scoring, but it is not prospective
public preregistration of the original or corrective generation study.

Frozen records are never edited to update their status. The original preparation
record remains a preparation snapshot; later completion and judging records
record subsequent events. Failed/unknown requests, protocol changes and retries
must remain explicit and append-only. No judging, new generation or thesis edits
were performed to prepare this publication bundle.
