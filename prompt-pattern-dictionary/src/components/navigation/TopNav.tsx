"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const tabs = [
  { href: '/logic', label: 'Logic' },
  { href: '/categories', label: 'Categories' },
  { href: '/patterns', label: 'Patterns' },
  { href: '/papers', label: 'Papers' },
  { href: '/matrix', label: 'Matrix' },
  { href: '/semantic', label: 'Semantic' },
  { href: '/taxonomy', label: 'Taxonomy' },
  { href: '/search', label: 'Search' },
];

export default function TopNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Global navigation" className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur border-b border-gray-200">
      <div className="container mx-auto px-3 py-2 flex items-center gap-3">
        {/* Home button with house icon */}
        <Link
          href="/"
          className="inline-flex items-center gap-1 rounded-md border border-gray-300 bg-white px-2.5 py-1.5 text-sm text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 shrink-0"
          aria-label="Go to homepage"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" aria-hidden="true" role="img" aria-label="Home icon">
            <path d="M11.47 3.84a.75.75 0 011.06 0l7 7a.75.75 0 01-1.06 1.06L18.5 10.03V18a2 2 0 01-2 2h-9a2 2 0 01-2-2v-7.97l-1.97 1.87a.75.75 0 11-1.06-1.06l7-7z" />
          </svg>
          <span aria-hidden>Home</span>
        </Link>

        {/* Tabs */}
        <div className="flex-1 overflow-x-auto">
          <nav aria-label="Primary" className="flex items-center gap-1 min-w-max">
            {tabs.map(tab => {
              const isActive = pathname.startsWith(tab.href);
              return (
                <Link
                  key={tab.href}
                  aria-current={isActive ? 'page' : undefined}
                  href={tab.href}
                  className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${isActive ? 'bg-blue-600 text-white border-blue-700' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                >
                  {tab.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </nav>
  );
}
