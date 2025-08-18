import fs from 'fs';
import path from 'path';
import Link from 'next/link';

interface Category { name: string; slug: string; patternCount: number }
interface Logic { name: string; slug: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[]; meta: { totalCategories: number } }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export default async function CategoriesPage() {
  const data = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  const categories: Category[] = data.logics.flatMap(l => l.categories);

  // Align counts with Home "Browse by Category" by applying semantic overrides when available
  let semantic: null | { categories: Record<string, { patternCount: number }> } = null;
  const semanticPath = path.join(process.cwd(), 'public', 'data', 'semantic-assignments.json');
  if (fs.existsSync(semanticPath)) {
    try {
      semantic = JSON.parse(fs.readFileSync(semanticPath, 'utf8'));
    } catch {
      // ignore JSON parse issues and fall back to base counts
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Categories ({categories.length})</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {categories.map(c => (
            <Link key={c.slug} href={`/category/${c.slug}`} className="block bg-white rounded p-4 border hover:border-blue-300 hover:bg-blue-50">
              <div className="flex items-center justify-between">
                <span className="text-blue-700 font-medium">{c.name}</span>
                <span className="text-xs text-gray-600">{(semantic?.categories?.[c.slug]?.patternCount ?? c.patternCount)} patterns</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
