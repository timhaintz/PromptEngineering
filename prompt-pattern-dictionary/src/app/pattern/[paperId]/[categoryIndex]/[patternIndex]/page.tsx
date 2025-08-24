/**
 * Pattern Detail Page
 *
 * Route: /pattern/{paperId}/{categoryIndex}/{patternIndex}
 * Anchors: #example-{paperId}-{categoryIndex}-{patternIndex}-{exampleIndex}
 */

import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import Breadcrumbs from '@/components/navigation/Breadcrumbs';
import { notFound } from 'next/navigation';

interface Example {
  id: string;
  index: number;
  content: string;
}

interface Pattern {
  id: string; // e.g., 10-29-0
  patternName: string;
  category: string;
  description?: string;
  examples: Example[];
  paper: { title: string; authors: string[]; url: string; apaReference?: string };
  tags: string[];
}

type SimilarPatterns = { similar: Record<string, { id: string; similarity: number }[]> };
type SimilarExamples = { similar: Record<string, { id: string; similarity: number }[]> };

// Minimal normalized pattern shape used here
interface NormalizedPattern {
  id: string;
  name?: string;
  category?: string;
  mediaType?: string;
  template?: {
    role?: string;
    context?: string;
    action?: string;
    format?: string;
    response?: string;
  };
  application?: string[];
  dependentLLM?: string | null;
  turn?: 'single' | 'multi' | string;
  promptExamples?: string[];
  related?: string[];
  reference?: { title?: string; authors?: string[]; url?: string; apa?: string };
  aiAssisted?: boolean;
  aiAssistedFields?: string[];
  aiAssistedModel?: string;
  aiAssistedAt?: string;
}

