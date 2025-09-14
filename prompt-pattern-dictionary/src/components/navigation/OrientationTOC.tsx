"use client";
import React, { useEffect, useState } from 'react';

interface SectionDef { id: string; label: string; }
interface OrientationTOCProps { sections: SectionDef[]; }

export default function OrientationTOC({ sections }: OrientationTOCProps) {
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
      { rootMargin: '0px 0px -70% 0px', threshold: [0, 0.1, 0.25] }
    );
    sections.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [sections]);

  return (
    <nav aria-label="Orientation sections" className="mb-12">
      <ul className="flex flex-wrap gap-2 text-sm">
        {sections.map(s => {
          const isActive = s.id === active;
          return (
            <li key={s.id}>
              <a
                href={`#${s.id}`}
                className={`inline-block px-3 py-1 rounded-full border focus:outline-none focus:ring-2 focus:ring-gray-700 transition-colors ${isActive ? 'bg-gray-900 text-white border-gray-900 hover:bg-black' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-100'}`}
                aria-current={isActive ? 'true' : undefined}
              >
                {s.label}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
