# Corrective evaluation and versioned judging

Six original evaluation items contain their instance input only in `naive_request`.
The historical renderer omitted that input from both structured variants when
`task_material` was empty. The corrective runner keeps the original instances and
naive requests and supplies the same request as the user message in every arm.
For the two structured arms, the original five-part prompt is the system message.
Reference answers are never added to generation messages.

The historical task definitions, generation files and scores remain available.
The new workflow writes to a separate directory and records its own protocol,
source hashes, schedule, messages, deployment configuration and returned model.
Taxonomy metadata in these records is the historical assignment, not an endorsed
resolution of the task-versus-parent classification review.

## Scope and interpretation

| Original source pattern | Instance |
| --- | --- |
| 20-2-0 | Compare attendance: 34,669 and 33,861 |
| 31-0-0 | Nine computers plus five per day, Monday through Thursday |
| 37-0-0 | Evaluate the original Great Wall visibility claim |
| 33-1-1 | Sarah, leadership training and conflict resolution premises |
| 32-26-0 | Alice's belief about a moved file |
| 6-0-0 | First letters of “Jack Ryan”, separated by spaces |

The corrective runner retains four historical model keys by default; its six-task
design with three variants and three repeats would produce 216 responses. The explicit contemporary example below selects
Sol, Luna and Grok-4.7: six tasks, three generators, three variants and three repeats,
for 162 new responses. Each generator supplies 54 responses, including a new naive
control for every task and repeat. The other twelve tasks are not regenerated.
This contemporary cohort does not replicate the old four-model comparison.
Select and document model keys before creating a new manifest; do not silently substitute a model mid-study or relabel
an unavailable historical deployment as its replacement.

This design evaluates the intended configuration with complete inputs. Input
restoration and message placement both change, so the experiment does not isolate
their separate causal effects. Three repeats measure limited within-task
variation; they do not turn the generated responses into independent task samples.
Historical and corrective cohorts must be reported separately, even if the same
judge scores both. Do not replace six old rows and describe the combined eighteen
as a single contemporaneous experiment.

## Azure configuration

The judge registry key is `gpt-6-astra`. The explicit contemporary generator keys
are `gpt-6.1-sol`, `gpt-6-luna` and `grok-4.7`. They use the shared resource settings
and distinct deployment variables:

- `AZUREVSEASTUS2_OPENAI_ENDPOINT`
- `AZUREVSEASTUS2_OPENAI_KEY` for API-key authentication, or Microsoft Entra credentials
- `AZUREVSEASTUS2_OPENAI_GPT61SOL_MODEL` for the Sol generator deployment name
- `AZUREVSEASTUS2_OPENAI_GPT6LUNA_MODEL` for the Luna generator deployment name
- `AZUREVSEASTUS2_GROK47_MODEL` for the Grok-4.7 generator deployment name
- `AZUREVSEASTUS2_OPENAI_GPT6ASTRA_MODEL` for the Astra judge deployment name

`evaluation/.env.example` lists blank settings for the judge, contemporary
generators and original generators. Keep populated credentials in a private `.env` file. Pass its path
explicitly; planning does not discover credentials or contact Azure.

The judge uses the Responses API, strict structured output and `max` reasoning
effort. The plan records this setting and execution rejects lower reasoning
settings. Higher effort can increase latency and token usage; it does not by
itself establish better judging. All three contemporary generators use the
Responses API and omit temperature. Sol and Luna request `max` reasoning effort;
Grok-4.7 omits the entire optional reasoning object because the deployment rejected
an explicit `reasoning.effort` setting. Its effective reasoning effort is
provider-managed and unverified; omission does not mean reasoning is disabled.
The omitted optional settings are fixed across all three arms within that model.
These settings do not establish equal reasoning budgets or compute across models.
No automatic parameter, provider or API fallback is enabled. Retain rejected
configuration probes separately from experimental responses.
Foundry lists Astra version `2026-09-03` and Sol version
`2026-09-29`; verify each actual deployment, version and upgrade policy before
collection. These documentation values do not verify an account's configuration.
A returned model alias alone does not establish an immutable snapshot.
See [Foundry Responses API support](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)
and [reasoning support](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reasoning),
plus the [Grok API settings](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) model capabilities.

The historical CLI's judge default remains unchanged. Use the versioned judging
workflow for new scores so that historical scores are not overwritten.

## Prepare and run the corrective cohort

From the repository root, create an offline, reviewable manifest in a new study
directory. Replace the example output path with a private study location.
Commit the reviewed implementation before creating the final manifest. Its Git
commit and source hashes describe the code used to prepare the run; changing
that commit or those source files invalidates the manifest. Record deployment
versions and upgrade policies separately before and after collection. Those
observations do not make an auto-upgrading deployment an immutable model snapshot.

```sh
.venv/bin/python -m evaluation.corrective_evaluation plan \
  --models gpt-6.1-sol,gpt-6-luna,grok-4.7 \
  --output-dir /absolute/path/to/study/corrective-six-current
```

Review the six instances and exact messages in `manifest.json`, confirm the
deployment identities and settings, and then execute that same manifest:

```sh
.venv/bin/python -m evaluation.corrective_evaluation generate \
  --output-dir /absolute/path/to/study/corrective-six-current \
  --env-file /absolute/path/to/private/.env --auth-mode api_key
```

Generation records the raw response and actual request. It stops on failed,
incomplete or changed-model results without silently changing prompts, providers
or schemas. An interrupted or failed request remains an audit event. Investigate
it before another attempt; do not remove its evidence to force a resume. A source
or configuration change requires a new documented cohort directory.

