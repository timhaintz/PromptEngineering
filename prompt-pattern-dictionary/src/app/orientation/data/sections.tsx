import React from 'react';
import Link from 'next/link';
import MermaidDiagram from '@/components/diagram/MermaidDiagram';
import { ClientDecisionTree } from '../components/ClientDecisionTree';
import CopyButton from '../components/CopyButton';

export interface OrientationSectionMeta {
  slug: string;
  id: string; // anchor id for combined page
  title: string;
  number: number;
  description: string;
  legacyAnchors?: string[]; // potential old ids
  component: React.ReactNode; // rendered body (without outer <section>)
}

interface GlossaryEntry {
  term: string;
  letter: string;
  definition: React.ReactNode;
}

interface LearningTrack {
  stage: string;
  outcome: string;
  focus: { label: string; href: string }[];
  checkpoint: string;
}

// Migrated components from legacy single-page Orientation (headings removed; page/all wrappers provide numbering headings).
// (Original QuickStart replaced below with concrete mini scenario + evaluation stub.)

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

const SIMILARITY_SCORE_LEGEND = [
  { range: '≥ 0.70', label: 'High structural overlap', guidance: 'Templates share most keys/constraints. Safe to A/B swap with minimal edits; validate metrics before production.' },
  { range: '0.50 – 0.69', label: 'Related variant', guidance: 'Same intent but different guardrails or personas. Borrow evaluation ideas and adaptation notes; do not paste Template verbatim.' },
  { range: '< 0.50', label: 'Exploratory only', guidance: 'Distant neighbor for inspiration and research browsing. Expect to re-author Template + metrics.' }
];

const SEARCH_SYNTAX_HINTS = [
  {
    control: 'Search text (default)',
    syntax: 'triage logs classification',
    details: 'Matches pattern name, description, category, tags, and first prompt examples. Combine domain + action words for best recall.'
  },
  {
    control: 'Boolean + Fuzzy toggle',
    syntax: 'reasoning AND ("policy review" OR triage) NOT translation · prompt~1',
    details: 'Enable the toggle to use AND / OR / NOT, phrase quotes, and fuzzy edit distance (slider 0–3). Use when you must include or exclude specific intents.'
  },
  {
    control: 'Search type dropdown',
    syntax: 'Type: Prompt Example',
    details: 'Switch between Prompt Pattern, Prompt Example, Category, or Logic searches. Example mode inspects the actual prompt body text.'
  },
  {
    control: 'Category selectors',
    syntax: 'Category type: Semantic AI → Filter by category: Evaluation & Scoring',
    details: 'Pivot between original research categories and semantic AI groupings; narrow results by a single category when browsing patterns/examples.'
  },
  {
    control: 'Logic filter (Category mode)',
    syntax: 'Search type: Category · Logic filter: Reasoning & Analysis',
    details: 'When viewing categories, filter to a logic family to explore adjacent pattern families without crafting textual queries.'
  },
  {
    control: 'Clear & reset',
    syntax: 'Pill: “Clear filters”',
    details: 'Use the pill in the control bar to drop accumulated filters before switching search types to avoid zero-result traps.'
  }
];

const SEARCH_STRATEGIES = [
  'Pair an intent verb with the artifact or domain (e.g., "rank" + "policy" or "summarize" + "transcript").',
  'If you remember a phrasing fragment, switch to Prompt Example mode and search the exact quote.',
  'Start broad, then layer category filters—overly specific compound queries often return nothing in sparse research domains.',
  'When Boolean filters are enabled, keep expressions short and lean on parentheses-free precedence: NOT > AND > OR.',
  'Use similarity chips on any matching pattern to pivot sideways once you have a promising baseline.',
  'Record interesting Pattern IDs immediately so you can compare or log adaptations later.'
];

const MANUAL_COMPARISON_STEPS = [
  'Open two candidate patterns (Ctrl/Cmd+Click Similar Patterns or use the comparison preview link) so each Template is visible side-by-side.',
  'Capture metadata: Pattern IDs, Knowledge Intent, category, and current version tags in your change log.',
  'Compare ROLE → RESPONSE keys line-by-line. Highlight any guardrail, schema, or persona differences that would impact evaluation.',
  'Review Application, Usage Summary, and AI-assisted notes to understand domain assumptions before borrowing text.',
  'Inspect Prompt Examples plus their Similar Example chips to see concrete structural differences or shared rationales.',
  'Summarize findings + next experiment in the Minimal Change Log snippet (pattern IDs, rationale, expected metric deltas).'
];

const FEATURE_FLAGS = [
  {
    env: 'NEXT_PUBLIC_SHOW_DECISION_TREE',
    surface: 'Choosing Patterns – Decision Tree widget',
    defaultState: 'Off (static heuristics only)',
    visibility: 'Set to “1” to render the interactive decision helper; when undefined the written heuristics remain.'
  },
  {
    env: 'NEXT_PUBLIC_SHOW_ORIENTATION_GRAPH',
    surface: 'Similarity Preview – static network teaser',
    defaultState: 'Off (graph hidden)',
    visibility: 'Set to “1” to expose the SVG teaser; default keeps load light on slower devices.'
  }
];

