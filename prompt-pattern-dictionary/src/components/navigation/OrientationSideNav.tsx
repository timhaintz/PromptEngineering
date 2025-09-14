"use client";
import React, { useEffect, useState } from 'react';

interface SectionDef { id: string; label: string; number?: string; }
interface OrientationSideNavProps { sections: SectionDef[]; }

/*
  Vertical side navigation for the Orientation page.
  - Highlights active section using IntersectionObserver
  - Sticky positioning on large screens
  - Accessible list navigation with aria-current
*/
export default function OrientationSideNav({ sections }: OrientationSideNavProps) {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length > 0) {
          setActive(visible[0].target.id);
        }
      },
      { rootMargin: '0px 0px -65% 0px', threshold: [0, 0.1, 0.25] }
    );
    sections.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [sections]);

  return (
    <nav aria-label="Orientation section navigation" className="hidden lg:block sticky top-24 max-h-[calc(100vh-7rem)] overflow-auto pr-2 text-sm" data-orientation-sidenav>
      <ul className="space-y-1">
        {sections.map(s => {
          const isActive = s.id === active;
          return (
            <li key={s.id}>
              <a
                href={`#${s.id}`}
                className={`flex gap-2 rounded px-2 py-1 leading-snug border-l-4 transition-colors ${isActive ? 'bg-indigo-50 border-indigo-600 text-indigo-800 font-medium' : 'border-transparent text-slate-700 hover:bg-slate-50 hover:border-slate-300'}`}
                aria-current={isActive ? 'true' : undefined}
              >
                {s.number && <span className="text-slate-600 w-6 tabular-nums text-right select-none">{s.number}</span>}
                <span className="flex-1">{s.label}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
