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
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