const GLOSSARY_ENTRIES: GlossaryEntry[] = [
  {
    term: 'Adaptation',
    letter: 'A',
    definition: (
      <>
        Domain-specific customization of a pattern while preserving the five-key Template labels. Track each change, cite the observed failure mode, and rerun evaluations (see{' '}
        <Link href="#adaptation" className="text-accent hover:underline">Adaptation & Remix</Link>).
      </>
    )
  },
  {
    term: 'Application',
    letter: 'A',
    definition: (
      <>
        Chips or prose describing where a pattern has been validated. They tether enrichment fields to research reality and appear in the{' '}
        <Link href="#pattern-anatomy" className="text-accent hover:underline">Pattern Anatomy</Link> layout.
      </>
    )
  },
  {
    term: 'Bias Mitigation',
    letter: 'B',
    definition: (
      <>
        The practice of inserting diverse examples, fairness assertions, and monitoring hooks so outputs perform evenly across cohorts. See the{' '}
        <Link href="#quality-evaluation" className="text-accent hover:underline">Quality & Evaluation</Link> section for taxonomy + metrics.
      </>
    )
  },
  {
    term: 'Bracketed Synthesis',
    letter: 'B',
    definition: (
      <>
        Optional single-line recap of ROLE → ACTION → FORMAT guardrails (e.g.,{' '}
        <code className="text-[11px]">[Rank proposals | output JSON | reject missing rollout notes]</code>). Must mirror the full Template—edit both together via{' '}
        <Link href="#pattern-anatomy" className="text-accent hover:underline">Pattern Anatomy</Link> guardrails.
      </>
    )
  },
  {
    term: 'Dual-Use Pattern',
    letter: 'D',
    definition: (
      <>
        A prompt structure that can help both defensive and potentially harmful tasks. Orientation labels these in{' '}
        <Link href="#accessibility-responsible-use" className="text-accent hover:underline">Accessibility & Responsible Use</Link> and pairs them with mitigation tips before adaptation.
      </>
    )
  },
  {
    term: 'Enrichment',
    letter: 'E',
    definition: (
      <>
        AI-assisted augmentation pipeline that fills General Explanation, Usage Summary, Knowledge Intent, Domain examples, and PEIL fields in{' '}
        <code className="text-[11px]">public/data/normalized-patterns.json</code>. Every enrichment run logs the assisting model + timestamp (see <code className="text-[11px]">aiAssisted*</code> fields) and respects the source Template.
      </>
    )
  },
  {
    term: 'Knowledge Intent',
    letter: 'K',
    definition: (
      <>
        Quadrant describing knowledge flow: Refinement & Clarification, Knowledge Retrieval, Co-Discovery & Exploration, or AI Tutoring & Tuning. It informs Quick Paths and{' '}
        <Link href="#search-similarity" className="text-accent hover:underline">Search & Similarity</Link> guidance when deciding which pattern to trust.
      </>
    )
  },
  {
    term: 'Pattern',
    letter: 'P',
    definition: (
      <>
        Named, reusable design for prompting a model with predictable behavior. It couples intent, structural scaffolding, and evaluation hooks—see{' '}
        <Link href="#what-is-a-pattern" className="text-accent hover:underline">What Is a Pattern</Link> for the narrative definition.
      </>
    )
  },
  {
    term: 'PEIL (Prompt Engineering Instructional Language)',
    letter: 'P',
    definition: (
      <>
        Structured system prompt derived from the authoritative Template + Application pairing. PEIL wraps, but never rewrites, research text so orchestration tooling can ingest it safely. Examples live in{' '}
        <Link href="#pattern-anatomy" className="text-accent hover:underline">Pattern Anatomy</Link>.
      </>
    )
  },
  {
    term: 'Provenance Badge',
    letter: 'P',
    definition: (
      <>
        Visual indicator marking AI-assisted fields across Orientation and pattern pages. The badge links to an explanation of enrichment scope plus review expectations in{' '}
        <Link href="#accessibility-responsible-use" className="text-accent hover:underline">Accessibility & Responsible Use</Link>.
      </>
    )
  },
  {
    term: 'Similarity',
    letter: 'S',
    definition: (
      <>
        Cosine similarity over embeddings built from pattern names, descriptions, and leading examples. Use it for exploratory navigation (see{' '}
        <Link href="#search-similarity" className="text-accent hover:underline">Search & Similarity UX</Link>)—evaluation still relies on metrics.
      </>
    )
  },
  {
    term: 'Template (5-Key)',
    letter: 'T',
    definition: (
      <>
        Canonical scaffold: ROLE, CONTEXT, ACTION, FORMAT, RESPONSE. It is the audit surface for every change request; details live in{' '}
        <Link href="#pattern-anatomy" className="text-accent hover:underline">Pattern Anatomy</Link>.
      </>
    )
  },
  {
    term: 'Usage Summary',
    letter: 'U',
    definition: (
      <>
        Pragmatic “how to run it” note derived during enrichment. It complements the Description (research voice) and General Explanation (teaching voice). Cross-reference{' '}
        <Link href="#pattern-anatomy" className="text-accent hover:underline">Pattern Anatomy</Link> to see how the fields align.
      </>
    )
  }
];

