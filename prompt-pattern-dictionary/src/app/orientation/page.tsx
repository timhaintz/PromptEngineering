import Link from 'next/link';
import React from 'react';
import MermaidDiagram from '@/components/diagram/MermaidDiagram';
import OrientationTOC from '@/components/navigation/OrientationTOC';
import OrientationSideNav from '@/components/navigation/OrientationSideNav';

import Link from 'next/link';
import { ORIENTATION_SECTIONS } from './data/sections';
import OrientationNav from './components/OrientationNav';

export const metadata = {
  title: 'Orientation | Prompt Pattern Dictionary',
  description: 'Hub for Orientation sections, quick start, and consolidated view.'
};

export default function OrientationHubPage() {
  return (
    <div>
      <h1 className="text-4xl font-bold tracking-tight text-slate-900 mb-6">Orientation</h1>
      <p className="text-slate-700 max-w-3xl leading-relaxed mb-6">Use this hub to jump into focused sections or view the full consolidated page. Each section is deliberately concise and accessible; the <em>All Sections</em> view preserves original anchor stability.</p>
      <div className="mb-10">
        <OrientationNav variant="inline" />
      </div>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
        {ORIENTATION_SECTIONS.map(sec => (
          <div key={sec.slug} className="border rounded-lg p-4 bg-white shadow-sm hover:shadow transition-shadow">
            <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2"><span className="text-slate-400 tabular-nums">{sec.number}.</span>{sec.title}</h2>
            <p className="text-sm text-slate-600 mt-1 mb-3">{sec.description}</p>
            <Link href={`/orientation/${sec.slug}`} className="text-indigo-600 text-sm font-medium hover:underline">Open Section →</Link>
          </div>
        ))}
        <div className="border rounded-lg p-4 bg-indigo-50 shadow-sm hover:shadow transition-shadow">
          <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2">All Sections</h2>
          <p className="text-sm text-slate-700 mt-1 mb-3">Read the complete Orientation content in one scrollable page (original format with anchors).</p>
            <Link href="/orientation/all" className="text-indigo-700 text-sm font-medium hover:underline">View All →</Link>
        </div>
        <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow transition-shadow">
          <h2 className="font-semibold text-slate-900 text-lg flex items-baseline gap-2">Cheat Sheet</h2>
          <p className="text-sm text-slate-600 mt-1 mb-3">Condensed printable reference (5‑Key template, lifecycle, evaluation metrics, anti‑patterns, responsible use).</p>
            <Link href="/orientation/cheatsheet" className="text-indigo-600 text-sm font-medium hover:underline">Open Cheat Sheet →</Link>
        </div>
      </div>
    </div>
  );
}

            <section id="choosing-patterns" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">5.</span> Choosing Patterns</h2>
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

            <section id="combining-patterns" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">6.</span> Combining Patterns</h2>
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

            <section id="adaptation" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">7.</span> Adaptation & Remix</h2>
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

            <section id="anti-patterns" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">8.</span> Anti-Patterns & Pitfalls</h2>
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

            <section id="quality-evaluation" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">9.</span> Quality & Evaluation</h2>
              <div className="space-y-3 text-sm">
                <p><strong>Suggested Metrics:</strong> accuracy, precision/recall (for extraction), structural compliance, rationale completeness, latency, token efficiency.</p>
                <p><strong>Failure Mode Taxonomy:</strong> (a) Misclassification (b) Missing field (c) Hallucinated field (d) Formatting drift (e) Biased or exclusionary phrasing.</p>
                <p><strong>Evaluation Harness:</strong> Start with a CSV/JSON golden set (10–50 rows). Add edge cases representing dialectal variation, varied names, and counterfactuals.</p>
                <p><strong>Change Discipline:</strong> If more than one structural edit occurs, re-baseline; track a diff log (date, change, metric deltas).</p>
                <p><strong>Automation Tip:</strong> Consider scripting a validation pass that checks for required keys and JSON parse success before human review.</p>
              </div>
            </section>

            <section id="accessibility-responsible-use" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">10.</span> Accessibility & Responsible Use</h2>
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

            <section id="glossary" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">11.</span> Glossary</h2>
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

            <section id="faq" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">12.</span> FAQ</h2>
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

            <section id="feedback" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">13.</span> Feedback & Continuous Improvement</h2>
              <p className="text-sm">Spotted ambiguity, accessibility gaps, missing inclusive examples, or structural drift? Please open an issue or PR. Reference the pattern ID(s), describe the observed issue, and (if possible) include a minimal reproducible example. Community stewardship maintains reliability.</p>
            </section>

            <section id="next-steps" className="scroll-mt-24">
              <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">14.</span> Next Steps</h2>
              <ul className="list-disc pl-5 text-sm space-y-1">
                <li><Link href="/patterns" className="text-blue-600 hover:underline">Browse patterns</Link> and shortlist 2–3 for your task.</li>
                <li>Create a tiny evaluation set (edge + typical cases) and record baseline outputs.</li>
                <li>Introduce structured adaptation with version tags.</li>
                <li>Share findings—improvements are welcomed.</li>
              </ul>
            </section>
            </div>{/* prose end */}
          </main>
        </div>
      </div>
    </div>
  );
}
