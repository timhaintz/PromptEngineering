#!/usr/bin/env node
/**
 * contrast_audit.js
 * Simple WCAG contrast audit for High-Contrast theme tokens.
 * Parses tokens.css, extracts key color variables for [data-theme='high-contrast'] and
 * computes contrast ratios of text vs surface backgrounds and accent vs surface.
 * Outputs JSON report to stdout. Intended as lightweight P4 verification.
 */
const fs = require('fs');
const path = require('path');

function parseHighContrastBlock(css){
  const match = css.match(/\[data-theme='high-contrast'\][^}]+{([^}]+)}/);
  if(!match) return {};
  const body = match[1];
  const vars = {};
  body.split(/;\s*/).forEach(line=>{
    const m = line.match(/--([a-z0-9-]+):\s*([^;]+)/i);
    if(m){ vars[m[1]] = m[2].trim(); }
  });
  return vars;
}

function hexToRgb(hex){
  hex = hex.replace('#','');
  if(hex.length===3) hex = hex.split('').map(c=>c+c).join('');
  const num = parseInt(hex,16);
  return { r:(num>>16)&255, g:(num>>8)&255, b:num&255 };
}

function relativeLuminance({r,g,b}){
  [r,g,b] = [r,g,b].map(v=>{
    v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);
  });
  return 0.2126*r + 0.7152*g + 0.0722*b;
}

function contrast(hexA, hexB){
  try {
    const L1 = relativeLuminance(hexToRgb(hexA));
    const L2 = relativeLuminance(hexToRgb(hexB));
    const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    return Number(ratio.toFixed(2));
  } catch { return null; }
}

const tokensPath = path.join(__dirname,'..','src','styles','tokens.css');
const css = fs.readFileSync(tokensPath,'utf8');
const vars = parseHighContrastBlock(css);

const pairs = [
  ['text-primary','surface-1'],
  ['text-secondary','surface-1'],
  ['text-muted','surface-1'],
  ['accent','surface-1'],
  ['accent-fg','accent'],
  ['focus-ring','surface-2']
];

const results = pairs.map(([fg,bg])=>{
  const fgVal = vars[fg];
  const bgVal = vars[bg];
  const ratio = fgVal && bgVal ? contrast(fgVal, bgVal) : null;
  const passAA = ratio!==null && ratio >= 4.5;
  const passEnhanced = ratio!==null && ratio >= 7;
  return { pair:`${fg} vs ${bg}`, fg:fgVal, bg:bgVal, ratio, passAA, passEnhanced };
});

const report = {
  generatedAt: new Date().toISOString(),
  mode: 'high-contrast',
  tokensFound: Object.keys(vars).length,
  results
};

console.log(JSON.stringify(report,null,2));
// Non-zero exit if any primary text pair fails enhanced target (≥7:1) for body text.
const primaryPair = results.find(r=>r.pair.startsWith('text-primary'));
if(primaryPair && !primaryPair.passEnhanced){
  process.exitCode = 1;
}