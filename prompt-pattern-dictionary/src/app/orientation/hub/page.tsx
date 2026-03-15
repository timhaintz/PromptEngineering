import Link from 'next/link';
import { ORIENTATION_SECTIONS } from '../data/sections';
import { QuickPathsPanel } from '../components/QuickPathsPanel';
import OrientationNav from '../components/OrientationNav';

const AUDIENCE_MAP = [
  {
    role: 'Researchers',
    intent: 'Compare methodologies, cite provenance, and explore similarity evidence.',
    link: '/orientation/similarity-preview'
  },
  {
    role: 'Practitioners',
    intent: 'Grab defensive/monitoring patterns and evaluation harness tips.',
    link: '/orientation/quality-evaluation'
  },
  {
    role: 'Students',
    intent: 'Learn the pattern anatomy, glossary, and lifecycle fundamentals.',
    link: '/orientation/pattern-anatomy'
  },
  {
    role: 'Tool Builders',
    intent: 'Reuse templates, PEIL prompts, and similarity signals inside your apps.',
    link: '/orientation/quick-start'
  }
];

export const metadata = {
  title: 'Orientation Hub | Ballarat AI Prompt Dictionary',
  description: 'Hub for Orientation sections, quick start, and consolidated view.'
};

export default function OrientationHubPage() {
  const meta = ORIENTATION_SECTIONS.find(s => s.slug === 'hub');

  return (
    <article className="prose max-w-none text-primary">
      <h1 className="flex items-baseline gap-3">
        {meta ? <span className="text-muted font-medium">{meta.number}.</span> : null}{' '}
        {meta?.title ?? 'Orientation Hub'}
      </h1>
      <div className="not-prose">
        <p className="text-base font-semibold text-primary max-w-3xl leading-relaxed">A research-grounded prompt pattern dictionary for building safer, evaluable AI workflows&mdash;not a generic prompt dump.</p>
        <p className="text-secondary max-w-3xl leading-relaxed mb-4">Use this hub to jump into focused sections or view the full consolidated page. Each section is deliberately concise and accessible; the <em>All Sections</em> view preserves original anchor stability.</p>
        <div className="mb-6 rounded-lg border border-muted bg-surface-1 shadow-sm p-4 text-sm text-secondary">
          <p><strong className="text-primary">Static, provenance-first experience:</strong> similarity scores, enrichment, and PEIL prompts are precomputed from research artifacts. No live model calls run in your browser; bring your own tooling when you move from exploration to testing.</p>
        </div>
        <div className="mb-10 space-y-4">
          <section aria-labelledby="audience-map-heading" className="border border-muted rounded-lg bg-surface-1 p-4 shadow-sm">
            <h2 id="audience-map-heading" className="text-xl font-semibold mb-2">
              Role → Intent Map
            </h2>
            <p className="text-sm text-secondary mb-3">Pick the description closest to your goal to jump into the right Orientation section.</p>
            <div className="grid sm:grid-cols-2 gap-3">
              {AUDIENCE_MAP.map(item => (
                <Link key={item.role} href={item.link} className="group border border-muted rounded-md p-3 bg-surface-2 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent" aria-label={`${item.role} quick intent link`}>
                  <p className="text-xs uppercase tracking-wide text-secondary mb-1">{item.role}</p>
                  <p className="text-sm text-primary font-medium mb-1">{item.intent}</p>
                  <span className="text-xs text-accent font-semibold group-hover:underline">Go to guidance →</span>
                </Link>
              ))}
            </div>
          </section>
          <OrientationNav variant="inline" />
          <QuickPathsPanel />
        </div>

        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
          {ORIENTATION_SECTIONS.map(sec => (
            <div key={sec.slug} className="border border-muted rounded-lg p-4 bg-surface-1 shadow-sm hover:bg-surface-hover transition-colors">
              <h2 className="font-semibold text-primary text-lg flex items-baseline gap-2"><span className="text-muted tabular-nums">{sec.number}.</span>{' '}{sec.title}</h2>
              <p className="text-sm text-secondary mt-1 mb-3">{sec.description}</p>
              <Link href={sec.slug === 'about' ? '/orientation' : `/orientation/${sec.slug}`} className="text-accent text-sm font-medium hover:underline">Open Section →</Link>
            </div>
          ))}
          <div className="border border-muted rounded-lg p-4 bg-surface-2 shadow-sm hover:bg-surface-hover transition-colors">
            <h2 className="font-semibold text-primary text-lg flex items-baseline gap-2">All Sections</h2>
            <p className="text-sm text-secondary mt-1 mb-3">Read the complete Orientation content in one scrollable page (original format with anchors).</p>
              <Link href="/orientation/all" className="text-accent text-sm font-medium hover:underline">View All →</Link>
          </div>
          <div className="border border-muted rounded-lg p-4 bg-surface-1 shadow-sm hover:bg-surface-hover transition-colors">
            <h2 className="font-semibold text-primary text-lg flex items-baseline gap-2">Cheat Sheet</h2>
            <p className="text-sm text-secondary mt-1 mb-3">Condensed printable reference (5‑Key template, lifecycle, evaluation metrics, anti‑patterns, responsible use).</p>
              <Link href="/orientation/cheatsheet" className="text-accent text-sm font-medium hover:underline">Open Cheat Sheet →</Link>
          </div>
        </div>
      </div>
    </article>
  );
}
