import fs from 'fs';
import path from 'path';
import Link from 'next/link';

interface Category { name: string; slug: string; patternCount: number }
interface Logic { name: string; slug: string; focus: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[]; meta: { totalCategories: number } }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export default async function LogicPage() {
  const data = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Logic Layers ({data.logics.length})</h1>
        <div className="space-y-6">
          {data.logics.map(l => (
            <div key={l.slug} className="bg-white rounded-lg p-6 shadow">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-gray-900">{l.name} Logic</h2>
                <p className="text-sm text-gray-600">{l.focus}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {l.categories.map(c => (
                  <Link key={c.slug} href={`/category/${c.slug}`} className="block bg-gray-50 rounded p-3 border hover:border-blue-300 hover:bg-blue-50">
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
    </div>
  );
}
