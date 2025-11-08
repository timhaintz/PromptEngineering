import React from 'react';
import Link from 'next/link';

interface ProvenanceBadgeProps {
  context?: 'orientation' | 'pattern' | string;
  className?: string;
}

/**
 * Unified provenance badge + disclaimer for AI-assisted metadata transparency.
 * P0 Orientation task: Standardize styling & messaging across Orientation pages.
 */
export function ProvenanceBadge({ context = 'orientation', className = '' }: ProvenanceBadgeProps) {
  return (
    <div className={className}>
      <span
        className="inline-flex items-center gap-1 px-2 py-1 rounded border border-muted bg-surface-2 text-xs font-medium text-secondary focus-ring"
        aria-describedby={`prov-desc-${context}`}
      >
        <svg aria-hidden="true" viewBox="0 0 16 16" className="w-3 h-3 text-accent">
          <path fill="currentColor" d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM7.25 4.5c0-.414.336-.75.75-.75s.75.336.75.75v4.75a.75.75 0 0 1-1.5 0V4.5Zm.75 8a1.125 1.125 0 1 1 0-2.25 1.125 1.125 0 0 1 0 2.25Z" />
        </svg>
        Provenance
      </span>
      <div id={`prov-desc-${context}`} className="sr-only">
        Some displayed fields may be AI-assisted (model generated or refined). Review domain-critical logic manually. See Accessibility & Responsible Use and footer Data & Provenance links for limitations.
      </div>
      <p className="mt-2 text-[11px] text-muted max-w-prose">
        Some pattern schema & usage guidance fields may be AI‑assisted. Verify critical reasoning before production. See{' '}<Link href="/orientation/accessibility-responsible-use" className="underline">Accessibility & Responsible Use</Link>{' '}and footer <span className="font-medium">Data &amp; Provenance</span>.
      </p>
    </div>
  );
}

export default ProvenanceBadge;
