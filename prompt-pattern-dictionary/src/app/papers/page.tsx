import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardGrid } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

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
      <div className="space-y-10">
        <PageHeader heading="Papers" subtitle={`${papers.length} source paper${papers.length !== 1 ? 's' : ''}`} />
        <CardGrid>
          {papers.map(p => {
            const authorLine = p.authors.slice(0,4).join(', ') + (p.authors.length > 4 ? ' et al.' : '');
            return (
              <Card
                key={p.paperId}
                header={<span className="block truncate" title={p.title}>{p.title}</span>}
                meta={<span>{p.count}</span>}
                className="surface-card-interactive"
              >
                <div className="text-xs text-muted mb-2 truncate" title={authorLine}>{authorLine}</div>
                <div className="flex items-center gap-2 text-xs">
                  <a href={p.url} target="_blank" rel="noopener noreferrer" className="text-secondary hover:text-primary focus-ring rounded-sm px-1">Source</a>
                  <Badge variant="generic" className="badge-id">Patterns: {p.count}</Badge>
                  <Link href={`/papers/${p.paperId}`} className="ml-auto text-secondary hover:text-primary focus-ring rounded-sm px-1 text-[11px]">Open →</Link>
                </div>
              </Card>
            );
          })}
        </CardGrid>
      </div>
    </PageShell>
  );
}
