export const metadata = {
  title: 'Orientation Cheat Sheet | Ballarat AI Prompt Dictionary',
  description: 'Printable condensed reference for core prompt pattern usage principles.'
};

import CheatSheetClient from './CheatSheetClient';

const blocks: Array<{ title: string; items: string[] }> = [
  { title: '5-Key Template', items: ['role: Persona / perspective','context: Background / constraints','action: Explicit task verb','format: Output structure or schema','response: Desired content style or limits']},
  { title: 'Lifecycle', items: ['Frame measurable task','Select 1–3 candidate patterns','Minimal adaptation (placeholders)','Pilot eval (edge + typical)','Analyze failure modes','Targeted structural refinements','Version + freeze','Monitor drift']},
  { title: 'Evaluation Metrics', items: ['Accuracy / precision / recall','Structural compliance','Rationale completeness','Latency & token cost','Bias / disparity checks']},
  { title: 'Failure Modes', items: ['Misclassification','Missing field','Hallucinated detail','Format drift','Biased phrasing']},
  { title: 'Adaptation Rules', items: ['Keep 5 keys stable','Use explicit placeholders','Limit examples (2–3 crisp)','Record rationale per change','Re-test after each structural edit']},
  { title: 'Combining Patterns (Flow)', items: ['Decompose → Extract → Reason → Verify','Validate each stage independently','Constrain intermediate outputs']},
  { title: 'Responsible Use', items: ['Avoid harmful intent','Preserve provenance metadata','Audit diverse inputs','Minimize sensitive data','Version & log changes']},
  { title: 'Anti-Patterns', items: ['Overloaded mega-prompt','Hidden evaluation criteria','Unbounded outputs','Adjective churn','Example bloat']}
];

export default function CheatSheetPage() {
  return <CheatSheetClient blocks={blocks} />;
}
