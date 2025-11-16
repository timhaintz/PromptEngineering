import React from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import MermaidDiagram from '@/components/diagram/MermaidDiagram';

const DecisionTreeWidget = dynamic(
  () => import('../components/DecisionTreeWidget').then(mod => ({ default: mod.DecisionTreeWidget })),
  {
    ssr: false,
    loading: () => <p className="text-xs text-muted">Loading decision aid…</p>
  }
);

export interface OrientationSectionMeta {
  slug: string;
  id: string; // anchor id for combined page
  title: string;
  number: number;
  description: string;
  legacyAnchors?: string[]; // potential old ids
  component: React.ReactNode; // rendered body (without outer <section>)
}

// Migrated components from legacy single-page Orientation (headings removed; page/all wrappers provide numbering headings).
// (Original QuickStart replaced below with concrete mini scenario + evaluation stub.)

const copySnippet = (codeElementId: string, liveRegionId: string) => {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') return;
  const source = document.getElementById(codeElementId);
  if (!source) return;
  const text = source.textContent ?? '';
  navigator.clipboard.writeText(text).then(() => {
    const liveRegion = document.getElementById(liveRegionId);
    if (liveRegion) liveRegion.textContent = 'Copied snippet to clipboard';
  });
};

const FAILURE_MODES = [
  {
    name: 'Misclassification',
    indicator: 'Correct label drops below target or rationales contradict verdict',
    action: 'Revisit ACTION rules, add contrastive examples, tighten evaluation rubric.'
  },
  {
    name: 'Missing Field',
    indicator: 'Required JSON keys absent or null >5% of runs',
    action: 'Promote fields into FORMAT instructions, add fail-closed guard (reject incomplete input).'
  },
  {
    name: 'Hallucinated Field',
    indicator: 'Model invents keys or unsupported references',
    action: 'Reinforce RESPONSE section with explicit “do not add” rule; include schema validator in harness.'
  },
  {
    name: 'Formatting Drift',
    indicator: 'Outputs stop parsing cleanly; increased ad-hoc prose',
    action: 'Add pre/post fences, reiterate deterministic ordering, and validate with parser before scoring.'
  },
  {
    name: 'Biased / Exclusionary Language',
    indicator: 'Stereotyped rationale wording or uneven error rates across demographic variants',
    action: 'Inject diverse edge cases, add fairness assertions, and log metrics per cohort.'
  }
];

const METRIC_GUIDANCE = [
  { metric: 'Exact Match %', use: 'Structured extraction or classification with discrete labels', target: '≥90% on a stratified golden set (min 40 items).' },
  { metric: 'JSON Validity Rate', use: 'Any schema-constrained response', target: '≥98% parse success with required keys present.' },
  { metric: 'Rationale Completeness', use: 'Explain-then-decide patterns', target: '100% of rows include non-empty rationale tied to evidence.' },
  { metric: 'Latency & Token Budget', use: 'Operational monitoring', target: 'Stay within agreed ceiling; alert when >20% slower or >15% longer than baseline.' }
];

const DRIFT_SIGNALS = [
  'Role fidelity slips (model begins ignoring ROLE persona after adaptations).',
  'Format error rate trends upward for the last 20 executions.',
  'Knowledge intent shifts unintentionally (e.g., retrieval prompt starts tutoring).',
  'Rationales reuse verbatim text from unrelated samples (indicates memorization or context leak).',
  'Guardrail phrases disappear (e.g., “Reject incomplete input”), hinting the Template was trimmed too aggressively.'
];

const TEMPLATE_EXCERPT = `ROLE: Rank policy proposals against zero-trust rubric.
CONTEXT: Each proposal includes scope, controls, and rollout notes.
ACTION: Produce a JSON table with fields policy_name, coverage_gap, escalation.
FORMAT: JSON array, deterministic order.
RESPONSE: Include one-sentence rationale per entry.`;

const BRACKETED_SYNTHESIS_EXAMPLE = `[Rank zero-trust proposals | return JSON array policy_name, coverage_gap, escalation, rationale | reject proposals missing rollout notes]`;

const JS_EVAL_HARNESS_CODE = `// eval-harness.test.ts
// Minimal illustrative harness (pseudo)
import { runModel } from '../model';
import golden from './golden.json'; // [{input, expectedClassification}]

test('structure & classification', async () => {
  const prompt = buildPrompt(golden.map(g => g.input));
  const raw = await runModel(prompt);
  const data = JSON.parse(raw);
  expect(Array.isArray(data)).toBe(true);
  expect(data).toHaveLength(golden.length);
  data.forEach((row, i) => {
    expect(['benign','suspicious','malicious']).toContain(row.classification);
    expect(row.rationale).toBeTruthy();
  });
});

test('golden alignment (sample)', async () => {
  const prompt = buildPrompt(golden.slice(0,3).map(g => g.input));
  const raw = await runModel(prompt);
  const data = JSON.parse(raw);
  data.forEach((row, i) => {
    // relaxed match for rationale keyword
    expect(row.classification).toBe(golden[i].expectedClassification);
  });
});

function buildPrompt(lines){
  return 'ROLE: classify security logs\\nACTION: output JSON array with classification,rationale\\nLOG_LINES:\\n' + lines.map((l,i)=> (i+1)+'. '+ l).join('\\n');
}`;

const PY_EVAL_HARNESS_CODE = `# test_evaluate_pattern.py
import json
from harness import run_model, load_golden

def test_structure_and_fields():
    golden = load_golden()
    prompt = build_prompt([case["input"] for case in golden])
    parsed = json.loads(run_model(prompt))
    assert len(parsed) == len(golden)
    for row in parsed:
        assert row.get("classification") in {"benign", "suspicious", "malicious"}
        assert isinstance(row.get("rationale"), str) and row["rationale"].strip()

def test_sample_alignment():
    sample = load_golden(limit=5)
    prompt = build_prompt([case["input"] for case in sample])
    parsed = json.loads(run_model(prompt))
    mismatches = [row for row, expected in zip(parsed, sample)
                  if row["classification"] != expected["expected"]]
    assert len(mismatches) <= 1, "More than one mismatch triggers adaptation"

def build_prompt(lines):
    joined = "\\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
    return f"""ROLE: classify security logs
CONTEXT: Each line contains timestamp + message
ACTION: Return JSON array with classification,rationale
FORMAT: JSON array, deterministic order
RESPONSE: Include rationale tied to evidence
LOG_LINES:\n{joined}
"""`;

