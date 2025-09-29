/**
 * Category Page
 * 
 * Displays all patterns in a specific category
 */

import { notFound } from 'next/navigation';
import PageShell from '@/components/layout/PageShell';
import Link from 'next/link';
import Breadcrumbs from '@/components/navigation/Breadcrumbs';
import { PageHeader } from '@/components/ui/PageHeader';
import Badge from '@/components/ui/Badge';
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

type NormalizedPatterns = { patterns: Array<{ id: string; mediaType?: string; dependentLLM?: string | null; application?: string | string[]; applicationTasksString?: string | null; turn?: string | null; template?: Record<string, string> | null; usageSummary?: string | null; aiAssisted?: boolean; aiAssistedFields?: string[]; aiAssistedModel?: string | null; aiAssistedAt?: string | null }> };
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
    <PageShell>
      <div className="space-y-12">
        {/* Header */}
        {/** Breadcrumbs **/}
        <Breadcrumbs />
        <div className="mb-6">
          <PageHeader heading={categoryName} subtitle={`${categoryPatterns.length} pattern${categoryPatterns.length !== 1 ? 's' : ''}`} />
          <div className="mt-3 flex flex-col gap-2">
            {categoryMeta?.logic && (
              <div className="inline-flex items-center gap-2 text-xs text-secondary">
                <span className="text-muted">Logic:</span>
                <Badge variant="category" className="text-[10px] font-semibold">{categoryMeta.logic}</Badge>
              </div>
            )}
            {categoryMeta?.description && (
              <p className="text-sm text-muted max-w-3xl whitespace-pre-wrap">
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
          applicationTasksString: n.applicationTasksString ?? null,
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
              <div key={p.id} id={`pattern-${p.id}`} className="surface-card">
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
          <div className="surface-card p-6 mt-12">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-primary">Related Categories (semantic)</h3>
              <Link href="/matrix" className="text-sm text-secondary hover:text-primary focus-ring rounded-sm px-1">Matrix</Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {relatedCategories.map(rc => (
                <Link
                  key={rc.slug}
                  href={`/category/${rc.slug}`}
                  className="tile text-sm flex items-center justify-between gap-2 focus-ring"
                  title={`Aggregate similarity score: ${rc.score.toFixed(2)} • from ${rc.count} pattern(s)`}
                >
                  <span className="truncate text-secondary">{rc.name}</span>
                  <span className="text-[10px] badge-id">{rc.score.toFixed(2)}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageShell>
  );
}
