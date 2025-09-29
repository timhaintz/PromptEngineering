import React from 'react';
import Link from 'next/link';
import MermaidDiagram from '@/components/diagram/MermaidDiagram';

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
const QuickStart = () => (
  <div>
    <ol className="list-decimal pl-6 space-y-1">
      <li><strong>State your task</strong>: e.g., “Extract product defects”, “Compare legal clauses”, “Score sentiment”.</li>
      <li><strong>Filter / scan relevant categories</strong>: Use category pages or search. Similarity suggestions can broaden the candidate list.</li>
      <li><strong>Open 1–2 candidate patterns</strong> and expand the Template (keep its structural keys intact).</li>
      <li><strong>Insert your domain variables</strong> (use explicit placeholders like <code>{'{{TEXT_BLOCK}}'}</code>).</li>
      <li><strong>Run on a tiny evaluation set</strong> (3–5 representative examples) before large scale use.</li>
      <li><strong>Record baseline metrics</strong> (accuracy, coverage, failure modes) – write them down.</li>
      <li><strong>Iterate structurally first</strong> (reorder, clarify intent) before stylistic tuning.</li>
      <li><strong>Lock and label version</strong> when stable; avoid silent drift.</li>
    </ol>
  <div className="mt-4 p-3 rounded border border-muted bg-surface-1 shadow-sm text-sm text-secondary">
      <p className="font-semibold mb-1">Principles:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li><strong>Clarity over cleverness</strong> – explicit instructions reduce hallucination risk.</li>
        <li><strong>Single responsibility</strong> – one pattern, one job; chain instead of overloading.</li>
        <li><strong>Measured change</strong> – modify one aspect at a time; re‑test.</li>
        <li><strong>Inclusive data</strong> – test with varied names, dialects, and contexts.</li>
        <li><strong>Document provenance</strong> – note if AI assisted any field.</li>
      </ul>
    </div>
  </div>
);

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
    <p>Each entry follows a consistent schema to support scanning and comparison. The Template exposes five canonical keys (<code>role</code>, <code>context</code>, <code>action</code>, <code>format</code>, <code>response</code>) plus an optional single‑line <em>bracketed synthesis</em>. Additional normalized attributes provide discoverability, provenance, and evaluation hooks.</p>
    <div className="mt-4 grid gap-4 md:grid-cols-2">
  <div className="p-4 rounded border border-muted bg-surface-1 shadow-sm">
        <h3 className="text-sm font-semibold mb-2">Field Overview</h3>
        <dl className="text-sm space-y-2">
          <div>
            <dt className="font-medium">Pattern Name</dt>
            <dd>Human-readable identifier of the design strategy.</dd>
          </div>
          <div>
            <dt className="font-medium">Description</dt>
            <dd>Short narrative explaining purpose & scope.</dd>
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
            <dd>Tags or scenario phrases describing contexts of use.</dd>
          </div>
          <div>
            <dt className="font-medium">Usage Summary</dt>
            <dd>Plain-language “how to apply” guidance (may be AI-assisted).</dd>
          </div>
          <div>
            <dt className="font-medium">Turn</dt>
            <dd>Indicates if pattern expects multi-turn setup.</dd>
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
        </ul>
      </div>
    </div>
    <div className="my-6 p-4 rounded-lg bg-surface-1 border border-muted shadow-sm">
      <p className="text-sm font-semibold text-accent mb-2">Structure Diagram</p>
      <div id="diagram-desc" className="sr-only">Diagram showing relationships: Pattern Name connects to Intent/Purpose, Template (with five keys and bracketed summary), Application, Examples & Similar, Adaptation Notes, Evaluation/Quality Hints, and Tags/Category.</div>
      <MermaidDiagram
        describedById="diagram-desc"
        className="mermaid"
        chart={`flowchart LR\n    A[Pattern Name]:::title --> B[Intent / Purpose]\n    B --> C[Template (5 keys)]\n    C --> C1[role]\n    C --> C2[context]\n    C --> C3[action]\n    C --> C4[format]\n    C --> C5[response]\n    C --> C6[Bracketed Summary]\n    A --> D[Application]\n    A --> E[Examples & Similar]\n    A --> F[Adaptation Notes]\n    A --> G[Evaluation / Quality Hints]\n    A --> H[Tags / Category]\n\n    classDef title fill:#1e3a8a,stroke:#1e3a8a,stroke-width:1,color:#fff;\n    classDef keys fill:#eef2ff,stroke:#4338ca,color:#1e1b4b;\n    class C,C1,C2,C3,C4,C5,C6 keys;`}
      />
  <p className="mt-2 text-xs text-muted">Rendered client-side with Mermaid; accessible fallback includes textual description.</p>
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

