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
        <p className="text-gray-700 max-w-2xl mb-10">A guided starting point for exploring, selecting, and adapting prompt patterns. Use this page to understand structure, lifecycle, and how to compose patterns effectively.</p>

        {/* In-page mini navigation with scrollspy */}
        <OrientationTOC sections={sections} />

        <div className="prose prose-slate max-w-none">
          <section id="quick-start">
            <h2>Quick Start</h2>
            <p>New here? Skim this first. (1) Pick a pattern aligned with your goal (e.g., classify, extract, reason). (2) Read its Template and Application examples. (3) Adapt minimally for your domain. (4) Evaluate output quality—iterate with controlled changes.</p>
            <ul>
              <li>Keep prompts atomic.</li>
              <li>Measure before changing.</li>
              <li>Prefer clarity over cleverness.</li>
            </ul>
          </section>

          <section id="what-is-a-pattern">
            <h2>What Is a Prompt Pattern?</h2>
            <p>A reusable structured strategy for eliciting reliable behavior from a language model. Each pattern names intent, codifies structure, and offers adaptation guidance. Patterns are not magic incantations—they are design primitives.</p>
          </section>

            <section id="pattern-anatomy">
              <h2>Anatomy of a Pattern</h2>
              <p>Each entry follows a consistent schema so you can scan and compare quickly. The Template always exposes five canonical keys (<code>role</code>, <code>context</code>, <code>action</code>, <code>format</code>, <code>response</code>) plus a bracketed one-line synthesis.</p>
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
              <p>Identify need → Select candidate pattern(s) → Customize Template minimally → Trial on representative examples → Measure error modes → Refine structurally (not stylistically) → Lock version → Monitor drift.</p>
            </section>

            <section id="choosing-patterns">
              <h2>Choosing the Right Pattern</h2>
              <p>Start from task archetype: classification, extraction, reasoning, transformation, generation, evaluation. Use tags and similarity suggestions to short‑list. Prototype two if unsure; pick the one with fewer critical failures.</p>
            </section>

            <section id="combining-patterns">
              <h2>Combining Patterns</h2>
              <p>Compose complex workflows by chaining (e.g., Decomposition → Structured Extraction → Verification). Ensure each handoff produces a stable, constrained intermediate representation. Compose incrementally.</p>
            </section>

            <section id="adaptation">
              <h2>Adaptation & Remix</h2>
              <p>When adapting, pin structure first; only alter domain semantics. Keep variable sections explicit (e.g., <code>{'{{INPUT_TEXT}}'}</code>). Avoid burying instructions inside examples. Document modifications for rollback.</p>
            </section>

            <section id="anti-patterns">
              <h2>Anti-Patterns & Pitfalls</h2>
              <p>Overloaded prompts, hidden criteria, vague success conditions, premature stylistic tuning, brittle copy-paste of long examples, unmeasured iteration. Refactor toward explicitness early.</p>
            </section>

            <section id="quality-evaluation">
              <h2>Quality & Evaluation</h2>
              <p>Define observable metrics (accuracy, consistency, latency, determinism). Use golden sets. Track regression when modifying the Template. Prefer structural adjustments before tweaking style adjectives.</p>
            </section>

            <section id="glossary">
              <h2>Glossary</h2>
              <dl>
                <dt>Pattern</dt>
                <dd>Structured reusable prompt design.</dd>
                <dt>Template</dt>
                <dd>Canonical 5-key structured specification of a pattern.</dd>
                <dt>Bracketed Summary</dt>
                <dd>One-line compressed representation of Template intent.</dd>
                <dt>Application</dt>
                <dd>Concrete usage guidance or contextual scenario.</dd>
                <dt>Adaptation</dt>
                <dd>Domain-specific tailoring while preserving structural intent.</dd>
              </dl>
            </section>

            <section id="faq">
              <h2>FAQ (Coming Soon)</h2>
              <p>We will populate this section after collecting common user questions (e.g., “Why five template keys?”, “How do I choose between two reasoning patterns?”).</p>
            </section>

            <section id="feedback">
              <h2>Feedback & Iteration</h2>
              <p>Found ambiguity or missing content? Open an issue or submit a PR referencing the pattern ID. Iterative curation sustains quality.</p>
            </section>

            <section id="next-steps">
              <h2>Next Steps</h2>
              <p><Link href="/patterns" className="text-blue-600 hover:underline">Browse all patterns</Link>, bookmark candidates, or prototype an evaluation harness.</p>
            </section>
        </div>
      </div>
    </div>
  );
}
