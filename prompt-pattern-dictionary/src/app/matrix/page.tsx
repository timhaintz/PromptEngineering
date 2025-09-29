import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';

// Matrix view of Logic Layers (rows) x Semantic Categories (columns)
// Counts represent number of patterns whose best semantic category = column, grouped by logic/category taxonomy

interface Pattern { id: string; patternName: string; category: string }

interface SemanticAssignments {
  categories: Record<string, { slug: string; name: string; patternCount: number; patterns: { id: string; name: string; similarity: number }[] }>;
  patterns: Record<string, { id: string; name?: string; currentCategory?: string | null; bestCategory: { slug: string; name: string; similarity: number } }>
}

interface Category { name: string; slug: string; patternCount: number }
interface Logic { name: string; slug: string; focus: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[] }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export default async function MatrixPage() {
  const patterns = loadJson<Pattern[]>('public/data/patterns.json');
  const taxonomy = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  const semantic = loadJson<SemanticAssignments>('public/data/semantic-assignments.json');

  // Build a map for fast lookups
  const patternById = new Map(patterns.map(p => [p.id, p] as const));

  // Helper: normalize a category name to slug and fix known spelling variants
  const toSlug = (name: string) =>
    name
      .toLowerCase()
      .replace(/&/g, 'and')
      .replace(/\s+/g, '-')
      .replace(/customization/g, 'customisation');

  // Build a quick lookup of taxonomy category slugs set for row validation
  const taxonomySlugs = new Set<string>();
  for (const l of taxonomy.logics) {
    for (const c of l.categories) taxonomySlugs.add(c.slug);
  }

  // Helper: map a human name to a taxonomy slug if possible
  const nameToTaxonomySlug = (name?: string | null): string | undefined => {
    if (!name) return undefined;
    const slugGuess = toSlug(name);
    if (taxonomySlugs.has(slugGuess)) return slugGuess;
    // Try matching by display name against taxonomy (case-insensitive)
    for (const l of taxonomy.logics) {
      const found = l.categories.find(c => c.name.toLowerCase() === name.toLowerCase());
      if (found) return found.slug;
    }
    return undefined;
  };

  // Collect all semantic category slugs used by bestCategory (columns)
  const semanticSlugs = new Set<string>();
  for (const pId of Object.keys(semantic.patterns)) {
    const best = semantic.patterns[pId]?.bestCategory?.slug;
    if (best) semanticSlugs.add(best);
  }
  const semanticColumns = Array.from(semanticSlugs).sort();

  // Build matrix rows per logic and their categories
  const rows = taxonomy.logics.map(l => ({
    logic: l,
    categories: l.categories.map(c => ({
      category: c,
      counts: Object.fromEntries(semanticColumns.map(col => [col, 0])) as Record<string, number>,
    }))
  }));

  // Count patterns into matrix using semantic bestCategory and robust row mapping
  for (const [pId, sem] of Object.entries(semantic.patterns)) {
    const bestSlug = sem?.bestCategory?.slug;
    if (!bestSlug) continue;

    // Determine the taxonomy row category slug for this pattern
    const pat = patternById.get(pId);
    // Prefer semantic currentCategory ONLY if it maps to a known taxonomy slug; otherwise, fall back to the original pattern category
    const fromSemantic = nameToTaxonomySlug(sem?.currentCategory);
    const fromPattern = nameToTaxonomySlug(pat?.category);
    const rowSlug = fromSemantic || fromPattern;
    if (!rowSlug) continue; // skip if we can't map to a taxonomy row

    for (const row of rows) {
      const cat = row.categories.find(rc => rc.category.slug === rowSlug);
      if (cat && typeof cat.counts[bestSlug] === 'number') {
        cat.counts[bestSlug] += 1;
        break;
      }
    }
  }

  return (
    <PageShell>
      <div className="space-y-12">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-primary">Taxonomy × Semantic Matrix</h1>
          <div className="flex items-center gap-3 text-sm">
            <Link href="/semantic" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">Semantic Analysis</Link>
            <Link href="/taxonomy" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">View Taxonomy</Link>
          </div>
        </div>
  <div className="surface-card overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-surface-1 transition-colors">
              <tr>
                <th className="sticky left-0 z-10 text-left p-3 font-semibold border-b bg-surface-1 text-secondary transition-colors">Logic / Category</th>
                {semanticColumns.map(col => (
                  <th key={col} className="p-3 text-left font-semibold text-secondary border-b">
                    <Link href={`/category/${col}`} className="text-secondary hover:text-primary focus-ring rounded-sm px-0.5">{col.replace(/-/g,' ')}</Link>
                  </th>
                ))}
              </tr>
            </thead>
            {/* Multiple tbody sections are valid HTML. Render one group per logic to avoid nested tbody hydration issues. */}
            {rows.map(row => (
              <tbody key={`group-${row.logic.slug}`}>
                <tr className="bg-surface-2 transition-colors">
                  <td colSpan={1 + semanticColumns.length} className="p-3 font-medium text-primary border-t">
                    {row.logic.name} Logic
                  </td>
                </tr>
                {row.categories.map(rc => (
                  <tr key={`cat-${row.logic.slug}-${rc.category.slug}`} className="hover:bg-surface-hover">
                    <td className="sticky left-0 z-10 p-3 border-t bg-surface-1 transition-colors">
                      <div>
                        <Link href={`/category/${rc.category.slug}`} className="text-secondary hover:text-primary font-medium focus-ring rounded-sm px-0.5">
                          {rc.category.name}
                        </Link>
                      </div>
                    </td>
                    {semanticColumns.map(col => {
                      const count = rc.counts[col] || 0;
                      const intensity = Math.min(1, count / 12); // normalize for simple heat effect
                      const level = intensity === 0 ? 0 : intensity < 0.25 ? 1 : intensity < 0.5 ? 2 : intensity < 0.75 ? 3 : 4;
                      const heatClass = `heat-${level}`;
                      const href = count > 0 ? `/category/${col}` : undefined;
                      return (
                        <td key={col} className={`p-3 border-t ${heatClass}`}>
                          {count > 0 ? (
                            <Link href={href!} className="inline-flex items-center justify-center w-8 h-6 rounded text-secondary hover:text-primary focus-ring" title={`${count} pattern(s)`}>
                              {count}
                            </Link>
                          ) : (
                            <span className="inline-block w-8 h-6 text-muted text-center">0</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            ))}
          </table>
        </div>

        <p className="text-xs text-muted mt-3">
          Counts per cell use semantic best-category assignments (columns). Rows are the original taxonomy categories mapped from each pattern&apos;s current/original category. This aligns with &quot;Semantic counts&quot; used across the site.
        </p>
      </div>
    </PageShell>
  );
}
