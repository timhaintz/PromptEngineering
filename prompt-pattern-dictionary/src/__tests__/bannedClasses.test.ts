/**
 * Regression test: disallow reintroduction of raw Tailwind palette classes that bypass theme tokens.
 * If you need a new semantic color, add a token + utility instead of using these directly.
 */
import fs from 'fs';
import path from 'path';

// Classes we consider forbidden in app source (case-sensitive substring match is fine for now)
const BANNED = [
  'text-gray-900', 'text-gray-800', 'text-gray-700', 'text-gray-600', 'text-blue-700', 'text-blue-800',
  'bg-blue-50', 'bg-blue-100', 'bg-purple-100', 'text-purple-700', 'bg-green-100', 'text-green-700'
];

// Directories to scan (add more if app structure changes)
const SRC_DIR = path.join(process.cwd(), 'src', 'app');

function gatherFiles(dir: string, acc: string[] = []) {
  for (const entry of fs.readdirSync(dir)) {
    const full = path.join(dir, entry);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) gatherFiles(full, acc);
    else if (/\.(tsx|jsx|ts|js)$/.test(entry)) acc.push(full);
  }
  return acc;
}

describe('banned utility classes', () => {
  const files = gatherFiles(SRC_DIR);
  it('contains no banned palette classes', () => {
    const offenders: { file: string; line: number; snippet: string; token: string }[] = [];
    for (const file of files) {
      const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
      lines.forEach((line, idx) => {
        for (const token of BANNED) {
          if (line.includes(token)) {
            offenders.push({ file: path.relative(process.cwd(), file), line: idx + 1, snippet: line.trim(), token });
          }
        }
      });
    }
    if (offenders.length) {
      const details = offenders.map(o => `${o.file}:${o.line} => [${o.token}] ${o.snippet}`).join('\n');
      throw new Error(`Found banned palette classes. Replace with semantic tokens.\n${details}`);
    }
  });
});
