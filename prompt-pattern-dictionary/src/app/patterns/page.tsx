import fs from 'fs';
import path from 'path';
import Link from 'next/link';

interface Example { id: string; index: number; content: string }
interface Pattern { id: string; patternName: string; description?: string; examples: Example[]; category: string; paper: { title: string; authors: string[]; url: string }; tags?: string[] }
interface NormalizedPattern { id: string; aiAssisted?: boolean; aiAssistedFields?: string[]; turn?: string }
interface Category { name: string; slug: string }
interface Logic { name: string; slug: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[] }

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

export default async function PatternsPage({ searchParams }: { searchParams?: Promise<{ enriched?: string; logic?: string; category?: string; turn?: string; sort?: string }> }) {
  const params = (await searchParams) || {};
  const onlyEnriched = params.enriched === '1';
  const logicFilter = params.logic || '';
  const categoryFilter = params.category || '';
  const turnFilter = params.turn || '';
  const sort = params.sort || 'name_asc';

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="mb-6 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-900">All Patterns ({filtered.length})</h1>
          <form method="get" className="bg-white rounded-lg p-3 shadow border flex flex-col md:flex-row md:items-end gap-3">
            <div className="flex flex-col">
              <label htmlFor="sort" className="text-xs text-gray-600">Sort</label>
              <select id="sort" name="sort" defaultValue={sort} className="border rounded px-2 py-1 text-sm">
                <option value="name_asc">Name (A→Z)</option>
                <option value="name_desc">Name (Z→A)</option>
                <option value="examples_asc">Examples (Few→Many)</option>
                <option value="examples_desc">Examples (Many→Few)</option>
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="logic" className="text-xs text-gray-600">Logic</label>
              <select id="logic" name="logic" defaultValue={logicFilter} className="border rounded px-2 py-1 text-sm">
                <option value="">All</option>
                {logicOptions.map(o => (<option key={o.value} value={o.value}>{o.label}</option>))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="category" className="text-xs text-gray-600">Category</label>
              <select id="category" name="category" defaultValue={categoryFilter} className="border rounded px-2 py-1 text-sm">
                <option value="">All</option>
                {visibleCategoryOptions.map(o => (<option key={o.value} value={o.value}>{o.label}</option>))}
              </select>
            </div>
            <div className="flex flex-col">
              <label htmlFor="turn" className="text-xs text-gray-600">Turn</label>
              <select id="turn" name="turn" defaultValue={turnFilter} className="border rounded px-2 py-1 text-sm">
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
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-3 py-1 rounded">Apply</button>
              <Link href="/patterns" className="text-sm text-gray-600 hover:text-gray-800">Reset</Link>
            </div>
          </form>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(p => {
            const norm = normMap.get(p.id);
            const parts = idParts(p.id);
            const href = `/pattern/${parts.paperId}/${parts.categoryIndex}/${parts.patternIndex}`;
            return (
              <Link key={p.id} href={href} className="block bg-white rounded-lg p-4 border hover:border-blue-300 hover:shadow">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-semibold text-gray-900 truncate">{p.patternName}</h2>
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