const CHANGE_LOG_SNIPPET = `pattern: 71-45-2
date: 2025-11-16
change:
  context: Added domain specificity for academic peer review (removed generic 'document' phrasing)
rationale: Improve clarity; reduce ambiguous artifact references
evaluation:
  sample_size: 8
  structure_compliance: 100%
  metric_delta: "Rationale completeness +12%"
notes: >
  Logged in evaluation notebook with before/after diff screenshot.
`;

const WhatIsPattern = () => (
  <div>
    <p>A prompt pattern is a <strong>reusable, named design structure</strong> for interacting with a language model so that behavior is <em>predictable, inspectable, and improvable</em>. It captures <em>intent</em>, <em>structural scaffolding</em>, and <em>adaptation guidance</em>. Think of patterns as <strong>primitives</strong> for assembling reliable language workflows—not secret incantations.</p>
    <p className="mt-3">Why they matter:</p>
    <ul className="list-disc pl-5 space-y-1">
      <li><strong>Shared vocabulary</strong> improves collaboration.</li>
      <li><strong>Structure reduces ambiguity</strong> and unintended model drift.</li>
      <li><strong>Comparability</strong> allows systematic evaluation.</li>
      <li><strong>Traceability</strong> helps audit and mitigate harmful or biased behavior.</li>
    </ul>
  </div>
);

