import Link from 'next/link';
import React from 'react';
import { ORIENTATION_SECTIONS } from '../data/sections';

interface Props { slug: string; }

export default function SectionPager({ slug }: Props) {
  const idx = ORIENTATION_SECTIONS.findIndex(s => s.slug === slug);
  const prev = idx > 0 ? ORIENTATION_SECTIONS[idx - 1] : null;
  const next = idx < ORIENTATION_SECTIONS.length - 1 ? ORIENTATION_SECTIONS[idx + 1] : null;
  return (
    <nav aria-label="Section pagination" className="mt-12 flex items-center justify-between gap-4 text-sm border-t pt-6">
      <div>
        {prev && (
          <Link href={`/orientation/${prev.slug}`} className="group inline-flex items-center gap-2 text-slate-600 hover:text-indigo-700">
            <span aria-hidden="true" className="text-indigo-600 group-hover:translate-x-[-2px] transition-transform">←</span>
            <span className="flex flex-col leading-tight">
              <span className="text-xs uppercase tracking-wide text-slate-600">Previous</span>
              <span>{prev.number}. {prev.title}</span>
            </span>
          </Link>
        )}
      </div>
  <div className="text-xs text-slate-600 flex-1 text-center hidden md:block">Orientation</div>
      <div>
        {next && (
          <Link href={`/orientation/${next.slug}`} className="group inline-flex items-center gap-2 text-slate-600 hover:text-indigo-700">
            <span className="flex flex-col items-end leading-tight">
              <span className="text-xs uppercase tracking-wide text-slate-600">Next</span>
              <span>{next.number}. {next.title}</span>
            </span>
            <span aria-hidden="true" className="text-indigo-600 group-hover:translate-x-[2px] transition-transform">→</span>
          </Link>
        )}
      </div>
    </nav>
  );
}
