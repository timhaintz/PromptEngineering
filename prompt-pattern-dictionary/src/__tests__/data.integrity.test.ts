// @jest-environment node
import fs from 'fs';
import path from 'path';
import type { NormalizedPromptPattern } from '../types/patterns';

interface SourcePattern {
  PatternName: string;
  Description?: string;
  ExamplePrompts?: Array<string | Record<string, unknown>>;
}

interface SourceCategory {
  PatternCategory: string;
  PromptPatterns: SourcePattern[];
}

interface SourcePaper {
  Title: string;
  APAReference?: string;
  Authors?: string[];
  URLReference: string;
  CategoriesAndPatterns: SourceCategory[];
}

interface SourceData {
  Source: { Titles: SourcePaper[] };
}

interface WebsitePattern {
  id: string;
  patternName: string;
  description: string;
  category: string;
  examples: Array<{ id: string; content: string; index: number }>;
  paper: {
    id: string;
    title: string;
    authors: string[];
    url: string;
    apaReference?: string;
  };
}

interface WebsiteStats {
  totalPapers: number;
  totalCategories: number;
  totalPatterns: number;
  totalExamples: number;
}

function normalizeSourceExample(example: string | Record<string, unknown>): string {
  if (typeof example === 'string') return example;
  const fields = Object.entries(example).filter(([, value]) => value !== null && typeof value !== 'undefined');
  if (fields.length === 1 && typeof fields[0][1] === 'string') return fields[0][1];
  return fields.map(([name, value]) => {
    const label = name.replace(/([a-z])([A-Z])/g, '$1 $2');
    const text = typeof value === 'string' ? value : JSON.stringify(value);
    return `${label}: ${text}`;
  }).join('\n\n');
}

describe('Chapter 4 taxonomy alignment', () => {
  const taxonomyFile = path.join(process.cwd(), 'public', 'data', 'pattern-categories.json');

  it('contains the thesis-defined six logic types and 26 subcategories', () => {
    const taxonomy = JSON.parse(fs.readFileSync(taxonomyFile, 'utf8')) as {
      meta: { totalLogics: number; totalCategories: number };
      logics: Array<{ name: string; categories: Array<{ slug: string }> }>;
    };
    const categorySlugsByLogic = Object.fromEntries(
      taxonomy.logics.map(logic => [logic.name, logic.categories.map(category => category.slug)]),
    );

    expect(taxonomy.meta).toMatchObject({ totalLogics: 6, totalCategories: 26 });
    expect(categorySlugsByLogic).toEqual({
      Across: ['argument', 'comparison', 'contradiction', 'cross-boundary', 'translation'],
      At: ['assessment', 'calculation', 'induction'],
      Beyond: ['hypothesise', 'logical-reasoning', 'prediction', 'simulation'],
      In: ['categorising', 'classification', 'clustering', 'error-identification', 'input-semantics', 'requirements-elicitation'],
      Out: ['context-control', 'decomposed-prompting', 'output-customisation', 'output-semantics', 'prompt-improvement', 'refactoring'],
      Over: ['summarising', 'synthesis'],
    });
  });

  it('uses unique canonical pattern IDs for taxonomy entries', () => {
    const taxonomy = JSON.parse(fs.readFileSync(taxonomyFile, 'utf8')) as {
      logics: Array<{ categories: Array<{ patterns?: Array<{ id: string }> }> }>;
    };
    const websitePatterns = JSON.parse(
      fs.readFileSync(path.join(process.cwd(), 'public', 'data', 'patterns.json'), 'utf8'),
    ) as WebsitePattern[];
    const canonicalIds = new Set(websitePatterns.map(pattern => pattern.id));
    const taxonomyIds = taxonomy.logics.flatMap(logic =>
      logic.categories.flatMap(category => (category.patterns ?? []).map(pattern => pattern.id)),
    );

    expect(new Set(taxonomyIds).size).toBe(taxonomyIds.length);
    expect(taxonomyIds.every(id => canonicalIds.has(id))).toBe(true);
  });
});

