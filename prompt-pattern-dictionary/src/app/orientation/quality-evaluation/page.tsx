import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Quality & Evaluation', description: 'Metrics, failure taxonomy, disciplined iteration.' };

export default function QualityEvaluationPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'quality-evaluation')!;
  return (
    <article className="prose prose-slate max-w-none">
  <h1 className="flex items-baseline gap-3"><span className="text-slate-600 font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={610} /></h1>
      <div className="mt-2 text-xs text-secondary bg-surface-2 border border-muted rounded p-2" role="note" aria-label="Related next steps">
        <strong>Related next steps:</strong> Iterate structure → <a href="/orientation/adaptation" className="text-accent hover:underline">Adaptation</a>; Revisit lifecycle → <a href="/orientation/lifecycle" className="text-accent hover:underline">Lifecycle</a>
      </div>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
