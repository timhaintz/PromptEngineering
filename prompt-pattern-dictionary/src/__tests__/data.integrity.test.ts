// @jest-environment node
import fs from 'fs';
import path from 'path';

describe('normalized-patterns data integrity', () => {
  const file = path.join(process.cwd(), 'public', 'data', 'normalized-patterns.json');
  let data: any;
  beforeAll(() => {
    expect(fs.existsSync(file)).toBe(true);
    const raw = fs.readFileSync(file, 'utf8');
    data = JSON.parse(raw);
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