const PatternAnatomy = () => (
  <div>
    <p>Each entry follows a consistent schema to support scanning, comparison, enrichment and evaluation. The Template exposes five canonical keys (<code>role</code>, <code>context</code>, <code>action</code>, <code>format</code>, <code>response</code>) plus an optional single‑line <em>bracketed synthesis</em>. Recent enrichment adds <strong>General Explanation</strong> (ELI12 summary), <strong>Usage Summary</strong> (pragmatic how‑to), <strong>Knowledge Intent</strong> (quadrant classification), and <strong>PEIL</strong> (Prompt Engineering Instructional Language) prompts. These fields improve pedagogy and adaptation while preserving the original research‑sourced <strong>Description</strong>.</p>
    <div id="peil" className="sr-only">Prompt Engineering Instructional Language (PEIL)</div>
    <div className="mt-4 grid gap-4 md:grid-cols-2">
  <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-2">Field Overview</h3>
        <dl className="text-sm space-y-2">
          <div>
            <dt className="font-medium">Pattern Name</dt>
            <dd>Human-readable identifier of the design strategy.</dd>
          </div>
          <div>
            <dt className="font-medium">Pattern ID</dt>
            <dd>Stable index (<code>paperId-category-pattern</code>) used for linking & similarity matrices.</dd>
          </div>
          <div>
            <dt className="font-medium">Description</dt>
            <dd>Research-sourced narrative explaining purpose & scope (authorial voice preserved).</dd>
          </div>
          <div>
            <dt className="font-medium">General Explanation</dt>
            <dd>ELI12 style pedagogical summary distilling core behavior (AI-assisted; do not overwrite Description).</dd>
          </div>
          <div>
            <dt className="font-medium">Media Type</dt>
            <dd>Primary input modality assumption (e.g., text).</dd>
          </div>
          <div>
            <dt className="font-medium">Dependent LLM</dt>
            <dd>If behavior relies on a model feature (e.g., tool use).</dd>
          </div>
          <div>
            <dt className="font-medium">Application</dt>
            <dd>Tags / scenario phrases describing contexts of use (research + derived domain examples).</dd>
          </div>
          <div>
            <dt className="font-medium">Usage Summary</dt>
            <dd>Plain-language “how to apply” steps (AI-assisted). Distinct from General Explanation (what) & Description (why).</dd>
          </div>
          <div>
            <dt className="font-medium">Turn</dt>
            <dd>Indicates if pattern expects multi-turn setup.</dd>
          </div>
          <div>
            <dt className="font-medium">Knowledge Intent</dt>
            <dd>Dominant knowledge-flow quadrant (Retrieval, Refinement, Co‑Discovery, Tutoring).</dd>
          </div>
          <div>
            <dt className="font-medium">Template</dt>
            <dd>Structured 5-key scaffold; expand to view; may include bracketed single-line form.</dd>
          </div>
          <div>
            <dt className="font-medium">Examples</dt>
            <dd>Canonical prompt instances; expandable; similarity links surface nearest neighbors.</dd>
          </div>
          <div>
            <dt className="font-medium">Similar Patterns</dt>
            <dd>Embeddings-based related entries for exploration.</dd>
          </div>
          <div>
            <dt className="font-medium">PEIL</dt>
            <dd>Generated structured system prompt combining template + application domain for consistent downstream use.</dd>
          </div>
          <div>
            <dt className="font-medium">AI-Assisted Badge</dt>
            <dd>Signals fields generated or refined with model help, supporting transparency.</dd>
          </div>
        </dl>
      </div>
  <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-2">Usage Guidance</h3>
        <ul className="list-disc pl-5 space-y-1 text-sm">
          <li><strong>Do not remove structural keys</strong>; populate them concretely.</li>
          <li><strong>Keep placeholders explicit</strong> (avoid implicit variable names).</li>
          <li><strong>Separate examples from instructions</strong>—don’t bury rules inside an example unless evaluating in-context demonstration.</li>
          <li><strong>Record changes</strong> to monitor regression risk.</li>
          <li><strong>Avoid domain stereotypes</strong> in examples; favor neutral or diverse representations.</li>
          <li><strong>Preserve Description fidelity</strong>; edit General Explanation / Usage Summary for clarity, not the research text.</li>
          <li><strong>Knowledge Intent</strong> must remain within the four supported quadrants—open an issue for ambiguous cases.</li>
          <li><strong>PEIL prompts</strong> are starting scaffolds: adjust variables, not structural logic; never overwrite authoritative Template.</li>
          <li><strong>AI-assisted fields</strong> (General Explanation, Usage Summary, PEIL) require manual review in regulated contexts.</li>
        </ul>
      </div>
    </div>
    <div className="mt-4 p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <h3 className="text-sm font-semibold mb-2">Template Mutation Guardrails</h3>
      <ol className="list-decimal pl-5 space-y-1 text-sm">
        <li><strong>Sequence edits:</strong> adjust context nouns → examples → ACTION wording before touching FORMAT or RESPONSE keys.</li>
        <li><strong>One structural change per iteration:</strong> re-evaluate after moving or rephrasing any key.</li>
        <li><strong>Bracket parity:</strong> keep the optional bracketed line synchronized with the full Template.</li>
        <li><strong>Fail-closed clauses stay visible:</strong> do not delete “reject/abort” instructions unless you log a mitigation.</li>
        <li><strong>Version every key change:</strong> bump pattern version and capture metrics whenever ROLE, ACTION, FORMAT, or RESPONSE text shifts.</li>
      </ol>
      <p className="text-xs text-secondary mt-2">Guardrails maintain comparability between evaluations and provide auditors a clear chain of custody for structural edits.</p>
    </div>
    <details className="my-6 p-4 rounded-lg bg-surface-1 border border-muted shadow-sm group">
      <summary className="cursor-pointer text-sm font-semibold text-accent mb-2 flex items-center gap-2">
        Simplified Structure Overview <span className="text-xs text-secondary font-normal">(keys & relationships)</span>
      </summary>
      <p className="text-xs text-secondary mb-3">Core relationships between a Pattern and its major components. Focus stays on the 5-Key Template as the structural nucleus; ancillary metadata supports discovery, evaluation, and adaptation.</p>
      <ul className="grid sm:grid-cols-2 gap-2 text-xs">
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Template</strong>: 5 keys + optional bracketed summary.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Examples</strong>: Canonical prompts feeding similarity links.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Application</strong>: Scenario tags guiding relevance.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>General Explanation</strong>: Pedagogical ELI12 summary (AI-assisted).</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Usage Summary</strong>: Operational steps / deployment hints.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Knowledge Intent</strong>: Quadrant classification powering analytics.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>PEIL</strong>: Structured system prompt variant for automation.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Adaptation Notes</strong>: Versioning & rationale traces.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Evaluation Hints</strong>: Metrics & failure taxonomy anchors.</li>
        <li className="p-2 rounded border border-muted bg-surface-2"><strong>Similar Patterns</strong>: Embedding neighbors for exploration.</li>
      </ul>
      <details className="mt-4 group">
        <summary className="cursor-pointer text-xs text-accent font-medium">Expanded Text Description (Accessibility)</summary>
        <p className="mt-2 text-xs leading-relaxed">A Pattern centers on its Template. The Template enumerates five required keys ensuring tasks are explicit and auditable. General Explanation and Usage Summary sit above the Template for pedagogical orientation (what it does) and operational guidance (how to apply). Knowledge Intent classifies the pattern’s knowledge flow quadrant for analytics and evaluation prioritization. PEIL derives a structured system prompt variant from the authoritative Template + Application tags—never rewriting the underlying research Template. Examples attach to the Pattern to demonstrate usage and seed similarity computations. Application tags contextualize domain fit. Adaptation Notes and Evaluation Hints form an iterative loop around the Template—changes to structure trigger re‑evaluation. Similar Patterns form a peripheral ring enabling lateral exploration without losing structural grounding.</p>
      </details>
    </details>
    <div className="mt-6 grid gap-4 md:grid-cols-2">
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
        <h3 className="text-sm font-semibold mb-2">Field Boundaries</h3>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>Description</strong>: Research-authoritative narrative. Preserve provenance; only fix typos.</li>
          <li><strong>General Explanation</strong>: Short ELI12 teaching paragraph translating research into plain language.</li>
          <li><strong>Usage Summary</strong>: Pragmatic “when/how to run this” outline including evaluation hooks.</li>
          <li><strong>Template vs PEIL</strong>: Template is the canonical 5-key scaffold; PEIL is a derivative automation prompt that must reuse those keys verbatim.</li>
        </ul>
      </div>
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
        <h3 className="text-sm font-semibold mb-2">PEIL Usage Example</h3>
        <p className="text-sm mb-2">Template excerpt:</p>
        <pre className="text-xs bg-surface-2 border border-muted rounded p-3 overflow-auto mb-3"><code>{TEMPLATE_EXCERPT}</code></pre>
        <p className="text-sm mb-1">PEIL derivation (never replaces Template, but wraps it for downstream automation):</p>
        <pre className="text-xs bg-surface-2 border border-muted rounded p-3 overflow-auto"><code>{`System Goal: Evaluate each zero-trust policy proposal for coverage gaps.
      Rules:
      - Reuse the ROLE/CONTEXT/ACTION/FORMAT/RESPONSE keys exactly as authored.
      - Reject inputs missing rollout notes.
      - Output JSON with fields policy_name, coverage_gap, escalation, rationale.
      - Flag policies lacking MFA in rollout plan as escalation="high".`}</code></pre>
        <p className="text-xs text-secondary mt-2">Notice how PEIL reiterates Template keys, adds operational guardrails, and is safe to paste into orchestration tooling while maintaining provenance.</p>
      </div>
    </div>
    <div className="mt-6 grid gap-4 md:grid-cols-2">
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
        <h3 className="text-sm font-semibold mb-2">Template ↔ Bracketed Synthesis</h3>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-secondary mb-1">Expanded 5-key structure</p>
            <pre className="text-xs bg-surface-2 border border-muted rounded p-3 overflow-auto"><code>{TEMPLATE_EXCERPT}</code></pre>
          </div>
          <div>
            <p className="text-xs text-secondary mb-1">Single-line bracketed recall</p>
            <pre className="text-xs bg-surface-2 border border-muted rounded p-3 overflow-auto"><code>{BRACKETED_SYNTHESIS_EXAMPLE}</code></pre>
          </div>
          <p className="text-xs text-secondary">Bracketed lines are optional summaries kept under ~120 characters and must reference the same ROLE → ACTION → FORMAT guardrails. They speed orientation but should never be edited without updating the full Template.</p>
        </div>
      </div>
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
        <h3 className="text-sm font-semibold mb-2">Bracket Usage Checklist</h3>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>No new instructions:</strong> only compress existing Template text.</li>
          <li><strong>Maintain order:</strong> mention ROLE intent before ACTION outputs.</li>
          <li><strong>Call out guardrails:</strong> include the most critical constraint (e.g., “reject incomplete input”).</li>
          <li><strong>Link to Template:</strong> clicking the badge scrolls to the expanded 5-key section to verify fidelity.</li>
          <li><strong>Version along with Template:</strong> whenever keys change, update the bracket line in the same commit/log entry.</li>
        </ul>
      </div>
    </div>
  </div>
);

