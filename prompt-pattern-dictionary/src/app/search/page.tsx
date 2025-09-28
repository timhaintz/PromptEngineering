/**
 * Search Page (smart)
 * - Blank by default (no results until a query or filter is set)
 * - Search type dropdown: Logic | Category | Prompt Pattern | Prompt Example
 * - Dynamic filters based on type
 */

'use client';

import { useMemo, useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { parseBooleanQuery, evaluateBooleanQuery } from '@/lib/search/booleanQuery';
import React from 'react';

interface Pattern {
  id: string;
  patternName: string;
  description: string;
  category: string;
  original_paper_category?: string;
  semantic_categorization?: { category: string; confidence: number };
  examples: Array<{ id: string; content: string | object; index: number }>;
  paper: { apaReference: string; title?: string; authors?: string[]; url?: string };
  tags: string[];
  searchableContent: string;
}

type Logic = { name: string; slug: string; focus: string; categories: { name: string; slug: string; patternCount: number }[] };
type PatternCategoriesData = { logics: Logic[] };
type SemanticAssignments = { categories: Record<string, { name: string; slug: string; logic?: string; patternCount: number }> };

type SearchType = 'logic' | 'category' | 'pattern' | 'example';

function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';
  const type = (searchParams.get('type') as SearchType) || 'pattern';
  const urlCategoryType = (searchParams.get('catType') as 'original' | 'semantic') || 'original';
  const urlSelectedCategory = searchParams.get('cat') || '';
  const urlLogic = searchParams.get('logic') || '';
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [catData, setCatData] = useState<PatternCategoriesData | null>(null);
  const [semantic, setSemantic] = useState<SemanticAssignments | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categoryType, setCategoryType] = useState<'original' | 'semantic'>('original');
  const [logicFilter, setLogicFilter] = useState<string>('');
  const [useBoolean, setUseBoolean] = useState<boolean>(false);
  const [fuzzyDistance, setFuzzyDistance] = useState<number>(0);
  const [showHelp, setShowHelp] = useState<boolean>(false);

  // Sync state from URL on load and when URL changes
  useEffect(() => {
    if (categoryType !== urlCategoryType) setCategoryType(urlCategoryType);
    if (selectedCategory !== urlSelectedCategory) setSelectedCategory(urlSelectedCategory);
    if (logicFilter !== urlLogic) setLogicFilter(urlLogic);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlCategoryType, urlSelectedCategory, urlLogic]);

  useEffect(() => {
    const loadAll = async () => {
      try {
        const [pRes, cRes, sRes] = await Promise.all([
          fetch('/data/patterns.json'),
          fetch('/data/pattern-categories.json'),
          fetch('/data/semantic-assignments.json').catch(() => null),
        ]);
        const pData = await pRes.json();
        setPatterns(pData);
        if (cRes) setCatData(await cRes.json());
        if (sRes && 'ok' in sRes && sRes.ok) setSemantic(await sRes.json());
      } catch (error) {
        console.error('Error loading search data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAll();
  }, []);

  const originalCategories = useMemo(() => [...new Set(patterns.map(p => p.original_paper_category || p.category))].sort(), [patterns]);
  const semanticCategories = useMemo(() => [...new Set(patterns.map(p => p.semantic_categorization?.category).filter(Boolean))].sort(), [patterns]);
  const categories = categoryType === 'semantic' ? semanticCategories : originalCategories;

  // Derived results for patterns/examples
  const { root: booleanAst } = useMemo(() => {
    if (!useBoolean || !query.trim()) return { root: null } as { root: null };
    return parseBooleanQuery(query);
  }, [query, useBoolean]);

  const highlightTerms = useMemo(() => {
    if (!query) return [] as string[];
    if (useBoolean && booleanAst) {
      // Re-parse to collect term nodes for highlighting
      const { terms } = parseBooleanQuery(query);
      return terms.map(t => t.value).filter(Boolean).slice(0, 15); // cap to avoid excessive spans
    }
    // Simple token split for legacy mode
    return query.toLowerCase().split(/\s+/).filter(w => w && w.length > 1).slice(0, 15);
  }, [query, useBoolean, booleanAst]);

  function applyHighlight(text: string): React.ReactNode {
    if (!highlightTerms.length) return <>{text}</>;
    let parts: Array<{ segment: string; match: boolean }> = [{ segment: text, match: false }];
    highlightTerms.forEach(term => {
      const newParts: typeof parts = [];
      const tLower = term.toLowerCase();
      parts.forEach(p => {
        if (p.match) { newParts.push(p); return; }
        let startIdx = 0; let idx;
        while ((idx = p.segment.toLowerCase().indexOf(tLower, startIdx)) !== -1) {
          if (idx > startIdx) newParts.push({ segment: p.segment.slice(startIdx, idx), match: false });
          newParts.push({ segment: p.segment.slice(idx, idx + term.length), match: true });
          startIdx = idx + term.length;
        }
        if (startIdx < p.segment.length) newParts.push({ segment: p.segment.slice(startIdx), match: false });
      });
      parts = newParts;
    });
    return <>{parts.map((p, i) => p.match ? <mark key={i} className="bg-yellow-200 text-gray-900 rounded px-0.5 shadow-[0_0_0_1px_rgba(0,0,0,0.05)]">{p.segment}</mark> : p.segment)}</>;
  }

  const filteredPatterns = useMemo(() => {
    if ((type === 'pattern' || type === 'example') && (!query && !selectedCategory)) return [];
    const text = query.toLowerCase();
    const inCategory = (p: Pattern) => {
      if (!selectedCategory) return true;
      return categoryType === 'semantic'
        ? p.semantic_categorization?.category === selectedCategory
        : (p.original_paper_category || p.category) === selectedCategory;
    };
    const patternMatchesBoolean = (p: Pattern) => {
      if (!booleanAst) return true; // handled earlier
      const fieldStrings: string[] = [
        p.patternName, p.description, p.category, p.searchableContent,
        p.tags.join(' '), p.semantic_categorization?.category || '',
        ...p.examples.map(ex => typeof ex.content === 'string' ? ex.content : JSON.stringify(ex.content))
      ].map(s => s.toLowerCase());
      return evaluateBooleanQuery(booleanAst, { fields: fieldStrings, defaultFuzzy: fuzzyDistance });
    };

    if (type === 'pattern') {
      return patterns.filter(p => inCategory(p) && (
        useBoolean
          ? patternMatchesBoolean(p)
          : (
            p.patternName.toLowerCase().includes(text) ||
            p.description.toLowerCase().includes(text) ||
            p.category.toLowerCase().includes(text) ||
            (p.semantic_categorization?.category?.toLowerCase().includes(text)) ||
            p.tags.some(t => t.toLowerCase().includes(text)) ||
            p.searchableContent.toLowerCase().includes(text)
          )
      ));
    }
    if (type === 'example') {
      return patterns.filter(p => inCategory(p) && (
        useBoolean ? patternMatchesBoolean(p) : p.examples.some(ex => {
          const content = typeof ex.content === 'string' ? ex.content : JSON.stringify(ex.content);
            return content.toLowerCase().includes(text);
          })
      ));
    }
    return [];
  }, [patterns, query, selectedCategory, categoryType, type, useBoolean, booleanAst, fuzzyDistance]);

  // Category search data
  const logicList = useMemo(() => catData?.logics ?? [], [catData]);
  const origCatOptions = useMemo(() => logicList.flatMap(l => l.categories.map(c => ({ ...c, logicSlug: l.slug, logicName: l.name }))), [logicList]);
  const semCatOptions = useMemo(() => {
    if (!semantic?.categories) return [] as Array<{ slug: string; name: string; patternCount: number; logicSlug?: string; logicName?: string }>;
    return Object.values(semantic.categories).map(c => ({ slug: c.slug, name: c.name, patternCount: c.patternCount, logicSlug: c.logic, logicName: c.logic ? logicList.find(l => l.slug === c.logic)?.name : undefined }));
  }, [semantic, logicList]);
  const categoryResults = useMemo(() => {
    if (type !== 'category') return [] as Array<{ slug: string; name: string; patternCount: number; logicSlug?: string; logicName?: string }>;
    if (!query && !logicFilter) return [];
    const text = query.toLowerCase();
    const source = categoryType === 'semantic' ? semCatOptions : origCatOptions;
    return source.filter(c => (
      (!logicFilter || c.logicSlug === logicFilter) && c.name.toLowerCase().includes(text)
    ));
  }, [type, categoryType, semCatOptions, origCatOptions, query, logicFilter]);

  // Logic search results
  const logicResults = useMemo(() => {
    if (type !== 'logic') return [] as Logic[];
    if (!query) return [];
    const text = query.toLowerCase();
    return logicList.filter(l => l.name.toLowerCase().includes(text) || l.focus.toLowerCase().includes(text));
  }, [type, query, logicList]);

  const getPatternRoute = (patternId: string | undefined): string | undefined => {
    if (!patternId) return undefined;
    const parts = patternId.split('-');
    if (parts.length < 3) return undefined;
    const [paperId, categoryIndex, patternIndex] = parts;
    if (!paperId || !categoryIndex || !patternIndex) return undefined;
    return `/papers/${paperId}#p-${categoryIndex}-${patternIndex}`;
  };

  const getExampleAnchor = (patternId: string, exampleIndex: number | undefined): string | undefined => {
    if (typeof exampleIndex !== 'number') return undefined;
    const [paperId, cIdx, pIdx] = patternId.split('-');
    if (!paperId || !cIdx || !pIdx) return undefined;
    return `#e-${cIdx}-${pIdx}-${exampleIndex}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-16">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Search</h1>
        </div>

        {/* Controls */}
  <div className="mb-6 rounded-lg shadow-md p-4 bg-white dark:bg-slate-800 dark:border-slate-600 hc:bg-black/70 transition-colors">
          <div className="flex flex-col md:flex-row gap-3 md:items-end">
            <div className="flex-1">
              <label htmlFor="search-input" className="block text-sm font-medium text-gray-800 mb-1">Search text</label>
              <input id="search-input" defaultValue={query} onChange={(e) => {
                const params = new URLSearchParams(Array.from(searchParams.entries()));
                params.set('q', e.target.value);
                params.set('type', type);
                router.replace(`/search?${params.toString()}`);
              }} placeholder={useBoolean ? 'e.g. chain AND reasoning NOT "few shot" prompt~1' : 'Type to search...'} className="w-full border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            {/* Boolean + Fuzzy Controls */}
            {(type === 'pattern' || type === 'example') && (
              <div className="flex flex-col gap-2 pt-6 md:pt-0">
                <label className="inline-flex items-center gap-2 text-sm text-gray-800">
                  <input type="checkbox" className="h-4 w-4" checked={useBoolean} onChange={(e) => setUseBoolean(e.target.checked)} />
                  Boolean + Fuzzy
                </label>
                <div className="flex items-center gap-2 text-xs text-gray-700">
                  <label htmlFor="fuzzy-distance" className="text-gray-700">Fuzzy</label>
                  <input id="fuzzy-distance" type="number" min={0} max={3} value={fuzzyDistance} disabled={!useBoolean} onChange={(e) => setFuzzyDistance(Math.max(0, Math.min(3, parseInt(e.target.value || '0', 10))))} className="w-14 border border-gray-300 rounded px-1 py-0.5 disabled:opacity-40" />
                  <button type="button" onClick={() => setShowHelp(s => !s)} className="text-blue-600 hover:text-blue-800">Help?</button>
                </div>
              </div>
            )}
            {showHelp && (
              <div className="absolute z-20 mt-24 md:mt-20 right-4 md:right-auto md:left-1/2 md:-translate-x-1/2 w-full md:w-96 bg-white border border-gray-300 shadow-lg rounded p-3 text-xs text-gray-700 space-y-2">
                <div className="flex justify-between items-center">
                  <strong className="text-gray-900">Boolean & Fuzzy Syntax</strong>
                  <button onClick={() => setShowHelp(false)} className="text-gray-500 hover:text-gray-800">✕</button>
                </div>
                <ul className="list-disc pl-4 space-y-1">
                  <li><code>AND</code>, <code>OR</code>, <code>NOT</code> (NOT has highest precedence).</li>
                  <li>Phrases: <code>&quot;chain of thought&quot;</code></li>
                  <li>Fuzzy: <code>prompt~1</code> (edit distance ≤ 1). Global fuzzy applied if checkbox set.</li>
                  <li>Implicit AND between adjacent terms.</li>
                  <li>Examples: <code>reasoning AND (NOT translation)</code> (parentheses future).</li>
                </ul>
                <p className="text-[11px] text-gray-500">Parentheses not yet supported; logic evaluates NOT &gt; AND &gt; OR.</p>
              </div>
            )}
            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-800 mb-1">Search type</label>
              <select id="type" value={type} onChange={(e) => {
                const params = new URLSearchParams(Array.from(searchParams.entries()));
                params.set('type', e.target.value);
                router.replace(`/search?${params.toString()}`);
              }} className="w-48 border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <option value="pattern">Prompt Pattern</option>
                <option value="example">Prompt Example</option>
                <option value="category">Category</option>
                <option value="logic">Logic</option>
              </select>
            </div>
            {(type === 'pattern' || type === 'example' || type === 'category') && (
              <div>
                <label htmlFor="category-type-select" className="block text-sm font-medium text-gray-800 mb-1">Category type</label>
                <select
                  id="category-type-select"
                  value={categoryType}
                  onChange={(e) => {
                    const val = e.target.value as 'original' | 'semantic';
                    setCategoryType(val);
                    const params = new URLSearchParams(Array.from(searchParams.entries()));
                    params.set('catType', val);
                    router.replace(`/search?${params.toString()}`);
                  }}
                  className="w-56 border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="original">Original Paper</option>
                  <option value="semantic">Semantic AI</option>
                </select>
              </div>
            )}
            {(type === 'pattern' || type === 'example') && (
              <div>
                <label htmlFor="category-filter-select" className="block text-sm font-medium text-gray-800 mb-1">Filter by category</label>
                <select
                  id="category-filter-select"
                  value={selectedCategory}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSelectedCategory(val);
                    const params = new URLSearchParams(Array.from(searchParams.entries()));
                    if (val) params.set('cat', val); else params.delete('cat');
                    router.replace(`/search?${params.toString()}`);
                  }}
                  className="w-56 border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All</option>
                  {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            )}
            {type === 'category' && (
              <div>
                <label htmlFor="logic-filter-select" className="block text-sm font-medium text-gray-800 mb-1">Filter by logic</label>
                <select
                  id="logic-filter-select"
                  value={logicFilter}
                  onChange={(e) => {
                    const val = e.target.value;
                    setLogicFilter(val);
                    const params = new URLSearchParams(Array.from(searchParams.entries()));
                    if (val) params.set('logic', val); else params.delete('logic');
                    router.replace(`/search?${params.toString()}`);
                  }}
                  className="w-56 border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All</option>
                  {logicList.map(l => <option key={l.slug} value={l.slug}>{l.name}</option>)}
                </select>
              </div>
            )}
            <div className="ml-auto flex items-end gap-3 text-sm text-gray-800">
              <span>
                {type === 'pattern' || type === 'example'
                  ? (filteredPatterns.length > 0 ? `${filteredPatterns.length} result(s)` : 'No results yet')
                  : type === 'category'
                    ? (categoryResults.length > 0 ? `${categoryResults.length} category(s)` : 'No results yet')
                    : (logicResults.length > 0 ? `${logicResults.length} logic group(s)` : 'No results yet')}
              </span>
              <button
                type="button"
                className="inline-flex items-center rounded border border-gray-300 px-2 py-1 text-xs bg-white text-gray-800 hover:bg-gray-50"
                onClick={() => {
                  const params = new URLSearchParams();
                  params.set('type', 'pattern');
                  router.replace(`/search?${params.toString()}`);
                  setSelectedCategory('');
                  setCategoryType('original');
                  setLogicFilter('');
                }}
              >
                Clear all
              </button>
            </div>
          </div>
        </div>

        {/* Pattern/Example Results */}
        {(type === 'pattern' || type === 'example') && (
          <div className="space-y-6">
            {filteredPatterns.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-700">
                Start by entering a query or choose filters above.
              </div>
            ) : (
              filteredPatterns.map((pattern) => (
                <div key={pattern.id} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        {(() => {
                          const route = getPatternRoute(pattern.id);
                          return route ? (
                            <Link href={route} className="text-xl font-semibold text-blue-700 hover:text-blue-900">
                              {pattern.patternName}
                            </Link>
                          ) : (
                            <h3 className="text-xl font-semibold text-gray-900">{pattern.patternName}</h3>
                          );
                        })()}
                        {pattern.id && (
                          <span className="shrink-0 inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 text-xs font-medium">
                            ID: {pattern.id}
                          </span>
                        )}
                      </div>
                      <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                        {pattern.category}
                      </span>
                    </div>
                  </div>

                  {pattern.description && (
                    <p className="text-gray-700 mb-4">{applyHighlight(pattern.description)}</p>
                  )}

                  {pattern.examples.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-md font-medium text-gray-900 mb-2">Examples:</h4>
                      <div className="space-y-2">
                        {pattern.examples.slice(0, 2).map((example) => {
                          const fullIndex = (typeof example.index === 'number' && pattern.id)
                            ? `${pattern.id}-${example.index}`
                            : undefined;
                          const route = getPatternRoute(pattern.id);
                          const anchor = pattern.id && typeof example.index === 'number' ? getExampleAnchor(pattern.id, example.index) : undefined;
                          const href = route && anchor ? `${route}${anchor}` : route;
                          return (
                            <div key={example.id} className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
                              <div className="flex items-start gap-2">
                                {fullIndex && (
                                  <span className="mt-0.5 inline-flex items-center rounded bg-gray-200 text-gray-800 px-1.5 py-0.5 text-[10px] font-semibold">
                                    {fullIndex}
                                  </span>
                                )}
                                {typeof example.content === 'string' ? (
                                  href ? (
                                    <Link href={href} className="text-blue-700 hover:text-blue-900 text-sm">
                                      {applyHighlight(example.content)}
                                    </Link>
                                  ) : (
                                    <p className="text-gray-700 text-sm">{applyHighlight(example.content)}</p>
                                  )
                                ) : (
                                  <div className="text-gray-700 text-sm">
                                    <div className="font-medium mb-2">Complex Example:</div>
                                    {href ? (
                                      <Link href={href} className="block">
                                        <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded max-h-32 overflow-y-auto">
                                          {JSON.stringify(example.content, null, 2)}
                                        </pre>
                                      </Link>
                                    ) : (
                                      <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded max-h-32 overflow-y-auto">
                                        {JSON.stringify(example.content, null, 2)}
                                      </pre>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                        {pattern.examples.length > 2 && (
                          <p className="text-sm text-gray-500">
                            +{pattern.examples.length - 2} more examples
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center text-sm text-gray-600">
                      <div>
                        <strong>Source:</strong>
                        {pattern.paper.url ? (
                          <a href={pattern.paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 ml-1">
                            {pattern.paper.title || pattern.paper.apaReference}
                          </a>
                        ) : (
                          <span className="ml-1">{pattern.paper.title || pattern.paper.apaReference}</span>
                        )}
                      </div>
                      {pattern.paper.authors && (
                        <div>
                          <strong>Authors:</strong> {pattern.paper.authors.join(', ')}
                        </div>
                      )}
                    </div>
                    {pattern.semantic_categorization && (
                      <div className="mt-2 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-600">Semantic Category:</span>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            {pattern.semantic_categorization.category}
                          </span>
                          <span className="text-gray-500">
                            ({(pattern.semantic_categorization.confidence * 100).toFixed(1)}% confidence)
                          </span>
                        </div>
                        {pattern.original_paper_category !== pattern.semantic_categorization.category && (
                          <div className="text-xs text-orange-600 mt-1">
                            ↗ Changed from: {pattern.original_paper_category || pattern.category}
                          </div>
                        )}
                      </div>
                    )}
                    {(() => {
                      const route = getPatternRoute(pattern.id);
                      return route ? (
                        <div className="mt-3">
                          <Link href={route} className="inline-flex items-center text-blue-700 hover:text-blue-900 text-sm">
                            View details →
                          </Link>
                        </div>
                      ) : null;
                    })()}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Category results */}
        {type === 'category' && (
          <div className="space-y-3">
            {categoryResults.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-600">Start by entering a query or choose filters above.</div>
            ) : (
              categoryResults.map(c => (
                <div key={c.slug} className="bg-white rounded p-4 border shadow-sm flex items-center justify-between">
                  <div>
                    <Link href={`/category/${c.slug}`} className="text-blue-700 hover:text-blue-900 font-medium">{c.name}</Link>
                    {c.logicName && <span className="ml-2 text-xs text-gray-600">({c.logicName})</span>}
                  </div>
                  <div className="text-xs text-gray-600">{c.patternCount ?? 0} patterns</div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Logic results */}
        {type === 'logic' && (
          <div className="space-y-4">
            {logicResults.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-600">Start by entering a query.</div>
            ) : (
              logicResults.map(l => (
                <div key={l.slug} className="bg-white rounded-lg p-6 shadow">
                  <div className="mb-1 text-lg font-semibold text-gray-900">{l.name} Logic</div>
                  <div className="text-sm text-gray-700 mb-3">{l.focus}</div>
                  <div className="flex flex-wrap gap-2">
                    {l.categories.map(c => (
                      <Link key={c.slug} href={`/category/${c.slug}`} className="inline-flex items-center rounded bg-gray-50 px-2 py-1 border hover:bg-blue-50 text-sm">
                        {c.name}
                        <span className="ml-2 text-[10px] text-gray-600">{c.patternCount}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-16">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    }>
      <SearchResults />
    </Suspense>
  );
}
