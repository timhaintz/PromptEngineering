import Link from 'next/link';
import fs from 'fs';
import path from 'path';
import SearchInterface from '@/components/search/SearchInterface';
import { loadPatternCategories, loadSemanticOverrides } from '@/lib/data/categories';
import type { PatternCategoriesData, Category, Logic } from '@/lib/data/categories';

// Use shared types from lib/data/categories to avoid duplication

async function getPatternCategories(): Promise<PatternCategoriesData> {
  return loadPatternCategories();
}

interface RawPattern {
  examples?: { id: string; content: string }[];
  paper?: { id: string };
}

async function loadRawPatterns(): Promise<RawPattern[]> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

async function getDatasetStats(): Promise<{ patternCount: number; exampleCount: number; sourceCount: number }> {
  const patterns = await loadRawPatterns();
  return {
    patternCount: patterns.length,
    exampleCount: patterns.reduce((sum, pattern) => sum + (pattern.examples?.length || 0), 0),
    sourceCount: new Set(patterns.map(pattern => pattern.paper?.id).filter(Boolean)).size,
  };
}

function getLogicSummary(logic: Logic): string {
  const detailed = logic.detailedDescription?.trim();
  if (detailed) {
    const firstParagraph = detailed.split('\n\n')[0] ?? detailed;
    return firstParagraph.replace(/\*\*(.*?)\*\*/g, '$1');
  }
  return logic.focus;
}

