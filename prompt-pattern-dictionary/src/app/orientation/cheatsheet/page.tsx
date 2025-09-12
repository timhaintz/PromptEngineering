import Link from 'next/link';

export const metadata = {
  title: 'Orientation Cheat Sheet | Prompt Pattern Dictionary',
  description: 'Printable condensed reference for core prompt pattern usage principles.'
};

/*
  Cheat Sheet Principles:
  - Fast scanning
  - Minimal prose, high information density
  - Print friendly (relies on global print media queries)
*/

const blocks: Array<{ title: string; items: string[] }> = [
  {
    title: '5-Key Template',
    items: [
      'role: Persona / perspective',
      'context: Background / constraints',
      'action: Explicit task verb',
      'format: Output structure or schema',
      'response: Desired content style or limits'
    ]
  },
  {
    title: 'Lifecycle',
    items: [
      'Frame measurable task',
      'Select 1–3 candidate patterns',
      'Minimal adaptation (placeholders)',
      'Pilot eval (edge + typical)',
      'Analyze failure modes',
      'Targeted structural refinements',
      'Version + freeze',
      'Monitor drift'
    ]
  },
  {
    title: 'Evaluation Metrics',
    items: [
      'Accuracy / precision / recall',
      'Structural compliance',
      'Rationale completeness',
      'Latency & token cost',
      'Bias / disparity checks'
    ]
  },
  {
    title: 'Failure Modes',
    items: [
      'Misclassification',
      'Missing field',
      'Hallucinated detail',
      'Format drift',
      'Biased phrasing'
    ]
  },
  {
    title: 'Adaptation Rules',
    items: [
      'Keep 5 keys stable',
      'Use explicit placeholders',
      'Limit examples (2–3 crisp)',
      'Record rationale per change',
      'Re-test after each structural edit'
    ]
  },
  {
    title: 'Combining Patterns (Flow)',
    items: [
      'Decompose → Extract → Reason → Verify',
      'Validate each stage independently',
      'Constrain intermediate outputs'
    ]
  },
  {
    title: 'Responsible Use',
    items: [
      'Avoid harmful intent',
      'Preserve provenance metadata',
      'Audit diverse inputs',
      'Minimize sensitive data',
      'Version & log changes'
    ]
  },
  {
    title: 'Anti-Patterns',
    items: [
      'Overloaded mega-prompt',
      'Hidden evaluation criteria',
      'Unbounded outputs',
      'Adjective churn',
      'Example bloat'
    ]
  }
];

export default function CheatSheetPage() {
  return (
    <div className="min-h-screen bg-white print:bg-white">
      <div className="container mx-auto px-4 py-8 lg:py-12">
        <div className="no-print mb-6 flex items-center justify-between flex-wrap gap-4">
          <h1 className="text-3xl font-bold text-gray-900">Orientation Cheat Sheet</h1>
          <div className="flex gap-3 text-sm">
            <Link href="/orientation" className="text-blue-600 hover:underline">Full Orientation</Link>
            <button onClick={() => window.print()} className="px-3 py-1 rounded border bg-gray-50 hover:bg-gray-100 text-gray-800">Print</button>
          </div>
        </div>
        <p className="text-sm text-gray-600 max-w-3xl mb-8">Concise reference for day-to-day prompt pattern work. See full Orientation for rationale and extended guidance.</p>

        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6 print:grid-cols-3">
          {blocks.map(block => (
            <div key={block.title} className="border rounded-lg p-4 bg-white shadow-sm break-inside-avoid print:shadow-none">
              <h2 className="text-sm font-semibold tracking-wide text-gray-800 mb-2 uppercase">{block.title}</h2>
              <ul className="text-xs space-y-1 leading-snug">
                {block.items.map((it, i) => <li key={i} className="flex gap-2"><span className="text-gray-400">•</span><span className="text-gray-800">{it}</span></li>)}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 text-xs text-gray-500 no-print">
          Generated: {new Date().toISOString().slice(0,10)} • Feedback welcome – open an issue with suggestions.
        </div>
      </div>
    </div>
  );
}