const Lifecycle = () => (
  <div>
    <ol className="list-decimal pl-6 space-y-1 text-sm">
      <li><strong>Need Framing</strong>: Clarify measurable outcome and constraints.</li>
      <li><strong>Candidate Selection</strong>: 1–3 patterns aligned with task archetype.</li>
      <li><strong>Minimal Adaptation</strong>: Insert domain specifics; keep structure intact.</li>
      <li><strong>Pilot Evaluation</strong>: Run against a stratified micro‑set (edge + typical cases).</li>
      <li><strong>Error Analysis</strong>: Categorize failures (ambiguity, formatting, bias, hallucination).</li>
      <li><strong>Targeted Refinement</strong>: Adjust keys; avoid piling adjectives.</li>
      <li><strong>Version Freeze</strong>: Tag as v1.x; store alongside metrics.</li>
      <li><strong>Monitoring</strong>: Periodic spot checks & drift watch (especially after model updates).</li>
    </ol>
  <p className="mt-3 text-sm text-secondary"><strong>Drift Indicator:</strong> If failure clusters reappear or confidence declines, re-open the adaptation phase—do not silently patch in production.</p>
  </div>
);

const Choosing = () => {
  const showTree = typeof process !== 'undefined' && process.env.NEXT_PUBLIC_SHOW_DECISION_TREE === '1';
  return (
    <div className="space-y-3 text-sm">
      <p><strong>Map task → Archetype:</strong> e.g. “Summarize transcripts” → Transformation; “Rank policy risks” → Evaluation; “Suggest refactors” → Reasoning / Refactoring hybrid.</p>
      <p><strong>Heuristics:</strong></p>
      <ul className="list-disc pl-5 space-y-1">
        <li><strong>Prefer simpler baseline</strong> before composite patterns.</li>
        <li><strong>Favor interpretability</strong> (clear keys, explicit criteria).</li>
        <li><strong>Bias surface</strong>: choose patterns that force explicit decision rationales when sensitive classifications arise.</li>
        <li><strong>Evidence richness</strong>: if auditability is critical, select patterns producing structured, inspectable fields.</li>
      </ul>
      <p><strong>Tie-break rule:</strong> Pick the pattern with fewer <em>critical</em> (not cosmetic) failures under pilot evaluation.</p>
      {showTree && (
        <div className="mt-4">
          <DecisionTreeWidget />
        </div>
      )}
    </div>
  );
};

const Combining = () => (
  <div>
    <p className="text-sm">Compose multi-step flows deliberately. Each link should produce a constrained artifact consumed safely by the next step.</p>
    <table className="text-xs mt-3 border w-full">
      <thead>
  <tr className="bg-surface-2 text-secondary">
          <th className="px-2 py-1 text-left font-semibold">Flow Stage</th>
          <th className="px-2 py-1 text-left font-semibold">Example Pattern</th>
          <th className="px-2 py-1 text-left font-semibold">Output Form</th>
          <th className="px-2 py-1 text-left font-semibold">Checks</th>
        </tr>
      </thead>
      <tbody>
        <tr className="border-t"><td className="px-2 py-1">Decompose</td><td className="px-2 py-1">Task Breakdown / Decomposition</td><td className="px-2 py-1">Bullet / JSON steps</td><td className="px-2 py-1">No overlaps; coverage complete</td></tr>
        <tr className="border-t"><td className="px-2 py-1">Extract</td><td className="px-2 py-1">Structured Extraction</td><td className="px-2 py-1">Key:value JSON</td><td className="px-2 py-1">Required keys present</td></tr>
        <tr className="border-t"><td className="px-2 py-1">Reason</td><td className="px-2 py-1">Chain / Justified Answer</td><td className="px-2 py-1">Rationales + answer</td><td className="px-2 py-1">No speculative leaps</td></tr>
        <tr className="border-t"><td className="px-2 py-1">Verify</td><td className="px-2 py-1">Consistency / Critique</td><td className="px-2 py-1">Pass/Fail + notes</td><td className="px-2 py-1">Deterministic format</td></tr>
      </tbody>
    </table>
    <p className="mt-3 text-sm"><strong>Tip:</strong> Validate each stage independently before chaining. Avoid premature parallelization.</p>
  </div>
);

const Adaptation = () => (
  <div>
    <ul className="list-disc pl-5 space-y-1 text-sm">
      <li><strong>Preserve structural keys</strong>; modify content, not the scaffold labels.</li>
      <li><strong>Use versioned placeholders</strong> (<code>{'{{CLAUSE_A}}'}</code>, <code>{'{{CLAUSE_B}}'}</code>) so diffs are meaningful.</li>
      <li><strong>Record rationale</strong> for each modification (links to observed failure modes).</li>
      <li><strong>Minimize example bloat</strong>: prefer 2–3 crisp examples over sprawling narratives.</li>
      <li><strong>Ethical adaptation</strong>: Avoid reinforcing stereotypes; stress neutral or diverse entities.</li>
      <li><strong>Re-run evaluation</strong> after each structural shift (no “silent merges”).</li>
      <li><strong>Bracket + Template parity</strong>: whenever you add/remove instruction text, update both the expanded keys and the bracketed summary.</li>
      <li><strong>Change discipline</strong>: one structural adjustment per commit/log entry keeps drift analysis straightforward.</li>
    </ul>
    <div className="mt-4 p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <h3 className="text-sm font-semibold mb-2">Minimal Change Log Snippet</h3>
      <p className="text-xs text-secondary mb-2">Capture every structural edit with pattern ID, rationale, and evaluation deltas. Copy the template below into your tracking doc or repo.</p>
      <div className="relative">
        <button type="button" aria-label="Copy change log snippet" className="absolute top-2 right-2 text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" onClick={() => copySnippet('change-log-snippet', 'change-log-live')}>Copy</button>
        <pre id="change-log-snippet" className="overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{CHANGE_LOG_SNIPPET}</code></pre>
        <div id="change-log-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
      </div>
    </div>
  <p className="mt-3 text-xs text-muted">If a pattern diverges heavily, consider naming it explicitly (fork) to preserve lineage.</p>
  </div>
);

