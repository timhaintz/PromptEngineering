import fs from 'fs';
import path from 'path';
import Link from 'next/link';

interface Example { id: string; index: number; content: string }
interface Pattern { id: string; patternName: string; description?: string; examples: Example[]; category: string; paper: { title: string; authors: string[]; url: string }; tags?: string[] }
interface NormalizedPattern { id: string; aiAssisted?: boolean; aiAssistedFields?: string[]; turn?: string }
interface Category { name: string; slug: string }
interface Logic { name: string; slug: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[] }

type SearchParams = { enriched?: string; logic?: string; category?: string; turn?: string; sort?: string; q?: string; tags?: string; letter?: string };

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function idParts(patternId: string): { paperId: string; categoryIndex: string; patternIndex: string } {
  const [paperId, categoryIndex, patternIndex] = patternId.split('-');
  return { paperId, categoryIndex, patternIndex };
}

function buildCategoryAndLogicMaps(data: PatternCategoriesData) {
  const categorySlugToName = new Map<string, string>();
  const categoryNameToLogicSlug = new Map<string, string>();
  const logicSlugToName = new Map<string, string>();
  const logicOptions: { value: string; label: string }[] = [];
  const categoryOptions: { value: string; label: string; logicSlug: string }[] = [];
  for (const l of data.logics) {
    logicSlugToName.set(l.slug, l.name);
    logicOptions.push({ value: l.slug, label: `${l.name}` });
    for (const c of l.categories) {
      categorySlugToName.set(c.slug, c.name);
      categoryNameToLogicSlug.set(c.name, l.slug);
      categoryOptions.push({ value: c.slug, label: c.name, logicSlug: l.slug });
    }
  }
  return { categorySlugToName, categoryNameToLogicSlug, logicSlugToName, logicOptions, categoryOptions };
}

function hasNormalizedObjectPatterns(val: unknown): val is { patterns: NormalizedPattern[] } {
  if (!val || typeof val !== 'object') return false;
  const obj = val as { patterns?: unknown };
  return Array.isArray(obj.patterns);
}

function parseTagsCsv(csv?: string): string[] {
  if (!csv) return [];
  return csv.split(',').map(t => t.trim()).filter(Boolean);
}

function joinTagsCsv(tags: string[]): string {
  return tags.join(',');
}

function buildQuery(current: SearchParams, updates: Partial<SearchParams>, removals: (keyof SearchParams)[] = []): string {
  const q = new URLSearchParams();
  const merged: Record<string, string> = {};
  // start with current
  for (const [k, v] of Object.entries(current)) {
    if (!v) continue;
    merged[k] = v as string;
  }
  // apply updates
  for (const [k, v] of Object.entries(updates)) {
    if (v === undefined || v === null || v === '') delete merged[k];
    else merged[k] = String(v);
  }
  // removals
  for (const r of removals) delete merged[r as string];
  // write
  for (const [k, v] of Object.entries(merged)) q.set(k, v);
  const s = q.toString();
  return s ? `?${s}` : '';
}

function initialLetter(str: string): string {
  if (!str) return '#';
  const ch = str[0].toUpperCase();
  return /[A-Z]/.test(ch) ? ch : '#';
}

