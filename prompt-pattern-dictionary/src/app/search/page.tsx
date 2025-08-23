/**
 * Search Results Page
 * 
 * Displays search results with filtering and pattern details
 */

'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

interface Pattern {
  id: string;
  patternName: string;
  description: string;
  category: string;
  original_paper_category?: string;
  semantic_categorization?: {
    category: string;
    confidence: number;
    top_alternatives: Array<{
      category: string;
      similarity: number;
    }>;
  };
  examples: Array<{
    id: string;
    content: string | object;
    index: number;
    semantic_categorization?: {
      category: string;
      confidence: number;
      top_alternatives: Array<{
        category: string;
        similarity: number;
      }>;
    };
  }>;
  paper: {
    apaReference: string;
    title?: string;
    authors?: string[];
    url?: string;
  };
  tags: string[];
  searchableContent: string;
}

function SearchResults() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [filteredPatterns, setFilteredPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [categoryType, setCategoryType] = useState<'original' | 'semantic'>('original');

  useEffect(() => {
    const loadPatterns = async () => {
      try {
        const response = await fetch('/data/patterns.json');
        const data = await response.json();
        setPatterns(data);
        
        // Filter patterns based on search query
        if (query) {
          const filtered = data.filter((pattern: Pattern) => 
            pattern.patternName.toLowerCase().includes(query.toLowerCase()) ||
            pattern.description.toLowerCase().includes(query.toLowerCase()) ||
            pattern.category.toLowerCase().includes(query.toLowerCase()) ||
            pattern.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
            pattern.examples.some(example => {
              const content = typeof example.content === 'string' ? example.content : JSON.stringify(example.content);
              return content.toLowerCase().includes(query.toLowerCase());
            })
          );
          setFilteredPatterns(filtered);
        } else {
          setFilteredPatterns(data);
        }
      } catch (error) {
        console.error('Error loading patterns:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPatterns();
  }, [query]);

  useEffect(() => {
    const baseFiltered = query ? patterns.filter((pattern: Pattern) => 
      pattern.patternName.toLowerCase().includes(query.toLowerCase()) ||
      pattern.description.toLowerCase().includes(query.toLowerCase()) ||
      pattern.category.toLowerCase().includes(query.toLowerCase()) ||
      (pattern.semantic_categorization?.category.toLowerCase().includes(query.toLowerCase())) ||
      pattern.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
      pattern.examples.some(example => {
        const content = typeof example.content === 'string' ? example.content : JSON.stringify(example.content);
        return content.toLowerCase().includes(query.toLowerCase());
      }) ||
      pattern.searchableContent.toLowerCase().includes(query.toLowerCase())
    ) : patterns;

    if (selectedCategory === 'all') {
      setFilteredPatterns(baseFiltered);
    } else {
      const categoryFiltered = baseFiltered.filter(pattern => {
        if (categoryType === 'semantic') {
          return pattern.semantic_categorization?.category === selectedCategory;
        } else {
          return (pattern.original_paper_category || pattern.category) === selectedCategory;
        }
      });
      setFilteredPatterns(categoryFiltered);
    }
  }, [selectedCategory, categoryType, patterns, query]);

  const originalCategories = [...new Set(patterns.map(p => p.original_paper_category || p.category))].sort();
  const semanticCategories = [...new Set(patterns.map(p => p.semantic_categorization?.category).filter(Boolean))].sort();
  const categories = categoryType === 'semantic' ? semanticCategories : originalCategories;

  const getPatternRoute = (patternId: string | undefined): string | undefined => {
    if (!patternId) return undefined;
    const parts = patternId.split('-');
    if (parts.length < 3) return undefined;
    const [paperId, categoryIndex, patternIndex] = parts;
    if (!paperId || !categoryIndex || !patternIndex) return undefined;
    return `/pattern/${paperId}/${categoryIndex}/${patternIndex}`;
  };

  const getExampleAnchor = (patternId: string, exampleIndex: number | undefined): string | undefined => {
    if (typeof exampleIndex !== 'number') return undefined;
    return `#example-${patternId}-${exampleIndex}`;
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
        {/* Header */}
        <div className="mb-8">
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Search Results
          </h1>
          {query && (
            <p className="text-gray-600">
              Showing results for &quot;<strong>{query}</strong>&quot; 
              ({filteredPatterns.length} patterns found)
            </p>
          )}
        </div>

        {/* Filters */}
        <div className="mb-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Category Type Toggle */}
              <div>
                <label htmlFor="category-type" className="block text-sm font-medium text-gray-700 mb-2">
                  Category Type:
                </label>
                <select
                  id="category-type"
                  value={categoryType}
                  onChange={(e) => {
                    setCategoryType(e.target.value as 'original' | 'semantic');
                    setSelectedCategory('all'); // Reset category selection
                  }}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="original">Original Paper Categories</option>
                  <option value="semantic">Semantic AI Categories</option>
                </select>
              </div>
              
              {/* Category Filter */}
              <div>
                <label htmlFor="category-filter" className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Category:
                </label>
                <select
                  id="category-filter"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Results Count */}
              <div className="flex items-end">
                <div className="text-sm text-gray-600">
                  <strong>{filteredPatterns.length}</strong> patterns found
                  {categoryType === 'semantic' && (
                    <div className="text-xs text-blue-600 mt-1">
                      Using AI semantic categories
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          {filteredPatterns.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No patterns found</h3>
              <p className="text-gray-600">
                Try adjusting your search terms or selecting a different category.
              </p>
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
                  <p className="text-gray-700 mb-4">{pattern.description}</p>
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
                                    {example.content}
                                  </Link>
                                ) : (
                                  <p className="text-gray-700 text-sm">{example.content}</p>
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
                        <a 
                          href={pattern.paper.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 ml-1"
                        >
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
                  
                  {/* Semantic categorization info */}
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
