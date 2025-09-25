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

interface RawPattern { examples?: { id: string; content: string }[] }

async function loadRawPatterns(): Promise<RawPattern[]> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

async function getActualPatternsCount(): Promise<number> {
  const patterns = await loadRawPatterns();
  return patterns.length;
}

async function getTotalExamplesCount(): Promise<number> {
  const patterns = await loadRawPatterns();
  return patterns.reduce((sum, p) => sum + (p.examples?.length || 0), 0);
}

export default async function HomePage() {
  const patternCategories = await getPatternCategories();
  // Load semantic assignments if available to override counts
  const semantic = loadSemanticOverrides();
  const actualPatternCount = await getActualPatternsCount();
  const totalExamples = await getTotalExamplesCount();

  return (
  <div className="min-h-screen bg-base">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-primary mb-4">
            Prompt Pattern Dictionary
          </h1>
          <p className="text-xl text-secondary max-w-3xl mx-auto mb-8">
            A comprehensive, searchable collection of prompt engineering patterns. 
            Discover, learn, and apply proven prompt patterns from academic research.
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
              Orientation / How to Use
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto mb-12" aria-label="Dataset statistics">
            <Link href="/patterns" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{actualPatternCount}</div>
              <div className="text-sm text-secondary">Patterns</div>
            </Link>
            <Link href="/search?mode=example" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted" aria-label={`View all ${totalExamples} prompt examples`}>
              <div className="text-2xl font-bold text-success">{totalExamples}</div>
              <div className="text-sm text-secondary">Examples</div>
            </Link>
            <Link href="/logic" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{patternCategories.logics.length}</div>
              <div className="text-sm text-secondary">Logic Layers</div>
            </Link>
            <Link href="/categories" className="bg-surface-1 rounded-lg p-4 shadow-md hover:shadow-lg transition border border-muted">
              <div className="text-2xl font-bold text-accent">{patternCategories.meta.totalCategories}</div>
              <div className="text-sm text-secondary">Categories</div>
            </Link>
          </div>
        </div>

        {/* Search Section */}
        <SearchInterface />

        {/* Similarity Features */}
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
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

        {/* Browse by Category */}
        <div className="max-w-6xl mx-auto mb-16">
          <div className="flex items-baseline justify-between mb-2">
            <h2 className="text-3xl font-semibold text-primary text-center md:text-left">
              Browse by Category
            </h2>
            <div className="flex items-center gap-3">
              {semantic && (
        <span title="Counts use semantic category assignments"
          className="inline-flex items-center gap-1 text-xs bg-surface-2 text-secondary border border-muted rounded px-2 py-1">
                  Semantic counts
                </span>
              )}
              <Link href="/taxonomy" className="text-sm text-accent hover:underline">View Taxonomy</Link>
            </div>
          </div>
          {/* Logic Groups */}
          <div className="space-y-8">
            {patternCategories.logics.map((logic: Logic) => (
              <div key={logic.slug} className="bg-surface-1 rounded-xl shadow-lg p-6 border border-muted">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-primary mb-2">
                    {logic.name} Logic
                  </h3>
                  <p className="text-secondary text-sm mb-2">
                    {logic.focus}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {logic.categories.map((category: Category) => (
                    <Link
                      key={category.slug}
                      href={`/category/${category.slug}`}
                      className="block bg-surface-2 hover:bg-surface-hover rounded-lg p-4 transition-colors border border-muted hover:border-accent"
                    >
                      <h4 className="text-md font-medium text-accent mb-1">
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
            Why Use This Dictionary?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Research-Based</h3>
              <p className="text-secondary text-sm">
                All patterns are extracted from peer-reviewed academic research papers with proper citations.
              </p>
            </div>
            
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Practical Examples</h3>
              <p className="text-secondary text-sm">
                Each pattern includes real-world examples you can copy and adapt for your use cases.
              </p>
            </div>
            
            <div className="bg-surface-1 rounded-lg p-6 shadow-md border border-muted">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Security Focused</h3>
              <p className="text-secondary text-sm">
                Specialized in cybersecurity applications with security considerations for each pattern.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
