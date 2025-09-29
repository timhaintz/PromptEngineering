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
  application?: string | string[] | null;
  applicationTasksString?: string | null;
  turn?: string | null;
  template?: Record<string, string> | null;
  usageSummary?: string | null;
  // New: raw single-line bracketed template representation for export/display
  templateRawBracketed?: string | null;
  aiAssisted?: boolean;
  aiAssistedFields?: string[] | null;
  aiAssistedModel?: string | null;
  aiAssistedAt?: string | null;
}

export interface SimilarMap { [exampleId: string]: Array<{ id: string; similarity: number }>; }
export interface SimilarPatternsMap { [patternId: string]: Array<{ id: string; similarity: number }>; }

function ExampleIdBadge({ id }: { id: string }) {
  return (
    <span className="badge-id text-[10px] font-semibold">{id}</span>
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
  const [bracketOpen, setBracketOpen] = useState(false); // optional bracketed view toggle

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

  const appVal = attrs?.application;
  const applicationString = typeof appVal === 'string' && appVal.trim() ? appVal.trim() : null;
  const appTags = Array.isArray(appVal) && appVal.length ? appVal : null;
  // Split tasks string into individual tasks (comma+space separated)
  const tasks = useMemo(() => {
    const raw = attrs?.applicationTasksString || '';
    return raw
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);
  }, [attrs?.applicationTasksString]);
  const [paperId, categoryIndex, patternIndex] = pattern.id.split('-');
  const isPolicyFallback = useMemo(() => {
    const note = "unable to process";
    const policy = "content management policy";
    if (applicationString) {
      const t = applicationString.toLowerCase();
      return t.includes(note) && t.includes(policy);
    }
    if (appTags && appTags.length === 1) {
      const t = (appTags[0] || '').toLowerCase();
      return t.includes(note) && t.includes(policy);
    }
    return false;
  }, [applicationString, appTags]);

  // Heuristic: if application items are long or contain punctuation/spaces like phrases,
  // render as a small list instead of chips. Keep chips for short tag-like items.
  const renderAsList = useMemo(() => {
    if (!appTags) return false;
    // If any item looks like a sentence/phrase, prefer list
    return appTags.some(s => {
      if (!s) return false;
      const trimmed = s.trim();
      // Consider long (> 28 chars) or contains a period/semicolon/comma as phrase-like
      return trimmed.length > 28 || /[\.;,]/.test(trimmed);
    });
  }, [appTags]);

  return (
  <div className="surface-card p-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 group">
            {/* Hover-only permalink chain icon (larger, like docs anchors) */}
            <a
              href={context === 'paper' ? `#p-${categoryIndex}-${patternIndex}` : `/papers/${paperId}#p-${categoryIndex}-${patternIndex}`}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-muted hover:text-secondary focus:opacity-100 focus-ring rounded-sm"
              title="Permalink"
              aria-label="Permalink"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 mr-1">
                <path d="M10.59 13.41a1 1 0 010-1.41l3.3-3.3a3 3 0 114.24 4.24l-1.65 1.65a1 1 0 11-1.41-1.41l1.65-1.65a1 1 0 10-1.42-1.42l-3.3 3.3a1 1 0 01-1.41 0z"/>
                <path d="M13.41 10.59a1 1 0 010 1.41l-3.3 3.3a3 3 0 11-4.24-4.24l1.65-1.65a1 1 0 111.41 1.41L7.29 12.3a1 1 0 101.42 1.42l3.3-3.3a1 1 0 011.41 0z"/>
              </svg>
            </a>
            <div className="text-lg font-semibold text-primary break-words">{pattern.patternName}</div>
            <ExampleIdBadge id={`ID: ${pattern.id}`} />
            {attrs?.aiAssisted && (attrs.aiAssistedFields || []).includes('usageSummary') && (
              <span
                className="inline-flex items-center rounded bg-amber-100 text-amber-800 px-1.5 py-0.5 text-[10px] font-medium border border-amber-200"
                title={
                  attrs.aiAssistedModel
                    ? `AI-assisted (usage summary) • ${attrs.aiAssistedModel}${attrs.aiAssistedAt ? ` • ${attrs.aiAssistedAt}` : ''}`
                    : 'AI-assisted (usage summary)'
                }
              >
                AI-assisted
              </span>
            )}
          </div>
        </div>
        {/* Removed Turn badge from header */}
      </div>

  {pattern.description && <p className="text-secondary mt-2 whitespace-pre-wrap">{pattern.description}</p>}

      {/* Definition list attributes */}
  <dl className="mt-3 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm">
        {/* Show Reference only on category pages */}
        {context === 'category' && paperTitle && paperUrl ? (
          <>
            <dt className="font-semibold text-secondary">Reference:</dt>
            <dd className="text-secondary">
              <a href={paperUrl} target="_blank" rel="noopener noreferrer" className="text-secondary hover:text-primary focus-ring rounded-sm px-0.5">{paperTitle}</a>
            </dd>
          </>
        ) : null}

  <dt className="font-semibold text-secondary">Media Type:</dt>
  <dd className="text-secondary">{attrs?.mediaType || 'N/A'}</dd>

  <dt className="font-semibold text-secondary">Dependent LLM:</dt>
  <dd className="text-secondary">{attrs?.dependentLLM ?? 'N/A'}</dd>

  <dt className="font-semibold text-secondary">Turn:</dt>
  <dd className="text-secondary">{attrs?.turn ? (attrs.turn.charAt(0).toUpperCase() + attrs.turn.slice(1)) : 'N/A'}</dd>

  <dt className="font-semibold text-secondary flex items-center">
          <button
            type="button"
            onClick={() => setTemplateOpen(v => !v)}
            className="mr-1 text-muted hover:text-secondary focus-ring rounded-sm"
            aria-controls={`tpl-${pattern.id}`}
            title={templateOpen ? 'Hide template' : 'Show template'}
          >
            <span className="text-sm">{templateOpen ? '▾' : '▸'}</span>
          </button>
          Template:
        </dt>
  <dd className="text-secondary">
          {templateOpen ? (
            <div id={`tpl-${pattern.id}`} className="space-y-2">
              <pre className="whitespace-pre-wrap bg-surface-2 p-2 rounded border text-xs">{templateText}</pre>
              {attrs?.templateRawBracketed ? (
                <div className="text-xs text-muted">
                  <button
                    type="button"
                    onClick={() => setBracketOpen(v => !v)}
                    className="text-secondary hover:text-primary underline focus-ring rounded-sm px-0.5"
                    aria-controls={`tplb-${pattern.id}`}
                    title={bracketOpen ? 'Hide bracketed form' : 'Show bracketed form'}
                  >
                    {bracketOpen ? 'Hide bracketed form' : 'Show bracketed form'}
                  </button>
                  {bracketOpen && (
                    <div id={`tplb-${pattern.id}`} className="mt-1 font-mono break-words bg-white border rounded p-2">
                      {attrs.templateRawBracketed}
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          ) : (
            <span className="text-muted select-none">(collapsed)</span>
          )}
        </dd>
        {/* Application moved under Template */}
  <dt className="font-semibold text-secondary">Application:</dt>
  <dd className="text-secondary">
          {/* Primary presentation: application tasks chips */}
          {tasks.length > 0 ? (
            <div className="flex flex-wrap gap-2" aria-label="Application tasks">
              {tasks.map((t, i) => (
                <span key={i} className="chip-task">{t}</span>
              ))}
            </div>
          ) : (
            // Fallback: preserve (but visually still show) legacy application data without deletion.
            <>
              {isPolicyFallback ? (
                <div className="inline-flex items-center gap-2 text-amber-800 bg-amber-50 border border-amber-200 rounded px-2 py-1 text-xs">
                  <span className="font-semibold">Notice:</span>
                  <span>{applicationString ?? (appTags ? appTags[0] : '')}</span>
                </div>
              ) : applicationString ? (
                <p className="text-sm whitespace-pre-wrap">{applicationString}</p>
              ) : appTags ? (
                renderAsList ? (
                  <ul className="list-disc pl-5 space-y-1">
                    {appTags.map((t, idx) => (
                      <li key={idx} className="leading-snug">{t}</li>
                    ))}
                  </ul>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {appTags.map((t, idx) => (
                      <span key={idx} className="chip-task">{t}</span>
                    ))}
                  </div>
                )
              ) : 'N/A'}
            </>
          )}
          {attrs?.usageSummary && (
            <div className="mt-2 text-muted">
              <span className="font-semibold">How to apply:</span> {attrs.usageSummary}
            </div>
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
              className="text-muted hover:text-secondary focus-ring rounded-sm"
              aria-controls={`ex-${pattern.id}`}
              title={examplesOpen ? 'Hide examples' : 'Show examples'}
            >
              <span className="text-base align-middle">{examplesOpen ? '▾' : '▸'}</span>
            </button>
            <div className="text-sm font-semibold text-primary">Prompt Examples ({pattern.examples.length})</div>
          </div>
          {/* Right-side actions removed: Permalink text and Paper link are no longer shown. */}
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
            <div className="text-sm font-semibold text-primary flex items-center gap-1">
              <span>Similar Patterns ({similarPatterns[pattern.id]?.length ?? 0})</span>
              <span
                aria-label="Pattern similarity info"
                role="img"
                className="inline-block cursor-help text-secondary hover:text-primary"
                title="Pattern similarity uses cosine similarity over an embedding composed of the pattern’s name, description, and up to the first three example prompts. Results are exploratory semantic neighbors—not a curated taxonomy. Separate per-example embeddings drive Similar Examples."
              >
                ℹ️
              </span>
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
  <li id={`e-${patternId.split('-')[1]}-${patternId.split('-')[2]}-${ex.index}`} className="p-3 rounded border-l-4 border-accent bg-surface-2">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2 min-w-0">
          <ExampleIdBadge id={`${patternId}-${ex.index}`} />
          <span className="text-sm text-secondary whitespace-pre-wrap break-words">{ex.content}</span>
        </div>
        <button
          type="button"
          onClick={() => setOpen(v => !v)}
          className="text-muted hover:text-secondary shrink-0 focus-ring rounded-sm"
          aria-controls={`sim-${patternId}-${ex.index}`}
          title={open ? 'Hide similar examples' : 'Show similar examples'}
        >
          <span className="text-sm">{open ? '▾' : '▸'}</span>
        </button>
      </div>
      {open && (
        <div id={`sim-${patternId}-${ex.index}`} className="mt-2">
          <div className="text-xs text-muted mb-1">Similar Examples</div>
          {similar.length ? (
            <div className="flex flex-wrap gap-2 overflow-x-auto">
              {similar.map((s, i) => (
                <Link key={i} href={exampleLinkFromId(s.id)} title={s.id} className="chip-task focus-ring">
                  <span>{s.id}</span>
                  <span className="text-muted">{formatScore(s.similarity)}</span>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-xs text-muted">No similar examples</div>
          )}
        </div>
      )}
    </li>
  );
}
