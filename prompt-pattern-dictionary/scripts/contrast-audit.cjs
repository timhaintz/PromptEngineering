#!/usr/bin/env node
/* Contrast Audit Script
 * Scans CSS custom properties in :root for color tokens and computes contrast ratios
 * against background surfaces. Generates a simple report and optional non-zero exit.
 */
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const shouldFail = args.includes('--fail');

const cssPath = path.join(process.cwd(), 'src', 'app', 'globals.css');
if (!fs.existsSync(cssPath)) {
  console.error('globals.css not found at', cssPath);
  process.exit(1);
}
const css = fs.readFileSync(cssPath, 'utf8');

// Extract :root variable definitions
const varBlockMatch = css.match(/:root\s*{([\s\S]*?)}/);
if (!varBlockMatch) {
  console.error('No :root block found.');
  process.exit(1);
}
const rootBlock = varBlockMatch[1];
const colorVars = {};
rootBlock.split(/;\n?/).forEach(line => {
  const m = line.match(/(--[a-zA-Z0-9-_]+):\s*([^;]+)/);
  if (m) {
    colorVars[m[1]] = m[2].trim();
  }
});

function parseColor(val) {
  if (!val) return null;
  if (val.startsWith('#')) {
    const hex = val.replace('#','');
    if (hex.length === 3) {
      const r = parseInt(hex[0]+hex[0],16);
      const g = parseInt(hex[1]+hex[1],16);
      const b = parseInt(hex[2]+hex[2],16);
      return {r,g,b};
    }
    if (hex.length === 6) {
      const r = parseInt(hex.slice(0,2),16);
      const g = parseInt(hex.slice(2,4),16);
      const b = parseInt(hex.slice(4,6),16);
      return {r,g,b};
    }
  }
  return null; // skip non-hex for now
}

function relLuminance({r,g,b}) {
  const srgb = [r,g,b].map(c => {
    const v = c/255;
    return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4);
  });
  return 0.2126*srgb[0] + 0.7152*srgb[1] + 0.0722*srgb[2];
}
function contrast(c1, c2) {
  const L1 = relLuminance(c1);
  const L2 = relLuminance(c2);
  const lighter = Math.max(L1,L2);
  const darker = Math.min(L1,L2);
  return (lighter + 0.05) / (darker + 0.05);
}

const bgKeys = Object.keys(colorVars).filter(k => /background|surface$/.test(k));
const fgKeys = Object.keys(colorVars).filter(k => ['--foreground','--color-accent','--color-link','--color-danger','--color-muted'].includes(k));

const issues = [];
const rows = [];
for (const bg of bgKeys) {
  const bgColor = parseColor(colorVars[bg]);
  if (!bgColor) continue;
  for (const fg of fgKeys) {
    const fgColor = parseColor(colorVars[fg]);
    if (!fgColor) continue;
    const ratio = contrast(bgColor, fgColor);
    const passesAA = ratio >= 4.5; // normal text baseline
    rows.push({bg, fg, ratio: ratio.toFixed(2), pass: passesAA});
    if (!passesAA) {
      issues.push({bg, fg, ratio});
    }
  }
}

console.log('Contrast Audit Report');
console.log('=====================');
rows.forEach(r => {
  console.log(`${r.fg} on ${r.bg}: ${r.ratio} ${r.pass ? 'PASS' : 'FAIL'}`);
});

if (issues.length) {
  console.log('\nFailing pairs (AA < 4.5):');
  issues.forEach(i => console.log(` - ${i.fg} on ${i.bg}: ${i.ratio}`));
  if (shouldFail) {
    console.error(`\nContrast audit failed with ${issues.length} failing pairs.`);
    process.exit(2);
  }
} else {
  console.log('\nAll checked pairs pass AA (4.5:1) baseline.');
}
