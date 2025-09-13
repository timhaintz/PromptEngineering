import React from 'react';
import OrientationNav from './components/OrientationNav';

export default function OrientationLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 lg:py-14">
      <div className="grid lg:grid-cols-[260px_1fr] gap-10" id="orientation-layout">
        <aside className="hidden lg:block sticky top-24 self-start">
          <OrientationNav variant="sidebar" />
        </aside>
        <div className="min-w-0" id="orientation-main">
          {children}
        </div>
      </div>
    </div>
  );
}
