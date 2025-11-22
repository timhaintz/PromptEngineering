import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Pattern Anatomy', description: 'Schema fields and 5-Key template structure.' };

export default function PatternAnatomyPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'pattern-anatomy')!;
  return (
    <article className="prose prose-slate max-w-none">
  <h1 className="flex items-baseline gap-3"><span className="text-slate-600 font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={680} /></h1>
      <div className="mt-2 text-xs text-secondary bg-surface-2 border border-muted rounded p-2" role="note" aria-label="Related next steps">
        <strong>Related next steps:</strong> Apply template → <a href="/orientation/quick-start" className="text-accent hover:underline">Quick Start</a>; Evaluate outputs → <a href="/orientation/quality-evaluation" className="text-accent hover:underline">Evaluation</a>
      </div>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
