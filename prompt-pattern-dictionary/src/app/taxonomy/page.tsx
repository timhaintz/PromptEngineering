import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import { loadSemanticOverrides, type SemanticAssignments } from '@/lib/data/categories';
import PageShell from '@/components/layout/PageShell';

interface Category { name: string; slug: string; patternCount: number }
interface Logic { name: string; slug: string; focus: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[]; meta: { totalCategories: number } }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export default async function TaxonomyPage() {
  const data = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  const semantic: SemanticAssignments | null = loadSemanticOverrides();
  return (
    <PageShell variant="narrow">
      <div className="space-y-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">PP Taxonomy</h1>
          <p className="text-secondary">Logic layers and categories derived from papers</p>
          {semantic && (
            <div className="mt-2 badge-ai" title="Counts use semantic category assignments when available">
              Semantic counts
            </div>
          )}
        </div>

  <div className="space-y-4 max-w-4xl mx-auto">
          {data.logics.map(l => {
            const total = l.categories.reduce((acc, c) => acc + (semantic?.categories?.[c.slug]?.patternCount ?? c.patternCount ?? 0), 0);
            return (
              <details key={l.slug} className="surface-card p-4" open>
                <summary className="cursor-pointer list-none">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-lg font-semibold text-primary">{l.name} Logic</div>
                      <div className="text-sm text-muted">{l.focus}</div>
                    </div>
                    <div className="text-xs text-muted">{total} patterns • {l.categories.length} categories</div>
                  </div>
                </summary>
                <ul className="list-disc ml-6 mt-3 text-primary">
                  {l.categories.map(c => (
                    <li key={c.slug} className="my-1">
                      <Link href={`/category/${c.slug}`} className="text-secondary hover:text-primary focus-ring rounded-sm px-0.5">
                        {c.name}
                      </Link>
                      <span className="text-xs text-muted ml-2">({semantic?.categories?.[c.slug]?.patternCount ?? c.patternCount} patterns)</span>
                    </li>
                  ))}
                </ul>
              </details>
            );
          })}
        </div>
      </div>
    </PageShell>
  );
}