const AntiPatterns = () => (
  <div className="space-y-4">
    <ul className="list-disc pl-5 space-y-1 text-sm">
      <li><strong>Overloaded Mega-Prompt</strong>: Multiple tasks → split & chain.</li>
      <li><strong>Hidden Criteria</strong>: Implicit judgment rules → move into explicit <code>format</code> or <code>response</code> instructions.</li>
      <li><strong>Style Churn</strong>: Iterating adjectives (“highly accurate”, “extremely concise”) with no metric plan.</li>
      <li><strong>Example Indigestion</strong>: Copying large corpora instead of curated, contrastive examples.</li>
      <li><strong>Ad Hoc Mutation</strong>: Unlogged edits degrade reproducibility.</li>
      <li><strong>Unbounded Outputs</strong>: Missing length or schema constraints → overflow & hallucination risk.</li>
      <li><strong>Bias Amplification</strong>: Narrow example diversity → skewed performance on underrepresented inputs.</li>
    </ul>
    <div>
      <h3 className="text-sm font-semibold mb-2">Remediation Mapping</h3>
      <table className="text-xs w-full border">
        <thead>
          <tr className="bg-surface-2 text-secondary">
            <th className="p-2 text-left font-semibold">Anti-Pattern</th>
            <th className="p-2 text-left font-semibold">Symptom</th>
            <th className="p-2 text-left font-semibold">Recommended Pattern</th>
            <th className="p-2 text-left font-semibold">Caution</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-t"><td className="p-2">Overloaded Mega-Prompt</td><td className="p-2">Mixed unrelated instructions</td><td className="p-2">Task Breakdown / Decomposition</td><td className="p-2">Keep steps atomic</td></tr>
          <tr className="border-t"><td className="p-2">Hidden Criteria</td><td className="p-2">Unstated scoring rules</td><td className="p-2">Structured Extraction + Explicit Format</td><td className="p-2">Define schema keys</td></tr>
          <tr className="border-t"><td className="p-2">Style Churn</td><td className="p-2">Endless adjective tweaking</td><td className="p-2">Refactor / Clarify</td><td className="p-2">Change one variable</td></tr>
          <tr className="border-t"><td className="p-2">Example Indigestion</td><td className="p-2">Huge uncurated block</td><td className="p-2">Contrastive Few Examples</td><td className="p-2">Prioritize diversity</td></tr>
          <tr className="border-t"><td className="p-2">Unbounded Outputs</td><td className="p-2">Rambling / overflow</td><td className="p-2">Structured Extraction / Bounded Response</td><td className="p-2">Set length/schema</td></tr>
        </tbody>
      </table>
    </div>
  </div>
);

