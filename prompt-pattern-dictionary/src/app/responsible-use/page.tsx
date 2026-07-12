import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import { PageHeader } from '@/components/ui/PageHeader';

export const metadata = {
  title: 'Responsible Use | Ballarat AI Prompt Taxonomy',
  description: 'Practical guidance for applying, evaluating, and reporting prompt patterns responsibly.'
};

const repositoryUrl = 'https://github.com/timhaintz/PromptEngineering';
const responsibleUseReportUrl = `${repositoryUrl}/issues/new?labels=responsible-use-review&title=Responsible%20use%20report`;
const metadataCorrectionUrl = `${repositoryUrl}/issues/new?labels=ai-assist-correction&title=AI-assisted%20metadata%20correction`;
const securityAdvisoryUrl = `${repositoryUrl}/security/advisories/new`;

const sectionClass = 'border-t border-muted pt-8';
const headingClass = 'text-xl font-semibold text-primary';
const bodyClass = 'mt-3 text-sm leading-7 text-secondary';
const listClass = 'mt-4 list-disc space-y-2 pl-5 text-sm leading-7 text-secondary';

export default function ResponsibleUsePage() {
  return (
    <PageShell variant="narrow">
      <article className="space-y-10">
        <PageHeader
          heading="Responsible Use"
          subtitle="Practical guidance for using the taxonomy with appropriate evidence, privacy, attribution, and human oversight."
        />

        <dl className="grid gap-x-8 gap-y-4 border-y border-muted py-5 text-sm sm:grid-cols-3">
          <div>
            <dt className="font-semibold text-primary">Status</dt>
            <dd className="mt-1 text-secondary">Active guidance</dd>
          </div>
          <div>
            <dt className="font-semibold text-primary">Applies to</dt>
            <dd className="mt-1 text-secondary">Patterns, examples, similarity data, and AI-assisted fields</dd>
          </div>
          <div>
            <dt className="font-semibold text-primary">Reviewed</dt>
            <dd className="mt-1 text-secondary">July 2026</dd>
          </div>
        </dl>

        <aside className="border-l-4 border-accent bg-surface-2 px-5 py-4" aria-labelledby="dual-use-heading">
          <h2 id="dual-use-heading" className="font-semibold text-primary">Research inclusion is not endorsement</h2>
          <p className="mt-2 text-sm leading-7 text-secondary">
            The corpus includes dual-use material such as jailbreak and adversarial prompt examples because these are part of the research record.
            Their presence supports analysis, defensive testing, and safer system design; it is not permission to deploy them against systems or people without authorization.
          </p>
        </aside>

        <section aria-labelledby="before-use-heading">
          <h2 id="before-use-heading" className={headingClass}>Before you apply a pattern</h2>
          <ol className="mt-5 list-decimal space-y-4 pl-5 text-sm leading-7 text-secondary">
            <li><strong className="text-primary">Confirm authority and purpose.</strong> Use the pattern only for a legitimate task and, where relevant, on systems you own or are authorized to assess.</li>
            <li><strong className="text-primary">Inspect provenance.</strong> Open the cited source and distinguish source-derived examples from AI-assisted explanations, applications, and PEIL prompts.</li>
            <li><strong className="text-primary">Minimize data.</strong> Replace personal, confidential, customer, credential, health, or regulated information with synthetic or de-identified values.</li>
            <li><strong className="text-primary">Test proportionately.</strong> Start in a controlled environment, include typical and edge cases, and evaluate accuracy, completeness, fabrication, bias, and format adherence.</li>
            <li><strong className="text-primary">Keep a human accountable.</strong> Review outputs before they influence people, security decisions, publication, legal advice, healthcare, or other consequential action.</li>
          </ol>
        </section>

        <div className="grid gap-10 md:grid-cols-2">
          <section className={sectionClass} aria-labelledby="appropriate-use-heading">
            <h2 id="appropriate-use-heading" className={headingClass}>Appropriate use</h2>
            <ul className={listClass}>
              <li>Research into prompt engineering, reliability, safety, and human-AI interaction.</li>
              <li>Education and training that retain source attribution and explain limitations.</li>
              <li>Defensive security evaluation in an authorized, isolated environment.</li>
              <li>Prompt quality testing with synthetic or non-sensitive data.</li>
              <li>Bias, accessibility, robustness, and failure-mode analysis.</li>
            </ul>
          </section>

          <section className={sectionClass} aria-labelledby="misuse-heading">
            <h2 id="misuse-heading" className={headingClass}>Do not use this taxonomy to</h2>
            <ul className={listClass}>
              <li>Target systems, accounts, datasets, or people without authorization.</li>
              <li>Create or deploy malware, exploit payloads, phishing, harassment, or deceptive content.</li>
              <li>Bypass safeguards to obtain harmful, private, proprietary, or restricted information.</li>
              <li>Present generated or AI-assisted text as a verbatim research finding.</li>
              <li>Make consequential decisions solely from an LLM response or similarity score.</li>
            </ul>
          </section>
        </div>

        <section className={sectionClass} aria-labelledby="evidence-heading">
          <h2 id="evidence-heading" className={headingClass}>Interpret the evidence correctly</h2>
          <dl className="mt-5 space-y-5 text-sm leading-7">
            <div>
              <dt className="font-semibold text-primary">Source patterns and examples</dt>
              <dd className="text-secondary">These preserve the collected research record. Cite the original source rather than this interface when making a scholarly claim.</dd>
            </div>
            <div>
              <dt className="font-semibold text-primary">AI-assisted fields</dt>
              <dd className="text-secondary">General explanations, applications, knowledge intent, and PEIL material may be model-generated or refined. Treat them as working guidance and verify domain-critical details.</dd>
            </div>
            <div>
              <dt className="font-semibold text-primary">Semantic assignments and similarity scores</dt>
              <dd className="text-secondary">These are embedding-based navigation aids. A nearest category or high similarity score indicates mathematical proximity, not equivalence, quality, safety, or empirical effectiveness.</dd>
            </div>
            <div>
              <dt className="font-semibold text-primary">Evaluation results</dt>
              <dd className="text-secondary">The thesis evaluation used an LLM judge across 648 responses. Human validation is documented as future work, so machine-judge scores should not be treated as final human preference evidence.</dd>
            </div>
          </dl>
        </section>

        <section className={sectionClass} aria-labelledby="reporting-heading">
          <h2 id="reporting-heading" className={headingClass}>Report a concern</h2>
          <p className={bodyClass}>Do not include credentials, private data, exploit payloads, or other sensitive material in a public issue.</p>
          <div className="mt-5 divide-y divide-[var(--border-default)] border-y border-muted">
            <div className="py-5 sm:flex sm:items-start sm:justify-between sm:gap-8">
              <div>
                <h3 className="font-semibold text-primary">Misuse, bias, or harmful adaptation</h3>
                <p className="mt-1 text-sm leading-6 text-secondary">Include the pattern ID, model/version, a de-identified example, expected behavior, and observed impact.</p>
              </div>
              <a href={responsibleUseReportUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex shrink-0 font-medium underline underline-offset-4 sm:mt-0">Open a report</a>
            </div>
            <div className="py-5 sm:flex sm:items-start sm:justify-between sm:gap-8">
              <div>
                <h3 className="font-semibold text-primary">Incorrect AI-assisted metadata</h3>
                <p className="mt-1 text-sm leading-6 text-secondary">Identify the pattern and field, explain the issue, and provide a source or reproducible rationale where possible.</p>
              </div>
              <a href={metadataCorrectionUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex shrink-0 font-medium underline underline-offset-4 sm:mt-0">Request a correction</a>
            </div>
            <div className="py-5 sm:flex sm:items-start sm:justify-between sm:gap-8">
              <div>
                <h3 className="font-semibold text-primary">Security vulnerability</h3>
                <p className="mt-1 text-sm leading-6 text-secondary">Use a private GitHub Security Advisory. Do not disclose an exploitable vulnerability in a public issue.</p>
              </div>
              <a href={securityAdvisoryUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex shrink-0 font-medium underline underline-offset-4 sm:mt-0">Report privately</a>
            </div>
          </div>
        </section>

        <section className={sectionClass} aria-labelledby="research-principles-heading">
          <h2 id="research-principles-heading" className={headingClass}>Research principles</h2>
          <p className={bodyClass}>
            The thesis follows principles of honesty, integrity, accountability, attribution, open access, misuse awareness, and AI safety.
            Derivative work should retain source citations, identify material that has been generated or adapted, and document changes that affect meaning or evaluation.
          </p>
          <p className="mt-4 text-sm leading-7 text-secondary">
            For accessibility guidance, see{' '}
            <Link href="/orientation/accessibility-responsible-use" className="font-medium underline underline-offset-4">Accessibility &amp; Responsible Use</Link>.
            For repository policy and contribution history, visit the{' '}
            <a href={repositoryUrl} target="_blank" rel="noreferrer" className="font-medium underline underline-offset-4">source repository</a>.
          </p>
        </section>
      </article>
    </PageShell>
  );
}
