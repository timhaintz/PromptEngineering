import fs from 'fs';
import path from 'path';
import Link from 'next/link';

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
    const currentName = sem?.currentCategory || pat?.category;
    if (!currentName) continue;
    let rowSlug = toSlug(currentName);
    if (!taxonomySlugs.has(rowSlug)) {
      // Try matching by display name against taxonomy
      for (const l of taxonomy.logics) {
        const found = l.categories.find(c => c.name.toLowerCase() === currentName.toLowerCase());
        if (found) { rowSlug = found.slug; break; }
      }
    }
    if (!taxonomySlugs.has(rowSlug)) continue; // skip if we can't map to a taxonomy row

    for (const row of rows) {
      const cat = row.categories.find(rc => rc.category.slug === rowSlug);
      if (cat && typeof cat.counts[bestSlug] === 'number') {
        cat.counts[bestSlug] += 1;
        break;
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Taxonomy × Semantic Matrix</h1>
          <div className="flex items-center gap-3">
            <Link href="/semantic" className="text-sm text-blue-600 hover:text-blue-800">Semantic Analysis</Link>
            <Link href="/taxonomy" className="text-sm text-blue-600 hover:text-blue-800">View Taxonomy</Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="sticky left-0 bg-gray-50 z-10 text-left p-3 font-semibold text-gray-700 border-b">Logic / Category</th>
                {semanticColumns.map(col => (
                  <th key={col} className="p-3 text-left font-semibold text-gray-700 border-b">
                    <Link href={`/category/${col}`} className="text-blue-700 hover:text-blue-900">{col.replace(/-/g,' ')}</Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tbody key={`group-${row.logic.slug}`}>
                  <tr className="bg-gray-100">
                    <td colSpan={1 + semanticColumns.length} className="p-3 font-medium text-gray-900 border-t">
                      {row.logic.name} Logic
                    </td>
                  </tr>
                  {row.categories.map(rc => (
                    <tr key={`cat-${row.logic.slug}-${rc.category.slug}`} className="hover:bg-blue-50">
                      <td className="sticky left-0 bg-white z-10 p-3 border-t">
                        <div>
                          <Link href={`/category/${rc.category.slug}`} className="text-blue-700 hover:text-blue-900 font-medium">
                            {rc.category.name}
                          </Link>
                        </div>
                      </td>
                      {semanticColumns.map(col => {
                        const count = rc.counts[col] || 0;
                        const intensity = Math.min(1, count / 12); // normalize for simple heat effect
                        const bg = intensity === 0 ? 'bg-white' : intensity < 0.25 ? 'bg-blue-50' : intensity < 0.5 ? 'bg-blue-100' : intensity < 0.75 ? 'bg-blue-200' : 'bg-blue-300';
                        const href = count > 0 ? `/category/${col}` : undefined;
                        return (
                          <td key={col} className={`p-3 border-t ${bg}`}>
                            {count > 0 ? (
                              <Link href={href!} className="inline-flex items-center justify-center w-8 h-6 rounded text-gray-800" title={`${count} pattern(s)`}>
                                {count}
                              </Link>
                            ) : (
                              <span className="inline-block w-8 h-6 text-gray-400 text-center">0</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-gray-600 mt-3">
          Counts per cell use semantic best-category assignments (columns). Rows are the original taxonomy categories mapped from each pattern&apos;s current/original category. This aligns with &quot;Semantic counts&quot; used across the site.
        </p>
      </div>
    </div>
  );
}
