import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import { loadPatternCategories, loadSemanticOverrides, applySemanticCounts } from '@/lib/data/categories';
import type { Category, PatternCategoriesData } from '@/lib/data/categories';

export default async function CategoriesPage() {
  const data = loadPatternCategories() as PatternCategoriesData;
  const baseCategories: Category[] = data.logics.flatMap(l => l.categories);
  const semantic = loadSemanticOverrides();
  const categories = applySemanticCounts(baseCategories, semantic);

  return (
    <PageShell>
      <div className="space-y-12">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-primary">Categories ({categories.length})</h1>
          {semantic && (
            <span title="Counts use semantic category assignments" className="badge-ai">
              Semantic counts
            </span>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {categories.map(c => (
            <Link key={c.slug} href={`/category/${c.slug}`} className="tile focus-ring">
              <div className="flex items-center justify-between">
                <span className="tile-title">{c.name}</span>
                <span className="tile-meta">{c.patternCount} patterns</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </PageShell>
  );
}
