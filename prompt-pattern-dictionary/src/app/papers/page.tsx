import fs from 'fs';
import path from 'path';
import PageShell from '@/components/layout/PageShell';
import { PageHeader } from '@/components/ui/PageHeader';
import PapersGrid from '@/components/papers/PapersGrid';

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
        <PapersGrid papers={papers} />
      </div>
    </PageShell>
  );
}
