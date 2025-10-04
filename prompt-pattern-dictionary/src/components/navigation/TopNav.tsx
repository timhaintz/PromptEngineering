"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import ThemeSwitcher from '@/components/ThemeSwitcher';

const tabs = [
  { href: '/orientation', label: 'Orientation' },
  { href: '/logic', label: 'Logic' },
  { href: '/categories', label: 'Categories' },
  { href: '/patterns', label: 'Patterns' },
  { href: '/examples', label: 'Examples' },
  { href: '/papers', label: 'Papers' },
  { href: '/taxonomy', label: 'Taxonomy' },
  { href: '/search', label: 'Search' },
];

export default function TopNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Global navigation" className="fixed top-0 left-0 right-0 z-50 bg-surface-1/80 backdrop-blur border-b border-muted">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-2 flex items-center gap-2 md:gap-3">
        {/* Home button with house icon */}
        <Link
          href="/"
          className="inline-flex items-center gap-1 rounded-md border border-muted bg-surface-2 px-2.5 py-1.5 text-sm text-secondary shadow-sm hover:bg-surface-hover focus-ring shrink-0 transition-colors"
          aria-label="Go to homepage"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" aria-hidden="true" role="img" aria-label="Home icon">
            <path d="M11.47 3.84a.75.75 0 011.06 0l7 7a.75.75 0 01-1.06 1.06L18.5 10.03V18a2 2 0 01-2 2h-9a2 2 0 01-2-2v-7.97l-1.97 1.87a.75.75 0 11-1.06-1.06l7-7z" />
          </svg>
          <span aria-hidden>Home</span>
        </Link>

        {/* Tabs */}
        <div className="flex-1 overflow-x-auto overflow-y-visible" style={{ WebkitOverflowScrolling: 'touch' }}>
          <nav
            aria-label="Primary"
            className="flex items-center gap-1 min-w-max px-1 md:px-0 md:justify-center"
          >
            {tabs.map(tab => {
              const isActive = pathname.startsWith(tab.href);
              return (
                <Link
                  key={tab.href}
                  aria-current={isActive ? 'page' : undefined}
                  href={tab.href}
                  className={`px-3 py-1.5 text-sm rounded-md border transition-colors focus-ring shrink-0 ${isActive ? 'active-pill font-medium' : 'bg-surface-2 text-secondary border-muted hover:bg-surface-hover'}`}
                >
                  {tab.label}
                </Link>
              );
            })}
            {/* Theme switcher access within scroll area on small screens */}
            <div className="md:hidden ml-1 shrink-0">
              <ThemeSwitcher />
            </div>
          </nav>
        </div>

        {/* Theme Switcher */}
        <div className="hidden md:flex shrink-0 items-center h-9">
          <ThemeSwitcher />
        </div>
      </div>
    </nav>
  );
}
