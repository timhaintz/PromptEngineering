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

function getLogicSummary(logic: Logic): string {
  const detailed = logic.detailedDescription?.trim();
  if (detailed) {
    const firstParagraph = detailed.split('\n\n')[0] ?? detailed;
    return firstParagraph.replace(/\*\*(.*?)\*\*/g, '$1');
  }
  return logic.focus;
}

export default async function LogicPage() {
  // Load base taxonomy and semantic overrides for counts
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
              <span title="Counts use semantic category assignments" className="badge-ai">
                {semantic.meta?.totalPatterns ? `${semantic.meta.totalPatterns} semantically assigned` : 'Semantic counts'}
              </span>
            )}
            <Link prefetch={false} href="/taxonomy" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">View Taxonomy</Link>
            <Link prefetch={false} href="/matrix" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">Matrix</Link>
          </div>
        </div>
        {semantic?.meta?.totalPatterns && (
          <p className="-mt-8 text-sm text-secondary">
            Counts reflect the current semantic embedding artifact, not the total number of source records.
          </p>
        )}
        <div className="space-y-6">
          {logics.map(l => (
            <div key={l.slug} className="surface-card p-6">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-primary">{l.name} Logic</h2>
                <p className="text-sm text-muted whitespace-pre-line">{getLogicSummary(l)}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {l.categories.map(c => (
                  <Link key={c.slug} prefetch={false} href={`/category/${c.slug}`} className="tile focus-ring">
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
