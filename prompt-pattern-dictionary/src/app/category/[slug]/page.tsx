/**
 * Category Page
 * 
 * Displays all patterns in a specific category
 */

import { notFound } from 'next/navigation';
import Link from 'next/link';
import Breadcrumbs from '@/components/navigation/Breadcrumbs';
import fs from 'fs';
import path from 'path';

interface Pattern {
  id: string;
  patternName: string;
  description: string;
  category: string;
  examples: Array<{
    id: string;
    content: string;
    index: number;
  }>;
  paper: {
    title: string;
    authors: string[];
    url: string;
  };
  tags: string[];
}

interface CategoryPageProps {
  params: Promise<{
    slug: string;
  }>;
}

async function getPatterns(): Promise<Pattern[]> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

type SemanticAssignments = {
  categories: Record<string, { name: string; slug: string; logic: string; description?: string; patternCount: number; patterns: { id: string; name: string; similarity: number }[] }>; 
  patterns: Record<string, { id: string; name: string; currentCategory?: string | null; bestCategory: { slug: string; name: string; similarity: number }; topCategories: { slug: string; name: string; similarity: number }[] }>
}

async function getSemanticAssignments(): Promise<SemanticAssignments | null> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'semantic-assignments.json');
  if (!fs.existsSync(filePath)) return null;
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

type SimilarPatterns = { similar: Record<string, { id: string; similarity: number }[]> };
async function getSimilarPatterns(): Promise<SimilarPatterns | null> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'similar-patterns.json');
  if (!fs.existsSync(filePath)) return null;
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

type SimilarExamples = { similar: Record<string, { id: string; similarity: number }[]> };
async function getSimilarExamples(): Promise<SimilarExamples | null> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'similar-examples.json');
  if (!fs.existsSync(filePath)) return null;
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

type CategoryEmbeddings = {
  metadata: {
    totalCategories: number;
  };
  categories: Record<string, { name: string; slug: string; logic?: string; description?: string }>;
};

async function getCategoryDescription(slug: string): Promise<{ description?: string; logic?: string } | null> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'category-embeddings.json');
  if (!fs.existsSync(filePath)) return null;
  const fileContents = fs.readFileSync(filePath, 'utf8');
  const data: CategoryEmbeddings = JSON.parse(fileContents);
  const entry = data.categories?.[slug];
  if (!entry) return null;
  return { description: entry.description, logic: entry.logic };
}

