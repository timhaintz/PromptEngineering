import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { ReadingTimeBadge } from '../components/ReadingTimeBadge';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Search & Similarity UX', description: 'Search syntax, similarity legend, and manual comparison workflow.' };

export default function SearchSimilarityPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'search-similarity')!;
  return (
    <article className="prose max-w-none text-primary">
      <h1 className="flex items-baseline gap-3"><span className="text-muted font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={600} /></h1>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
