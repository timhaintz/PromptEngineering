import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';
import OrientationNav from '../components/OrientationNav';
import Link from 'next/link';

export const metadata = {
  title: 'Orientation – All Sections | Prompt Pattern Dictionary',
  description: 'Complete consolidated Orientation reference (legacy single-page view).'
};

export default function OrientationAllPage() {
  return (
    <div>
      <header className="mb-10 border-b pb-6">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 mb-4">Orientation – All Sections</h1>
        <p className="text-slate-700 max-w-4xl leading-relaxed">This consolidated page preserves the original single-page anchor structure while individual section pages provide focused, faster-loading, and more navigable experiences.</p>
        <p className="mt-4 text-sm text-slate-600">Prefer focused pages? Return to the <Link href="/orientation" className="text-indigo-600 hover:underline">Orientation hub</Link>.</p>
      </header>
      <div className="lg:hidden mb-8">
        <OrientationNav variant="inline" />
      </div>
      <div className="prose prose-slate max-w-none">
        {ORIENTATION_SECTIONS.map(sec => (
          <section id={sec.id} key={sec.id} className="scroll-mt-24 mb-14">
            <h2 className="flex items-baseline gap-2"><span className="text-slate-400 font-medium">{sec.number}.</span> {sec.title}</h2>
            {/* Real content will replace placeholders during migration */}
            {sec.component}
            <div className="mt-6 text-xs text-slate-400">Section slug: {sec.slug}</div>
          </section>
        ))}
      </div>
    </div>
  );
}
