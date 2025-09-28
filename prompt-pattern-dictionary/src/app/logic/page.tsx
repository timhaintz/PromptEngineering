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
          <h1 className="text-2xl font-bold text-gray-900">Logic Layers ({data.logics.length})</h1>
          <div className="flex items-center gap-3">
            {semantic && (
              <span
                title="Counts use semantic category assignments"
                className="inline-flex items-center gap-1 text-xs bg-purple-100 text-purple-700 border border-purple-200 rounded px-2 py-1"
              >
                Semantic counts
              </span>
            )}
            <Link href="/taxonomy" className="text-sm text-blue-600 hover:text-blue-800">View Taxonomy</Link>
            <Link href="/matrix" className="text-sm text-blue-600 hover:text-blue-800">Matrix</Link>
          </div>
        </div>
        <div className="space-y-6">
          {logics.map(l => (
            <div key={l.slug} className="surface-card p-6">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-gray-900">{l.name} Logic</h2>
                <p className="text-sm text-gray-600">{l.focus}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {l.categories.map(c => (
                  <Link key={c.slug} href={`/category/${c.slug}`} className="block rounded p-3 border border-muted bg-surface-2 hover:border-[var(--color-accent)] hover:bg-surface-hover transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="text-blue-700 font-medium">{c.name}</span>
                      <span className="text-xs text-gray-600">{c.patternCount} patterns</span>
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
