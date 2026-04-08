import React from 'react';
import Link from 'next/link';
import { ORIENTATION_SECTIONS } from './data/sections';
import { ReadingTimeBadge } from './components/ReadingTimeBadge';
import SectionPager from './components/SectionPager';

export const metadata = { title: 'Orientation – About', description: 'What, Why & How of the Ballarat AI Prompt Taxonomy.' };

export default function OrientationLandingPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'about');
  
  if (!meta) return <div>Section not found</div>;

  return (
    <article className="prose max-w-none text-primary">
      <h1 className="flex items-baseline gap-3"><span className="text-muted font-medium">{meta.number}.</span> {meta.title} <ReadingTimeBadge words={600} /></h1>
      {meta.component}
      
      <div className="my-8 flex justify-center">
        <Link href="/orientation/hub" className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-accent hover:bg-accent-hover transition-colors shadow-sm">
          Start Using the Patterns →
        </Link>
      </div>

      <SectionPager slug={meta.slug} />
    </article>
  );
}