const LEARNING_TRACKS: LearningTrack[] = [
  {
    stage: '1. Foundations',
    outcome: 'Understand what prompt patterns are and why the 5-Key scaffold matters.',
    focus: [
      { label: 'Quick Start', href: '/orientation/quick-start' },
      { label: 'What Is a Pattern', href: '/orientation/what-is-a-pattern' },
      { label: 'Pattern Anatomy', href: '/orientation/pattern-anatomy' }
    ],
    checkpoint: 'You can describe the difference between Description, General Explanation, Usage Summary, Template, Knowledge Intent, and PEIL.'
  },
  {
    stage: '2. Structural Mastery',
    outcome: 'Practice selecting and chaining patterns while avoiding anti-patterns.',
    focus: [
      { label: 'Lifecycle', href: '/orientation/lifecycle' },
      { label: 'Choosing Patterns', href: '/orientation/choosing-patterns' },
      { label: 'Combining Patterns', href: '/orientation/combining-patterns' },
      { label: 'Anti-Patterns', href: '/orientation/anti-patterns' }
    ],
    checkpoint: 'You maintain a change log per adaptation and can articulate why each structural adjustment was made.'
  },
  {
    stage: '3. Evaluation & Adaptation',
    outcome: 'Align evaluation harnesses with failure modes before publishing updates.',
    focus: [
      { label: 'Adaptation & Remix', href: '/orientation/adaptation' },
      { label: 'Quality & Evaluation', href: '/orientation/quality-evaluation' }
    ],
    checkpoint: 'You have a repeatable harness, metric targets, and drift monitoring for the pattern you’re iterating.'
  },
  {
    stage: '4. Discovery & Similarity',
    outcome: 'Use search syntax and similarity pivots to find adjacent research before inventing from scratch.',
    focus: [
      { label: 'Search & Similarity UX', href: '/orientation/search-similarity' },
      { label: 'Similarity Preview', href: '/orientation/similarity-preview' }
    ],
    checkpoint: 'You can defend why a candidate pattern was chosen and cite the similarity legend bands that informed the decision.'
  },
  {
    stage: '5. Responsible Scaling',
    outcome: 'Bake accessibility, provenance, and responsible use signals into rollouts.',
    focus: [
      { label: 'Accessibility & Responsible Use', href: '/orientation/accessibility-responsible-use' },
      { label: 'Glossary', href: '/orientation/glossary' },
      { label: 'Learning Path & Roadmap', href: '/orientation/learning-path' }
    ],
    checkpoint: 'You can point to accessibility test evidence and the most recent contrast audit before shipping.'
  }
];

const PATTERN_SUBMISSION_PLACEHOLDER = `## Pattern Submission
labels: orientation-feedback, education

pattern_id: TBD
pattern_title:
source_paper:
summary: <!-- 2-3 sentences -->
why_it_matters:
evidence: <!-- link to research or evaluation logs -->
requested_actions:
`;

