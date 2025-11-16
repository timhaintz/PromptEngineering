import Link from 'next/link';
import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';

interface Props { slug: string; }

export default function SectionPager({ slug }: Props) {
  const idx = ORIENTATION_SECTIONS.findIndex(s => s.slug === slug);
  const prev = idx > 0 ? ORIENTATION_SECTIONS[idx - 1] : null;
  const next = idx < ORIENTATION_SECTIONS.length - 1 ? ORIENTATION_SECTIONS[idx + 1] : null;
  const feedbackLinks = [
    { href: 'https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=orientation-feedback', label: 'Share feedback', description: 'General clarity, roadmap updates' },
    { href: 'https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=a11y-regression', label: 'Report a11y regression', description: 'Contrast, focus, AT bugs' },
    { href: 'https://github.com/timhaintz/PromptEngineering4Cybersecurity/issues/new?labels=education', label: 'Request learning aid', description: 'Tutorial or AT walkthrough ideas' }
  ];
  return (
    <>
      <div className="mt-10 p-4 rounded-lg border border-dashed border-muted bg-surface-1 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold text-primary">Need changes to this section?</p>
            <p className="text-xs text-secondary">Open GitHub in a new tab, reference the section slug (<code className="text-[11px]">{slug}</code>), and tag issues with <code className="text-[11px]">orientation-feedback</code>, <code className="text-[11px]">a11y-regression</code>, or <code className="text-[11px]">education</code>.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {feedbackLinks.map(link => (
              <a key={link.label} href={link.href} target="_blank" rel="noreferrer" className="inline-flex flex-col items-start px-3 py-2 rounded border border-muted bg-surface-2 text-xs text-primary hover:bg-surface-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent">
                <span className="font-semibold text-sm">{link.label}</span>
                <span className="text-[11px] text-secondary">{link.description}</span>
              </a>
            ))}
          </div>
        </div>
      </div>
    <nav aria-label="Section pagination" className="mt-6 flex items-center justify-between gap-4 text-sm border-t border-muted pt-6 text-secondary">
      <div>
        {prev && (
          <Link href={`/orientation/${prev.slug}`} className="group inline-flex items-center gap-2 text-secondary hover:text-accent transition-colors">
            <span aria-hidden="true" className="text-accent group-hover:translate-x-[-2px] transition-transform">←</span>
            <span className="flex flex-col leading-tight">
              <span className="text-xs uppercase tracking-wide text-muted">Previous</span>
              <span>{prev.number}. {prev.title}</span>
            </span>
          </Link>
        )}
      </div>
  <div className="text-xs text-muted flex-1 text-center hidden md:block">Orientation</div>
      <div>
        {next && (
          <Link href={`/orientation/${next.slug}`} className="group inline-flex items-center gap-2 text-secondary hover:text-accent transition-colors">
            <span className="flex flex-col items-end leading-tight">
              <span className="text-xs uppercase tracking-wide text-muted">Next</span>
              <span>{next.number}. {next.title}</span>
            </span>
            <span aria-hidden="true" className="text-accent group-hover:translate-x-[2px] transition-transform">→</span>
          </Link>
        )}
      </div>
    </nav>
    </>
  );
}
