import fs from 'fs';
import path from 'path';

type PatternRecord = {
  id: string;
  paper: {
    id: string;
  };
};

const PATTERNS_PATH = path.join(process.cwd(), 'public/data/patterns.json');

let cachedPaperIds: string[] | null = null;
let cachedPatterns: PatternRecord[] | null = null;

function loadPatterns(): PatternRecord[] {
  if (cachedPatterns) {
    return cachedPatterns;
  }

  if (!fs.existsSync(PATTERNS_PATH)) {
    cachedPatterns = [];
    return cachedPatterns;
  }

  const raw = fs.readFileSync(PATTERNS_PATH, 'utf8');
  cachedPatterns = JSON.parse(raw) as PatternRecord[];
  return cachedPatterns;
}

export function getAllPaperIds(): string[] {
  if (cachedPaperIds) {
    return cachedPaperIds;
  }

  const patterns = loadPatterns();
  cachedPaperIds = Array.from(new Set(patterns.map((pattern) => pattern.paper.id))).sort();
  return cachedPaperIds;
}

export function getAllPatternTriples(): Array<{
  paperId: string;
  categoryIndex: string;
  patternIndex: string;
}> {
  const patterns = loadPatterns();
  return patterns
    .map((pattern) => {
      const [paperId, categoryIndex, patternIndex] = pattern.id.split('-');
      return { paperId, categoryIndex, patternIndex };
    })
    .filter((triple) => triple.paperId && triple.categoryIndex && triple.patternIndex);
}
