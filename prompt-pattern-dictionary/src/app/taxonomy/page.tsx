import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import { loadSemanticOverrides, type SemanticAssignments } from '@/lib/data/categories';

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
  <div className="min-h-screen bg-base">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">PP Taxonomy</h1>
          <p className="text-gray-700">Logic layers and categories derived from papers</p>
          {semantic && (
            <div className="mt-2 inline-flex items-center gap-1 text-xs bg-purple-100 text-purple-700 border border-purple-200 rounded px-2 py-1" title="Counts use semantic category assignments when available">
              Semantic counts
            </div>
          )}
        </div>

        <div className="space-y-4 max-w-4xl mx-auto">
          {data.logics.map(l => {
            const total = l.categories.reduce((acc, c) => acc + (semantic?.categories?.[c.slug]?.patternCount ?? c.patternCount ?? 0), 0);
            return (
              <details key={l.slug} className="rounded-lg p-4 shadow border bg-white dark:bg-slate-800 dark:border-slate-600 hc:bg-black/70 transition-colors" open>
                <summary className="cursor-pointer list-none">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-lg font-semibold text-gray-900">{l.name} Logic</div>
                      <div className="text-sm text-gray-700">{l.focus}</div>
                    </div>
                    <div className="text-xs text-gray-600">{total} patterns • {l.categories.length} categories</div>
                  </div>
                </summary>
                <ul className="list-disc ml-6 mt-3 text-gray-900">
                  {l.categories.map(c => (
                    <li key={c.slug} className="my-1">
                      <Link href={`/category/${c.slug}`} className="text-blue-700 hover:text-blue-900">
                        {c.name}
                      </Link>
                      <span className="text-xs text-gray-600 ml-2">({semantic?.categories?.[c.slug]?.patternCount ?? c.patternCount} patterns)</span>
                    </li>
                  ))}
                </ul>
              </details>
            );
          })}
        </div>
      </div>
    </div>
  );
}
