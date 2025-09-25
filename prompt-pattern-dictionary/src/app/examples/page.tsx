import fs from 'fs';
import path from 'path';
import Link from 'next/link';

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
  examples?: { id: string; content: string }[];
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
      const excerpt = ex.content
        .replace(/\s+/g, ' ') // collapse whitespace
        .slice(0, 140)
        .trim();
      entries.push({
        exampleId: ex.id,
        patternId: p.id,
        patternName: p.patternName,
        category: p.category,
        excerpt: excerpt + (ex.content.length > 140 ? '…' : ''),
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

export default function ExamplesPage({ searchParams }: { searchParams: { page?: string; q?: string; group?: string } }) {
  const page = Math.max(1, parseInt(searchParams.page || '1', 10));
  const query = (searchParams.q || '').trim().toLowerCase();
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
    <div className="min-h-screen bg-base">
      <div className="container mx-auto px-4 py-16">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-primary mb-3">All Prompt Examples</h1>
          <p className="text-secondary max-w-2xl mx-auto">
            An alphabetical, paginated index of every example across all patterns. Use the quick filter to narrow results. Each row links back to the parent pattern.
          </p>
        </header>

        <form role="search" className="mb-6 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center" aria-label="Filter examples">
          <label className="flex-1">
            <span className="sr-only">Search examples</span>
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="Filter by text, pattern, or category…"
              className="w-full px-4 py-2 rounded-md border border-muted bg-surface-1 text-primary placeholder:text-tertiary focus-ring outline-none"
            />
          </label>
          <button type="submit" className="px-5 py-2 rounded-md bg-accent text-white font-medium hover:opacity-90 focus-ring">Filter</button>
          {query && (
            <Link href="/examples" className="px-4 py-2 rounded-md border border-muted bg-surface-1 text-secondary hover:bg-surface-hover focus-ring" aria-label="Clear filter">Clear</Link>
          )}
        </form>

        <div className="mb-4 text-sm text-secondary" aria-live="polite">
          Showing <span className="font-medium">{slice.length}</span> of <span className="font-medium">{total}</span> example{total !== 1 && 's'} (page {page} of {totalPages}){query && <> for query “{query}”</>}.
        </div>

        <ul className="space-y-3" aria-label="Example list">
          {slice.map(example => (
            <li key={example.exampleId} className="p-4 rounded-md bg-surface-1 border border-muted shadow-sm hover:shadow transition">
              <div className="flex flex-wrap items-baseline gap-2 mb-1">
                <code className="text-xs px-2 py-0.5 rounded bg-surface-2 border border-muted text-secondary" aria-label="Example ID">{example.exampleId}</code>
                <Link href={`/papers/${example.patternId.split('-')[0]}#e-${example.patternId}-${example.exampleId.split('-').slice(-1)}`} className="text-sm text-accent hover:underline" aria-label="Go to example in paper">Open</Link>
                <span className="text-xs px-2 py-0.5 rounded bg-surface-2 border border-muted text-secondary">{example.category}</span>
              </div>
              <div className="text-sm text-primary mb-1">{example.excerpt}</div>
              <div className="text-xs text-tertiary">Pattern: <Link href={`/patterns?focus=${example.patternId}`} className="text-accent hover:underline">{example.patternName}</Link></div>
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
                className={`min-w-[2.25rem] text-center rounded-md border px-2 py-1 text-sm focus-ring transition-colors ${isCurrent ? 'bg-accent text-white border-accent' : 'bg-surface-1 border-muted text-secondary hover:bg-surface-hover'}`}
              >
                {p}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
