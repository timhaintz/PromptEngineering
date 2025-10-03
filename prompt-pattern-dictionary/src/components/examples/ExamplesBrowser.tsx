'use client';

import { useCallback, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Badge from '@/components/ui/Badge';
import { PageHeader } from '@/components/ui/PageHeader';

type PatternExampleEntry = {
  exampleId: string;
  patternId: string;
  patternName: string;
  category: string;
  excerpt: string;
};

const PAGE_SIZE = 100;

function buildPageHref(
  baseSearch: string,
  query: string,
  targetPage: number,
): string {
  const params = new URLSearchParams(baseSearch);
  if (query) {
    params.set('q', query);
  } else {
    params.delete('q');
  }

  if (targetPage !== 1) {
    params.set('page', String(targetPage));
  } else {
    params.delete('page');
  }

  const suffix = params.toString();
  return suffix ? `/examples?${suffix}` : '/examples';
}

interface ExamplesBrowserProps {
  entries: PatternExampleEntry[];
}

export function ExamplesBrowser({ entries }: ExamplesBrowserProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchParamsString = searchParams.toString();

  const query = useMemo(() => {
    const params = new URLSearchParams(searchParamsString);
    const raw = params.get('q');
    return raw ? raw.trim() : '';
  }, [searchParamsString]);

  const page = useMemo(() => {
    const params = new URLSearchParams(searchParamsString);
    const raw = params.get('page');
    const parsed = raw ? Number.parseInt(raw, 10) : 1;
    if (Number.isNaN(parsed) || parsed < 1) return 1;
    return parsed;
  }, [searchParamsString]);

  const loweredQuery = query.toLowerCase();

  const filtered = useMemo(() => {
    if (!loweredQuery) return entries;
    return entries.filter((entry) =>
      entry.excerpt.toLowerCase().includes(loweredQuery) ||
      entry.patternName.toLowerCase().includes(loweredQuery) ||
      entry.category.toLowerCase().includes(loweredQuery),
    );
  }, [entries, loweredQuery]);

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const slice = filtered.slice(startIndex, startIndex + PAGE_SIZE);

  const handleSubmit = useCallback(
    (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const nextQuery = (formData.get('q') as string | null)?.trim() ?? '';
      const params = new URLSearchParams(searchParamsString);
      if (nextQuery) {
        params.set('q', nextQuery);
      } else {
        params.delete('q');
      }
      params.delete('page');
      const suffix = params.toString();
      router.push(suffix ? `/examples?${suffix}` : '/examples');
    },
    [router, searchParamsString],
  );

  const handleClear = useCallback(() => {
    router.push('/examples');
  }, [router]);

  return (
    <div className="space-y-8">
      <PageHeader
        heading="All Prompt Examples"
        subtitle="Alphabetical, filterable index of every example. Each links to its parent pattern."
      />

      <form
        role="search"
        className="mb-6 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center"
        aria-label="Filter examples"
        onSubmit={handleSubmit}
      >
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
        {query ? (
          <button
            type="button"
            onClick={handleClear}
            className="pill-filter"
            aria-label="Clear filter"
          >
            Clear
          </button>
        ) : null}
      </form>

      <div className="mb-4 text-sm text-secondary" aria-live="polite">
        Showing <span className="font-medium">{slice.length}</span> of{' '}
        <span className="font-medium">{total}</span> example{total !== 1 && 's'} (page {currentPage} of {totalPages})
        {query && <> for query “{query}”</>}.
      </div>

      <ul className="space-y-3" aria-label="Example list">
        {slice.map((example) => {
          const [paperId, categoryIndex, patternIndex] = example.patternId.split('-');
          const exampleIndex = example.exampleId.split('-').pop();
            const exampleHref = paperId && categoryIndex && patternIndex && exampleIndex !== undefined
              ? `/papers/${paperId}#e-${categoryIndex}-${patternIndex}-${exampleIndex}`
            : undefined;
          return (
            <li key={example.exampleId} className="surface-card p-4 hover:surface-card-hover transition">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <code className="badge-id" aria-label="Example ID">{example.exampleId}</code>
                {exampleHref ? (
                  <Link href={exampleHref} className="pill-filter text-xs" aria-label="Go to example in paper">
                    Open
                  </Link>
                ) : null}
                <Badge variant="category" className="text-[10px] font-semibold">{example.category}</Badge>
              </div>
              <div className="text-sm text-secondary mb-1">{example.excerpt}</div>
              <div className="text-xs text-muted">
                Pattern:{' '}
                <Link
                  href={`/patterns?focus=${example.patternId}`}
                  className="text-secondary hover:text-primary focus-ring rounded-sm px-0.5"
                >
                  {example.patternName}
                </Link>
              </div>
            </li>
          );
        })}
      </ul>

      <nav className="mt-8 flex items-center justify-center gap-2" aria-label="Examples pagination">
        {Array.from({ length: totalPages }).map((_, idx) => {
          const target = idx + 1;
          const isCurrent = target === currentPage;
          const href = buildPageHref(searchParamsString, query, target);
          return (
            <Link
              key={target}
              href={href}
              aria-current={isCurrent ? 'page' : undefined}
              className={`min-w-[2.25rem] text-center rounded-md border px-2 py-1 text-sm focus-ring transition-colors ${
                isCurrent ? 'active-pill' : 'bg-surface-1 border-muted text-secondary hover:bg-surface-hover'
              }`}
            >
              {target}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
