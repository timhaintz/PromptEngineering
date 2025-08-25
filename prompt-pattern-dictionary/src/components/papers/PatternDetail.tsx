'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

export interface Example { id: string; index: number; content: string }
export interface PatternBasics {
  id: string;
  patternName: string;
  description?: string;
  category: string;
  examples: Example[];
}

export interface NormalizedAttrs {
  mediaType?: string | null;
  dependentLLM?: string | null;
  application?: string[] | null;
  turn?: string | null;
  template?: Record<string, string> | null;
}

export interface SimilarMap { [exampleId: string]: Array<{ id: string; similarity: number }>; }
export interface SimilarPatternsMap { [patternId: string]: Array<{ id: string; similarity: number }>; }

function ExampleIdBadge({ id }: { id: string }) {
  return (
    <span className="inline-flex items-center rounded bg-gray-200 text-gray-800 px-1.5 py-0.5 text-[10px] font-semibold">
      {id}
    </span>
  );
}

function formatScore(n: number) {
  return n.toFixed(2);
}

function exampleLinkFromId(exId: string) {
  // id format: paper-categoryIndex-patternIndex-exampleIndex => a-b-c-d
  const parts = exId.split('-');
  if (parts.length !== 4) return '#';
  const [p, b, c, d] = parts;
  return `/papers/${p}#e-${b}-${c}-${d}`;
}

