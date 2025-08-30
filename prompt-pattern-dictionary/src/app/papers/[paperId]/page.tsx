import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import PatternDetail, { type NormalizedAttrs, type SimilarMap, type SimilarPatternsMap } from '@/components/papers/PatternDetail';
import { notFound } from 'next/navigation';

interface Example { id: string; index: number; content: string }
interface Pattern { id: string; patternName: string; description?: string; examples: Example[]; category: string; paper: { id: string; title: string; authors: string[]; url: string } }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function idParts(patternId: string): { paperId: string; categoryIndex: string; patternIndex: string } {
  const [paperId, categoryIndex, patternIndex] = patternId.split('-');
  return { paperId, categoryIndex, patternIndex };
}

export default async function PaperDetail({ params }: { params: Promise<{ paperId: string }> }) {
  const { paperId } = await params;
  const patterns = loadJson<Pattern[]>('public/data/patterns.json');
  const normalized = loadJson<{ patterns: Array<{ id: string; mediaType?: string; dependentLLM?: string | null; application?: string | string[]; turn?: string | null; template?: Record<string, string> | null; usageSummary?: string | null; aiAssisted?: boolean; aiAssistedFields?: string[]; aiAssistedModel?: string | null; aiAssistedAt?: string | null }> }>('public/data/normalized-patterns.json');
  const similar = loadJson<{ similar: SimilarMap }>('public/data/similar-examples.json');
  const similarPatterns = loadJson<{ similar: SimilarPatternsMap }>('public/data/similar-patterns.json');
  const filtered = patterns.filter(p => p.paper.id === paperId);
  if (!filtered.length) return notFound();

  const paper = filtered[0].paper;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="mb-6">
          <Link href="/papers" className="text-blue-600 hover:text-blue-800">← Back to Papers</Link>
        </div>

        <div className="bg-white rounded-lg p-6 shadow">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-gray-900">{paper.title}</h1>
            <div className="text-sm text-gray-600">{paper.authors.join(', ')}</div>
            <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-sm hover:text-blue-800">Source</a>
          </div>

          <h2 className="text-lg font-semibold text-gray-900 mb-3">Patterns ({filtered.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map(p => {
              const parts = idParts(p.id);
              const anchor = `p-${parts.categoryIndex}-${parts.patternIndex}`;
              return (
                <a key={p.id} href={`#${anchor}`} className="block bg-gray-50 rounded-lg p-4 border hover:border-blue-300 hover:shadow">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <h3 className="text-md font-semibold text-gray-900 truncate">{p.patternName}</h3>
                      <div className="text-xs text-gray-600">Category: {p.category}</div>
                      <div className="text-xs text-gray-600">Examples: {p.examples.length}</div>
                    </div>
                    <span className="text-[10px] text-gray-500 font-mono">{p.id}</span>
                  </div>
                </a>
              );
            })}
          </div>

          <h2 className="text-lg font-semibold text-gray-900 mt-8 mb-3">Details</h2>
          <div className="space-y-4">
            {filtered.map(p => {
              const parts = idParts(p.id);
              const anchor = `p-${parts.categoryIndex}-${parts.patternIndex}`;
              // map of first example id for each pattern in the entire dataset
              // build once outside loop for perf if needed; here simple inline
              const firstExampleMap: Record<string, string | undefined> = Object.fromEntries(
                patterns.map(pp => [pp.id, pp.examples[0]?.id])
              );
              const attrs: NormalizedAttrs | null = (() => {
                const n = normalized.patterns.find(x => x.id === p.id);
                if (!n) return null;
                return {
                  mediaType: n.mediaType ?? null,
                  dependentLLM: n.dependentLLM ?? null,
                  // Ensure application is always mapped from normalized top-level field
                  application: n.application ?? null,
                  turn: n.turn ?? null,
                  template: n.template ?? null,
                  usageSummary: n.usageSummary ?? null,
                  aiAssisted: n.aiAssisted ?? false,
                  aiAssistedFields: n.aiAssistedFields ?? null,
                  aiAssistedModel: n.aiAssistedModel ?? null,
                  aiAssistedAt: n.aiAssistedAt ?? null,
                };
              })();
              return (
                <div key={p.id} id={anchor}>
                  <PatternDetail
                    pattern={{ id: p.id, patternName: p.patternName, description: p.description, category: p.category, examples: p.examples }}
                    attrs={attrs}
                    similar={similar.similar}
                    similarPatterns={similarPatterns.similar}
                    patternFirstExample={firstExampleMap}
                    showSimilarPatterns={true}
                  />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
