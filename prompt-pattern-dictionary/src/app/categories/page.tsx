import Link from 'next/link';
import { loadPatternCategories, loadSemanticOverrides, applySemanticCounts } from '@/lib/data/categories';

interface Category { name: string; slug: string; patternCount: number }
interface Logic { name: string; slug: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[]; meta: { totalCategories: number } }

export default async function CategoriesPage() {
  const data = loadPatternCategories() as PatternCategoriesData;
  const baseCategories: Category[] = data.logics.flatMap(l => l.categories);
  const semantic = loadSemanticOverrides();
  const categories = applySemanticCounts(baseCategories, semantic);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Categories ({categories.length})</h1>
          {semantic && (
            <span title="Counts use semantic category assignments"
                  className="inline-flex items-center gap-1 text-xs bg-purple-100 text-purple-700 border border-purple-200 rounded px-2 py-1">
              Semantic counts
            </span>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {categories.map(c => (
            <Link key={c.slug} href={`/category/${c.slug}`} className="block bg-white rounded p-4 border hover:border-blue-300 hover:bg-blue-50">
              <div className="flex items-center justify-between">
                <span className="text-blue-700 font-medium">{c.name}</span>
                <span className="text-xs text-gray-600">{c.patternCount} patterns</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
