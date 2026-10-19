# Astra judging results snapshot — 20 October 2026

This snapshot contains **810 validated ratings for 810 distinct responses**, from
**811 inference attempts**: 743 original successes, 66 continuation successes and
one explicitly authorised retry. The **648 historical** responses and **162
corrective** responses retain their original cohort identities.

The original timeout remains quarantined, with its outcome, token usage and charge
unknown. The successful second attempt supplies the previously missing rating;
it does not resolve the first attempt. See [timeout-and-retry.json](timeout-and-retry.json).
There are **81 unresolved Astra review flags** (74 historical and 7 corrective).
See [unresolved-flags.json](unresolved-flags.json) for the verbatim reasons and
record links. Astra remains the scoring mechanism; human rescoring was discontinued.
No scores, answer-status classifications or flags were changed or adjudicated.

## Using this snapshot

Use [publication-index.json](publication-index.json) to enumerate the 810 records
under `judgements/`. Each record preserves the exact submitted judge request
(including the response being assessed and rubric), exact final judge output text,
original parsed rating record, four separate 1–5 scores, rationales, evidence quotes,
review reasons, source identity and hashes, recorded token usage and cost accounting.
The original generation responses and frozen plan are already committed in this
repository; each record's `source.source_file` is relative to the repository root.
`source.cohort` remains `original` or `corrective-six-v1`; these must not be pooled
silently. No composite, statistical comparison or category remapping is included.

[snapshot.json](snapshot.json) records counts, execution provenance, known usage,
the recorded cost estimate, and integrity checks. Known usage is 3,824,252 tokens
(2,160,781 input and 1,663,471 output). Known estimated cost is A$136.407912915304,
excluding the original timeout's unknown charge. These are recorded estimates,
not a statement of current credit or final billed cost.

## Integrity and publication policy

Run `shasum -a 256 -c SHA256SUMS` from this directory to verify every snapshot file.
Pin the Git commit containing this directory when conducting later analyses.
The index provides both original private-file hashes and public derivative hashes.
`original_rating_record.raw_result_sha256` and the accounting raw hash refer to the
private original raw record, not the sanitized publication file. Canonical artifact
hashes use sorted-key UTF-8 JSON with `ensure_ascii=False`, comma/colon separators
and no whitespace, excluding `artifact_sha256`.

The existing research-field preservation policy is retained: scientific inputs,
outputs and usage remain exact, while credentials, authentication records, resource
endpoints and IDs, provider request/response IDs, full provider envelopes and provider
reasoning output content remain private. The derivative policy additionally omits
runtime authentication mode and the redundant deployment-name field. Model aliases
inside the exact request and returned output metadata remain unchanged. Original
execution records, continuation and retry amendments are preserved privately and
identified by hashes; this snapshot does not overwrite their preparation records.

The frozen protocol and calibration record remain in
[`../peil-six-task-20261018-r01/judging/`](../peil-six-task-20261018-r01/judging/).
Their historical planned human-review steps are not claims of completed review:
the later decision to discontinue human rescoring is disclosed above. Model ratings
are not ground truth, unresolved flags are not silently resolved, and the recorded
model version does not prove immutable weights. This is an output snapshot for later
analysis, with no performance conclusions, analysis reports/code or thesis edits.