export default async function PatternsPage({ searchParams }: { searchParams?: Promise<SearchParams> }) {
  const params = (await searchParams) || {};
  const onlyEnriched = params.enriched === '1';
  const logicFilter = params.logic || '';
  const categoryFilter = params.category || '';
  const turnFilter = params.turn || '';
  const sort = params.sort || 'name_asc';
  const q = (params.q || '').toLowerCase();
  const selectedTags = parseTagsCsv(params.tags);
  const letterFilter = (params.letter || '').toUpperCase();

  const patterns = loadJson<Pattern[]>('public/data/patterns.json');
  const normalizedRaw = loadJson<{ patterns: NormalizedPattern[] } | NormalizedPattern[] | null>('public/data/normalized-patterns.json');
  const normalizedArr = Array.isArray(normalizedRaw)
    ? normalizedRaw
    : (hasNormalizedObjectPatterns(normalizedRaw) ? normalizedRaw.patterns : []);
  const normMap = new Map<string, NormalizedPattern>(normalizedArr.map(n => [n.id, n]));

  const catData = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  const { categorySlugToName, categoryNameToLogicSlug, logicOptions, categoryOptions } = buildCategoryAndLogicMaps(catData);

  // Resolve category filter to category name for matching against patterns.json
  const selectedCategoryName = categoryFilter ? (categorySlugToName.get(categoryFilter) || '') : '';

  // Build tag counts
  const tagCounts = new Map<string, number>();
  for (const p of patterns) {
    for (const t of (p.tags || [])) {
      tagCounts.set(t, (tagCounts.get(t) || 0) + 1);
    }
  }
  const topTags = Array.from(tagCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 24)
    .map(([tag, count]) => ({ tag, count }));

  // Apply filters
  let filtered = patterns.filter(p => {
    if (onlyEnriched && !normMap.get(p.id)?.aiAssisted) return false;
    if (logicFilter) {
      const logicOfCategory = categoryNameToLogicSlug.get(p.category);
      if (logicOfCategory !== logicFilter) return false;
    }
    if (selectedCategoryName) {
      if (p.category !== selectedCategoryName) return false;
    }
    if (turnFilter) {
      const t = (normMap.get(p.id)?.turn || '').toLowerCase();
      if (!t || t !== turnFilter.toLowerCase()) return false;
    }
    if (letterFilter) {
      const init = initialLetter(p.patternName);
      if (init !== letterFilter) return false;
    }
    if (q) {
      const hay = `${p.patternName} ${p.description || ''} ${(p.tags || []).join(' ')} ${p.paper.title}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (selectedTags.length) {
      const tags = new Set((p.tags || []).map(t => t.toLowerCase()));
      for (const t of selectedTags) {
        if (!tags.has(t.toLowerCase())) return false;
      }
    }
    return true;
  });

  // Sorting
  filtered = filtered.sort((a, b) => {
    switch (sort) {
      case 'name_desc':
        return b.patternName.localeCompare(a.patternName);
      case 'examples_asc':
        return a.examples.length - b.examples.length;
      case 'examples_desc':
        return b.examples.length - a.examples.length;
      case 'name_asc':
      default:
        return a.patternName.localeCompare(b.patternName);
    }
  });

  // Limit categories in the dropdown when a logic is selected
  const visibleCategoryOptions = logicFilter ? categoryOptions.filter(c => c.logicSlug === logicFilter) : categoryOptions;

  // Active filter badges
  const activeBadges: { label: string; removeHref: string }[] = [];
  if (onlyEnriched) activeBadges.push({ label: 'Enriched', removeHref: buildQuery(params, {}, ['enriched']) });
  if (logicFilter) activeBadges.push({ label: `Logic: ${logicOptions.find(o => o.value === logicFilter)?.label || logicFilter}` , removeHref: buildQuery(params, {}, ['logic']) });
  if (selectedCategoryName) activeBadges.push({ label: `Category: ${selectedCategoryName}`, removeHref: buildQuery(params, {}, ['category']) });
  if (turnFilter) activeBadges.push({ label: `Turn: ${turnFilter}`, removeHref: buildQuery(params, {}, ['turn']) });
  if (letterFilter) activeBadges.push({ label: `Starts with: ${letterFilter}`, removeHref: buildQuery(params, {}, ['letter']) });
  if (q) activeBadges.push({ label: `Search: ${q}`, removeHref: buildQuery(params, { q: '' }) });
  for (const t of selectedTags) {
    const newTags = selectedTags.filter(x => x.toLowerCase() !== t.toLowerCase());
    activeBadges.push({ label: `Tag: ${t}`, removeHref: buildQuery(params, { tags: joinTagsCsv(newTags) }) });
  }

  // Alphabet bar
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'.split('');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="mb-4 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-900">All Patterns ({filtered.length})</h1>
          <form method="get" className="rounded-lg p-3 shadow border flex flex-col md:flex-row md:items-end gap-3 bg-white dark:bg-slate-800 dark:border-slate-600 hc:bg-black/70 hc:border-slate-500 transition-colors">
            <div className="flex flex-col">
              <label htmlFor="q" className="text-xs text-gray-600">Search</label>
              <input
                id="q"
                name="q"
                defaultValue={params.q || ''}
                placeholder="Search name, description, tags, paper"
                className="border rounded px-2 py-1 text-sm w-56 bg-white text-gray-800 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 dark:placeholder-slate-400 hc:bg-black/60 hc:text-white hc:border-slate-500"
              />
            </div>
            <div className="flex flex-col">
              <label htmlFor="sort" className="text-xs text-gray-600">Sort</label>
              <select id="sort" name="sort" defaultValue={sort} className="border rounded px-2 py-1 text-sm bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hc:bg-black/60 hc:text-white hc:border-slate-500">
                <option value="name_asc">Name (A→Z)</option>
                <option value="name_desc">Name (Z→A)</option>
                <option value="examples_asc">Examples (Few→Many)</option>
                <option value="examples_desc">Examples (Many→Few)</option>
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="logic" className="text-xs text-gray-600">Logic</label>
              <select id="logic" name="logic" defaultValue={logicFilter} className="border rounded px-2 py-1 text-sm bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hc:bg-black/60 hc:text-white hc:border-slate-500">
                <option value="">All</option>
                {logicOptions.map(o => (<option key={o.value} value={o.value}>{o.label}</option>))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="category" className="text-xs text-gray-600">Category</label>
              <select id="category" name="category" defaultValue={categoryFilter} className="border rounded px-2 py-1 text-sm bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hc:bg-black/60 hc:text-white hc:border-slate-500">
                <option value="">All</option>
                {visibleCategoryOptions.map(o => (<option key={o.value} value={o.value}>{o.label}</option>))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="turn" className="text-xs text-gray-600">Turn</label>
              <select id="turn" name="turn" defaultValue={turnFilter} className="border rounded px-2 py-1 text-sm bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hc:bg-black/60 hc:text-white hc:border-slate-500">
                <option value="">All</option>
                <option value="single">Single</option>
                <option value="multi">Multi</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="enriched" name="enriched" value="1" defaultChecked={onlyEnriched} className="h-4 w-4" />
              <label htmlFor="enriched" className="text-sm text-gray-700">Enriched only</label>
            </div>
            <div className="flex items-center gap-2">
              <button type="submit" className="bg-blue-800 hover:bg-blue-900 text-white text-sm px-3 py-1 rounded">Apply</button>
              <Link href="/patterns" className="text-sm text-gray-600 hover:text-gray-800">Reset</Link>
            </div>
          </form>
        </div>

        {/* Active filter badges */}
        {activeBadges.length ? (
          <div className="mb-4 flex flex-wrap gap-2">
            {activeBadges.map((b, i) => (
              <Link key={i} href={b.removeHref || '/patterns'} className="inline-flex items-center gap-1 border rounded-full px-2 py-1 text-xs text-gray-700 hover:border-blue-300 bg-white dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hc:bg-black/60 hc:text-white hc:border-slate-500">
                <span>{b.label}</span>
                <span className="text-gray-500">×</span>
              </Link>
            ))}
          </div>
        ) : null}

        {/* Alphabet jump bar */}
        <div className="mb-4 flex flex-wrap items-center gap-1">
          <span className="text-xs text-gray-600 mr-2">Jump to:</span>
          {letters.map(l => (
            <Link key={l} href={buildQuery(params, { letter: l === letterFilter ? '' : l })} className={`inline-block px-2 py-1 text-xs rounded border transition-colors ${l === letterFilter ? 'bg-blue-700 text-white border-blue-800' : 'bg-white text-gray-700 border-gray-300 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hover:border-blue-300 hc:bg-black/60 hc:text-white hc:border-slate-500'}`}>
              {l}
            </Link>
          ))}
        </div>

        {/* Top tag chips */}
        <div className="mb-6">
          <div className="text-xs text-gray-600 mb-1">Top tags</div>
          <div className="flex flex-wrap gap-2">
            {topTags.map(({ tag, count }) => {
              const has = selectedTags.some(t => t.toLowerCase() === tag.toLowerCase());
              const newTags = has ? selectedTags.filter(t => t.toLowerCase() !== tag.toLowerCase()) : [...selectedTags, tag];
              const href = buildQuery(params, { tags: joinTagsCsv(newTags) });
              return (
                <Link key={tag} href={href} className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs transition-colors ${has ? 'bg-blue-700 text-white border-blue-800' : 'bg-white text-gray-700 border-gray-300 dark:bg-slate-700 dark:text-slate-100 dark:border-slate-500 hover:border-blue-300 hc:bg-black/60 hc:text-white hc:border-slate-500'}`}> 
                  <span>{tag}</span>
                  <span className="text-slate-600">{count}</span>
                </Link>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(p => {
            const norm = normMap.get(p.id);
            const parts = idParts(p.id);
            const href = `/papers/${parts.paperId}#p-${parts.categoryIndex}-${parts.patternIndex}`;
            return (
              <Link key={p.id} href={href} className="block rounded-lg p-4 border hover:border-blue-300 hover:shadow bg-white dark:bg-slate-800 dark:border-slate-600 dark:hover:border-blue-400 hc:bg-black/70 hc:border-slate-500 transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-semibold text-gray-900 break-words whitespace-normal flex-1">{p.patternName}</h2>
                      <span className="inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 text-[10px] font-semibold">{p.category}</span>
                      {norm?.aiAssisted ? (
                        <span title={`AI-assisted fields: ${(norm.aiAssistedFields || []).join(', ')}`}
                              className="inline-flex items-center rounded-full bg-yellow-50 text-yellow-800 border border-yellow-200 px-2 py-0.5 text-[10px] font-semibold">
                          AI-assisted
                        </span>
                      ) : null}
                    </div>
                    {p.description ? (
                      <p className="text-sm text-gray-700 mt-1 line-clamp-2">{p.description}</p>
                    ) : null}
                    <div className="mt-2 text-xs text-gray-600">Examples: {p.examples.length}{norm?.turn ? ` • ${norm.turn === 'multi' ? 'Multi' : 'Single'}` : ''}</div>
                  </div>
                  <span className="text-[10px] text-gray-500 font-mono">{p.id}</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
