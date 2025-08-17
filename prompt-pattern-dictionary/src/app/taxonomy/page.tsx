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

export default async function TaxonomyPage() {
  const data = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">PP Taxonomy</h1>
          <p className="text-gray-700">Logic layers and categories derived from papers</p>
        </div>

        <div className="space-y-6 max-w-4xl mx-auto">
          {data.logics.map(l => (
            <div key={l.slug} className="bg-white rounded-lg p-4 shadow border">
              <div className="mb-2">
                <div className="text-lg font-semibold text-gray-900">{l.name} Logic</div>
                <div className="text-sm text-gray-700">{l.focus}</div>
              </div>
              <ul className="list-disc ml-6 text-gray-900">
                {l.categories.map(c => (
                  <li key={c.slug} className="my-1">
                    <Link href={`/category/${c.slug}`} className="text-blue-700 hover:text-blue-900">
                      {c.name}
                    </Link>
                    <span className="text-xs text-gray-600 ml-2">({c.patternCount} patterns)</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