const CONTRIBUTION_NOTE_PLACEHOLDER = `## Orientation Contribution
section:
observed_gap:
label: orientation-feedback | a11y-regression | education
details:
link_or_attachment:
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
          <ClientDecisionTree />
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
        <CopyButton 
          text={CHANGE_LOG_SNIPPET}
          liveRegionId="change-log-live"
          ariaLabel="Copy change log snippet"
          className="absolute top-2 right-2 text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
        />
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
            <CopyButton 
              text={PY_EVAL_HARNESS_CODE}
              liveRegionId="eval-harness-py-live"
              ariaLabel="Copy Python harness"
              className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            />
          </div>
          <pre id="eval-harness-py" className="overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{PY_EVAL_HARNESS_CODE}</code></pre>
          <div id="eval-harness-py-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
        </div>
        <div className="p-3 rounded border border-muted bg-surface-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">JavaScript · Jest</span>
            <CopyButton 
              text={JS_EVAL_HARNESS_CODE}
              liveRegionId="eval-harness-js-live"
              ariaLabel="Copy JavaScript harness"
              className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            />
          </div>
          <pre id="eval-harness-js" className="overflow-auto text-xs bg-surface-2 p-3 rounded border border-muted"><code>{JS_EVAL_HARNESS_CODE}</code></pre>
          <div id="eval-harness-js-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
        </div>
      </div>
      <p className="text-xs text-muted mt-2">Automation tip: run schema validation before expensive scoring, then log pass/fail + metric deltas alongside the change log snippet.</p>
    </div>
  </div>
);

const SearchSimilarityGuidance = () => (
  <div className="space-y-6 text-sm">
    <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">Search syntax mini-guide</h3>
        <Link href="/search" className="text-xs text-accent hover:underline">Open search</Link>
      </div>
      <table className="text-xs w-full border mt-3">
        <thead>
          <tr className="bg-surface-2 text-secondary">
            <th className="p-2 text-left font-semibold">Control</th>
            <th className="p-2 text-left font-semibold">Syntax / Example</th>
            <th className="p-2 text-left font-semibold">What it does</th>
          </tr>
        </thead>
        <tbody>
          {SEARCH_SYNTAX_HINTS.map(hint => (
            <tr key={hint.control} className="border-t align-top">
              <td className="p-2 font-medium">{hint.control}</td>
              <td className="p-2 whitespace-pre-line">{hint.syntax}</td>
              <td className="p-2">{hint.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-secondary mt-2">The Boolean helper drawer on the search page repeats these rules with operator precedence reminders.</p>
    </div>

    <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <h3 className="text-sm font-semibold mb-2">Best-effort query plays</h3>
      <ul className="list-disc pl-5 space-y-1 text-sm">
        {SEARCH_STRATEGIES.map(strategy => (
          <li key={strategy}>{strategy}</li>
        ))}
      </ul>
      <p className="text-xs text-secondary mt-2">If a query returns zero results, clear filters, drop adjectives, and try a different search type before assuming the pattern is missing.</p>
    </div>

    <div className="grid gap-4 md:grid-cols-2">
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-2">Similarity score legend</h3>
        <table className="text-xs w-full border">
          <thead>
            <tr className="bg-surface-2 text-secondary">
              <th className="p-2 text-left font-semibold">Score Band</th>
              <th className="p-2 text-left font-semibold">Meaning</th>
            </tr>
          </thead>
          <tbody>
            {SIMILARITY_SCORE_LEGEND.map(row => (
              <tr key={row.range} className="border-t">
                <td className="p-2 font-medium">{row.range}</td>
                <td className="p-2">{row.label}<span className="block text-xs text-secondary">{row.guidance}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="text-xs text-secondary mt-2">Scores rely on cached embeddings (pattern name + description + first three examples). Treat them as discovery signals, not discrete evaluation metrics.</p>
        <div className="mt-3 p-3 rounded border border-dashed border-muted bg-surface-2 text-xs text-secondary">
          <p className="font-semibold text-primary mb-1">Preview-only expectation</p>
          <p>Orientation previews and the <Link href="/comparison" className="text-accent underline">comparison</Link> route currently use precomputed similarity tables. Live ad-hoc embedding generation, exports, and multi-pattern matrices are on the roadmap—until they ship, leverage the manual workflow below and your evaluation harness.</p>
        </div>
      </div>

      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-semibold">Manual comparison workflow</h3>
          <CopyButton 
            text={CHANGE_LOG_SNIPPET}
            liveRegionId="change-log-live"
            className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            Copy change-log template
          </CopyButton>
        </div>
        <ol className="list-decimal pl-5 space-y-1 text-sm mt-2">
          {MANUAL_COMPARISON_STEPS.map(step => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <p className="text-xs text-secondary mt-2">Use the change log snippet (see Adaptation section) to capture what you compared, which metrics moved, and any drift hypotheses. Attach screenshot diffs or evaluation outputs when possible.</p>
      </div>
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
    <div className="p-4 rounded border border-dashed border-muted bg-surface-1 shadow-sm">
      <h4 className="text-sm font-semibold mb-1">Contrast audit snapshot (Nov 2025)</h4>
      <p className="text-xs text-secondary">Automated checks via <code className="text-[11px]">scripts/contrast_audit.js</code> confirmed <strong>text-primary vs surface-1</strong> at 19.95:1 and all sampled pairs ≥14:1 across Light, Dark, and High-Contrast modes. See <Link href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/prompt-pattern-dictionary/docs/ACCESSIBILITY.md" className="text-accent hover:underline" target="_blank" rel="noreferrer">ACCESSIBILITY.md</Link> for the full matrix.</p>
    </div>
    <details className="group border border-muted rounded-md p-3 bg-surface-1">
      <summary className="cursor-pointer font-semibold text-accent">Assistive technology walkthrough</summary>
      <ol className="list-decimal pl-5 space-y-1 mt-3 text-sm">
        <li>Use the <strong>Skip to Section Navigation</strong> link to bypass the hero, then land on the inline nav.</li>
        <li>Jump to the desired section via heading navigation; each section title includes the number so screen reader rotor shortcuts remain predictable.</li>
        <li>Copy snippets (evaluation harness, change log, contribution templates) using the labeled buttons—each announces success via an <code className="text-[11px]">aria-live</code> region.</li>
        <li>Explore Glossary anchors with the A–Z jump bar; focus order matches alphabetical order so you always know where you are.</li>
        <li>Use the Feedback CTA buttons (below every section) to open GitHub in a new tab without losing Orientation context.</li>
      </ol>
      <p className="text-xs text-secondary mt-2">If you rely on additional assistive tech workflows, tag your issue with <code className="text-[11px]">education</code> so we can document new best practices.</p>
    </details>
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

const AboutDictionary = () => (
  <div className="space-y-8 text-sm leading-relaxed">
    <section>
      <h2 className="text-lg font-semibold text-primary mb-3">Ballarat AI Prompt Dictionary: What, Why & How</h2>
      <p className="mb-4">
        The Ballarat AI Prompt Dictionary is an <a href="https://github.com/timhaintz/PromptEngineering" target="_blank" rel="noreferrer" className="text-accent hover:underline">open-source research platform and search tool</a> that compiles hundreds of proven prompt patterns from academic work. The webpage itself is hosted in the <a href="https://github.com/timhaintz/PromptEngineering/tree/main/prompt-pattern-dictionary" target="_blank" rel="noreferrer" className="text-accent hover:underline">prompt-pattern-dictionary</a> directory of the repository. A prompt pattern is a reusable, named template for interacting with large language models (LLMs). Each pattern defines a five-part “5-Key” scaffold—Role, Context, Action, Format and Response—to capture intent, provide structural guidance and adaptation advice, and maximise predictability, reproducibility and auditability. By standardising these key elements, the dictionary makes it possible to compare prompts systematically, reduce ambiguity and drift, and monitor for bias or harmful behaviours.
      </p>
      <p>
        You can start by clearly stating your task—for example, “Rank policy risks” or “Compare legal clauses”—and then browse or search the library by theme. The logic layers and categories help you navigate: for instance, “Beyond” logic covers prompts that push the AI’s capabilities, while the Hypothesise category within “Beyond” focuses on generative speculation. Each individual pattern page expands to show a concise description, a general explanation, a usage summary, a detailed 5-Key template (with variables to fill), example prompts and a list of similar patterns.
      </p>
    </section>

    <section>
      <h2 className="text-lg font-semibold text-primary mb-3">Logic Layers and Categories</h2>
      <p className="mb-4">
        A key insight from the underlying research is that English prepositions provide a natural metaphor for structuring the universe of prompt tasks. The dictionary’s six logic layers are inspired by prepositions—Across, At, Beyond, In, Out and Over—each describing a different behavioural relationship between the prompt and the LLM:
      </p>
      <ul className="list-disc pl-5 space-y-2 mb-4">
        <li><strong>Across Logic</strong> spans multiple domains or disciplines, integrating diverse knowledge.</li>
        <li><strong>At Logic</strong> targets a specific scenario or context.</li>
        <li><strong>Beyond Logic</strong> explores new capabilities, innovating beyond standard tasks.</li>
        <li><strong>In Logic</strong> focuses on introspective or self-reflective tasks.</li>
        <li><strong>Out Logic</strong> covers prompts for generating outputs such as code or creative text.</li>
        <li><strong>Over Logic</strong> supports comprehensive coverage, summarisation and synthesis.</li>
      </ul>
      <p>
        Within these layers, the library organises patterns into twenty-five categories (with acronyms like ARG for Argument, CAL for Calculation, HYP for Hypothesise, etc.), each capturing a particular task archetype. For example, the categories “Assessment”, “Calculation” and “Logical Reasoning” reside in the At and Beyond logic layers, while “Summarising” and “Synthesis” live in the Over layer. This dual taxonomy—logic layer plus category—acts as a mental map, aligning with research that uses prepositional logic and task typology to organise human-AI conversation patterns.
      </p>
    </section>

    <section>
      <h2 className="text-lg font-semibold text-primary mb-3">Prompt Engineering Instructional Language (PEIL)</h2>
      <p className="mb-4">
        Building on the five-key schema and informed by prompt engineering research, the dictionary introduces the Prompt Engineering Instructional Language (PEIL). PEIL is an instructional scaffold that helps automate the creation of robust system prompts. You can use the <a href="https://github.com/timhaintz/PromptEngineering/blob/main/peil_prompt_generator.py" target="_blank" rel="noreferrer" className="text-accent hover:underline">PEIL Prompt Generator</a> to automate this process. It decomposes a prompt specification into a set of variables—Role, Provide Clear Context, Break Down Complex Questions, Provide Specific Instructions, Define Conciseness, Research-Based Prompting Techniques (e.g. Chain-of-Thought, Few-Shot etc.), and State Desired Output—which are combined to produce a final system prompt. Each of these variables corresponds to an element of the underlying 5-Key structure and codifies best practices found in prompt engineering literature. For instance:
      </p>
      <ul className="list-disc pl-5 space-y-2 mb-4">
        <li><strong>Role</strong> defines the persona or expertise the model should assume (e.g., “You are a cybersecurity expert”).</li>
        <li><strong>Provide Clear Context</strong> sets the domain and focus, grounding the model’s responses.</li>
        <li><strong>Break Down Complex Questions</strong> decomposes broad tasks into smaller, explicit sub-questions, fostering step-by-step reasoning (a core technique like Chain-of-Thought).</li>
        <li><strong>Provide Specific Instructions</strong> delineates essential requirements, constraints or mandatory inclusions.</li>
        <li><strong>Define Conciseness</strong> sets word or token limits to control verbosity.</li>
        <li><strong>Research-Based Techniques</strong> invites the inclusion of methods from scholarly work on prompting, such as instruction-prompt hybrids combining a guiding sentence with bullet-point rules—an approach supported by studies advocating hybrid prompt structures.</li>
        <li><strong>State Desired Output</strong> specifies the target format, scope and expected information in the response.</li>
      </ul>
      <p>
        PEIL thus provides a structured, research-informed framework for designing prompts that are clear, concise and conducive to reliable AI responses. It highlights the synergy between theoretical insights (like the 5-Key scaffold and prepositional logic layers) and practical prompting techniques from recent research, supporting both novice and advanced users in crafting instructive prompts that align with best practices.
      </p>
    </section>
  </div>
);

// Glossary (restored after patch collision)
const Glossary = () => {
  const letters = Array.from(new Set(GLOSSARY_ENTRIES.map(entry => entry.letter)));
  let lastLetter = '';
  return (
    <div>
      <nav aria-label="Glossary index" className="mb-3 flex flex-wrap gap-1 text-[11px]">
        {letters.map(letter => (
          <a key={letter} href={`#term-${letter}`} className="px-1.5 py-0.5 rounded bg-surface-2 border border-muted hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" aria-label={`Jump to terms starting with ${letter}`}>{letter}</a>
        ))}
      </nav>
      <dl className="space-y-3 text-sm">
        {GLOSSARY_ENTRIES.map(entry => {
          const letterChanged = entry.letter !== lastLetter;
          lastLetter = entry.letter;
          return (
            <div key={entry.term}>
              {letterChanged && <div id={`term-${entry.letter}`} aria-hidden="true"></div>}
              <dt className="font-medium">{entry.term}</dt>
              <dd className="text-sm text-secondary">{entry.definition}</dd>
            </div>
          );
        })}
      </dl>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm">
          <h3 className="text-sm font-semibold mb-2">Data cadence & embedding transparency</h3>
          <p className="text-sm mb-2">Research data lives in <code className="text-[11px]">public/data/normalized-patterns.json</code> with supporting stats inside <code className="text-[11px]">public/data/stats.json</code>. We expose the same metadata in Orientation so users know when artifacts last refreshed.</p>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            <li><strong>Weekly ingest (or within 72h of a paper update):</strong> running the normalization pipeline rewrites <code className="text-[11px]">normalized-patterns.json</code> plus the provenance fields that show up in Pattern pages.</li>
            <li><strong>Embedding refresh policy:</strong> similarity vectors (<code className="text-[11px]">similar-patterns.json</code> + <code className="text-[11px]">similar-examples.json</code>) regenerate at least monthly or whenever ≥10 patterns/examples change so Search & Comparison stay aligned.</li>
            <li><strong>Transparency surfaces:</strong> the Orientation hub cites <code className="text-[11px]">stats.json.lastProcessed</code> and <code className="text-[11px]">aiAssistedAt</code> timestamps so readers can confirm freshness before trusting enrichment or similarity hints.</li>
          </ul>
          <p className="text-xs text-secondary mt-2">If you notice stale data, open an issue referencing the last processed timestamp and affected pattern IDs.</p>
        </div>
        <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm text-sm overflow-x-auto">
          <h3 className="text-sm font-semibold mb-2">Feature-flag visibility</h3>
          <table className="text-xs w-full border">
            <thead>
              <tr className="bg-surface-2 text-secondary">
                <th className="p-2 text-left font-semibold">Env flag</th>
                <th className="p-2 text-left font-semibold">Surface</th>
                <th className="p-2 text-left font-semibold">Default / visibility</th>
              </tr>
            </thead>
            <tbody>
              {FEATURE_FLAGS.map(flag => (
                <tr key={flag.env} className="border-t align-top">
                  <td className="p-2 font-mono text-[11px]">{flag.env}</td>
                  <td className="p-2">{flag.surface}</td>
                  <td className="p-2 text-xs">
                    <span className="block font-semibold">Default: {flag.defaultState}</span>
                    <span className="text-secondary">{flag.visibility}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-secondary mt-2">Flags are client-visible (prefixed with <code className="text-[11px]">NEXT_PUBLIC_</code>) so you can audit which exploratory widgets are being shown in any given deployment.</p>
        </div>
      </div>
    </div>
  );
};

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
  <div className="space-y-5 text-sm">
    <p className="text-secondary">Spotted ambiguity, accessibility gaps, missing inclusive examples, or structural drift? Please open an issue or PR. Reference the pattern ID(s), describe the observed issue, and include a minimal reproducible example when possible.</p>
    <div className="grid gap-4 md:grid-cols-3">
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-1">Label cheat sheet</h3>
        <ul className="text-xs space-y-1">
          <li><code className="text-[11px]">orientation-feedback</code>: general suggestions, roadmap alignment, clarity requests.</li>
          <li><code className="text-[11px]">a11y-regression</code>: contrast failures, missing labels, keyboard traps.</li>
          <li><code className="text-[11px]">education</code>: requests for examples, tutorials, or AT walkthroughs.</li>
        </ul>
        <p className="text-xs text-secondary mt-2">Add multiple labels if an issue spans categories.</p>
      </div>
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-1">Feedback entry points</h3>
        <ul className="list-disc pl-4 space-y-1">
          <li><a href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=orientation-feedback" target="_blank" rel="noreferrer" className="text-accent hover:underline">Orientation feedback issue</a></li>
          <li><a href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=a11y-regression" target="_blank" rel="noreferrer" className="text-accent hover:underline">Accessibility regression report</a></li>
          <li><a href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=education" target="_blank" rel="noreferrer" className="text-accent hover:underline">Education/resource request</a></li>
        </ul>
        <p className="text-xs text-secondary mt-2">Need to submit privately? Email listed in <Link href="/orientation/accessibility-responsible-use" className="text-accent hover:underline">Responsible Use</Link>.</p>
      </div>
      <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-1">Pattern / submission placeholders</h3>
        <p className="text-xs text-secondary">Use the templates below to keep proposals consistent—paste them directly into GitHub issues.</p>
      </div>
    </div>
    <div className="grid gap-4 md:grid-cols-2">
      <div className="p-3 rounded border border-muted bg-surface-2 relative">
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-sm">Pattern submission outline</span>
          <CopyButton
            text={PATTERN_SUBMISSION_PLACEHOLDER}
            liveRegionId="pattern-submission-live"
            ariaLabel="Copy pattern submission placeholder"
            className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-1 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          />
        </div>
        <pre id="pattern-submission-placeholder" className="overflow-auto text-xs"><code>{PATTERN_SUBMISSION_PLACEHOLDER}</code></pre>
        <div id="pattern-submission-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
      </div>
      <div className="p-3 rounded border border-muted bg-surface-2 relative">
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-sm">Orientation contribution note</span>
          <CopyButton
            text={CONTRIBUTION_NOTE_PLACEHOLDER}
            liveRegionId="orientation-contribution-live"
            ariaLabel="Copy contribution placeholder"
            className="text-[10px] px-2 py-1 rounded border border-muted bg-surface-1 hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          />
        </div>
        <pre id="orientation-contribution-placeholder" className="overflow-auto text-xs"><code>{CONTRIBUTION_NOTE_PLACEHOLDER}</code></pre>
        <div id="orientation-contribution-live" className="mt-1 text-xs text-secondary" aria-live="polite"></div>
      </div>
    </div>
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

const LearningPath = () => (
  <div className="space-y-6 text-sm">
    <p>Move through Orientation deliberately instead of skimming every section in one sitting. The roadmap below mirrors the Phase 6 plan in our <a className="text-accent hover:underline" href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/prompt-pattern-dictionary/docs/PRD.md#phase-6-orientation-enhancements--onboarding-expansion" target="_blank" rel="noreferrer">living PRD</a>.</p>
    <div className="grid gap-4 md:grid-cols-2">
      {LEARNING_TRACKS.map(track => (
        <div key={track.stage} className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-secondary mb-1">{track.stage}</p>
          <p className="font-semibold text-primary mb-2">{track.outcome}</p>
          <div className="space-y-1">
            <p className="text-xs text-secondary">Focus:</p>
            <ul className="list-disc pl-4 space-y-1">
              {track.focus.map(item => (
                <li key={`${track.stage}-${item.href}`}><Link href={item.href} className="text-accent hover:underline">{item.label}</Link></li>
              ))}
            </ul>
          </div>
          <p className="mt-3 text-xs text-secondary"><strong>Checkpoint:</strong> {track.checkpoint}</p>
        </div>
      ))}
    </div>
    <div className="p-4 rounded border border-dashed border-muted bg-surface-2 shadow-sm">
      <h3 className="text-sm font-semibold mb-1">AI-assisted correction path & telemetry readiness</h3>
      <p className="mb-2">If an AI-assisted field (General Explanation, Usage Summary, PEIL, Knowledge Intent) looks incorrect, file an issue with the <code className="text-[11px]">ai-assist-correction</code> label so we can trace the enrichment run and update the source JSON. Planned telemetry events (<code className="text-[11px]">orientation_quick_path_click</code>, <code className="text-[11px]">evaluation_copy_action</code>, <code className="text-[11px]">glossary_search</code>) are documented in <a className="text-accent hover:underline" href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/prompt-pattern-dictionary/docs/telemetry.md" target="_blank" rel="noreferrer">docs/telemetry.md</a> and can be wired into a backend once we migrate off static hosting.</p>
      <div className="flex flex-wrap gap-2">
        <a href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=ai-assist-correction" target="_blank" rel="noreferrer" className="inline-flex items-center justify-center px-3 py-1.5 rounded border border-muted bg-surface-1 text-xs font-semibold text-primary hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent">Open correction issue</a>
        <a href="https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=orientation-feedback" target="_blank" rel="noreferrer" className="inline-flex items-center justify-center px-3 py-1.5 rounded border border-muted bg-surface-1 text-xs font-semibold text-primary hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent">Share roadmap feedback</a>
      </div>
      <p className="text-xs text-secondary mt-2">Prefer to just follow along? Watch the Phase 6 roadmap section in the PRD—every accepted sub-phase is timestamped so you can see when guidance last evolved.</p>
    </div>
  </div>
);

const OrientationHubSection = () => (
  <div className="space-y-4">
    <p className="text-sm">The Orientation Hub serves as the central navigation point for all orientation materials. It provides a role-based guide to help you find the most relevant sections for your needs.</p>
    <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
      <h3 className="text-sm font-semibold mb-2">Hub Highlights</h3>
      <ul className="list-disc pl-5 space-y-1 text-sm">
        <li><strong>Role → Intent Map:</strong> Find guidance tailored to Researchers, Practitioners, Students, or Tool Builders.</li>
        <li><strong>Quick Paths:</strong> Jump straight to key resources like the Evaluation Harness or Pattern Anatomy.</li>
        <li><strong>Consolidated View:</strong> Access the &quot;All Sections&quot; page for a single-page reading experience.</li>
      </ul>
      <div className="mt-4">
        <Link href="/orientation/hub" className="text-accent text-sm font-medium hover:underline">Go to Orientation Hub →</Link>
      </div>
    </div>
  </div>
);

export const ORIENTATION_SECTIONS: OrientationSectionMeta[] = [
  { slug: 'about', id: 'about', title: 'About the Dictionary', number: 1, description: 'What, Why & How of the Ballarat AI Prompt Dictionary.', component: <AboutDictionary /> },
  { slug: 'hub', id: 'hub', title: 'Orientation Hub', number: 2, description: 'Central navigation hub with role-based guides and quick paths.', component: <OrientationHubSection /> },
  { slug: 'quick-start', id: 'quick-start', title: 'Quick Start', number: 3, description: 'Practical 8-step startup path for using patterns safely.', component: <QuickStart /> },
  { slug: 'what-is-a-pattern', id: 'what-is-a-pattern', title: 'What Is a Pattern', number: 4, description: 'Definition, value, and collaboration benefits.', component: <WhatIsPattern /> },
  { slug: 'pattern-anatomy', id: 'pattern-anatomy', title: 'Pattern Anatomy', number: 5, description: 'Schema fields, 5-Key template, usage guidance diagram.', component: <PatternAnatomy /> },
  { slug: 'lifecycle', id: 'lifecycle', title: 'Lifecycle', number: 6, description: 'From need framing through monitoring & drift detection.', component: <Lifecycle /> },
  { slug: 'choosing-patterns', id: 'choosing-patterns', title: 'Choosing Patterns', number: 7, description: 'Heuristics for selecting candidate patterns.', component: <Choosing /> },
  { slug: 'combining-patterns', id: 'combining-patterns', title: 'Combining Patterns', number: 8, description: 'Safe compositional chaining strategies.', component: <Combining /> },
  { slug: 'adaptation', id: 'adaptation', title: 'Adaptation & Remix', number: 9, description: 'Principled iteration, versioning, ethical considerations.', component: <Adaptation /> },
  { slug: 'anti-patterns', id: 'anti-patterns', title: 'Anti-Patterns', number: 10, description: 'Common failure modes and refactoring cues.', component: <AntiPatterns /> },
  { slug: 'quality-evaluation', id: 'quality-evaluation', title: 'Quality & Evaluation', number: 11, description: 'Metrics, failure taxonomy, baselining discipline.', component: <Evaluation /> },
  { slug: 'search-similarity', id: 'search-similarity', title: 'Search & Similarity UX', number: 12, description: 'Search syntax, similarity legend, and manual comparison workflow.', component: <SearchSimilarityGuidance /> },
  { slug: 'similarity-preview', id: 'similarity-preview', title: 'Similarity Preview', number: 13, description: 'Teaser: sample similarity scores, evaluation/adaptation loop, optional static network graph.', component: <SimilarityPreview /> },
  { slug: 'accessibility-responsible-use', id: 'accessibility-responsible-use', title: 'Accessibility & Responsible Use', number: 14, description: 'Inclusive, transparent, and safe utilization guidelines.', component: <AccessibilityResponsible /> },
  { slug: 'glossary', id: 'glossary', title: 'Glossary', number: 15, description: 'Key terms and definitions.', component: <Glossary /> },
  { slug: 'faq', id: 'faq', title: 'FAQ', number: 16, description: 'Frequently asked clarifications.', component: <FAQ /> },
  { slug: 'feedback', id: 'feedback', title: 'Feedback', number: 17, description: 'How to contribute improvements and report issues.', component: <Feedback /> },
  { slug: 'next-steps', id: 'next-steps', title: 'Next Steps', number: 18, description: 'Where to go after orienting.', component: <NextSteps /> },
  { slug: 'learning-path', id: 'learning-path', title: 'Learning Path & Roadmap', number: 19, description: 'Staged journey plus AI-assisted correction and telemetry notes.', component: <LearningPath /> }
];