## Provenance and run identity

Commit the reviewed implementation first (the run's implementation commit, C0).
Assign each collection a unique run ID, separate from the reusable protocol ID,
and freeze its manifest in a new directory outside the checkout. Record the run
ID, C0, manifest location, exact source files, deployment observations and settings
in the accompanying run record. Label the manifest's canonical-JSON SHA-256 and
the saved file's byte SHA-256 separately; they are different hashes. Create an
annotated run tag on C0 that references the frozen manifest hash. Never retarget
that tag or alter a frozen manifest after collection begins.

The recorded shuffle seed determines request order, not model sampling; no model
sampling seed is sent. Preserve every attempted request, failed attempt, raw
response and ineligible result. Keep later result and analysis commits linked to
the run ID and C0, without replacing the original artifacts. Record decisions at
the time they are made; preparation after historical data were observed must not
be described as prospective preregistration of that historical study.

## Rejudging saved responses

Saved responses can be scored without access to their original generator.
All three original repeats comprise 648 responses; the historical first-repeat
subset comprises 216. The selected saved-response scope and the new corrective
responses must use the same audited reference material and new judge protocol.
Preserve the old scores as a separate measurement and report changes in judge,
rubric, input visibility and scoring coverage.

The new protocol evaluates one response per independent request. Model, variant,
taxonomy and cohort metadata are withheld from the judge, and request order is
shuffled with a recorded seed. Response style can still reveal aspects of the
prompt, so this does not guarantee complete blinding. Four anchored dimensions
are accuracy, formatting, fabrication avoidance and completeness; higher is
better. Protocol `single-response-judge-v3` makes the distinction explicit: a
response with no substantive answer to the actual task receives accuracy 1 and
completeness 1.
Formatting assesses the clarity and applicable representation of what is actually
presented. Missing answer content alone does not lower formatting. An appropriate
clarification-only response need not follow an answer-only output format and can
receive formatting 5 and fabrication avoidance 5.

Answer status concerns an attempted answer to the actual requested task or
instance, independently of its quality. `answered` includes full, partial,
wrong and unsupported actual attempts, even when followed by a question.
`clarification` means there is no actual answer attempt and the response requests
input; an explicitly labelled hypothetical illustration may accompany that
request. `no_answer` means there is neither an actual answer attempt nor an input
request. If the task itself asks for an illustration, an illustration can be an
actual answer attempt.

`appropriate_clarification=true` is reserved for `clarification` with a warranted
request for essential missing input. It must be false for `answered` and
`no_answer`. For an answered response, false says nothing about the quality of a
follow-up question. A clearly labelled invented hypothetical is not fabricated
actual task data merely because it is invented; unmarked invented task inputs
remain assessable as fabrication under the unchanged numeric rubric. The strict
cross-field validator rejects contradictory flags; execution preserves the raw
judge response before rejection and does not write a rating for it.

Reference and formatting rules need a consistent task-level audit before scoring.
The audit must carry the current protocol version and the exact global
`formatting_policy` and `answer_status_policy` seeded by `audit-draft`. Both
policies must match the current protocol. Review every task's formatting rules
and actual-task/illustration distinction under those policies; correctness and
coverage requirements belong in their own dimensions. Do not merely relabel a
version-1 or version-2 audit or reuse its completed scores.
In particular, retain the Great Wall question but accept justified qualifications
about viewing conditions, and never penalise the naive answer for structured-only
formatting or decomposition instructions. A newer judge is not itself evidence
of better judging. Check a balanced sample against the audited references before
the full batch. Sol generation with Astra judging uses different models within
the same provider/model family; a different-family sensitivity remains a separate
option.

Create a reference-audit draft from the saved generations, then review its task
facts and acceptance criteria. An approved audit record means that reference
review is complete; it is not an institutional or supervisor approval.

```sh
.venv/bin/python -m evaluation.rejudging audit-draft \
  --source evaluation/results --run-scope all \
  --output /absolute/path/to/study/reference-audit-v3.json
```

Once the corrected generations exist, include both cohorts in the judging plan:

```sh
.venv/bin/python -m evaluation.rejudging plan \
  --source evaluation/results \
  --source /absolute/path/to/study/corrective-six-current \
  --run-scope all --audit /absolute/path/to/study/reference-audit-v3.json \
  --output /absolute/path/to/study/judging-astra-v3/plan.json
```

For a preview of the 648 saved responses before generation, omit the second
`--source`. That is a preparation artifact, not the final combined scoring batch.
The three-generator example has 810 combined responses only if all 648 historical
and 162 new responses are eligible. The old four-generator design would produce
864 only with all 216 corrective outputs. Review any skipped or incomplete coverage.

```sh
.venv/bin/python -m evaluation.rejudging execute \
  --plan /absolute/path/to/study/judging-astra-v3/plan.json \
  --env-file /absolute/path/to/private/.env --auth-mode api_key
```

`--limit N` limits new requests for a staged execution. Completed valid ratings
can be resumed with the same plan and settings; a changed plan is a new version.
Keep previous calibration judgements separate when modifying the judge or rubric;
create a new reviewed audit, plan and calibration directory for version 3. Old
plans and raw responses remain evidence of the previous protocol. Review flags
must be resolved or reported as unresolved coverage, never silently dropped.

## Offline verification

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_evaluation_transport.py tests/test_corrective_evaluation.py \
  tests/test_rejudging.py
```

The tests prohibit network access. An offline pass validates construction and
recordkeeping; it does not confirm deployment availability or new experimental
results.
