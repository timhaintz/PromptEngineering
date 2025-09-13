import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import SectionPager from '../components/SectionPager';

export const metadata = { title: 'Orientation – Anti-Patterns', description: 'Common pitfalls and how to avoid them.' };

export default function AntiPatternsPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'anti-patterns')!;
  return (
    <article className="prose prose-slate max-w-none">
      <h1 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">{meta.number}.</span> {meta.title}</h1>
      {meta.component}
      <SectionPager slug={meta.slug} />
    </article>
  );
}