function loadJson<T = unknown>(rel: string): T | null {
  const filePath = path.join(process.cwd(), rel);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function idParts(patternId: string): { paperId: string; categoryIndex: string; patternIndex: string } {
  const [paperId, categoryIndex, patternIndex] = patternId.split('-');
  return { paperId, categoryIndex, patternIndex };
}

function categoryToSlug(category: string): string {
  return category.toLowerCase().replace(/\s+/g, '-');
}

function exampleAnchor(fullIndex: string): string {
  return `example-${fullIndex}`;
}

function hasNormalizedObjectPatterns(val: unknown): val is { patterns: NormalizedPattern[] } {
  if (!val || typeof val !== 'object') return false;
  // Use a safe structural check without resorting to 'any'
  const obj = val as { patterns?: unknown };
  return Array.isArray(obj.patterns);
}

export default async function PatternDetail({ params }: { params: Promise<{ paperId: string; categoryIndex: string; patternIndex: string }> }) {
  const { paperId, categoryIndex, patternIndex } = await params;
  const targetId = `${paperId}-${categoryIndex}-${patternIndex}`;

  // Load data
  const patterns = loadJson<Pattern[]>('public/data/patterns.json') || [];
  const similarPatterns = loadJson<SimilarPatterns>('public/data/similar-patterns.json');
  const similarExamples = loadJson<SimilarExamples>('public/data/similar-examples.json');
  const normalized = loadJson<{ patterns: NormalizedPattern[] } | NormalizedPattern[] | null>('public/data/normalized-patterns.json');

  const pattern = patterns.find(p => p.id === targetId);
  if (!pattern) return notFound();

  const norm: NormalizedPattern | null = Array.isArray(normalized)
    ? (normalized.find((p) => p.id === targetId) || null)
    : (hasNormalizedObjectPatterns(normalized)
        ? (normalized.patterns.find((p) => p.id === targetId) || null)
        : null);

  const categorySlug = categoryToSlug(pattern.category);

  const patternLink = (id: string) => {
    const parts = idParts(id);
    return `/pattern/${parts.paperId}/${parts.categoryIndex}/${parts.patternIndex}`;
  };

  const exampleLink = (fullIndex: string) => {
    const [pId, cIdx, patIdx] = fullIndex.split('-');
    return `/pattern/${pId}/${cIdx}/${patIdx}#${exampleAnchor(fullIndex)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <Breadcrumbs />

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{pattern.patternName}</h1>
                <span className="inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 text-xs font-medium">ID: {pattern.id}</span>
                <Link href={`/category/${categorySlug}`} className="inline-flex items-center rounded-full bg-gray-100 text-gray-700 border border-gray-200 px-2 py-0.5 text-xs font-medium hover:bg-blue-50">{pattern.category}</Link>
                {norm?.aiAssisted ? (
                  <span title={`AI-assisted fields: ${(norm.aiAssistedFields || []).join(', ')}`}
                        className="inline-flex items-center rounded-full bg-yellow-50 text-yellow-800 border border-yellow-200 px-2 py-0.5 text-[10px] font-semibold">
                    AI-assisted
                  </span>
                ) : null}
              </div>
              {pattern.description && <p className="text-gray-700 mb-3">{pattern.description}</p>}

              {/* Left-column labels: Media Type, Dependent LLM, Application, Turn, Template */}
              {(norm?.mediaType || norm?.application?.length || typeof norm?.dependentLLM !== 'undefined' || norm?.turn || norm?.template) && (
                <div className="mb-4 text-sm">
                  <dl className="grid grid-cols-1 md:grid-cols-[max-content_1fr] gap-x-4 gap-y-1 items-start text-gray-800">
                    {norm?.mediaType && (
                      <>
                        <dt className="font-semibold text-slate-800">Media Type:</dt>
                        <dd className="mb-1">{norm.mediaType}</dd>
                      </>
                    )}
                    {typeof norm?.dependentLLM !== 'undefined' && (
                      <>
                        <dt className="font-semibold text-slate-800">Dependent LLM:</dt>
                        <dd className="mb-1">{norm?.dependentLLM || 'N/A'}</dd>
                      </>
                    )}
                    {norm?.application?.length ? (
                      <>
                        <dt className="font-semibold text-slate-800">Application:</dt>
                        <dd className="mb-1">
                          <span className="inline-flex flex-wrap gap-1.5">
                            {norm.application.map((a: string) => (
                              <span key={a} className="inline-block bg-gray-100 text-gray-900 text-xs px-2 py-0.5 rounded border">{a}</span>
                            ))}
                          </span>
                        </dd>
                      </>
                    ) : null}
                    {norm?.turn && (
                      <>
                        <dt className="font-semibold text-slate-800">Turn:</dt>
                        <dd className="mb-1">{norm.turn === 'multi' ? 'Multi' : 'Single'}</dd>
                      </>
                    )}
                    {norm?.template && (
                      <>
                        <dt className="font-semibold text-slate-800">Template:</dt>
                        <dd className="mb-1">
                          <details>
                            <summary className="cursor-pointer select-none text-blue-700 hover:text-blue-900">Show template</summary>
                            <div className="mt-2 whitespace-pre-wrap text-gray-800">
                              {[
                                norm.template.role ? `Role: ${norm.template.role}` : null,
                                norm.template.context ? `Context: ${norm.template.context}` : null,
                                norm.template.action ? `Action: ${norm.template.action}` : null,
                                norm.template.format ? `Format: ${norm.template.format}` : null,
                                norm.template.response ? `Response: ${norm.template.response}` : null,
                              ].filter(Boolean).join('\n')}
                            </div>
                          </details>
                        </dd>
                      </>
                    )}
                  </dl>
                  {norm?.aiAssisted ? (
                    <div className="mt-2 text-xs text-gray-700">
                      Some fields may be AI-assisted (model: {norm.aiAssistedModel || 'LLM'}) and could contain inaccuracies.
                    </div>
                  ) : null}
                </div>
              )}

              {/* Prompt Examples (collapsible with +/-) */}
              <div className="mt-4">
                <details open>
                  <summary className="text-lg font-semibold text-gray-900 cursor-pointer select-none">
                    Prompt Examples ({pattern.examples.length})
                  </summary>
                  <div className="mt-2 space-y-3">
                    {pattern.examples.map(ex => {
                      const fullIndex = `${pattern.id}-${ex.index}`;
                      const similars = similarExamples?.similar?.[fullIndex] || [];
                      return (
                        <div key={ex.id} id={exampleAnchor(fullIndex)} className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
                          <div className="flex items-start gap-2">
                            <span className="mt-0.5 inline-flex items-center rounded bg-gray-200 text-gray-800 px-1.5 py-0.5 text-[10px] font-semibold">{fullIndex}</span>
                            <p className="text-gray-800 text-sm break-words">{ex.content}</p>
                          </div>
                          {similars.length ? (
                            <div className="mt-2 text-[11px] text-gray-600">
                              <details>
                                <summary className="font-semibold text-gray-800 cursor-pointer select-none">Similar Examples</summary>
                                <div className="mt-1 flex flex-wrap gap-1.5">
                                  {similars.slice(0, 8).map(se => (
                                    <Link key={se.id} href={exampleLink(se.id)} className="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 border border-gray-200 hover:bg-blue-50">
                                      <span className="font-mono mr-1">{se.id}</span>
                                      <span className="text-gray-500">{se.similarity.toFixed(2)}</span>
                                    </Link>
                                  ))}
                                </div>
                              </details>
                            </div>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                </details>
              </div>

              {/* Related PPs */}
              {norm?.related?.length ? (
                <div className="mt-6">
                  <div className="font-semibold text-gray-900 mb-2">Related PPs</div>
                  <div className="flex flex-wrap gap-2 text-xs">
                    {norm.related.map((rid: string) => (
                      <Link key={rid} href={patternLink(rid)} className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 hover:bg-blue-50 border border-gray-200">
                        <span className="font-mono">{rid}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              ) : null}

              {/* Reference */}
              <div className="mt-6 border-t pt-4 text-sm text-gray-700">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                  <div>
                    <strong>Source:</strong>
                    <a href={(norm?.reference?.url || pattern.paper.url)} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 ml-1">{norm?.reference?.title || pattern.paper.title}</a>
                  </div>
                  <div>
                    <strong>Authors:</strong> {(norm?.reference?.authors?.length ? norm.reference.authors : pattern.paper.authors).slice(0, 3).join(', ')}{(norm?.reference?.authors?.length ? norm.reference.authors : pattern.paper.authors).length > 3 ? ' et al.' : ''}
                  </div>
                </div>
                {norm?.reference?.apa ? (
                  <div className="mt-2 text-xs text-gray-600">
                    <strong>APA:</strong> {norm.reference.apa}
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          {/* Similar Patterns */}
          {similarPatterns?.similar?.[pattern.id]?.length ? (
            <div className="mt-6">
              <div className="font-semibold text-gray-900 mb-2">Similar Patterns</div>
              <div className="flex flex-wrap gap-2 text-xs">
                {similarPatterns.similar[pattern.id].slice(0, 10).map(sp => (
                  <Link key={sp.id} href={patternLink(sp.id)} className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 hover:bg-blue-50 border border-gray-200">
                    <span className="font-mono mr-1">{sp.id}</span>
                    <span className="text-gray-500">{sp.similarity.toFixed(2)}</span>
                  </Link>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