export default async function HomePage() {
  const patternCategories = await getPatternCategories();
  // Load semantic assignments if available to override counts
  const semantic = loadSemanticOverrides();
  const datasetStats = await getDatasetStats();
  const showExperimentalTools = process.env.NEXT_PUBLIC_SHOW_EXPERIMENTAL_TOOLS === 'true';

  return (
  <div className="min-h-screen bg-base">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-primary mb-4">
            Ballarat AI Prompt Taxonomy
          </h1>
          <p className="text-xl text-secondary max-w-3xl mx-auto mb-8">
            Explore {datasetStats.patternCount} prompt patterns and {datasetStats.exampleCount} examples
            drawn from {datasetStats.sourceCount} cited sources, organized into six prepositional logic types.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
            <Link
              href="/patterns"
              className="inline-flex items-center gap-2 rounded-md bg-surface-1 text-accent border border-accent px-6 py-3 font-medium shadow hover:bg-surface-hover focus:outline-none focus-ring"
            >
              Browse Patterns
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
            <Link href="/orientation" className="inline-flex items-center gap-2 rounded-md border border-accent text-accent bg-surface-1 px-6 py-3 font-medium shadow hover:bg-surface-hover focus:outline-none focus-ring">
              Start with the Guide
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto mb-12" aria-label="Dataset statistics">
            <Link href="/patterns" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{datasetStats.patternCount}</div>
              <div className="text-sm text-secondary">Patterns</div>
            </Link>
            <Link href="/examples" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted" aria-label={`View all ${datasetStats.exampleCount} prompt examples`}>
              <div className="text-2xl font-bold text-success">{datasetStats.exampleCount}</div>
              <div className="text-sm text-secondary">Examples</div>
            </Link>
            <Link href="/papers" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{datasetStats.sourceCount}</div>
              <div className="text-sm text-secondary">Sources</div>
            </Link>
            <Link href="/categories" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{patternCategories.meta.totalCategories}</div>
              <div className="text-sm text-secondary">Taxonomy Categories</div>
            </Link>
          </div>
        </div>

        {/* Search Section */}
        <SearchInterface />

        {/* Similarity Features */}
        {showExperimentalTools && (
        <div className="max-w-6xl mx-auto mb-16">
          <h2 className="text-3xl font-semibold text-primary mb-8 text-center">
            AI-Powered Analysis Tools
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Semantic Analysis */}
            <Link
              href="/semantic"
              className="block bg-surface-1 rounded-xl shadow-lg hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-accent"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-primary mb-2">
                    Semantic Category Matrix
                  </h3>
                  <p className="text-secondary mb-4">
                    Explore dual categorization with AI-powered semantic analysis. Compare original paper categories 
                    with semantic categories and discover pattern-example relationships.
                  </p>
                  <div className="flex items-center text-accent font-medium">
                    Explore Matrix
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </Link>

            {/* Pattern Comparison */}
            <Link
              href="/comparison"
              className="block bg-surface-1 rounded-xl shadow-lg hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-accent"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-primary mb-2">
                    Pattern Comparison
                  </h3>
                  <p className="text-secondary mb-4">
                    Compare multiple patterns side-by-side using semantic similarity analysis. 
                    Discover relationships and validate your approach with quantitative similarity scores.
                  </p>
                  <div className="flex items-center text-accent font-medium">
                    Compare Patterns
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </Link>

            {/* Similarity Playground */}
            <Link
              href="/playground"
              className="block bg-surface-1 rounded-xl shadow-lg hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-accent"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-primary mb-2">
                    Similarity Playground
                  </h3>
                  <p className="text-secondary mb-4">
                    Describe your prompt goal in natural language and discover the most relevant 
                    patterns using AI-powered semantic search and similarity matching.
                  </p>
                  <div className="flex items-center text-accent font-medium">
                    Try Playground
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>
        )}

        {/* Browse by Category */}
        <div className="max-w-6xl mx-auto mb-16">
          <div className="flex items-baseline justify-between mb-2">
            <h2 className="text-3xl font-semibold text-primary text-center md:text-left">
              Browse the Semantic Taxonomy
            </h2>
            <div className="flex items-center gap-3">
              {semantic && (
        <span title={`Counts use semantic category assignments for ${semantic.meta?.totalPatterns ?? 'the embedded'} patterns`}
          className="inline-flex items-center gap-1 text-xs bg-surface-2 text-secondary border border-muted rounded px-2 py-1">
                  {semantic.meta?.totalPatterns ? `${semantic.meta.totalPatterns} semantically assigned` : 'Semantic counts'}
                </span>
              )}
              <Link href="/taxonomy" className="text-sm text-accent hover:underline">View Taxonomy</Link>
            </div>
          </div>
          <p className="text-sm text-secondary mb-8 max-w-3xl">
            The {patternCategories.meta.totalCategories} normalized categories below span {patternCategories.logics.length} logic layers.
            They are distinct from the original category labels used by individual sources.
            {semantic?.meta?.totalPatterns && semantic.meta.totalPatterns < datasetStats.patternCount
              ? ` Current category counts cover ${semantic.meta.totalPatterns} embedded patterns; ${datasetStats.patternCount - semantic.meta.totalPatterns} patterns await semantic analysis.`
              : ''}
          </p>
          {/* Logic Groups */}
          <div className="space-y-8">
            {patternCategories.logics.map((logic: Logic) => (
              <div key={logic.slug} className="bg-surface-1 rounded-xl shadow-lg p-6 border border-muted">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-primary mb-2">
                    {logic.name} Logic
                  </h3>
                  <p className="text-secondary text-sm mb-2 whitespace-pre-line">
                    {getLogicSummary(logic)}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {logic.categories.map((category: Category) => (
                    <Link
                      key={category.slug}
                      href={`/category/${category.slug}`}
                      className="block bg-surface-2 hover:bg-surface-hover rounded-lg p-4 transition-colors border border-muted hover:border-accent"
                    >
                      <h4 className="text-md font-medium text-secondary mb-1">
                        {category.name}
                      </h4>
                      <p className="text-secondary text-sm">
                        {(semantic?.categories?.[category.slug]?.patternCount ?? category.patternCount)} patterns
                      </p>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-semibold text-primary mb-8">
            Why Use This Taxonomy?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center mx-auto mb-4 border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Traceable Sources</h3>
              <p className="text-secondary text-sm">
                Every pattern links back to its cited source, including research papers, websites, and repositories.
              </p>
            </div>
            
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center mx-auto mb-4 border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Practical Examples</h3>
              <p className="text-secondary text-sm">
                Source-provided prompt examples can be inspected and adapted, with responsible-use guidance for applied work.
              </p>
            </div>
            
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
                  <div className="w-12 h-12 surface-card rounded-lg flex items-center justify-center mx-auto mb-4 border border-muted">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Research Taxonomy</h3>
              <p className="text-secondary text-sm">
                Compare source-paper labels with a consistent six-layer taxonomy designed for cross-paper analysis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
