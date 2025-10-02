import fs from 'fs';
import path from 'path';
import { Suspense } from 'react';
import { PatternsBrowser } from '@/components/patterns/PatternsBrowser';

interface Example { id: string; index: number; content: string }
interface PatternRecord { id: string; patternName: string; description?: string; examples: Example[]; category: string; paper: { title: string; authors: string[]; url: string }; tags?: string[] }
interface NormalizedPattern { id: string; aiAssisted?: boolean; aiAssistedFields?: string[]; turn?: string | null }
interface Category { name: string; slug: string }
interface Logic { name: string; slug: string; categories: Category[] }
interface PatternCategoriesData { logics: Logic[] }

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function buildCategoryAndLogicMaps(data: PatternCategoriesData) {
  const categorySlugToName: Record<string, string> = {};
  const categoryNameToLogicSlug: Record<string, string> = {};
  const logicOptions: { value: string; label: string }[] = [];
  const categoryOptions: { value: string; label: string; logicSlug: string }[] = [];
  for (const l of data.logics) {
    logicOptions.push({ value: l.slug, label: `${l.name}` });
    for (const c of l.categories) {
      categorySlugToName[c.slug] = c.name;
      categoryNameToLogicSlug[c.name] = l.slug;
      categoryOptions.push({ value: c.slug, label: c.name, logicSlug: l.slug });
    }
  }
  return { categorySlugToName, categoryNameToLogicSlug, logicOptions, categoryOptions };
}

function hasNormalizedObjectPatterns(val: unknown): val is { patterns: NormalizedPattern[] } {
  if (!val || typeof val !== 'object') return false;
  const obj = val as { patterns?: unknown };
  return Array.isArray(obj.patterns);
}

export const dynamic = 'error';

export default function PatternsPage() {
  const patterns = loadJson<PatternRecord[]>('public/data/patterns.json');
  const normalizedRaw = loadJson<{ patterns: NormalizedPattern[] } | NormalizedPattern[] | null>('public/data/normalized-patterns.json');
  const normalizedArr = Array.isArray(normalizedRaw)
    ? normalizedRaw
    : (hasNormalizedObjectPatterns(normalizedRaw) ? normalizedRaw.patterns : []);
  const isTestEnv = process.env.NODE_ENV === 'test';
  const limitedPatterns = isTestEnv ? patterns.slice(0, 40) : patterns;
  const limitedIds = new Set(limitedPatterns.map((pattern) => pattern.id));
  const normalized: Record<string, NormalizedPattern> = {};
  for (const item of normalizedArr) {
    if (!limitedIds.has(item.id)) continue;
    normalized[item.id] = item;
  }

  const catData = loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
  const { categorySlugToName, categoryNameToLogicSlug, logicOptions, categoryOptions } = buildCategoryAndLogicMaps(catData);
  const patternSummaries = limitedPatterns.map((pattern) => ({
    id: pattern.id,
    patternName: pattern.patternName,
    description: pattern.description,
    category: pattern.category,
    tags: pattern.tags || [],
    exampleCount: pattern.examples.length,
  }));

  return (
    <Suspense fallback={<div className="py-16 text-center text-muted">Loading patterns…</div>}>
      <PatternsBrowser
        patterns={patternSummaries}
        normalized={normalized}
        logicOptions={logicOptions}
        categoryOptions={categoryOptions}
        categorySlugToName={categorySlugToName}
        categoryNameToLogicSlug={categoryNameToLogicSlug}
      />
    </Suspense>
  );
}
