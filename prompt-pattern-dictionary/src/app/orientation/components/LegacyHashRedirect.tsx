"use client";
import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';

// Mapping legacy hash -> target route strategy.
// If value starts with '/' treat as direct route (no hash). If contains '#', navigate to that hash on consolidated page.
// For now, we route known section ids to their dedicated page and fall back to /orientation/all for unknown hashes.
const sectionSlugs = [
  'quick-start','what-is-a-pattern','pattern-anatomy','lifecycle','choosing-patterns','combining-patterns','adaptation','anti-patterns','quality-evaluation','accessibility-responsible-use','glossary','faq','feedback','next-steps'
];

export default function LegacyHashRedirect() {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const hash = window.location.hash.replace('#','');
    if (!hash) return;

    // If already on all page, let native anchor behavior occur.
    if (pathname === '/orientation/all') return;

    // Direct match to a section slug: navigate to that page.
    if (sectionSlugs.includes(hash) && pathname !== `/orientation/${hash}`) {
      // Replace history to avoid stacking.
      router.replace(`/orientation/${hash}`);
      return;
    }

    // Otherwise, send to consolidated page with original hash.
    if (hash && pathname !== '/orientation/all') {
      router.replace(`/orientation/all#${hash}`);
    }
  // run only once on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}
