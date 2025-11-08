import React from 'react';
import OrientationNav from './components/OrientationNav';
import LegacyHashRedirect from './components/LegacyHashRedirect';
import ProvenanceBadge from '@/components/ProvenanceBadge';

export default function OrientationLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 lg:py-14" id="orientation-container">
      <LegacyHashRedirect />
      {/* Skip Links (P0 Accessibility): become visible on focus */}
      <div className="sr-only focus-within:not-sr-only absolute left-4 top-4 z-50 flex flex-col gap-2" aria-label="Skip links">
        <a href="#orientation-main" className="focus-ring px-3 py-2 rounded bg-surface-2 border border-muted text-xs font-medium text-secondary">Skip to content</a>
        <a href="#orientation-nav" className="focus-ring px-3 py-2 rounded bg-surface-2 border border-muted text-xs font-medium text-secondary">Skip to section navigation</a>
      </div>
      <div className="grid lg:grid-cols-[260px_1fr] gap-10" id="orientation-layout">
        <aside className="hidden lg:flex flex-col gap-4 sticky top-24 self-start">
          <OrientationNav variant="sidebar" />
        </aside>
        <div className="min-w-0" id="orientation-main">
          <ProvenanceBadge context="orientation" className="mb-6" />
          {/* Readability controls removed (font size & width). Browser zoom / reader modes recommended. */}
          {children}
        </div>
      </div>
    </div>
  );
}
