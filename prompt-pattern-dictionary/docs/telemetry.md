# Telemetry Event Schema (Orientation & Taxonomy)

> Draft for Phase 6 P5 – Continuous Learning. Non-invasive, privacy-conscious instrumentation plan. No PII; only interaction intent and coarse timing. Opt-out respected via local storage flag (`pe-telemetry-optout`).

## Principles
- Minimal footprint: capture essential learning & reliability indicators only.
- Transparency: document every event; expose public README summary.
- Privacy: no raw prompt content, no user identifiers; hashed session id (ephemeral) optional.
- Accessibility Respect: do not fire events on hidden / off-screen elements.

## Core Orientation Events
| Event Name | Trigger | Payload Fields | Notes |
|------------|--------|----------------|-------|
| orientation_quick_path_click | User activates a Quick Paths intent link | `{ intentSlug: string, ts: ISOString }` | Intent slugs: defensive, adapt, evaluate, similarity, clarity |
| evaluation_copy_action | User copies evaluation harness stub or code block | `{ section: string, codeLength: number, ts: ISOString }` | `section` e.g. `quality-evaluation`; length used for sizing distribution |
| glossary_search | User activates a glossary jump or term reveal | `{ termInitial: string, ts: ISOString }` | Initial A–Z anchor only |
| similarity_preview_open_compare | User clicks comparison view link in Similarity Preview | `{ patternIds: string[], count: number, ts: ISOString }` | `patternIds` sanitized IDs (no content) |
| decision_tree_select_goal | User selects a goal in decision tree | `{ goal: string, suggestedCategories: string[], ts: ISOString }` | Categories as normalized slugs |
| anti_pattern_table_view | Anti-pattern remediation table enters viewport | `{ visibleCount: number, ts: ISOString }` | IntersectionObserver based |

## Taxonomy & Pattern Detail Events (Existing / Extended)
| Event Name | Trigger | Payload Fields | Notes |
| pattern_expand_template | Template expanded from collapsed state | `{ patternId: string, ts: ISOString }` | Pattern ID only |
| pattern_expand_examples | Examples disclosure toggled open | `{ patternId: string, exampleCount: number, ts: ISOString }` | Count helps measure density usage |
| similar_examples_chip_click | User selects a similar example chip | `{ fromExampleId: string, toExampleId: string, similarity: number, ts: ISOString }` | similarity rounded to 2 decimals |
| application_task_chip_click | User clicks an application task chip | `{ patternId: string, task: string, ts: ISOString }` | Future filtering feature |

## Event Payload Guardrails
- All string fields length limited (patternId ≤ 16 chars, intentSlug ≤ 24).
- similarity numeric fields rounded to 2 decimals client side.
- No raw prompt text or example content captured.
- Timestamps in UTC ISO format.

## Implementation Outline
```typescript
interface TelemetryEventBase { name: string; ts: string; }
interface QuickPathClick extends TelemetryEventBase { name: 'orientation_quick_path_click'; intentSlug: string; }
interface EvaluationCopyAction extends TelemetryEventBase { name: 'evaluation_copy_action'; section: string; codeLength: number; }
interface GlossarySearch extends TelemetryEventBase { name: 'glossary_search'; termInitial: string; }
interface SimilarityPreviewOpenCompare extends TelemetryEventBase { name: 'similarity_preview_open_compare'; patternIds: string[]; count: number; }
interface DecisionTreeSelectGoal extends TelemetryEventBase { name: 'decision_tree_select_goal'; goal: string; suggestedCategories: string[]; }
interface AntiPatternTableView extends TelemetryEventBase { name: 'anti_pattern_table_view'; visibleCount: number; }

// Pattern detail events
interface PatternExpandTemplate extends TelemetryEventBase { name: 'pattern_expand_template'; patternId: string; }
interface PatternExpandExamples extends TelemetryEventBase { name: 'pattern_expand_examples'; patternId: string; exampleCount: number; }
interface SimilarExamplesChipClick extends TelemetryEventBase { name: 'similar_examples_chip_click'; fromExampleId: string; toExampleId: string; similarity: number; }
interface ApplicationTaskChipClick extends TelemetryEventBase { name: 'application_task_chip_click'; patternId: string; task: string; }

type OrientationTelemetryEvent = QuickPathClick | EvaluationCopyAction | GlossarySearch | SimilarityPreviewOpenCompare | DecisionTreeSelectGoal | AntiPatternTableView;

type PatternTelemetryEvent = PatternExpandTemplate | PatternExpandExamples | SimilarExamplesChipClick | ApplicationTaskChipClick;

type TelemetryEvent = OrientationTelemetryEvent | PatternTelemetryEvent;

function emitTelemetry(e: TelemetryEvent){
  if (localStorage.getItem('pe-telemetry-optout') === '1') return;
  navigator.sendBeacon('/api/telemetry', JSON.stringify(e));
}
```

## Storage & Processing
- Ingest endpoint batches events; daily rollup (counts, distribution of intents, feature adoption).
- No user-level analytics; only aggregate counts and ratios.
- Potential future field: `sessionIdHash` (SHA-256 of ephemeral session seed) to approximate unique sessions without identity linking.

## Reporting Metrics (Examples)
| Metric | Derivation |
|--------|------------|
| Quick Path usage distribution | count(events where name='orientation_quick_path_click') by intentSlug |
| Evaluation harness adoption | count(evaluation_copy_action) / sessions |
| Decision tree utilization | count(decision_tree_select_goal) / sessions |
| Example exploration depth | avg(similar_examples_chip_click per pattern_expand_examples) |
| Pattern expansion rate | pattern_expand_template events / unique pattern views |

## Governance
- Changes to telemetry require PR updating this file + a changelog entry.
- Opt-out mechanism documented in README.
- Security review ensures endpoint rejects oversized payloads and unknown event names.

## Roadmap Considerations
- Add anonymized latency buckets (client measure) for harness copy reaction times.
- Incorporate accessibility interaction events (e.g., skip link usage) for improvement targeting.
- Periodic public summary of non-sensitive aggregate metrics.
