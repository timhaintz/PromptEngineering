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
const SIMILAR_PATTERNS_FILE = path.join(DATA_DIR, 'similar-patterns.json');
const OUTPUT_FILE = path.join(DATA_DIR, 'normalized-patterns.json');
const PRESERVE_ENRICHED = String(process.env.PRESERVE_ENRICHED ?? '1') !== '0';

function loadJson(file) {
  if (!fs.existsSync(file)) return null;
  const raw = fs.readFileSync(file, 'utf-8');
  // Remove UTF-8 BOM if present to avoid JSON.parse errors on Windows
  const cleaned = raw.replace(/^\uFEFF/, '');
  return JSON.parse(cleaned);
}

// Map to required media types for the PRD
// Allowed values: "Text Only", "Text2Audio", "Text2Image", "Text2Video", "Audio2Text", "Image2Text", "Video2Text"
function inferMediaType(pattern) {
  const cat = (pattern.category || '').toLowerCase();
  const tags = (pattern.tags || []).map(t => String(t).toLowerCase());
  const textBlob = [pattern.description || '', ...(pattern.examples || []).map(e => (e?.content || ''))].join(' ').toLowerCase();

  const has = (re) => re.test(textBlob) || tags.some(t => re.test(t)) || re.test(cat);

  // Text to Image
  if (has(/image|vision|visual|graphviz|dall-?e|stable\s*diffusion|draw|diagram|visualize/)) {
    return 'Text2Image';
  }
  // Text to Audio
  if (has(/audio\s*(generation|synthesis)|text\s*to\s*speech|tts/)) {
    return 'Text2Audio';
  }
  // Text to Video
  if (has(/video\s*(generation|synthesis)|text\s*to\s*video/)) {
    return 'Text2Video';
  }
  // Image to Text (captioning, OCR)
  if (has(/ocr|caption|describe\s+(the\s+)?image|alt[-\s]?text|image\s*to\s*text/)) {
    return 'Image2Text';
  }
  // Audio to Text (ASR)
  if (has(/transcribe|speech\s*to\s*text|asr|audio\s*to\s*text/)) {
    return 'Audio2Text';
  }
  // Video to Text (summarization)
  if (has(/summarize\s+(this\s+)?video|video\s*to\s*text|transcript\s+video/)) {
    return 'Video2Text';
  }
  return 'Text Only';
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

function relatedPatternsFromSimilar(similarMap, patternId, limit = 8) {
  if (!similarMap || !patternId) return [];
  const arr = similarMap[patternId] || [];
  return arr.slice(0, limit).map(x => x.id);
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
  const simPatterns = loadJson(SIMILAR_PATTERNS_FILE) || null;
  const similarMap = simPatterns && simPatterns.similar ? simPatterns.similar : null;
  // Load existing normalized file (if present) to preserve enriched fields
  const existing = loadJson(OUTPUT_FILE);
  const existingMap = existing && Array.isArray(existing.patterns)
    ? Object.fromEntries(existing.patterns.map(p => [p.id, p]))
    : {};

  function mergePreservingEnriched(newItem, oldItem) {
    if (!PRESERVE_ENRICHED || !oldItem) return newItem;
    const oldEnrichedFields = new Set(Array.isArray(oldItem.aiAssistedFields) ? oldItem.aiAssistedFields : []);
    const maybePreserve = (fieldName) => {
      if (oldEnrichedFields.has(fieldName) && typeof oldItem[fieldName] !== 'undefined') {
        newItem[fieldName] = oldItem[fieldName];
      }
    };
    // Preserve known enrichable fields
    maybePreserve('application');
    maybePreserve('template');
    // Preserve the raw bracketed template string if it was enriched
    if (typeof oldItem.templateRawBracketed !== 'undefined') {
      newItem.templateRawBracketed = oldItem.templateRawBracketed;
    }
    maybePreserve('dependentLLM');
    maybePreserve('turn');
    // usageSummary may not exist on the base schema – copy if enriched
    maybePreserve('usageSummary');

    // Merge AI assistance metadata
    if (oldItem.aiAssisted) newItem.aiAssisted = true;
    const newFields = new Set(Array.isArray(newItem.aiAssistedFields) ? newItem.aiAssistedFields : []);
    oldEnrichedFields.forEach(f => newFields.add(f));
    if (newFields.size > 0) newItem.aiAssistedFields = Array.from(newFields);
    if (oldItem.aiAssistedModel && !newItem.aiAssistedModel) newItem.aiAssistedModel = oldItem.aiAssistedModel;
    if (oldItem.aiAssistedAt && !newItem.aiAssistedAt) newItem.aiAssistedAt = oldItem.aiAssistedAt;

    return newItem;
  }

  const normalized = patterns.map(p => {
    const firstExample = normalizeExampleText(p.examples && p.examples[0]);
    const tpl = parseTemplate(firstExample);
    const base = {
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
      // Prefer similar-patterns.json for linkable related IDs; fallback to similarity-analysis bestMatch otherwise
      related: (similarMap ? relatedPatternsFromSimilar(similarMap, p.id) : [])
        || [],
      reference: {
        title: p.paper?.title || '',
        authors: p.paper?.authors || [],
        url: p.paper?.url || '',
        apa: p.paper?.apaReference || ''
      }
    };
    return mergePreservingEnriched(base, existingMap[p.id]);
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
