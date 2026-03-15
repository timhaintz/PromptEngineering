import React from 'react';
import Link from 'next/link';

interface QuickPathItem { slug: string; title: string; description: string; href: string; }

const ITEMS: QuickPathItem[] = [
  { slug: 'defensive', title: 'Defensive Patterns', description: 'Discover patterns focused on security and mitigation.', href: '/search?mode=pattern&query=defensive' },
  { slug: 'adapt', title: 'Adapt an Existing Prompt', description: 'Learn principled adaptation & versioning.', href: '/orientation/adaptation' },
  { slug: 'evaluate', title: 'Evaluate Prompt Quality', description: 'Metrics & harness guidance for robust assessment.', href: '/orientation/quality-evaluation' },
  { slug: 'similar', title: 'Explore Similar Patterns', description: 'Use similarity suggestions to broaden candidates.', href: '/search?mode=pattern&similar=true' },
  { slug: 'clarity', title: 'Improve Clarity', description: 'Refine structure before wording for reliable outputs.', href: '/orientation/choosing-patterns' }
];

export function QuickPathsPanel() {
  return (
    <section aria-labelledby="quick-paths-heading" className="mt-8">
      <h2 id="quick-paths-heading" className="text-xl font-semibold mb-3">
        Quick Paths
      </h2>
      <p className="text-sm text-secondary mb-4">Common intents to accelerate onboarding. Choose one to jump directly to guidance.</p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {ITEMS.map(item => (
          <div key={item.slug} className="group border border-muted rounded-lg bg-surface-1 p-3 shadow-sm focus-within:outline-none focus-within:ring-2 focus-within:ring-accent" role="group" aria-labelledby={`qp-${item.slug}-title`}>
            <h3 id={`qp-${item.slug}-title`} className="text-sm font-semibold mb-1">{item.title}</h3>
            <p className="text-xs text-secondary mb-2 leading-relaxed">{item.description}</p>
            <Link
              href={item.href}
              className="inline-flex items-center gap-1 text-xs font-medium text-accent hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded"
              aria-label={`Go to ${item.title}`}
            >
              Open <span aria-hidden="true">→</span>
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}
