import Link from 'next/link';
import React from 'react';
import MermaidDiagram from '@/components/diagram/MermaidDiagram';
import OrientationTOC from '@/components/navigation/OrientationTOC';

export const metadata = {
  title: 'Orientation | Prompt Pattern Dictionary',
  description: 'Guided starting point for exploring, selecting, and adapting prompt patterns.'
};

const sections = [
  { id: 'orientation-intro', label: 'Intro' },
  { id: 'quick-start', label: 'Quick Start' },
  { id: 'what-is-a-pattern', label: 'What Is a Pattern' },
  { id: 'pattern-anatomy', label: 'Anatomy' },
  { id: 'lifecycle', label: 'Lifecycle' },
  { id: 'choosing-patterns', label: 'Choosing' },
  { id: 'combining-patterns', label: 'Combining' },
  { id: 'adaptation', label: 'Adaptation' },
  { id: 'anti-patterns', label: 'Anti-Patterns' },
  { id: 'quality-evaluation', label: 'Quality' },
  { id: 'accessibility-responsible-use', label: 'Accessibility' },
  { id: 'glossary', label: 'Glossary' },
  { id: 'faq', label: 'FAQ' },
  { id: 'feedback', label: 'Feedback' },
  { id: 'next-steps', label: 'Next Steps' }
];

