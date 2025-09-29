import fs from 'fs';
import path from 'path';

// Directories to scan for legacy --color-* references (excluding styles where tokens were intentionally removed)
const ROOT = path.join(__dirname, '..', '..');
const SCAN_DIRS = [
  path.join(ROOT, 'src'),
  path.join(ROOT, 'app'),
  path.join(ROOT, 'components'),
];

const LEGACY_PATTERN = /--color-[a-z0-9-]+/i;

function collectFiles(dir: string, acc: string[]) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    if (e.name.startsWith('.')) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      // skip Next.js build and public data
      if (['.next', 'public', '__tests__'].includes(e.name)) continue;
      collectFiles(full, acc);
    } else if (/\.(tsx?|css|md)$/.test(e.name)) {
      acc.push(full);
    }
  }
}

describe('legacy design token ban', () => {
  it('contains no remaining --color-* variable references in source', () => {
    const files: string[] = [];
    for (const dir of SCAN_DIRS) collectFiles(dir, files);
    const offenders: { file: string; line: number; match: string }[] = [];
    for (const f of files) {
      const content = fs.readFileSync(f, 'utf8');
      const lines = content.split(/\r?\n/);
      lines.forEach((line, idx) => {
        const m = line.match(LEGACY_PATTERN);
        if (m) offenders.push({ file: path.relative(ROOT, f), line: idx + 1, match: m[0] });
      });
    }
    if (offenders.length) {
      const report = offenders
        .map(o => `${o.file}:${o.line} -> ${o.match}`)
        .join('\n');
      fail(`Found legacy --color-* variable references after semantic refactor:\n${report}`);
    }
  });
});
