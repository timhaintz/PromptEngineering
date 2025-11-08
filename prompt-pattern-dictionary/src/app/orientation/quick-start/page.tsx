import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Quick Start', description: '8-step quick start for using prompt patterns.' };

export default function QuickStartPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'quick-start')!;
  return (
    <article className="prose max-w-none text-primary">
	  <h1 className="flex items-baseline gap-3"><span className="text-muted font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={750} /></h1>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
