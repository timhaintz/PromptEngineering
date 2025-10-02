import fs from 'fs';
import path from 'path';
import { Suspense } from 'react';
import PageShell from '@/components/layout/PageShell';
import { ExamplesBrowser } from '@/components/examples/ExamplesBrowser';

interface PatternExampleEntry {
  exampleId: string;
  patternId: string;
  patternName: string;
  category: string;
  excerpt: string;
}

interface RawPattern {
  id: string;
  patternName: string;
  category: string;
  examples?: { id: string; content: unknown }[];
}

function loadPatterns(): RawPattern[] {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const text = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(text);
}

function buildExampleIndex(): PatternExampleEntry[] {
  const patterns = loadPatterns();
  const entries: PatternExampleEntry[] = [];
  for (const p of patterns) {
    for (const ex of p.examples || []) {
      if (typeof ex.content !== 'string') continue;
      const raw = ex.content;
      const excerpt = raw
        .replace(/\s+/g, ' ') // collapse whitespace
        .slice(0, 140)
        .trim();
      entries.push({
        exampleId: ex.id,
        patternId: p.id,
        patternName: p.patternName,
        category: p.category,
        excerpt: excerpt + (raw.length > 140 ? '…' : ''),
      });
    }
  }
  // Alphabetical by excerpt first token (case-insensitive)
  entries.sort((a, b) => a.excerpt.toLowerCase().localeCompare(b.excerpt.toLowerCase()));
  return entries;
}

export const metadata = {
  title: 'All Prompt Examples',
  description: 'Alphabetical index of all prompt examples across patterns with quick navigation.',
};

export const dynamic = 'error';

export default function ExamplesPage() {
  const all = buildExampleIndex();
  return (
    <PageShell>
      <Suspense fallback={<div className="py-16 text-center text-muted">Loading examples…</div>}>
        <ExamplesBrowser entries={all} />
      </Suspense>
    </PageShell>
  );
}
