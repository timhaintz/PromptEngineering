import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = {
  title: 'Orientation – Learning Path & Roadmap',
  description: 'Staged journey through the Orientation content plus AI-assisted correction guidance.'
};

export default function LearningPathPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'learning-path')!;
  return (
    <article className="prose max-w-none text-primary">
      <h1 className="flex items-baseline gap-3"><span className="text-muted font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={620} /></h1>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
