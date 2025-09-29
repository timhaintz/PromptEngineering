import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import {
  loadPatternCategories,
  loadSemanticOverrides,
  applySemanticCounts,
  type PatternCategoriesData,
  type Category,
  type Logic,
} from '@/lib/data/categories';

export default async function LogicPage() {
  // Load base taxonomy (dictionary) and semantic overrides for counts
  const data: PatternCategoriesData = loadPatternCategories();
  const semantic = loadSemanticOverrides();
  // Apply semantic counts per logic's categories to ensure consistency with Browse/Categories pages
  const logics: Logic[] = data.logics.map(l => ({
    ...l,
    categories: applySemanticCounts(l.categories, semantic) as Category[],
  }));
  return (
    <PageShell>
      <div className="space-y-12">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-primary">Logic Layers ({data.logics.length})</h1>
          <div className="flex items-center gap-3 text-sm">
            {semantic && (
              <span title="Counts use semantic category assignments" className="badge-ai">Semantic counts</span>
            )}
            <Link href="/taxonomy" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">View Taxonomy</Link>
            <Link href="/matrix" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">Matrix</Link>
          </div>
        </div>
        <div className="space-y-6">
          {logics.map(l => (
            <div key={l.slug} className="surface-card p-6">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-primary">{l.name} Logic</h2>
                <p className="text-sm text-muted">{l.focus}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {l.categories.map(c => (
                  <Link key={c.slug} href={`/category/${c.slug}`} className="tile focus-ring">
                    <div className="flex items-center justify-between">
                      <span className="tile-title">{c.name}</span>
                      <span className="tile-meta">{c.patternCount} patterns</span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </PageShell>
  );
}