export default function PatternDetail({
  pattern,
  attrs,
  similar,
  similarPatterns,
  patternFirstExample,
  context = 'paper',
  paperTitle,
  paperUrl,
  showSimilarPatterns = false,
}: {
  pattern: PatternBasics;
  attrs: NormalizedAttrs | null;
  similar: SimilarMap;
  similarPatterns: SimilarPatternsMap;
  patternFirstExample: Record<string, string | undefined>;
  context?: 'paper' | 'category';
  paperTitle?: string;
  paperUrl?: string;
  showSimilarPatterns?: boolean;
}) {
  const id = pattern.id;
  const [examplesOpen, setExamplesOpen] = useState(false); // default condensed per user
  const [templateOpen, setTemplateOpen] = useState(false); // default collapsed
  const [similarPatternsOpen, setSimilarPatternsOpen] = useState(false); // default collapsed

  // Remember examples panel state per pattern id
  useEffect(() => {
    try {
      const key = `pp:examples:${id}`;
      const saved = localStorage.getItem(key);
      if (saved !== null) setExamplesOpen(saved === '1');
    } catch {}
  }, [id]);
  useEffect(() => {
    try {
      localStorage.setItem(`pp:examples:${id}`, examplesOpen ? '1' : '0');
    } catch {}
  }, [id, examplesOpen]);

  const templateText = useMemo(() => {
    if (!attrs?.template || Object.keys(attrs.template).length === 0) return 'N/A';
    const lines: string[] = [];
    for (const [k, v] of Object.entries(attrs.template)) {
      if (!v) continue;
      lines.push(`${k}: ${v}`);
    }
    return lines.length ? lines.join('\n') : 'N/A';
  }, [attrs?.template]);

  const appTags = attrs?.application && attrs.application.length ? attrs.application : null;
  const [paperId, categoryIndex, patternIndex] = pattern.id.split('-');

  return (
    <div className="border rounded-lg p-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <div className="text-lg font-semibold text-gray-900 break-words">{pattern.patternName}</div>
            <ExampleIdBadge id={`ID: ${pattern.id}`} />
          </div>
        </div>
        {attrs?.turn && (
          <div className="shrink-0 self-start">
            <span className="inline-flex items-center rounded bg-indigo-100 text-indigo-700 px-2 py-0.5 text-xs font-medium" title="Turn">
              Turn: {attrs.turn.charAt(0).toUpperCase() + attrs.turn.slice(1)}
            </span>
          </div>
        )}
      </div>

      {pattern.description && <p className="text-gray-700 mt-2 whitespace-pre-wrap">{pattern.description}</p>}

      {/* Definition list attributes */}
      <dl className="mt-3 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1">
        <dt className="font-semibold text-slate-700">Media Type:</dt>
        <dd className="text-gray-800">{attrs?.mediaType || 'N/A'}</dd>

        <dt className="font-semibold text-slate-700">Dependent LLM:</dt>
        <dd className="text-gray-800">{attrs?.dependentLLM ?? 'N/A'}</dd>

        <dt className="font-semibold text-slate-700">Application:</dt>
        <dd className="text-gray-800">
          {appTags ? (
            <div className="flex flex-wrap gap-2">
              {appTags.map((t, idx) => (
                <span key={idx} className="inline-flex items-center rounded-full bg-gray-100 text-gray-800 px-2 py-0.5 text-xs border">
                  {t}
                </span>
              ))}
            </div>
          ) : (
            'N/A'
          )}
        </dd>

        <dt className="font-semibold text-slate-700">Turn:</dt>
        <dd className="text-gray-800">{attrs?.turn ? (attrs.turn.charAt(0).toUpperCase() + attrs.turn.slice(1)) : 'N/A'}</dd>

        <dt className="font-semibold text-slate-700 flex items-center">
          <button
            type="button"
            onClick={() => setTemplateOpen(v => !v)}
            className="mr-1 text-gray-700 hover:text-gray-900"
            aria-controls={`tpl-${pattern.id}`}
            title={templateOpen ? 'Hide template' : 'Show template'}
          >
            <span className="text-sm">{templateOpen ? '▾' : '▸'}</span>
          </button>
          Template:
        </dt>
        <dd className="text-gray-800">
          {templateOpen ? (
            <pre id={`tpl-${pattern.id}`} className="whitespace-pre-wrap bg-gray-50 p-2 rounded border text-sm">{templateText}</pre>
          ) : (
            <span className="text-gray-500 select-none">(collapsed)</span>
          )}
        </dd>
      </dl>

      {/* Prompt Examples section */}
      <div className="mt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setExamplesOpen(v => !v)}
              className="text-gray-700 hover:text-gray-900"
              aria-controls={`ex-${pattern.id}`}
              title={examplesOpen ? 'Hide examples' : 'Show examples'}
            >
              <span className="text-base align-middle">{examplesOpen ? '▾' : '▸'}</span>
            </button>
            <div className="text-sm font-semibold text-gray-900">Prompt Examples ({pattern.examples.length})</div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href={context === 'paper' ? `#p-${categoryIndex}-${patternIndex}` : `/papers/${paperId}#p-${categoryIndex}-${patternIndex}`}
              className="text-blue-600 text-xs hover:text-blue-800"
            >
              Permalink
            </a>
            {context === 'category' && (
              <a
                href={`/papers/${paperId}`}
                className="text-blue-600 text-xs hover:text-blue-800"
                title={paperUrl ? `Source: ${paperUrl}` : undefined}
              >
                Paper: {paperTitle || paperId}
              </a>
            )}
          </div>
        </div>

        {examplesOpen && (
          <ul id={`ex-${pattern.id}`} className="mt-2 space-y-2">
            {pattern.examples.map(ex => {
              const exSims = similar[ex.id] || [];
              let fallback: Array<{ id: string; similarity: number }> = [];
              if (!exSims.length) {
                const patSims = similarPatterns[pattern.id] || [];
                fallback = patSims
                  .map(s => ({ id: patternFirstExample[s.id] || '', similarity: s.similarity }))
                  .filter(x => !!x.id)
                  .slice(0, 5) as Array<{ id: string; similarity: number }>;
              }
              return (
                <ExampleRow key={ex.id} patternId={pattern.id} ex={ex} similar={exSims.length ? exSims : fallback} />
              );
            })}
          </ul>
        )}
      </div>

      {showSimilarPatterns && (similarPatterns[pattern.id]?.length ?? 0) > 0 && (
        <div className="mt-4 border-t pt-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSimilarPatternsOpen(v => !v)}
              className="text-gray-700 hover:text-gray-900"
              aria-controls={`sp-${pattern.id}`}
              title={similarPatternsOpen ? 'Hide similar patterns' : 'Show similar patterns'}
            >
              <span className="text-base align-middle">{similarPatternsOpen ? '▾' : '▸'}</span>
            </button>
            <div className="text-sm font-semibold text-gray-900">
              Similar Patterns ({similarPatterns[pattern.id]?.length ?? 0})
            </div>
          </div>
          {similarPatternsOpen && (
            <div id={`sp-${pattern.id}`} className="mt-2">
              <div className="flex flex-wrap gap-2">
                {(similarPatterns[pattern.id] ?? []).slice(0, 8).map((sp, i) => {
                  const parts = sp.id.split('-');
                  const href = parts.length === 3 ? `/papers/${parts[0]}#p-${parts[1]}-${parts[2]}` : '#';
                  return (
                    <Link key={i} href={href} title={sp.id} className="inline-flex items-center gap-1 rounded-full bg-gray-100 text-gray-800 px-2 py-0.5 text-xs border hover:bg-blue-50">
                      <span className="font-mono">{sp.id}</span>
                      <span className="text-gray-500">{formatScore(sp.similarity)}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function ExampleRow({ patternId, ex, similar }: { patternId: string; ex: Example; similar: Array<{ id: string; similarity: number }> }) {
  const [open, setOpen] = useState(false); // default collapsed for similar examples
  return (
    <li id={`e-${patternId.split('-')[1]}-${patternId.split('-')[2]}-${ex.index}`} className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2 min-w-0">
          <ExampleIdBadge id={`${patternId}-${ex.index}`} />
          <span className="text-sm text-gray-800 whitespace-pre-wrap break-words">{ex.content}</span>
        </div>
        <button
          type="button"
          onClick={() => setOpen(v => !v)}
          className="text-gray-700 hover:text-gray-900 shrink-0"
          aria-controls={`sim-${patternId}-${ex.index}`}
          title={open ? 'Hide similar examples' : 'Show similar examples'}
        >
          <span className="text-sm">{open ? '▾' : '▸'}</span>
        </button>
      </div>
      {open && (
        <div id={`sim-${patternId}-${ex.index}`} className="mt-2">
          <div className="text-xs text-gray-600 mb-1">Similar Examples</div>
          {similar.length ? (
            <div className="flex flex-wrap gap-2 overflow-x-auto">
              {similar.map((s, i) => (
                <Link key={i} href={exampleLinkFromId(s.id)} title={s.id} className="inline-flex items-center gap-1 rounded-full bg-gray-100 text-gray-800 px-2 py-0.5 text-xs border">
                  <span>{s.id}</span>
                  <span className="text-gray-500">{formatScore(s.similarity)}</span>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-xs text-gray-500">No similar examples</div>
          )}
        </div>
      )}
    </li>
  );
}
