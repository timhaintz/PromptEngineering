import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';

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
    <PageShell>
      <div className="space-y-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Papers ({papers.length})</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {papers.map(p => (
            <div key={p.paperId} className="relative group">
              {/* Visual card content */}
              <div className="surface-card p-4 group-hover:border-[var(--color-accent)] group-hover:shadow-md pointer-events-none transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <h2 className="text-md font-semibold text-gray-900 mb-1 break-words">{p.title}</h2>
                    <div className="text-xs text-gray-600 mb-1">{p.authors.slice(0,4).join(', ')}{p.authors.length > 4 ? ' et al.' : ''}</div>
                    {/* Source link under authors */}
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="pointer-events-auto relative z-10 text-blue-600 text-xs hover:text-blue-800"
                    >
                      Source
                    </a>
                    <div className="text-xs text-gray-600 mt-2">Patterns: {p.count}</div>
                  </div>
                </div>
              </div>
              {/* Full-tile clickable overlay to paper details */}
              <Link
                href={`/papers/${p.paperId}`}
                aria-label={`Open ${p.title}`}
                className="absolute inset-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 z-0"
              >
                <span className="sr-only">Open paper</span>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </PageShell>
  );
}