const Choosing = () => (
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
  </div>
);

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
    </ul>
  <p className="mt-3 text-xs text-muted">If a pattern diverges heavily, consider naming it explicitly (fork) to preserve lineage.</p>
  </div>
);

const AntiPatterns = () => (
  <div>
    <ul className="list-disc pl-5 space-y-1 text-sm">
      <li><strong>Overloaded Mega-Prompt</strong>: Multiple tasks → split & chain.</li>
      <li><strong>Hidden Criteria</strong>: Implicit judgment rules → move into explicit <code>format</code> or <code>response</code> instructions.</li>
      <li><strong>Style Churn</strong>: Iterating adjectives (“highly accurate”, “extremely concise”) with no metric plan.</li>
      <li><strong>Example Indigestion</strong>: Copying large corpora instead of curated, contrastive examples.</li>
      <li><strong>Ad Hoc Mutation</strong>: Unlogged edits degrade reproducibility.</li>
      <li><strong>Unbounded Outputs</strong>: Missing length or schema constraints → overflow & hallucination risk.</li>
      <li><strong>Bias Amplification</strong>: Narrow example diversity → skewed performance on underrepresented inputs.</li>
    </ul>
  </div>
);

const Evaluation = () => (
  <div className="space-y-3 text-sm">
    <p><strong>Suggested Metrics:</strong> accuracy, precision/recall (for extraction), structural compliance, rationale completeness, latency, token efficiency.</p>
    <p><strong>Failure Mode Taxonomy:</strong> (a) Misclassification (b) Missing field (c) Hallucinated field (d) Formatting drift (e) Biased or exclusionary phrasing.</p>
    <p><strong>Evaluation Harness:</strong> Start with a CSV/JSON golden set (10–50 rows). Add edge cases representing dialectal variation, varied names, and counterfactuals.</p>
    <p><strong>Change Discipline:</strong> If more than one structural edit occurs, re-baseline; track a diff log (date, change, metric deltas).</p>
    <p><strong>Automation Tip:</strong> Consider scripting a validation pass that checks for required keys and JSON parse success before human review.</p>
  </div>
);

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

const Glossary = () => (
  <div>
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
    <details className="group border rounded mb-2 p-3 bg-white">
      <summary className="cursor-pointer font-medium">Why five template keys?</summary>
      <p className="mt-2 text-sm">They balance expressive coverage (intent, situational framing, required action, output schema, expected shape/tone) with cognitive load. More keys lowered adoption; fewer reduced precision.</p>
    </details>
    <details className="group border rounded mb-2 p-3 bg-white">
      <summary className="cursor-pointer font-medium">Can I add new keys?</summary>
      <p className="mt-2 text-sm">Yes—locally. If broadly useful, open a proposal so tooling and documentation can stay aligned. Keep custom keys succinct.</p>
    </details>
    <details className="group border rounded mb-2 p-3 bg-white">
      <summary className="cursor-pointer font-medium">How do I detect bias?</summary>
      <p className="mt-2 text-sm">In evaluation, insert controlled variants (names, dialects, region terms) and compare outcome disparities. Investigate structural omissions before applying ad‑hoc wording patches.</p>
    </details>
    <details className="group border rounded mb-2 p-3 bg-white">
      <summary className="cursor-pointer font-medium">When should I fork a pattern?</summary>
      <p className="mt-2 text-sm">If structural keys change semantics (e.g., merging roles, introducing multi-step embedded reasoning) or examples shift domain irreversibly—create a named fork for traceability.</p>
    </details>
    <details className="group border rounded p-3 bg-white">
      <summary className="cursor-pointer font-medium">How are similar patterns computed?</summary>
      <p className="mt-2 text-sm">Vector embeddings over normalized text fields (name, description, usage-related content, examples). Scores surface exploratory neighbors, not authoritative taxonomy.</p>
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
  { slug: 'accessibility-responsible-use', id: 'accessibility-responsible-use', title: 'Accessibility & Responsible Use', number: 10, description: 'Inclusive, transparent, and safe utilization guidelines.', component: <AccessibilityResponsible /> },
  { slug: 'glossary', id: 'glossary', title: 'Glossary', number: 11, description: 'Key terms and definitions.', component: <Glossary /> },
  { slug: 'faq', id: 'faq', title: 'FAQ', number: 12, description: 'Frequently asked clarifications.', component: <FAQ /> },
  { slug: 'feedback', id: 'feedback', title: 'Feedback', number: 13, description: 'How to contribute improvements and report issues.', component: <Feedback /> },
  { slug: 'next-steps', id: 'next-steps', title: 'Next Steps', number: 14, description: 'Where to go after orienting.', component: <NextSteps /> }
];
