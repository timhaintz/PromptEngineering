export const metadata = {
  title: 'Orientation Cheat Sheet | Ballarat AI Prompt Taxonomy',
  description: 'Printable condensed reference for core prompt pattern usage principles.'
};

import CheatSheetClient from './CheatSheetClient';

// Refinements: each item ≤160 chars, concise actionable phrasing; avoid redundancy with Orientation full text.
const blocks: Array<{ title: string; items: string[] }> = [
  { title: '5-Key Template', items: [
    'role: assign clear persona / stance',
    'context: essential background & constraints only',
    'action: single explicit task verb',
    'format: target schema / shape (JSON, list, table)',
    'response: style, tone, length guardrails'
  ]},
  { title: 'Lifecycle', items: [
    'Frame measurable outcome & constraints',
    'Select 1–3 aligned candidate patterns',
    'Adapt minimally (placeholders, domain vars)',
    'Pilot evaluate (edge + typical set)',
    'Cluster failures by mode',
    'Refine structure before wording',
    'Version + freeze with metrics',
    'Monitor drift & reopen if regress'
  ]},
  { title: 'Evaluation Metrics', items: [
    'Accuracy / precision / recall as applicable',
    'Structural compliance (required keys)',
    'Rationale completeness (evidence present)',
    'Latency + token efficiency',
    'Bias / disparity across controlled variants'
  ]},
  { title: 'Failure Modes', items: [
    'Misclassification or incorrect label',
    'Missing required field',
    'Hallucinated / fabricated detail',
    'Formatting drift from schema',
    'Biased / exclusionary phrasing'
  ]},
  { title: 'Adaptation Rules', items: [
    'Preserve 5 key labels',
    'Use explicit versioned placeholders',
    'Limit examples (2–3 contrastive)',
    'Log rationale per structural change',
    'Re-test after each structural edit'
  ]},
  { title: 'Combining Patterns (Flow)', items: [
    'Decompose → Extract → Reason → Verify chain',
    'Validate each stage independently first',
    'Constrain outputs consumed by next stage'
  ]},
  { title: 'Responsible Use', items: [
    'Avoid harmful or abusive generation',
    'Preserve AI provenance metadata',
    'Audit diverse demographic inputs',
    'Minimize sensitive personal data',
    'Version prompts + change log'
  ]},
  { title: 'Anti-Patterns', items: [
    'Overloaded mega-prompt (split tasks)',
    'Hidden evaluation criteria (make explicit)',
    'Unbounded outputs (length/schema)',
    'Adjective churn w/out metrics',
    'Example bloat (prefer curated few)'
  ]}
];

export default function CheatSheetPage() {
  return <CheatSheetClient blocks={blocks} />;
}