describe('canonical source and website data parity', () => {
  const sourceFile = path.join(process.cwd(), '..', 'promptpatterns.json');
  const patternsFile = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const statsFile = path.join(process.cwd(), 'public', 'data', 'stats.json');

  let sourcePapers: SourcePaper[];
  let websitePatterns: WebsitePattern[];
  let websiteStats: WebsiteStats;

  beforeAll(() => {
    const source = JSON.parse(fs.readFileSync(sourceFile, 'utf8')) as SourceData;
    sourcePapers = source.Source.Titles;
    websitePatterns = JSON.parse(fs.readFileSync(patternsFile, 'utf8')) as WebsitePattern[];
    websiteStats = JSON.parse(fs.readFileSync(statsFile, 'utf8')) as WebsiteStats;
  });

  it('preserves every source record and example in source order', () => {
    const expectedPatterns: WebsitePattern[] = [];

    sourcePapers.forEach((paper, paperIndex) => {
      paper.CategoriesAndPatterns.forEach((category, categoryIndex) => {
        category.PromptPatterns.forEach((pattern, patternIndex) => {
          const id = `${paperIndex}-${categoryIndex}-${patternIndex}`;
          expectedPatterns.push({
            id,
            patternName: pattern.PatternName,
            description: pattern.Description ?? '',
            category: category.PatternCategory,
            examples: (pattern.ExamplePrompts ?? []).map((example, index) => ({
              id: `${id}-${index}`,
              content: normalizeSourceExample(example),
              index,
            })),
            paper: {
              id: String(paperIndex),
              title: paper.Title,
              authors: paper.Authors ?? [],
              url: paper.URLReference,
              apaReference: paper.APAReference,
            },
          });
        });
      });
    });

    expect(websitePatterns).toMatchObject(expectedPatterns);
  });

  it('has unique IDs and complete required provenance fields', () => {
    const patternIds = websitePatterns.map(pattern => pattern.id);
    expect(new Set(patternIds).size).toBe(patternIds.length);

    for (const pattern of websitePatterns) {
      expect(pattern.patternName.trim()).not.toBe('');
      expect(pattern.category.trim()).not.toBe('');
      expect(pattern.paper.title.trim()).not.toBe('');
      expect(() => new URL(pattern.paper.url)).not.toThrow();
      for (const example of pattern.examples) {
        expect(example.content.trim()).not.toBe('');
      }
    }
  });

  it('reports counts that match the canonical source', () => {
    const sourceCategories = sourcePapers.reduce(
      (total, paper) => total + paper.CategoriesAndPatterns.length,
      0,
    );
    const sourceExamples = websitePatterns.reduce(
      (total, pattern) => total + pattern.examples.length,
      0,
    );

    expect(websiteStats).toMatchObject({
      totalPapers: sourcePapers.length,
      totalCategories: sourceCategories,
      totalPatterns: websitePatterns.length,
      totalExamples: sourceExamples,
    });
    expect({
      sources: sourcePapers.length,
      patterns: websitePatterns.length,
      examples: sourceExamples,
    }).toEqual({ sources: 73, patterns: 906, examples: 1869 });
  });
});

