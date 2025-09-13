import React from 'react';
import OrientationNav from './components/OrientationNav';
import LegacyHashRedirect from './components/LegacyHashRedirect';
import ReadabilityControls from './components/ReadabilityControls';

export default function OrientationLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 lg:py-14">
      <LegacyHashRedirect />
      <div className="grid lg:grid-cols-[260px_1fr] gap-10" id="orientation-layout">
        <aside className="hidden lg:flex flex-col gap-4 sticky top-24 self-start">
          <ReadabilityControls />
          <OrientationNav variant="sidebar" />
        </aside>
        <div className="min-w-0" id="orientation-main">
          {/* Secondary placement for controls on small screens */}
          <div className="lg:hidden mb-6"><ReadabilityControls /></div>
          {children}
        </div>
      </div>
    </div>
  );
}
