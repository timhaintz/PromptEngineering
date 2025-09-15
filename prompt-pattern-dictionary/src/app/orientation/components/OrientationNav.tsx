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
                <Link href={`/orientation/${s.slug}`} className={`flex gap-2 rounded px-2 py-1 border-l-4 leading-snug transition-colors focus-ring ${active ? 'bg-[var(--color-accent-active-bg)] border-[var(--color-accent)] text-primary font-medium' : 'border-transparent text-secondary hover:bg-surface-hover hover:border-muted'}`} aria-current={active ? 'page' : undefined}>
                  <span className="text-secondary w-6 tabular-nums text-right select-none" aria-hidden="true">{s.number}.</span>
                  <span className="flex-1">{s.title}</span>
                </Link>
              </li>
            );
          })}
          <li className="pt-2 mt-2 border-t border-muted"><Link href="/orientation/all" className="block px-2 py-1 text-secondary hover:text-primary hover:bg-surface-hover rounded">All Sections</Link></li>
          <li><Link href="/orientation/cheatsheet" className="block px-2 py-1 text-secondary hover:text-primary hover:bg-surface-hover rounded">Cheat Sheet</Link></li>
        </ul>
      ) : (
        <div className="flex flex-wrap gap-2">
          {ORIENTATION_SECTIONS.map(s => (
            <Link key={s.slug} href={`/orientation/${s.slug}`} className="text-xs px-3 py-1 rounded-full border border-muted bg-surface-1 hover:bg-surface-hover text-secondary hover:text-primary transition-colors">{s.number}. {s.title}</Link>
          ))}
          <Link href="/orientation/all" className="text-xs px-3 py-1 rounded-full border border-muted bg-surface-1 hover:bg-surface-hover text-secondary hover:text-primary transition-colors">All</Link>
        </div>
      )}
    </nav>
  );
}