describe('semantic analysis coverage', () => {
  const dataDir = path.join(process.cwd(), 'public', 'data');
  const websitePatterns = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'patterns.json'), 'utf8'),
  ) as WebsitePattern[];
  const taxonomy = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'pattern-categories.json'), 'utf8'),
  ) as { logics: Array<{ categories: Array<{ slug: string }> }> };
  const embeddingIndex = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'embedding-index.json'), 'utf8'),
  ) as { patternToPaper: Record<string, string | number> };
  const categoryEmbeddings = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'category-embeddings.json'), 'utf8'),
  ) as { categories: Record<string, unknown> };
  const semantic = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'semantic-assignments.json'), 'utf8'),
  ) as {
    meta: { totalPatterns: number; totalCategories: number };
    patterns: Record<string, unknown>;
    categories: Record<string, { patterns: Array<{ id: string }> }>;
  };
  const similarPatterns = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'similar-patterns.json'), 'utf8'),
  ) as { similar: Record<string, unknown> };
  const similarExamples = JSON.parse(
    fs.readFileSync(path.join(dataDir, 'similar-examples.json'), 'utf8'),
  ) as { similar: Record<string, unknown> };

  const canonicalPatternIds = websitePatterns.map(pattern => pattern.id).sort();
  const canonicalExampleIds = websitePatterns
    .flatMap(pattern => pattern.examples.map(example => example.id))
    .sort();
  const taxonomySlugs = taxonomy.logics
    .flatMap(logic => logic.categories.map(category => category.slug))
    .sort();

  it('covers every canonical pattern and thesis category', () => {
    expect(semantic.meta).toMatchObject({
      totalPatterns: canonicalPatternIds.length,
      totalCategories: taxonomySlugs.length,
    });
    expect(Object.keys(embeddingIndex.patternToPaper).sort()).toEqual(canonicalPatternIds);
    expect(Object.keys(semantic.patterns).sort()).toEqual(canonicalPatternIds);
    expect(Object.keys(categoryEmbeddings.categories).sort()).toEqual(taxonomySlugs);
    expect(Object.keys(semantic.categories).sort()).toEqual(taxonomySlugs);
  });

  it('assigns each pattern once and covers all similarity records', () => {
    const assignedIds = Object.values(semantic.categories)
      .flatMap(category => category.patterns.map(pattern => pattern.id))
      .sort();

    expect(assignedIds).toEqual(canonicalPatternIds);
    expect(Object.keys(similarPatterns.similar).sort()).toEqual(canonicalPatternIds);
    expect(Object.keys(similarExamples.similar).sort()).toEqual(canonicalExampleIds);
  });
});

describe('normalized-patterns data integrity', () => {
  const file = path.join(process.cwd(), 'public', 'data', 'normalized-patterns.json');
  interface NormalizedPatternsFile {
    patterns: NormalizedPromptPattern[];
    // allow additional metadata keys without failing type checking
    [key: string]: unknown;
  }
  let data: NormalizedPatternsFile;
  beforeAll(() => {
    expect(fs.existsSync(file)).toBe(true);
    const raw = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '').trim();
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw) as unknown;
    } catch (e) {
      throw new Error(`normalized-patterns.json failed to parse: ${String(e)}`);
    }
    if (!parsed || typeof parsed !== 'object' || !('patterns' in parsed) || !Array.isArray((parsed as { patterns?: unknown }).patterns)) {
      throw new Error('normalized-patterns.json malformed: missing patterns array');
    }
    data = parsed as NormalizedPatternsFile;
  });

  it('has patterns array', () => {
    expect(Array.isArray(data.patterns)).toBe(true);
    expect(data.patterns.length).toBeGreaterThan(0);
  });

  it('each pattern has non-empty applicationTasksString', () => {
    const missing: string[] = [];
    for (const p of data.patterns) {
      const val = p.applicationTasksString;
      if (typeof val !== 'string' || !val.trim()) {
        missing.push(p.id);
      }
    }
    if (missing.length) {
      throw new Error(`Patterns missing applicationTasksString: ${missing.slice(0,20).join(', ')}${missing.length>20?` ... (+${missing.length-20} more)`:''}`);
    }
  });

  it('contains no CP850 mojibake in preserved enrichment fields', () => {
    const serialized = JSON.stringify(data.patterns);
    for (const marker of ['ÔÇ', 'Ôë', 'Ôå', 'Ôê', 'Ôö', 'Ôû', 'Ôò', '├', '┬', '┼', '─', '╬', '╠', 'ãÆ']) {
      expect(serialized).not.toContain(marker);
    }
  });
});
