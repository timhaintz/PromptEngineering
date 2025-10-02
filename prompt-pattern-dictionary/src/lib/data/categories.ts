import fs from 'fs';
import path from 'path';

export interface Pattern {
  id: string;
  name: string;
  description?: string;
  exampleCount?: number;
}

export interface Category {
  name: string;
  slug: string;
  description: string;
  patternCount: number;
  patterns?: Pattern[];
  hasLatexTable?: boolean;
}

export interface Logic {
  name: string;
  slug: string;
  description: string;
  focus: string;
  detailedDescription: string;
  categories: Category[];
}

export interface PatternCategoriesData {
  meta: {
    generatedAt: string;
    description: string;
    totalLogics: number;
    totalCategories: number;
  };
  logics: Logic[];
}

export interface SemanticAssignments {
  categories: Record<string, { patternCount: number }>;
}

function loadJson<T>(rel: string): T {
  const filePath = path.join(process.cwd(), rel);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

export function loadPatternCategories(): PatternCategoriesData {
  return loadJson<PatternCategoriesData>('public/data/pattern-categories.json');
}

export function loadSemanticOverrides(): SemanticAssignments | null {
  const semanticPath = path.join(process.cwd(), 'public', 'data', 'semantic-assignments.json');
  if (!fs.existsSync(semanticPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(semanticPath, 'utf8')) as SemanticAssignments;
  } catch {
    return null;
  }
}

export function applySemanticCounts(categories: Category[], semantic: SemanticAssignments | null): Category[] {
  if (!semantic || !semantic.categories) return categories;
  return categories.map(c => ({
    ...c,
    patternCount: semantic.categories[c.slug]?.patternCount ?? c.patternCount,
  }));
}

let cachedCategorySlugs: string[] | null = null;

export function getAllCategorySlugs(): string[] {
  if (cachedCategorySlugs) {
    return cachedCategorySlugs;
  }

  const data = loadPatternCategories();
  const slugs = data.logics.flatMap(logic => logic.categories.map(category => category.slug));
  cachedCategorySlugs = Array.from(new Set(slugs)).sort();
  return cachedCategorySlugs;
}
