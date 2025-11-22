import React from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Responsible Use & Ethical Guidelines',
  description: 'Principles, acceptable use, prohibited behaviors, safeguards, and reporting for the Prompt Pattern Dictionary.'
};

export default function ResponsibleUsePage() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1 className="mb-2">Responsible Use & Ethical Guidelines</h1>
      <p className="text-sm">This page outlines principles and guardrails for ethical, privacy‑respectful and secure usage of the prompt pattern dictionary, similarity tooling, and enrichment features.</p>

      <section>
        <h2>Core Principles</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li><strong>Transparency & Attribution:</strong> Cite original research; retain provenance badges.</li>
          <li><strong>Security-Conscious Usage:</strong> Favor defensive and resilience patterns; contextualize risky examples.</li>
          <li><strong>Privacy & Minimization:</strong> Exclude sensitive personal, customer, or regulated data from prompts.</li>
          <li><strong>Non-Malicious Research:</strong> Use similarity/comparison for constructive academic or defensive analysis only.</li>
          <li><strong>Accuracy & Validation:</strong> Treat AI-enriched metadata as advisory; verify before production decisions.</li>
          <li><strong>Inclusivity & Accessibility:</strong> Maintain WCAG-aligned language and structure.</li>
        </ul>
      </section>

      <section>
        <h2>Acceptable Use Examples</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li>Academic or industry research on prompt engineering safety and effectiveness.</li>
          <li>Defensive cybersecurity tooling development and evaluative pattern adaptation.</li>
          <li>Educational materials, workshops, and tutorials with proper citation.</li>
          <li>Internal prompt quality evaluation with synthetic or non-sensitive data.</li>
          <li>Gap analysis for defensive coverage, bias, or evaluation rigor.</li>
        </ul>
      </section>

      <section>
        <h2>Prohibited / Misuse Scenarios</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li>Generating real exploit payloads or malware operational instructions.</li>
          <li>Crafting phishing or social engineering content for unsanctioned deployment.</li>
          <li>Bypassing model safety or exfiltrating proprietary system prompts.</li>
          <li>Fingerprinting sensitive proprietary datasets via similarity harvesting.</li>
          <li>Automated scraping / rate abuse beyond documented export capabilities.</li>
        </ul>
      </section>

      <section>
        <h2>Safeguards & Controls</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li><strong>Provenance Badges:</strong> AI-assisted fields display unified badge + disclaimer.</li>
          <li><strong>Defensive Cross-Links:</strong> Dual-use patterns will reference mitigation alternatives.</li>
          <li><strong>Caution Badges (Planned):</strong> Visual indicator for dual-use entries with guidance.</li>
          <li><strong>Telemetry Privacy (Planned):</strong> Minimal opt-in events excluding prompt content.</li>
          <li><strong>Issue Templates:</strong> Public forms for misuse reports & AI field corrections.</li>
          <li><strong>Rate Limiting (Planned):</strong> Future dynamic endpoints will enforce reasonable quotas.</li>
        </ul>
      </section>

      <section>
        <h2>Reporting & Escalation</h2>
        <p className="text-sm">Security vulnerabilities: follow <Link href="/SECURITY" className="underline">SECURITY.md</Link> guidance (private advisory or email). Misuse or ethical concerns: open an issue with label <code>responsible-use-review</code> using the template. AI metadata corrections: use the <code>ai-assist-correction</code> template.</p>
      </section>

      <section>
        <h2>Open Source & Licensing</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li>Retain source citations in derivative educational summaries.</li>
          <li>AI-enriched summaries share repository license; do not present as verbatim research quotes.</li>
          <li>Forks must preserve this page and clearly mark added safety changes.</li>
        </ul>
      </section>

      <section>
        <h2>Future Enhancements</h2>
        <ul className="list-disc pl-6 text-sm space-y-1">
          <li>Client-side misuse heuristics to highlight suspicious prompt structures.</li>
          <li>Risk scoring API integration for pattern dual-use classification.</li>
          <li>Transparency dashboard: counts of caution badges, corrections processed, reports triaged.</li>
        </ul>
      </section>

      <hr />
      <p className="text-xs text-muted">Living document – propose changes via PR referencing related issue labels (<code>responsible-use-review</code>, <code>ai-assist-correction</code>).</p>
    </article>
  );
}
