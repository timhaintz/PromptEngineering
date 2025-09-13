"use client";
import React from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ORIENTATION_SECTIONS } from '../data/sections';

interface Props { variant?: 'sidebar' | 'inline'; }

export default function OrientationNav({ variant = 'sidebar' }: Props) {
  const pathname = usePathname();
  const isAll = pathname?.endsWith('/orientation/all');
  const currentSlug = pathname?.split('/').pop();

  return (
    <nav aria-label="Orientation sections" data-variant={variant} className={variant === 'sidebar' ? 'text-sm' : 'flex flex-wrap gap-2'}>
      {variant === 'sidebar' ? (
        <ul className="space-y-1">
          {ORIENTATION_SECTIONS.map(s => {
            const active = currentSlug === s.slug || (isAll && false);
            return (
              <li key={s.slug}>
                <Link href={`/orientation/${s.slug}`} className={`flex gap-2 rounded px-2 py-1 border-l-4 leading-snug transition-colors ${active ? 'bg-indigo-50 border-indigo-600 text-indigo-800 font-medium' : 'border-transparent text-slate-700 hover:bg-slate-50 hover:border-slate-300'}`} aria-current={active ? 'page' : undefined}>
                  <span className="text-slate-400 w-6 tabular-nums text-right select-none">{s.number}.</span>
                  <span className="flex-1">{s.title}</span>
                </Link>
              </li>
            );
          })}
          <li className="pt-2 mt-2 border-t"><Link href="/orientation/all" className="block px-2 py-1 text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded">All Sections</Link></li>
          <li><Link href="/orientation/cheatsheet" className="block px-2 py-1 text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded">Cheat Sheet</Link></li>
        </ul>
      ) : (
        <div className="flex flex-wrap gap-2">
          {ORIENTATION_SECTIONS.map(s => (
            <Link key={s.slug} href={`/orientation/${s.slug}`} className="text-xs px-3 py-1 rounded-full border bg-white hover:bg-slate-50 text-slate-700">{s.number}. {s.title}</Link>
          ))}
          <Link href="/orientation/all" className="text-xs px-3 py-1 rounded-full border bg-white hover:bg-slate-50 text-slate-700">All</Link>
        </div>
      )}
    </nav>
  );
}
