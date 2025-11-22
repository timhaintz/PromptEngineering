#!/usr/bin/env node
/**
 * orientation_redundancy_scan.js
 * Scans Orientation section source for duplicate paragraph strings (exact match) > 120 chars repeated ≥2 times.
 * Outputs a JSON report listing duplicated paragraphs, counts, and file:line locations.
 */

const fs = require('fs');
const path = require('path');

const targetFile = path.join(__dirname, '..', 'src', 'app', 'orientation', 'data', 'sections.tsx');
const content = fs.readFileSync(targetFile, 'utf8');

// Rough paragraph heuristic: split on line breaks; join contiguous lines until blank.
const lines = content.split(/\r?\n/);
let paragraphs = [];
let buffer = [];
let lineStart = 0;

function flushParagraph(endLine) {
  if (buffer.length) {
    const text = buffer.join(' ').trim();
    if (text.length) {
      paragraphs.push({ text, start: lineStart + 1, end: endLine });
    }
    buffer = [];
  }
}

lines.forEach((line, idx) => {
  if (line.trim() === '') {
    flushParagraph(idx);
    lineStart = idx + 1;
  } else {
    if (buffer.length === 0) lineStart = idx;
    buffer.push(line.trim());
  }
});
flushParagraph(lines.length - 1);

// Filter long paragraphs (>120 chars) and count duplicates
const longParas = paragraphs.filter(p => p.text.length > 120);
const map = new Map();
longParas.forEach(p => {
  const key = p.text;
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(p);
});

const duplicates = [];
for (const [text, occ] of map.entries()) {
  if (occ.length > 1) {
    duplicates.push({ text, occurrences: occ.length, locations: occ.map(o => ({ startLine: o.start, endLine: o.end })) });
  }
}

const report = { generatedAt: new Date().toISOString(), file: targetFile, duplicateParagraphs: duplicates };
console.log(JSON.stringify(report, null, 2));

if (duplicates.length) {
  process.exitCode = 1; // non-zero to highlight action needed
}
