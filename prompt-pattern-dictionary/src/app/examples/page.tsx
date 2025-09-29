import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import { PageHeader } from '@/components/ui/PageHeader';
import Badge from '@/components/ui/Badge';

interface PatternExampleEntry {
  exampleId: string;
  patternId: string;
  patternName: string;
  category: string;
  excerpt: string;
}

interface RawPattern {
  id: string;
  patternName: string;
  category: string;
  examples?: { id: string; content: unknown }[];
}

function loadPatterns(): RawPattern[] {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const text = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(text);
}

function buildExampleIndex(): PatternExampleEntry[] {
  const patterns = loadPatterns();
  const entries: PatternExampleEntry[] = [];
  for (const p of patterns) {
    for (const ex of p.examples || []) {
      if (typeof ex.content !== 'string') continue;
      const raw = ex.content;
      const excerpt = raw
        .replace(/\s+/g, ' ') // collapse whitespace
        .slice(0, 140)
        .trim();
      entries.push({
        exampleId: ex.id,
        patternId: p.id,
        patternName: p.patternName,
        category: p.category,
        excerpt: excerpt + (raw.length > 140 ? '…' : ''),
      });
    }
  }
  // Alphabetical by excerpt first token (case-insensitive)
  entries.sort((a, b) => a.excerpt.toLowerCase().localeCompare(b.excerpt.toLowerCase()));
  return entries;
}

export const metadata = {
  title: 'All Prompt Examples',
  description: 'Alphabetical index of all prompt examples across patterns with quick navigation.',
};

const PAGE_SIZE = 100; // initial conservative page size; adjust if needed

// NOTE: Next.js 15 internal type generation currently expects `searchParams` to be assignable
// to `Promise<any> | undefined` (seen in .next/types/... checkFields). Our earlier explicit
// union including a plain object caused a constraint failure. Using `any` keeps compatibility
// while we normalize at runtime and still retain some local safety below.
// When Next exposes a stable PageProps type that includes the object form again, we can tighten this.
// Define a minimal structural type that is still broad enough for Next.js internals.
// We include an index signature (string -> unknown) so we can refine later.
// Optionally promise-like to satisfy internal PageProps constraint.
export default async function ExamplesPage({ searchParams }: { searchParams?: Promise<unknown> }) {
  // Resolve (or no-op) the search params; Next may provide a promise.
  const resolved = searchParams ? await searchParams : undefined;
  const sp = (resolved && typeof resolved === 'object' ? resolved : {}) as Record<string, string | string[] | undefined>;
  const pageParam = Array.isArray(sp.page) ? sp.page[0] : sp.page;
  const qParam = Array.isArray(sp.q) ? sp.q[0] : sp.q;
  const page = Math.max(1, parseInt(pageParam || '1', 10));
  const query = (qParam || '').trim().toLowerCase();
  const all = buildExampleIndex();

  const filtered = query
    ? all.filter(e =>
        e.excerpt.toLowerCase().includes(query) ||
        e.patternName.toLowerCase().includes(query) ||
        e.category.toLowerCase().includes(query)
      )
    : all;

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = (page - 1) * PAGE_SIZE;
  const slice = filtered.slice(start, start + PAGE_SIZE);

  return (
    <PageShell>
      <div className="space-y-8">
        <PageHeader heading="All Prompt Examples" subtitle="Alphabetical, filterable index of every example. Each links to its parent pattern." />

  <form role="search" className="mb-6 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center" aria-label="Filter examples">
          <label className="flex-1">
            <span className="sr-only">Search examples</span>
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="Filter by text, pattern, or category…"
              className="input-base w-full px-3 py-2"
            />
          </label>
          <button type="submit" className="btn-primary">Filter</button>
          {query && (
            <Link href="/examples" className="pill-filter" aria-label="Clear filter">Clear</Link>
          )}
        </form>

        <div className="mb-4 text-sm text-secondary" aria-live="polite">
          Showing <span className="font-medium">{slice.length}</span> of <span className="font-medium">{total}</span> example{total !== 1 && 's'} (page {page} of {totalPages}){query && <> for query “{query}”</>}.
        </div>

        <ul className="space-y-3" aria-label="Example list">
          {slice.map(example => (
            <li key={example.exampleId} className="surface-card p-4 hover:surface-card-hover transition">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <code className="badge-id" aria-label="Example ID">{example.exampleId}</code>
                <Link href={`/papers/${example.patternId.split('-')[0]}#e-${example.patternId}-${example.exampleId.split('-').slice(-1)}`} className="pill-filter text-xs" aria-label="Go to example in paper">Open</Link>
                <Badge variant="category" className="text-[10px] font-semibold">{example.category}</Badge>
              </div>
              <div className="text-sm text-secondary mb-1">{example.excerpt}</div>
              <div className="text-xs text-muted">Pattern: <Link href={`/patterns?focus=${example.patternId}`} className="text-secondary hover:text-primary focus-ring rounded-sm px-0.5">{example.patternName}</Link></div>
            </li>
          ))}
        </ul>

        {/* Pagination */}
        <nav className="mt-8 flex items-center justify-center gap-2" aria-label="Examples pagination">
          {Array.from({ length: totalPages }).map((_, i) => {
            const p = i + 1;
            const isCurrent = p === page;
            const params = new URLSearchParams();
            if (query) params.set('q', query);
            if (p !== 1) params.set('page', String(p));
            const href = `/examples${params.toString() ? `?${params.toString()}` : ''}`;
            return (
              <Link
                key={p}
                href={href}
                aria-current={isCurrent ? 'page' : undefined}
                className={`min-w-[2.25rem] text-center rounded-md border px-2 py-1 text-sm focus-ring transition-colors ${isCurrent ? 'active-pill' : 'bg-surface-1 border-muted text-secondary hover:bg-surface-hover'}`}
              >
                {p}
              </Link>
            );
          })}
        </nav>
      </div>
    </PageShell>
  );
}
