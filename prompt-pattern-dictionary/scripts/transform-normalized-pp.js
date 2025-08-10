/**
 * Normalize patterns into PRD "Prompt Pattern Schema (normalized)" shape.
 * Inputs: public/data/patterns.json, public/data/similarity-analysis.json
 * Output: public/data/normalized-patterns.json
 * No embeddings are generated. Uses heuristics documented in PRD.
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'public', 'data');
const PATTERNS_FILE = path.join(DATA_DIR, 'patterns.json');
const SIMILARITY_FILE = path.join(DATA_DIR, 'similarity-analysis.json');
const OUTPUT_FILE = path.join(DATA_DIR, 'normalized-patterns.json');

function loadJson(file) {
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, 'utf-8'));
}

function inferMediaType(pattern) {
  const cat = (pattern.category || '').toLowerCase();
  const tags = (pattern.tags || []).map(t => String(t).toLowerCase());
  if (cat.includes('visual') || cat.includes('image') || tags.some(t => /visual|image|multimodal/.test(t))) {
    return 'multimodal';
  }
  return 'text';
}

function inferTurn(examples) {
  const joined = (examples || []).map(e => e.content || '').join(' ').toLowerCase();
  if (/from now on|in this conversation|whenever you|each time you/i.test(joined)) return 'multi';
  return 'single';
}

function parseTemplate(exampleText) {
  // Minimal heuristic extraction from example text.
  const text = String(exampleText ?? '').trim();
  if (!text) return {};
  const template = {};
  // role
  const roleMatch = text.match(/^(you are|act as|assume the role of)[^\n.]*[\n.]?/i);
  if (roleMatch) template.role = roleMatch[0].trim();
  // action
  const actionMatch = text.match(/\b(generate|create|explain|classify|summarize|translate|analyze)\b[^\n.]*/i);
  if (actionMatch) template.action = actionMatch[0].trim();
  // format
  const formatMatch = text.match(/\b(return|output|respond)\b[^\n.]*\b(json|yaml|bullets?|table)\b[^\n.]*/i);
  if (formatMatch) template.format = formatMatch[0].trim();
  // context: try grabbing leading context up to first imperative
  if (!template.context) {
    const ctx = text.split(/\b(generate|create|explain|classify|summarize|translate|analyze)\b/i)[0];
    if (ctx && ctx.length > 10) template.context = ctx.trim();
  }
  return template;
}

function relatedPatterns(simMap, patternId) {
  if (!simMap || !patternId) return [];
  const entry = simMap[patternId];
  if (!entry) return [];
  // If full neighbor list not present, fallback to bestMatch only
  const best = entry.bestMatch ? [entry.bestMatch] : [];
  // Note: similarity-analysis.json may not include explicit neighbor IDs; we only return [] here.
  // Future enhancement: compute nearest neighbors from embeddings if available.
  return best
    .filter(Boolean)
    .map(b => ({ category: b.category, similarity: b.similarity }));
}

function normalizeExampleText(example) {
  if (!example) return '';
  const v = (typeof example === 'object' && example !== null && 'content' in example) ? example.content : example;
  if (typeof v === 'string') return v;
  if (Array.isArray(v)) return v.map(x => (typeof x === 'string' ? x : '')).join(' ');
  try { return String(v); } catch { return ''; }
}

function normalize() {
  console.log('Normalizing patterns into PRD schema...');
  const patterns = loadJson(PATTERNS_FILE) || [];
  const sim = loadJson(SIMILARITY_FILE) || {};
  const simMap = sim.patterns || {};

  const normalized = patterns.map(p => {
    const firstExample = normalizeExampleText(p.examples && p.examples[0]);
    const tpl = parseTemplate(firstExample);
    return {
      id: p.id,
      category: p.category,
      name: p.patternName,
      mediaType: inferMediaType(p),
      description: p.description || '',
      template: tpl,
      application: (p.tags || []).filter(t => t && String(t).length > 1),
      dependentLLM: null,
      turn: inferTurn(p.examples),
      promptExamples: (p.examples || []).map(normalizeExampleText).filter(Boolean),
      related: relatedPatterns(simMap, p.id),
      reference: {
        title: p.paper?.title || '',
        authors: p.paper?.authors || [],
        url: p.paper?.url || '',
        apa: p.paper?.apaReference || ''
      }
    };
  });

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify({ metadata: { count: normalized.length, generatedAt: new Date().toISOString() }, patterns: normalized }, null, 2));
  console.log(`Wrote ${normalized.length} normalized patterns to ${OUTPUT_FILE}`);
}

if (require.main === module) {
  try {
    normalize();
    process.exit(0);
  } catch (e) {
    console.error('Normalization failed:', e);
    process.exit(1);
  }
}

module.exports = { normalize };
