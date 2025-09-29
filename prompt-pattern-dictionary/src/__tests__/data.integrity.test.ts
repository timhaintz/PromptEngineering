// @jest-environment node
import fs from 'fs';
import path from 'path';
import type { NormalizedPromptPattern } from '../types/patterns';

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
    const raw = fs.readFileSync(file, 'utf8');
    const parsed = JSON.parse(raw) as unknown;
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
});
