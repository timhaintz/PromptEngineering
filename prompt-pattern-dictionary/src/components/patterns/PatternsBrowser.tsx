'use client';

import { useCallback, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import { Card, CardGrid } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { PageHeader } from '@/components/ui/PageHeader';
import { withBasePath } from '@/utils/paths';

type PatternSummary = {
  id: string;
  patternName: string;
  description?: string;
  category: string;
  tags: string[];
  exampleCount: number;
};

type NormalizedInfo = {
  aiAssisted?: boolean;
  aiAssistedFields?: string[];
  turn?: string | null;
};

type Option = {
  value: string;
  label: string;
};

type CategoryOption = Option & {
  logicSlug: string;
};

interface PatternsBrowserProps {
  patterns: PatternSummary[];
  normalized: Record<string, NormalizedInfo>;
  logicOptions: Option[];
  categoryOptions: CategoryOption[];
  categorySlugToName: Record<string, string>;
  categoryNameToLogicSlug: Record<string, string>;
}

type SearchParamsShape = {
  enriched?: string;
  logic?: string;
  category?: string;
  turn?: string;
  sort?: string;
  q?: string;
  tags?: string;
  letter?: string;
  focus?: string;
};

const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'.split('');

function parseTagsCsv(csv?: string): string[] {
  if (!csv) return [];
  return csv.split(',').map((tag) => tag.trim()).filter(Boolean);
}

function joinTagsCsv(tags: string[]): string {
  return tags.join(',');
}

function initialLetter(value: string): string {
  if (!value) return '#';
  const ch = value.charAt(0).toUpperCase();
  return /[A-Z]/.test(ch) ? ch : '#';
}

function buildQueryString(
  baseSearch: string,
  updates: Partial<SearchParamsShape>,
  removals: Array<keyof SearchParamsShape> = [],
): string {
  const params = new URLSearchParams(baseSearch);

  for (const [key, value] of Object.entries(updates)) {
    if (value === undefined || value === null || value === '') {
      params.delete(key);
    } else {
      params.set(key, String(value));
    }
  }

  for (const removal of removals) {
    params.delete(removal);
  }

  const suffix = params.toString();
  return suffix ? `?${suffix}` : '';
}

function idParts(patternId: string): { paperId: string; categoryIndex: string; patternIndex: string } {
  const [paperId, categoryIndex, patternIndex] = patternId.split('-');
  return { paperId, categoryIndex, patternIndex };
}

export function PatternsBrowser({
  patterns,
  normalized,
  logicOptions,
  categoryOptions,
  categorySlugToName,
  categoryNameToLogicSlug,
}: PatternsBrowserProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchParamsString = searchParams.toString();

  const params = useMemo(() => {
    const result: SearchParamsShape = {};
    const qs = new URLSearchParams(searchParamsString);
    qs.forEach((value, key) => {
      result[key as keyof SearchParamsShape] = value;
    });
    return result;
  }, [searchParamsString]);

  const onlyEnriched = params.enriched === '1';
  const logicFilter = params.logic || '';
  const categoryFilter = params.category || '';
  const turnFilter = params.turn || '';
  const sort = params.sort || 'name_asc';
  const q = (params.q || '').toLowerCase();
  const selectedTags = useMemo(() => parseTagsCsv(params.tags), [params.tags]);
  const letterFilter = (params.letter || '').toUpperCase();

  const selectedCategoryName = categoryFilter ? (categorySlugToName[categoryFilter] || '') : '';

  const tagCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const pattern of patterns) {
      for (const tag of pattern.tags) {
        counts.set(tag, (counts.get(tag) || 0) + 1);
      }
    }
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 24)
      .map(([tag, count]) => ({ tag, count }));
  }, [patterns]);

  const filteredPatterns = useMemo(() => {
    return patterns.filter((pattern) => {
      if (onlyEnriched && !normalized[pattern.id]?.aiAssisted) return false;
      if (logicFilter) {
        const logicSlug = categoryNameToLogicSlug[pattern.category];
        if (logicSlug !== logicFilter) return false;
      }
      if (selectedCategoryName && pattern.category !== selectedCategoryName) return false;
      if (turnFilter) {
        const turn = (normalized[pattern.id]?.turn || '').toLowerCase();
        if (!turn || turn !== turnFilter.toLowerCase()) return false;
      }
      if (letterFilter) {
        const initial = initialLetter(pattern.patternName);
        if (initial !== letterFilter) return false;
      }
      if (q) {
        const haystack = `${pattern.patternName} ${pattern.description || ''} ${pattern.tags.join(' ')}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (selectedTags.length) {
        const tagSet = new Set(pattern.tags.map((tag) => tag.toLowerCase()));
        for (const selected of selectedTags) {
          if (!tagSet.has(selected.toLowerCase())) return false;
        }
      }
      return true;
    });
  }, [
    patterns,
    normalized,
    onlyEnriched,
    logicFilter,
    selectedCategoryName,
    turnFilter,
    letterFilter,
    q,
    selectedTags,
    categoryNameToLogicSlug,
  ]);

  const sortedPatterns = useMemo(() => {
    const copy = [...filteredPatterns];
    switch (sort) {
      case 'name_desc':
        copy.sort((a, b) => b.patternName.localeCompare(a.patternName));
        break;
      case 'examples_asc':
        copy.sort((a, b) => a.exampleCount - b.exampleCount);
        break;
      case 'examples_desc':
        copy.sort((a, b) => b.exampleCount - a.exampleCount);
        break;
      case 'name_asc':
      default:
        copy.sort((a, b) => a.patternName.localeCompare(b.patternName));
        break;
    }
    return copy;
  }, [filteredPatterns, sort]);

  const visibleCategoryOptions = logicFilter
    ? categoryOptions.filter((option) => option.logicSlug === logicFilter)
    : categoryOptions;

  const buildHref = useCallback(
    (updates: Partial<SearchParamsShape>, removals: Array<keyof SearchParamsShape> = []) =>
      buildQueryString(searchParamsString, updates, removals),
    [searchParamsString],
  );

  const activeBadges = useMemo(() => {
    const badges: { label: string; href: string }[] = [];
    if (onlyEnriched) badges.push({ label: 'Enriched', href: buildHref({}, ['enriched']) });
    if (logicFilter) {
      const label = logicOptions.find((option) => option.value === logicFilter)?.label || logicFilter;
      badges.push({ label: `Logic: ${label}`, href: buildHref({}, ['logic']) });
    }
    if (selectedCategoryName) {
      badges.push({ label: `Category: ${selectedCategoryName}`, href: buildHref({}, ['category']) });
    }
    if (turnFilter) {
      badges.push({ label: `Turn: ${turnFilter}`, href: buildHref({}, ['turn']) });
    }
    if (letterFilter) {
      badges.push({ label: `Starts with: ${letterFilter}`, href: buildHref({}, ['letter']) });
    }
    if (q) {
      badges.push({ label: `Search: ${q}`, href: buildHref({ q: '' }) });
    }
    for (const tag of selectedTags) {
      const remaining = selectedTags.filter((item) => item.toLowerCase() !== tag.toLowerCase());
      badges.push({ label: `Tag: ${tag}`, href: buildHref({ tags: joinTagsCsv(remaining) }) });
    }
    return badges;
  }, [
    onlyEnriched,
    logicFilter,
    selectedCategoryName,
    turnFilter,
    letterFilter,
    q,
    selectedTags,
    buildHref,
    logicOptions,
  ]);

  const handleSubmit = useCallback(
    (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const next = new URLSearchParams(searchParamsString);

      const apply = (key: keyof SearchParamsShape, value: string | null) => {
        if (value && value.trim()) {
          next.set(key, value.trim());
        } else {
          next.delete(key);
        }
      };

      apply('q', (formData.get('q') as string) || '');
      apply('sort', (formData.get('sort') as string) || 'name_asc');
      apply('logic', (formData.get('logic') as string) || '');
      apply('category', (formData.get('category') as string) || '');
      apply('turn', (formData.get('turn') as string) || '');

      if (formData.get('enriched')) {
        next.set('enriched', '1');
      } else {
        next.delete('enriched');
      }

      next.delete('letter');

      const suffix = next.toString();
      router.push(suffix ? `/patterns?${suffix}` : '/patterns');
    },
    [router, searchParamsString],
  );

  const handleReset = useCallback(() => {
    router.push('/patterns');
  }, [router]);

  return (
    <PageShell>
      <div className="space-y-12">
        <div className="mb-4 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <PageHeader
            compact
            heading={<span>All Patterns <span className="text-muted font-normal">({sortedPatterns.length})</span></span>}
          />
          <form
            method="get"
            className="surface-card p-3 flex flex-col md:flex-row md:items-end gap-3"
            onSubmit={handleSubmit}
          >
            <div className="flex flex-col">
              <label htmlFor="patterns-q" className="text-xs text-muted">Search</label>
              <input
                id="patterns-q"
                name="q"
                defaultValue={params.q || ''}
                placeholder="Search name, description, tags, paper"
                className="input-base w-56"
              />
            </div>
            <div className="flex flex-col">
              <label htmlFor="patterns-sort" className="text-xs text-muted">Sort</label>
              <select id="patterns-sort" name="sort" defaultValue={sort} className="input-base">
                <option value="name_asc">Name (A→Z)</option>
                <option value="name_desc">Name (Z→A)</option>
                <option value="examples_asc">Examples (Few→Many)</option>
                <option value="examples_desc">Examples (Many→Few)</option>
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="patterns-logic" className="text-xs text-muted">Logic</label>
              <select id="patterns-logic" name="logic" defaultValue={logicFilter} className="input-base">
                <option value="">All</option>
                {logicOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="patterns-category" className="text-xs text-muted">Category</label>
              <select id="patterns-category" name="category" defaultValue={categoryFilter} className="input-base">
                <option value="">All</option>
                {visibleCategoryOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="patterns-turn" className="text-xs text-muted">Turn</label>
              <select id="patterns-turn" name="turn" defaultValue={turnFilter} className="input-base">
                <option value="">All</option>
                <option value="single">Single</option>
                <option value="multi">Multi</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="patterns-enriched" name="enriched" value="1" defaultChecked={onlyEnriched} className="h-4 w-4" />
              <label htmlFor="patterns-enriched" className="text-sm text-muted">Enriched only</label>
            </div>
            <div className="flex items-center gap-2">
              <button type="submit" className="btn-primary text-sm px-3 py-1">Apply</button>
              <button type="button" onClick={handleReset} className="text-sm text-muted hover:underline">Reset</button>
            </div>
          </form>
        </div>

        {activeBadges.length ? (
          <div className="mb-4 flex flex-wrap gap-2">
            {activeBadges.map((badge) => (
              <Link key={badge.label} href={badge.href || '/patterns'} className="chip-filter">
                <span>{badge.label}</span>
                <span className="text-muted">×</span>
              </Link>
            ))}
          </div>
        ) : null}

        <div className="mb-4 flex flex-wrap items-center gap-1">
          <span className="text-xs text-muted mr-2">Jump to:</span>
          {LETTERS.map((letter) => {
            const href = buildHref({ letter: letter === letterFilter ? '' : letter });
            const isActive = letter === letterFilter;
            return (
              <Link
                key={letter}
                href={href}
                className={`pill-filter ${isActive ? '!bg-[var(--accent)] !text-white !border-[var(--accent)]' : ''}`}
              >
                {letter}
              </Link>
            );
          })}
        </div>

        <div className="mb-6">
          <div className="text-xs text-muted mb-1">Top tags</div>
          <div className="flex flex-wrap gap-2">
            {tagCounts.map(({ tag, count }) => {
              const active = selectedTags.some((selected) => selected.toLowerCase() === tag.toLowerCase());
              const nextTags = active
                ? selectedTags.filter((selected) => selected.toLowerCase() !== tag.toLowerCase())
                : [...selectedTags, tag];
              const href = buildHref({ tags: joinTagsCsv(nextTags) });
              return (
                <Link
                  key={tag}
                  href={href}
                  className={`chip-filter ${active ? '!bg-[var(--accent)] !text-white !border-[var(--accent)]' : ''}`}
                >
                  <span>{tag}</span>
                  <span className="text-muted">{count}</span>
                </Link>
              );
            })}
          </div>
        </div>

        <CardGrid>
          {sortedPatterns.map((pattern) => {
            const norm = normalized[pattern.id];
            const { paperId, categoryIndex, patternIndex } = idParts(pattern.id);
            const href = withBasePath(`/papers/${paperId}#p-${categoryIndex}-${patternIndex}`);
            const turnLabel = norm?.turn ? (norm.turn === 'multi' ? 'Multi-turn' : 'Single-turn') : null;
            return (
              <Card key={pattern.id} href={href}>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="flex-1 text-primary font-semibold break-words leading-snug" title={pattern.patternName}>
                    {pattern.patternName}
                  </span>
                  <span className="badge-id text-[10px] font-semibold shrink-0">{pattern.id}</span>
                </div>
                <div className="flex flex-wrap gap-2 text-xs mb-2">
                  <Badge variant="category" className="text-[10px] font-semibold">{pattern.category}</Badge>
                  {norm?.aiAssisted ? (
                    <Badge
                      variant="ai"
                      className="text-[10px] font-semibold"
                      title={`AI-assisted fields: ${(norm.aiAssistedFields || []).join(', ')}`}
                    >
                      AI-assisted
                    </Badge>
                  ) : null}
                  {turnLabel ? (
                    <Badge variant="generic" className="text-[10px] font-semibold">{turnLabel}</Badge>
                  ) : null}
                </div>
                {pattern.description ? (
                  <p className="text-sm text-muted line-clamp-2">{pattern.description}</p>
                ) : null}
                <div className="mt-3 text-xs text-muted">
                  Examples: {pattern.exampleCount}
                </div>
              </Card>
            );
          })}
        </CardGrid>
      </div>
    </PageShell>
  );
}