const Evaluation = () => (
  <div className="space-y-5 text-sm">
    <div>
      <h3 className="text-sm font-semibold mb-2">Metrics & Drift Watch</h3>
      <table className="text-xs w-full border" aria-label="Suggested evaluation metrics">
        <thead>
          <tr className="bg-surface-2 text-secondary">
            <th className="p-2 text-left font-semibold">Metric</th>
            <th className="p-2 text-left font-semibold">Use When</th>
            <th className="p-2 text-left font-semibold">Target / Trigger</th>
          </tr>
        </thead>
        <tbody>
          {METRIC_GUIDANCE.map(row => (
            <tr key={row.metric} className="border-t">
              <td className="p-2 font-medium">{row.metric}</td>
              <td className="p-2">{row.use}</td>
              <td className="p-2">{row.target}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-3">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-secondary">Prompt Drift Signals</h4>
        <ul className="list-disc pl-5 space-y-1 mt-1 text-sm">
          {DRIFT_SIGNALS.map(signal => (
            <li key={signal}>{signal}</li>
          ))}
        </ul>
        <p className="text-xs text-muted mt-2">Investigate when any signal persists for &gt;2 evaluation cycles; log mitigation steps in the change log.</p>
      </div>
    </div>
    <div>
      <h3 className="text-sm font-semibold mb-2">Failure Mode Taxonomy</h3>
      <table className="text-xs w-full border">
        <thead>
          <tr className="bg-surface-2 text-secondary">
            <th className="p-2 text-left font-semibold">Mode</th>
            <th className="p-2 text-left font-semibold">Indicator</th>
            <th className="p-2 text-left font-semibold">Corrective Action</th>
          </tr>
        </thead>
        <tbody>
          {FAILURE_MODES.map(mode => (
            <tr key={mode.name} className="border-t">
              <td className="p-2 font-medium">{mode.name}</td>
              <td className="p-2">{mode.indicator}</td>
              <td className="p-2">{mode.action}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-secondary mt-2">Tag each evaluation finding with one of these modes before proposing adaptations—this keeps remediation focused.</p>
    </div>
    <div>
      <h3 className="text-sm font-semibold mb-2">Evaluation Harness Examples</h3>
      <p className="text-xs text-secondary mb-3">Start with a CSV/JSON golden set (10–50 rows). Each harness below enforces JSON validity, label coverage, and light alignment checks. Swap in your own <code>run_model</code> implementation.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="p-3 rounded border border-muted bg-surface-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">Python · pytest</span>
            <button type="button" aria-label="Copy Python harness" className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" onClick={() => copySnippet('eval-harness-py', 'eval-harness-py-live')}>Copy</button>
          </div>
          <pre id="eval-harness-py" className="overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{PY_EVAL_HARNESS_CODE}</code></pre>
          <div id="eval-harness-py-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
        </div>
        <div className="p-3 rounded border border-muted bg-surface-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">JavaScript · Jest</span>
            <button type="button" aria-label="Copy JavaScript harness" className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" onClick={() => copySnippet('eval-harness-js', 'eval-harness-js-live')}>Copy</button>
          </div>
          <pre id="eval-harness-js" className="overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{JS_EVAL_HARNESS_CODE}</code></pre>
          <div id="eval-harness-js-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
        </div>
      </div>
      <p className="text-xs text-muted mt-2">Automation tip: run schema validation before expensive scoring, then log pass/fail + metric deltas alongside the change log snippet.</p>
    </div>
  </div>
);

// P3 – Interactive Teasers
const SimilarityPreview = () => {
  const sample = [
    { id: '0-0-0', score: 0.74 },
    { id: '0-1-0', score: 0.69 },
    { id: '71-26-6', score: 0.65 }
  ];
  const showGraph = typeof process !== 'undefined' && process.env.NEXT_PUBLIC_SHOW_ORIENTATION_GRAPH === '1';
  return (
    <div className="space-y-4 text-sm">
      <p><strong>Semantic Similarity Preview:</strong> Example related patterns surfaced via cosine similarity over embedding vectors (name + description + up to first 3 examples). Scores are exploratory and aid lateral discovery—not categorical truth.</p>
      <table className="text-xs w-full border mt-2" aria-describedby="similarity-preview-alt">
        <thead>
          <tr className="bg-surface-2 text-secondary">
            <th className="p-2 text-left font-semibold">Pattern ID</th>
            <th className="p-2 text-left font-semibold">Similarity Score</th>
          </tr>
        </thead>
        <tbody>
          {sample.map(row => (
            <tr key={row.id} className="border-t">
              <td className="p-2"><Link href={`/pattern/${row.id}`} className="text-accent hover:underline" aria-label={`View pattern ${row.id}`}>{row.id}</Link></td>
              <td className="p-2" aria-label={`Similarity ${row.score.toFixed(2)}`}>{row.score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div id="similarity-preview-alt" className="sr-only">Three sample patterns with descending cosine similarity scores (0.74, 0.69, 0.65) demonstrating relative semantic proximity. Use the comparison tool for real-time multi-pattern analysis.</div>
      <p className="text-xs text-secondary">Try the interactive comparison: <Link href={`/compare?patterns=${sample.map(s=>s.id).join(',')}`} className="text-accent underline">Open comparison view</Link>.</p>
      <details className="group p-3 rounded border border-muted bg-surface-1 shadow-sm">
        <summary className="cursor-pointer font-medium text-accent text-sm">Adaptation ↔ Evaluation Loop Diagram</summary>
        <div className="mt-2">
          <MermaidDiagram chart={`flowchart LR\n  Adaptation[Adaptation] --> Evaluation[Evaluation]\n  Evaluation --> ErrorAnalysis[Error Analysis]\n  ErrorAnalysis --> Refinement[Targeted Refinement]\n  Refinement --> Adaptation\n  classDef cycle fill:#334155,stroke:#64748b,color:#fff;\n  class Adaptation,Evaluation,ErrorAnalysis,Refinement cycle;`} />
          <details className="mt-3 text-xs">
            <summary className="cursor-pointer text-accent">Expanded Text Description (Accessibility)</summary>
            <p className="mt-1 leading-relaxed">The loop begins with Adaptation of a prompt pattern, proceeds to Evaluation against golden or stratified cases. Results feed Error Analysis categorizing failures, which informs Targeted Refinement. Refinement produces a revised pattern returning to Adaptation, forming a continuous reliability cycle.</p>
          </details>
        </div>
      </details>
      {showGraph && (
        <div>
          <details className="group p-3 rounded border border-muted bg-surface-1 shadow-sm">
            <summary className="cursor-pointer font-medium text-accent text-sm">Sample Pattern Connection Graph (Static)</summary>
            <div className="mt-2">
              <p className="text-xs mb-2">Illustrative miniature network—node proximity suggests higher similarity. This static teaser does not reflect dynamic scoring.</p>
              <div role="img" aria-label="Static network graph with three nodes A, B, C connected by lines showing mutual relationships" className="mx-auto w-full max-w-xs">
                <svg viewBox="0 0 200 120" className="w-full h-auto" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <style>{`.node{fill:var(--color-accent-bg,#0ea5e9);stroke:var(--color-accent,#0369a1);stroke-width:2}`}</style>
                  </defs>
                  <line x1="60" y1="60" x2="140" y2="40" stroke="var(--color-border,#64748b)" strokeWidth="1.5" />
                  <line x1="60" y1="60" x2="120" y2="90" stroke="var(--color-border,#64748b)" strokeWidth="1.5" />
                  <line x1="140" y1="40" x2="120" y2="90" stroke="var(--color-border,#64748b)" strokeWidth="1.5" strokeDasharray="4 2" />
                  <circle cx="60" cy="60" r="14" className="node" />
                  <circle cx="140" cy="40" r="14" className="node" />
                  <circle cx="120" cy="90" r="14" className="node" />
                  <text x="60" y="64" textAnchor="middle" fontSize="10" fill="#fff">A</text>
                  <text x="140" y="44" textAnchor="middle" fontSize="10" fill="#fff">B</text>
                  <text x="120" y="94" textAnchor="middle" fontSize="10" fill="#fff">C</text>
                </svg>
              </div>
              <p className="text-[10px] text-secondary mt-2">Enable dynamic graph features on the full comparison page; this orientation preview remains static for performance.</p>
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

const AccessibilityResponsible = () => (
  <div className="space-y-3 text-sm">
    <p>This project aims to support equitable, auditable, and safe prompt engineering practice. Use patterns in ways that respect user dignity, privacy, and legal constraints.</p>
    <h3 className="text-sm font-semibold mt-4">Accessibility Practices</h3>
    <ul className="list-disc pl-5 space-y-1">
      <li><strong>Structure:</strong> All interactive toggles are buttons with discernible text or labels; headings are hierarchical; focus order follows visual order.</li>
      <li><strong>Keyboard:</strong> Pattern detail expansion (examples, template, bracket form) is fully keyboard operable.</li>
      <li><strong>Color Contrast:</strong> Palette targets WCAG AA; report any insufficient contrast combinations.</li>
      <li><strong>Motion / Load:</strong> Mermaid diagrams render progressively with textual fallback.</li>
      <li><strong>Assistive Navigation:</strong> Anchors include scroll margin (offset) for reduced visual occlusion.</li>
    </ul>
    <h3 className="text-sm font-semibold mt-4">Responsible Use Guidelines</h3>
    <ul className="list-disc pl-5 space-y-1">
      <li><strong>No Harmful Generation:</strong> Do not adapt patterns to produce disallowed or abusive content.</li>
      <li><strong>Bias Monitoring:</strong> Evaluate outputs against diverse demographic and contextual inputs.</li>
      <li><strong>Transparency:</strong> Preserve AI-assisted metadata; do not remove provenance indicators.</li>
      <li><strong>Data Minimization:</strong> Avoid embedding sensitive personal data in examples or placeholders.</li>
      <li><strong>Audit Trails:</strong> Version prompts; log rationale for structural changes.</li>
    </ul>
    <h3 className="text-sm font-semibold mt-4">Escalation & Reporting</h3>
    <p>Report potential misuse, accessibility barriers, or biased outcomes via the repository issue tracker. Include reproduction steps, environment (model version), and anonymized sample input/output where possible.</p>
  </div>
);
// Rewritten Quick Start (P1)
const QuickStart = () => (
  <div className="space-y-6">
    <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
      <p className="font-semibold mb-2">Mini Scenario: Defensive Log Triage</p>
      <p className="mb-3">Goal: Classify security log lines as <code>benign</code>, <code>suspicious</code>, or <code>malicious</code> with short rationale. We adapt a <em>Structured Extraction + Justified Answer</em> style pattern.</p>
      <details className="group">
        <summary className="cursor-pointer text-accent font-medium">Runnable Prompt Template (fill placeholders)</summary>
        <pre className="mt-2 overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{`You are a security analysis assistant.\n\nROLE: Classify log entries.\nCONTEXT: Each line is an independent event from an application security log.\nACTION: For each provided LOG_LINE produce a JSON object with fields: classification (benign|suspicious|malicious), rationale (short), indicators (array).\nFORMAT: Return a JSON array, one object per line. No prose outside JSON.\nRESPONSE: Emphasize conservative escalation: if unsure between benign and suspicious choose suspicious.\n\nLOG_LINES:\n1. {{LOG_LINE_1}}\n2. {{LOG_LINE_2}}\n3. {{LOG_LINE_3}}\n`}</code></pre>
      </details>
      <details className="group mt-3">
        <summary className="cursor-pointer text-accent font-medium">Example Filled Prompt</summary>
        <pre className="mt-2 overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{`LOG_LINES:\n1. Failed login for user 'svc-build' from 10.4.6.7 after 12 attempts\n2. GET /healthz 200 15ms\n3. Outbound connection to 185.23.91.2 on port 4444 established by process powershell.exe`}</code></pre>
      </details>
      <details className="group mt-3">
        <summary className="cursor-pointer text-accent font-medium">Evaluation Harness Stub (Node / Jest)</summary>
        <pre className="mt-2 overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{`// pseudo-eval.test.ts\n// assuming callModel(prompt) returns model JSON string\nconst GOLDEN = [\n  { classification: 'suspicious', rationale: /12 attempts/i },\n  { classification: 'benign' },\n  { classification: 'malicious', rationale: /outbound/i }\n];\n\n test('classification structure', async () => {\n   const output = JSON.parse(await callModel(filledPrompt));\n   expect(output).toHaveLength(3);\n   output.forEach(o => expect(['benign','suspicious','malicious']).toContain(o.classification));\n });\n\n test('critical rationale hints present', async () => {\n   const output = JSON.parse(await callModel(filledPrompt));\n   expect(output[0].rationale).toMatch(GOLDEN[0].rationale);\n });`}</code></pre>
      </details>
    </div>
    <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-accent/10 text-accent text-[11px] font-bold">5</span>
        Five-Minute Tour
      </h3>
      <ol className="list-decimal pl-6 space-y-2 text-sm">
        <li><strong>Search with intent keywords</strong> (e.g., “triage logs”, “refine policy”). Use the homepage search bar or Quick Paths.</li>
        <li><strong>Open a pattern</strong> and note the <code className="text-xs">ID</code> badge for future similarity lookups.</li>
        <li><strong>Expand the Template & bracketed summary</strong> to internalize the five keys before editing.</li>
        <li><strong>Copy one Prompt Example</strong>, swap placeholders with your context, and respect schema/formatting constraints.</li>
        <li><strong>Scan Similar Patterns + Knowledge Intent</strong> to compare nearby strategies; jot deltas in a lightweight change log.</li>
        <li><strong>Run the evaluation harness stub (or yours)</strong> on 3–5 cases, capture pass/fail plus rationale snippets, and decide next adaptation step.</li>
      </ol>
      <p className="text-xs text-secondary mt-3">Track Pattern IDs, Template tweaks, and evaluation results in a shared doc—this becomes the minimal audit trail for later comparison.</p>
    </div>
    <div>
      <ol className="list-decimal pl-6 space-y-1">
        <li><strong>State your task</strong> explicitly with measurable outcome.</li>
        <li><strong>Find candidate patterns</strong> (search + similarity suggestions).</li>
        <li><strong>Open pattern & expand Template</strong> (do not delete keys).</li>
        <li><strong>Inject domain variables</strong> with explicit placeholders.</li>
        <li><strong>Draft evaluation harness</strong> (JSON parse + key checks).</li>
        <li><strong>Pilot on 3–5 varied examples</strong> (edge + typical).</li>
        <li><strong>Refine structurally first</strong> then wording.</li>
        <li><strong>Version & log metrics</strong> before wider use.</li>
      </ol>
    </div>
    <div className="p-3 rounded border border-muted bg-surface-1 shadow-sm text-sm text-secondary">
      <p className="font-semibold mb-1">Principles:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li><strong>Clarity over cleverness</strong> – explicit instructions reduce hallucination.</li>
        <li><strong>Single responsibility</strong> – one pattern, one job.</li>
        <li><strong>Measured change</strong> – alter one dimension per iteration.</li>
        <li><strong>Inclusive data</strong> – vary names, locales, benign vs edge cases.</li>
        <li><strong>Document provenance</strong> – track AI-assisted fields.</li>
      </ul>
    </div>
  </div>
);
// Glossary (restored after patch collision)
const Glossary = () => (
  <div>
    <nav aria-label="Glossary index" className="mb-3 flex flex-wrap gap-1 text-[11px]">
      {"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map(ch => (
        <a key={ch} href={`#term-${ch}`} className="px-1.5 py-0.5 rounded bg-surface-2 border border-muted hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" aria-label={`Jump to terms starting with ${ch}`}>{ch}</a>
      ))}
    </nav>
    <dl className="space-y-2 text-sm">
      <div>
        <dt className="font-medium">Pattern</dt>
        <dd>Named structural design for consistent model interaction.</dd>
      </div>
      <div>
        <dt className="font-medium">Template (5-Key)</dt>
        <dd>Standard scaffold: role, context, action, format, response.</dd>
      </div>
      <div>
        <dt className="font-medium">Bracketed Summary</dt>
        <dd>Compact single-line representation of the Template intent.</dd>
      </div>
      <div>
        <dt className="font-medium">Application</dt>
        <dd>Scenario tags or prose describing where the pattern applies.</dd>
      </div>
      <div>
        <dt className="font-medium">Usage Summary</dt>
        <dd>Concise guidance describing pragmatic deployment steps.</dd>
      </div>
      <div>
        <dt className="font-medium">Adaptation</dt>
        <dd>Domain-specific customization with structural integrity preserved.</dd>
      </div>
      <div>
        <dt className="font-medium">Similarity</dt>
        <dd>Embedding-based proximity score guiding exploration.</dd>
      </div>
      <div>
        <dt className="font-medium">Bias Mitigation</dt>
        <dd>Process of designing prompts and examples to reduce skew across demographic or contextual variation.</dd>
      </div>
    </dl>
  </div>
);

const FAQ = () => (
  <div>
    <details className="group border rounded mb-2 p-3 bg-surface-1">
      <summary className="cursor-pointer font-medium">Why five template keys?</summary>
      <p className="mt-2 text-sm">They balance expressive coverage (intent, situational framing, required action, output schema, expected shape/tone) with cognitive load. More keys lowered adoption; fewer reduced precision.</p>
    </details>
  <details className="group border rounded mb-2 p-3 bg-surface-1">
      <summary className="cursor-pointer font-medium">Can I add new keys?</summary>
      <p className="mt-2 text-sm">Yes—locally. If broadly useful, open a proposal so tooling and documentation can stay aligned. Keep custom keys succinct.</p>
    </details>
  <details className="group border rounded mb-2 p-3 bg-surface-1">
      <summary className="cursor-pointer font-medium">How do I detect bias?</summary>
      <p className="mt-2 text-sm">In evaluation, insert controlled variants (names, dialects, region terms) and compare outcome disparities. Investigate structural omissions before applying ad‑hoc wording patches.</p>
    </details>
  <details className="group border rounded mb-2 p-3 bg-surface-1">
      <summary className="cursor-pointer font-medium">When should I fork a pattern?</summary>
      <p className="mt-2 text-sm">If structural keys change semantics (e.g., merging roles, introducing multi-step embedded reasoning) or examples shift domain irreversibly—create a named fork for traceability.</p>
    </details>
  <details className="group border rounded p-3 bg-surface-1">
      <summary className="cursor-pointer font-medium">How are similar patterns computed?</summary>
      <p className="mt-2 text-sm">Pattern similarity uses cosine similarity over an embedding composed of the pattern’s name, description, and up to the first three example prompts. Results are exploratory semantic neighbors—not a curated taxonomy.</p>
      <p className="mt-2 text-sm">Separate per‑example embeddings are also generated for example‑to‑example cosine similarity; these appear in the UI under <span className="font-semibold">Similar Examples</span>.</p>
    </details>
  </div>
);

const Feedback = () => (
  <div>
  <p className="text-sm text-secondary">Spotted ambiguity, accessibility gaps, missing inclusive examples, or structural drift? Please open an issue or PR. Reference the pattern ID(s), describe the observed issue, and (if possible) include a minimal reproducible example. Community stewardship maintains reliability.</p>
  </div>
);

const NextSteps = () => (
  <div>
    <ul className="list-disc pl-5 text-sm space-y-1">
  <li><Link href="/patterns" className="text-accent hover:underline">Browse patterns</Link> and shortlist 2–3 for your task.</li>
      <li>Create a tiny evaluation set (edge + typical cases) and record baseline outputs.</li>
      <li>Introduce structured adaptation with version tags.</li>
      <li>Share findings—improvements are welcomed.</li>
    </ul>
  </div>
);

export const ORIENTATION_SECTIONS: OrientationSectionMeta[] = [
  { slug: 'quick-start', id: 'quick-start', title: 'Quick Start', number: 1, description: 'Practical 8-step startup path for using patterns safely.', component: <QuickStart /> },
  { slug: 'what-is-a-pattern', id: 'what-is-a-pattern', title: 'What Is a Pattern', number: 2, description: 'Definition, value, and collaboration benefits.', component: <WhatIsPattern /> },
  { slug: 'pattern-anatomy', id: 'pattern-anatomy', title: 'Pattern Anatomy', number: 3, description: 'Schema fields, 5-Key template, usage guidance diagram.', component: <PatternAnatomy /> },
  { slug: 'lifecycle', id: 'lifecycle', title: 'Lifecycle', number: 4, description: 'From need framing through monitoring & drift detection.', component: <Lifecycle /> },
  { slug: 'choosing-patterns', id: 'choosing-patterns', title: 'Choosing Patterns', number: 5, description: 'Heuristics for selecting candidate patterns.', component: <Choosing /> },
  { slug: 'combining-patterns', id: 'combining-patterns', title: 'Combining Patterns', number: 6, description: 'Safe compositional chaining strategies.', component: <Combining /> },
  { slug: 'adaptation', id: 'adaptation', title: 'Adaptation & Remix', number: 7, description: 'Principled iteration, versioning, ethical considerations.', component: <Adaptation /> },
  { slug: 'anti-patterns', id: 'anti-patterns', title: 'Anti-Patterns', number: 8, description: 'Common failure modes and refactoring cues.', component: <AntiPatterns /> },
  { slug: 'quality-evaluation', id: 'quality-evaluation', title: 'Quality & Evaluation', number: 9, description: 'Metrics, failure taxonomy, baselining discipline.', component: <Evaluation /> },
  { slug: 'similarity-preview', id: 'similarity-preview', title: 'Similarity Preview', number: 10, description: 'Teaser: sample similarity scores, evaluation/adaptation loop, optional static network graph.', component: <SimilarityPreview /> },
  { slug: 'accessibility-responsible-use', id: 'accessibility-responsible-use', title: 'Accessibility & Responsible Use', number: 11, description: 'Inclusive, transparent, and safe utilization guidelines.', component: <AccessibilityResponsible /> },
  { slug: 'glossary', id: 'glossary', title: 'Glossary', number: 12, description: 'Key terms and definitions.', component: <Glossary /> },
  { slug: 'faq', id: 'faq', title: 'FAQ', number: 13, description: 'Frequently asked clarifications.', component: <FAQ /> },
  { slug: 'feedback', id: 'feedback', title: 'Feedback', number: 14, description: 'How to contribute improvements and report issues.', component: <Feedback /> },
  { slug: 'next-steps', id: 'next-steps', title: 'Next Steps', number: 15, description: 'Where to go after orienting.', component: <NextSteps /> }
];