export default function OrientationPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      <div className="container mx-auto px-4 py-10 lg:py-16">
  <h1 id="orientation-intro" className="text-4xl font-bold text-gray-900 mb-4">Orientation</h1>
  <p className="text-gray-700 max-w-3xl mb-6">Welcome. This guide helps you confidently explore, evaluate, adapt, and combine prompt patterns. It is designed to be <strong>concise, systematic, inclusive, and accessible</strong>. You can jump straight to a section using the in‑page navigation, use your browser's find feature (<kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>F</kbd>), or navigate by headings with assistive technologies.</p>
  <p className="text-gray-600 text-sm max-w-3xl mb-10">Keyboard tips: Press <kbd>Tab</kbd> to reach the mini navigation chips, <kbd>Shift+Tab</kbd> to move backwards, and use native browser heading navigation (e.g. <kbd>H</kbd> in many screen reader modes). All expandable elements (such as templates and example groups) expose clear button labels and ARIA relationships.</p>
  <p className="text-xs text-gray-500 max-w-3xl mb-6">Need a printable reference? A condensed <Link href="/orientation/cheatsheet" className="text-blue-600 underline">Cheat Sheet</Link> page is available (beta).</p>

        {/* In-page mini navigation with scrollspy */}
        <OrientationTOC sections={sections} />

        <div className="prose prose-slate max-w-none">
          <section id="quick-start">
            <h2>Quick Start</h2>
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
            <div className="mt-4 p-3 rounded border bg-white shadow-sm text-sm text-gray-700">
              <p className="font-semibold mb-1">Principles:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li><strong>Clarity over cleverness</strong> – explicit instructions reduce hallucination risk.</li>
                <li><strong>Single responsibility</strong> – one pattern, one job; chain instead of overloading.</li>
                <li><strong>Measured change</strong> – modify one aspect at a time; re‑test.</li>
                <li><strong>Inclusive data</strong> – test with varied names, dialects, and contexts.</li>
                <li><strong>Document provenance</strong> – note if AI assisted any field.</li>
              </ul>
            </div>
          </section>

          <section id="what-is-a-pattern">
            <h2>What Is a Prompt Pattern?</h2>
            <p>A prompt pattern is a <strong>reusable, named design structure</strong> for interacting with a language model so that behavior is <em>predictable, inspectable, and improvable</em>. It captures <em>intent</em>, <em>structural scaffolding</em>, and <em>adaptation guidance</em>. Think of patterns as <strong>primitives</strong> for assembling reliable language workflows—not secret incantations.</p>
            <p className="mt-3">Why they matter:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Shared vocabulary</strong> improves collaboration.</li>
              <li><strong>Structure reduces ambiguity</strong> and unintended model drift.</li>
              <li><strong>Comparability</strong> allows systematic evaluation.</li>
              <li><strong>Traceability</strong> helps audit and mitigate harmful or biased behavior.</li>
            </ul>
          </section>

            <section id="pattern-anatomy">
              <h2>Anatomy of a Pattern</h2>
              <p>Each entry follows a consistent schema to support scanning and comparison. The Template exposes five canonical keys (<code>role</code>, <code>context</code>, <code>action</code>, <code>format</code>, <code>response</code>) plus an optional single‑line <em>bracketed synthesis</em>. Additional normalized attributes provide discoverability, provenance, and evaluation hooks.</p>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="p-4 rounded border bg-white shadow-sm">
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
                <div className="p-4 rounded border bg-white shadow-sm">
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
              <div className="my-6 p-4 rounded-lg bg-white border border-indigo-200 shadow-sm">
                <p className="text-sm font-semibold text-indigo-700 mb-2">Structure Diagram</p>
                <div id="diagram-desc" className="sr-only">Diagram showing relationships: Pattern Name connects to Intent/Purpose, Template (with five keys and bracketed summary), Application, Examples & Similar, Adaptation Notes, Evaluation/Quality Hints, and Tags/Category.</div>
                <MermaidDiagram
                  describedById="diagram-desc"
                  className="mermaid"
                  chart={`flowchart LR\n    A[Pattern Name]:::title --> B[Intent / Purpose]\n    B --> C[Template (5 keys)]\n    C --> C1[role]\n    C --> C2[context]\n    C --> C3[action]\n    C --> C4[format]\n    C --> C5[response]\n    C --> C6[Bracketed Summary]\n    A --> D[Application]\n    A --> E[Examples & Similar]\n    A --> F[Adaptation Notes]\n    A --> G[Evaluation / Quality Hints]\n    A --> H[Tags / Category]\n\n    classDef title fill:#1e3a8a,stroke:#1e3a8a,stroke-width:1,color:#fff;\n    classDef keys fill:#eef2ff,stroke:#4338ca,color:#1e1b4b;\n    class C,C1,C2,C3,C4,C5,C6 keys;`}
                />
                <p className="mt-2 text-xs text-gray-500">Rendered client-side with Mermaid; accessible fallback includes textual description.</p>
              </div>
            </section>

            <section id="lifecycle">
              <h2>Pattern Lifecycle</h2>
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
              <p className="mt-3 text-sm text-gray-700"><strong>Drift Indicator:</strong> If failure clusters reappear or confidence declines, re-open the adaptation phase—do not silently patch in production.</p>
            </section>

            <section id="choosing-patterns">
              <h2>Choosing the Right Pattern</h2>
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
            </section>

            <section id="combining-patterns">
              <h2>Combining Patterns</h2>
              <p className="text-sm">Compose multi-step flows deliberately. Each link should produce a constrained artifact consumed safely by the next step.</p>
              <table className="text-xs mt-3 border w-full">
                <thead>
                  <tr className="bg-gray-100 text-gray-700">
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
            </section>

            <section id="adaptation">
              <h2>Adaptation & Remix</h2>
              <ul className="list-disc pl-5 space-y-1 text-sm">
                <li><strong>Preserve structural keys</strong>; modify content, not the scaffold labels.</li>
                <li><strong>Use versioned placeholders</strong> (<code>{'{{CLAUSE_A}}'}</code>, <code>{'{{CLAUSE_B}}'}</code>) so diffs are meaningful.</li>
                <li><strong>Record rationale</strong> for each modification (links to observed failure modes).</li>
                <li><strong>Minimize example bloat</strong>: prefer 2–3 crisp examples over sprawling narratives.</li>
                <li><strong>Ethical adaptation</strong>: Avoid reinforcing stereotypes; stress neutral or diverse entities.</li>
                <li><strong>Re-run evaluation</strong> after each structural shift (no “silent merges”).</li>
              </ul>
              <p className="mt-3 text-xs text-gray-600">If a pattern diverges heavily, consider naming it explicitly (fork) to preserve lineage.</p>
            </section>

            <section id="anti-patterns">
              <h2>Anti-Patterns & Pitfalls</h2>
              <ul className="list-disc pl-5 space-y-1 text-sm">
                <li><strong>Overloaded Mega-Prompt</strong>: Multiple tasks → split & chain.</li>
                <li><strong>Hidden Criteria</strong>: Implicit judgment rules → move into explicit <code>format</code> or <code>response</code> instructions.</li>
                <li><strong>Style Churn</strong>: Iterating adjectives (“highly accurate”, “extremely concise”) with no metric plan.</li>
                <li><strong>Example Indigestion</strong>: Copying large corpora instead of curated, contrastive examples.</li>
                <li><strong>Ad Hoc Mutation</strong>: Unlogged edits degrade reproducibility.</li>
                <li><strong>Unbounded Outputs</strong>: Missing length or schema constraints → overflow & hallucination risk.</li>
                <li><strong>Bias Amplification</strong>: Narrow example diversity → skewed performance on underrepresented inputs.</li>
              </ul>
            </section>

            <section id="quality-evaluation">
              <h2>Quality & Evaluation</h2>
              <div className="space-y-3 text-sm">
                <p><strong>Suggested Metrics:</strong> accuracy, precision/recall (for extraction), structural compliance, rationale completeness, latency, token efficiency.</p>
                <p><strong>Failure Mode Taxonomy:</strong> (a) Misclassification (b) Missing field (c) Hallucinated field (d) Formatting drift (e) Biased or exclusionary phrasing.</p>
                <p><strong>Evaluation Harness:</strong> Start with a CSV/JSON golden set (10–50 rows). Add edge cases representing dialectal variation, varied names, and counterfactuals.</p>
                <p><strong>Change Discipline:</strong> If more than one structural edit occurs, re-baseline; track a diff log (date, change, metric deltas).</p>
                <p><strong>Automation Tip:</strong> Consider scripting a validation pass that checks for required keys and JSON parse success before human review.</p>
              </div>
            </section>

            <section id="accessibility-responsible-use">
              <h2>Accessibility & Responsible Use</h2>
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
            </section>

            <section id="glossary">
              <h2>Glossary</h2>
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
            </section>

            <section id="faq">
              <h2>FAQ</h2>
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
            </section>

            <section id="feedback">
              <h2>Feedback & Continuous Improvement</h2>
              <p className="text-sm">Spotted ambiguity, accessibility gaps, missing inclusive examples, or structural drift? Please open an issue or PR. Reference the pattern ID(s), describe the observed issue, and (if possible) include a minimal reproducible example. Community stewardship maintains reliability.</p>
            </section>

            <section id="next-steps">
              <h2>Next Steps</h2>
              <ul className="list-disc pl-5 text-sm space-y-1">
                <li><Link href="/patterns" className="text-blue-600 hover:underline">Browse patterns</Link> and shortlist 2–3 for your task.</li>
                <li>Create a tiny evaluation set (edge + typical cases) and record baseline outputs.</li>
                <li>Introduce structured adaptation with version tags.</li>
                <li>Share findings—improvements are welcomed.</li>
              </ul>
            </section>
        </div>
      </div>
    </div>
  );
}