function slugToCategory(slug: string): string {
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const { slug } = await params;
  const categoryName = slugToCategory(slug);
  const allPatterns = await getPatterns();
  const semantic = await getSemanticAssignments();
  const similar = await getSimilarPatterns();
  const similarExamples = await getSimilarExamples();
  const categoryMeta = await getCategoryDescription(slug);

  // Prefer semantic assignments; fallback to original if missing
  let categoryPatterns: Pattern[] = [];
  if (semantic && semantic.categories[slug]) {
    const ids = semantic.categories[slug].patterns.map(p => p.id);
    const map = new Map(allPatterns.map(p => [p.id, p] as const));
    categoryPatterns = ids.map(id => map.get(id)).filter(Boolean) as Pattern[];
  } else {
    categoryPatterns = allPatterns.filter(pattern => 
      pattern.category.toLowerCase() === categoryName.toLowerCase()
    );
  }

  if (categoryPatterns.length === 0) {
    notFound();
  }

  // Derive related categories using semantic similarity across patterns in this category
  const relatedCategoryScores: Record<string, { slug: string; name: string; score: number; count: number }> = {};
  if (semantic?.patterns) {
    for (const p of categoryPatterns) {
      const sem = semantic.patterns[p.id];
      if (!sem?.topCategories) continue;
      for (const tc of sem.topCategories) {
        if (!tc?.slug || tc.slug === slug) continue;
        const key = tc.slug;
        if (!relatedCategoryScores[key]) {
          relatedCategoryScores[key] = { slug: tc.slug, name: tc.name, score: 0, count: 0 };
        }
        relatedCategoryScores[key].score += (typeof tc.similarity === 'number' ? tc.similarity : 0);
        relatedCategoryScores[key].count += 1;
      }
    }
  }
  const relatedCategories = Object.values(relatedCategoryScores)
    .sort((a, b) => b.score - a.score || b.count - a.count)
    .slice(0, 8);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        {/** Breadcrumbs **/}
        <Breadcrumbs />
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {categoryName}
          </h1>
          <div className="flex flex-col gap-2">
            <div className="text-gray-600">
              {categoryPatterns.length} pattern{categoryPatterns.length !== 1 ? 's' : ''} in this category
            </div>
            {categoryMeta?.logic && (
              <div className="inline-flex items-center gap-2">
                <span className="text-xs font-medium text-gray-500">Logic:</span>
                <span className="inline-flex items-center rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 text-xs font-medium">
                  {categoryMeta.logic}
                </span>
              </div>
            )}
            {categoryMeta?.description && (
              <p className="text-sm text-gray-700 max-w-3xl whitespace-pre-wrap">
                {categoryMeta.description}
              </p>
            )}
          </div>
        </div>

        {/* Patterns Grid */}
        <div className="space-y-6">
          {categoryPatterns.map((pattern) => (
            <div key={pattern.id} id={`pattern-${pattern.id}`} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {pattern.patternName}
                    </h3>
                    {/* Pattern index/id */}
                    {pattern.id && (
                      <span className="shrink-0 inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 text-xs font-medium">
                        ID: {pattern.id}
                      </span>
                    )}
                    {/* Semantic score badge */}
                    {semantic?.patterns?.[pattern.id]?.bestCategory?.slug === slug && (
                      <span title={`Semantic similarity score to ${categoryName}`}
                        className="shrink-0 inline-flex items-center rounded-full bg-purple-50 text-purple-700 border border-purple-200 px-2 py-0.5 text-xs font-medium">
                        sim: {semantic.patterns[pattern.id].bestCategory.similarity.toFixed(2)}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {pattern.tags.slice(0, 5).map((tag) => (
                      <span
                        key={tag}
                        className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {pattern.description && (
                <p className="text-gray-700 mb-4">{pattern.description}</p>
              )}

              {pattern.examples.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">
                    Examples ({pattern.examples.length}):
                  </h4>
                  <div className="space-y-2">
                    {pattern.examples.slice(0, 3).map((example) => {
                      const fullIndex = typeof example.index === 'number' && pattern.id
                        ? `${pattern.id}-${example.index}`
                        : undefined;
                      return (
                        <div key={example.id} id={fullIndex ? `example-${fullIndex}` : undefined} className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
                          <div className="flex items-start gap-2">
                            {/* Example full index badge (pattern.id-example.index) */}
                            {fullIndex && (
                              <span className="mt-0.5 inline-flex items-center rounded bg-gray-200 text-gray-800 px-1.5 py-0.5 text-[10px] font-semibold">
                                {fullIndex}
                              </span>
                            )}
                            <p className="text-gray-700 text-sm break-words">{example.content}</p>
                          </div>
                          {/* Similar examples */}
                          {fullIndex && similarExamples?.similar?.[fullIndex]?.length ? (
                            <div className="mt-2 text-[11px] text-gray-600">
                              <div className="font-semibold text-gray-800 mb-1">Similar Examples</div>
                              <div className="flex flex-wrap gap-1.5">
                                {similarExamples.similar[fullIndex].map(se => {
                                  const [pId, cIdx, patIdx] = se.id.split('-');
                                  const href = `/pattern/${pId}/${cIdx}/${patIdx}#example-${se.id}`;
                                  return (
                                  <Link key={se.id} href={href} className="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 border border-gray-200 hover:bg-blue-50">
                                    <span className="font-mono mr-1">{se.id}</span>
                                    <span className="text-gray-500">{se.similarity.toFixed(2)}</span>
                                  </Link>
                                  );
                                })}
                              </div>
                            </div>
                          ) : null}
                        </div>
                      );
                    })}
                    {pattern.examples.length > 3 && (
                      <p className="text-sm text-gray-500">
                        +{pattern.examples.length - 3} more examples available
                      </p>
                    )}
                  </div>
                </div>
              )}

              <div className="border-t pt-4">
                <div className="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center text-sm text-gray-600 space-y-2 sm:space-y-0">
                  <div>
                    <strong>Source:</strong> 
                    <a 
                      href={pattern.paper.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 ml-1"
                    >
                      {pattern.paper.title}
                    </a>
                  </div>
                  <div>
                    <strong>Authors:</strong> {pattern.paper.authors.slice(0, 3).join(', ')}
                    {pattern.paper.authors.length > 3 && ' et al.'}
                  </div>
                </div>
                {/* Similar Patterns */}
                {similar?.similar?.[pattern.id]?.length ? (
                  <div className="mt-3 text-xs text-gray-600">
                    <div className="font-semibold text-gray-800 mb-1">Similar Patterns</div>
                    <div className="flex flex-wrap gap-2">
                      {similar.similar[pattern.id].slice(0, 5).map(sp => {
                        const [pId, cIdx, patIdx] = sp.id.split('-');
                        const href = `/pattern/${pId}/${cIdx}/${patIdx}`;
                        return (
                        <Link key={sp.id} href={href} className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 hover:bg-blue-50 border border-gray-200">
                          <span className="font-mono mr-1">{sp.id}</span>
                          <span className="text-gray-500">{sp.similarity.toFixed(2)}</span>
                        </Link>
                        );
                      })}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>

        {/* Related Categories (semantic) */}
        {relatedCategories.length > 0 && (
          <div className="mt-12 bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Related Categories (semantic)</h3>
              <Link href="/semantic" className="text-sm text-blue-600 hover:text-blue-800">Matrix</Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {relatedCategories.map(rc => (
                <Link
                  key={rc.slug}
                  href={`/category/${rc.slug}`}
                  className="flex items-center justify-between gap-2 text-blue-700 hover:text-blue-900 text-sm p-2 rounded border border-gray-200 hover:border-blue-300 transition-colors"
                  title={`Aggregate similarity score: ${rc.score.toFixed(2)} • from ${rc.count} pattern(s)`}
                >
                  <span>{rc.name}</span>
                  <span className="text-[10px] text-gray-600 bg-gray-100 rounded px-1.5 py-0.5 border">{rc.score.toFixed(2)}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
