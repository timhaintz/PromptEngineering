import fs from 'fs';
import path from 'path';
import Link from 'next/link';

interface Pattern { id: string; paper: { id: string; title: string; authors: string[]; url: string } }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export default async function PapersPage() {
  const patterns = loadJson<Pattern[]>('public/data/patterns.json');

  const byPaper = new Map<string, { paperId: string; title: string; authors: string[]; url: string; count: number }>();
  for (const p of patterns) {
    const key = p.paper.id;
    const cur = byPaper.get(key);
    if (cur) {
      cur.count += 1;
    } else {
      byPaper.set(key, { paperId: p.paper.id, title: p.paper.title, authors: p.paper.authors, url: p.paper.url, count: 1 });
    }
  }

  const papers = Array.from(byPaper.values()).sort((a, b) => a.title.localeCompare(b.title));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Papers ({papers.length})</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {papers.map(p => (
            <div key={p.paperId} className="relative">
              {/* Main clickable tile */}
              <Link
                href={`/papers/${p.paperId}`}
                className="block bg-white rounded-lg p-4 border hover:border-blue-300 hover:shadow focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <h2 className="text-md font-semibold text-gray-900 mb-1 break-words">{p.title}</h2>
                    <div className="text-xs text-gray-600 mb-2">{p.authors.slice(0,4).join(', ')}{p.authors.length > 4 ? ' et al.' : ''}</div>
                    <div className="text-xs text-gray-600">Patterns: {p.count}</div>
                  </div>
                </div>
              </Link>
              {/* Keep Source link, positioned over the card */}
              <a
                href={p.url}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute top-2 right-2 text-gray-600 text-xs hover:text-gray-800 bg-white/80 backdrop-blur rounded px-1"
              >
                Source
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
