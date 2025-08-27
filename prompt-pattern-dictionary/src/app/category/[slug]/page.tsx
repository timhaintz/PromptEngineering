/**
 * Category Page
 * 
 * Displays all patterns in a specific category
 */

import { notFound } from 'next/navigation';
import Link from 'next/link';
import Breadcrumbs from '@/components/navigation/Breadcrumbs';
import PatternDetail, { type NormalizedAttrs, type SimilarMap, type SimilarPatternsMap } from '@/components/papers/PatternDetail';
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

type NormalizedPatterns = { patterns: Array<{ id: string; mediaType?: string; dependentLLM?: string | null; application?: string[]; turn?: string | null; template?: Record<string, string> | null; usageSummary?: string | null; aiAssisted?: boolean; aiAssistedFields?: string[]; aiAssistedModel?: string | null; aiAssistedAt?: string | null }> };
async function getNormalized(): Promise<NormalizedPatterns | null> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'normalized-patterns.json');
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
  const normalized = await getNormalized();
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

        {/* Patterns (unified look) */}
        <div className="space-y-4">
          {categoryPatterns.map(p => {
            const n = normalized?.patterns.find(x => x.id === p.id);
            const attrs: NormalizedAttrs | null = n ? {
              mediaType: n.mediaType ?? null,
              dependentLLM: n.dependentLLM ?? null,
              application: n.application ?? null,
              turn: n.turn ?? null,
              template: n.template ?? null,
              usageSummary: n.usageSummary ?? null,
              aiAssisted: n.aiAssisted ?? false,
              aiAssistedFields: n.aiAssistedFields ?? null,
              aiAssistedModel: n.aiAssistedModel ?? null,
              aiAssistedAt: n.aiAssistedAt ?? null,
            } : null;
            const allFirstExamples = Object.fromEntries(allPatterns.map(pp => [pp.id, pp.examples[0]?.id]));
            return (
              <div key={p.id} id={`pattern-${p.id}`} className="bg-white rounded-lg shadow">
                <PatternDetail
                  pattern={{ id: p.id, patternName: p.patternName, description: p.description, category: p.category, examples: p.examples }}
                  attrs={attrs}
                  similar={(similarExamples?.similar ?? {}) as SimilarMap}
                  similarPatterns={(similar?.similar ?? {}) as SimilarPatternsMap}
                  patternFirstExample={allFirstExamples}
                  context="category"
                  paperTitle={p.paper.title}
                  paperUrl={p.paper.url}
                  showSimilarPatterns={true}
                />
              </div>
            );
          })}
        </div>

        {/* Related Categories (semantic) */}
        {relatedCategories.length > 0 && (
          <div className="mt-12 bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Related Categories (semantic)</h3>
              <Link href="/matrix" className="text-sm text-blue-600 hover:text-blue-800">Matrix</Link>
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
