import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Similarity Preview', description: 'Teaser: sample similarity scores, evaluation/adaptation loop, optional static network graph.' };

export default function SimilarityPreviewPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'similarity-preview')!;
  return (
    <article className="prose max-w-none text-primary">
      <h1 className="flex items-baseline gap-3"><span className="text-muted font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={500} /></h1>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
