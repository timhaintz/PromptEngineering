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

const CP850_EXTENDED_CODE_POINTS = [
  0x00c7, 0x00fc, 0x00e9, 0x00e2, 0x00e4, 0x00e0, 0x00e5, 0x00e7, 0x00ea, 0x00eb, 0x00e8, 0x00ef, 0x00ee, 0x00ec, 0x00c4, 0x00c5,
  0x00c9, 0x00e6, 0x00c6, 0x00f4, 0x00f6, 0x00f2, 0x00fb, 0x00f9, 0x00ff, 0x00d6, 0x00dc, 0x00f8, 0x00a3, 0x00d8, 0x00d7, 0x0192,
  0x00e1, 0x00ed, 0x00f3, 0x00fa, 0x00f1, 0x00d1, 0x00aa, 0x00ba, 0x00bf, 0x00ae, 0x00ac, 0x00bd, 0x00bc, 0x00a1, 0x00ab, 0x00bb,
  0x2591, 0x2592, 0x2593, 0x2502, 0x2524, 0x00c1, 0x00c2, 0x00c0, 0x00a9, 0x2563, 0x2551, 0x2557, 0x255d, 0x00a2, 0x00a5, 0x2510,
  0x2514, 0x2534, 0x252c, 0x251c, 0x2500, 0x253c, 0x00e3, 0x00c3, 0x255a, 0x2554, 0x2569, 0x2566, 0x2560, 0x2550, 0x256c, 0x00a4,
  0x00f0, 0x00d0, 0x00ca, 0x00cb, 0x00c8, 0x0131, 0x00cd, 0x00ce, 0x00cf, 0x2518, 0x250c, 0x2588, 0x2584, 0x00a6, 0x00cc, 0x2580,
  0x00d3, 0x00df, 0x00d4, 0x00d2, 0x00f5, 0x00d5, 0x00b5, 0x00fe, 0x00de, 0x00da, 0x00db, 0x00d9, 0x00fd, 0x00dd, 0x00af, 0x00b4,
  0x00ad, 0x00b1, 0x2017, 0x00be, 0x00b6, 0x00a7, 0x00f7, 0x00b8, 0x00b0, 0x00a8, 0x00b7, 0x00b9, 0x00b3, 0x00b2, 0x25a0, 0x00a0,
];
const CP850_BYTE_BY_CHARACTER = new Map(
  CP850_EXTENDED_CODE_POINTS.map((codePoint, index) => [String.fromCodePoint(codePoint), index + 0x80]),
);
const UTF8_DECODER = new TextDecoder('utf-8', { fatal: true });

function decodeCp850Sequence(value) {
  const bytes = [];
  for (const character of value) {
    const codePoint = character.codePointAt(0);
    if (codePoint < 0x80) {
      bytes.push(codePoint);
      continue;
    }
    const byte = CP850_BYTE_BY_CHARACTER.get(character);
    if (typeof byte === 'undefined') return null;
    bytes.push(byte);
  }

  try {
    const decoded = UTF8_DECODER.decode(Uint8Array.from(bytes));
    const decodedCharacters = Array.from(decoded);
    return decodedCharacters.length === 1 && decodedCharacters[0].codePointAt(0) >= 0x80
      ? decoded
      : null;
  } catch {
    return null;
  }
}

function repairMojibakeString(value) {
  let current = value;
  for (let pass = 0; pass < 3; pass++) {
    let repaired = '';
    let changed = false;

    for (let index = 0; index < current.length;) {
      let replacement = null;
      let replacementLength = 0;
      for (const length of [4, 3, 2]) {
        const candidate = current.slice(index, index + length);
        if (candidate.length !== length) continue;
        const decoded = decodeCp850Sequence(candidate);
        if (decoded) {
          replacement = decoded;
          replacementLength = length;
          break;
        }
      }

      if (replacement) {
        repaired += replacement;
        index += replacementLength;
        changed = true;
      } else {
        repaired += current[index];
        index += 1;
      }
    }

    current = repaired;
    if (!changed) break;
  }
  return current;
}

function repairPreservedValue(value) {
  if (typeof value === 'string') return repairMojibakeString(value);
  if (Array.isArray(value)) return value.map(repairPreservedValue);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, entry]) => [key, repairPreservedValue(entry)]));
  }
  return value;
}

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
        newItem[fieldName] = repairPreservedValue(oldItem[fieldName]);
      }
    };
    // Preserve known enrichable fields
    maybePreserve('application');
    maybePreserve('template');
    maybePreserve('generalExplanation');
    maybePreserve('domainIndustryExamples');
    maybePreserve('peilPrompt');
    // Preserve application domain/task chips string when enriched
    maybePreserve('applicationTasksString');
    // Preserve knowledge intent quadrant labels assigned via enrichment tooling
    maybePreserve('knowledgeIntent');
    // Preserve the raw bracketed template string if it was enriched
    if (typeof oldItem.templateRawBracketed !== 'undefined') {
      newItem.templateRawBracketed = repairPreservedValue(oldItem.templateRawBracketed);
    }
    maybePreserve('dependentLLM');
    maybePreserve('turn');
    // usageSummary may not exist on the base schema – copy if enriched
    maybePreserve('usageSummary');

    // Unconditionally preserve applicationTasksString if it existed previously,
    // even if aiAssistedFields didn't explicitly list it (backward compatibility)
    if (typeof oldItem.applicationTasksString !== 'undefined') {
      newItem.applicationTasksString = repairPreservedValue(oldItem.applicationTasksString);
    }
    if (typeof oldItem.knowledgeIntent !== 'undefined') {
      newItem.knowledgeIntent = repairPreservedValue(oldItem.knowledgeIntent);
    }

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
    // Derive application tags (currently sourced from pattern.tags). These may be used
    // both for the `application` array and to generate a stable applicationTasksString
    // used by the UI for "Application Domains & Tasks" chips. Previously this field
    // was only present if an enrichment step populated it; that made the section
    // disappear on fresh builds. We now always generate a deterministic fallback.
    const applicationTags = (p.tags || []).filter(t => t && String(t).length > 1);
    // Fallback heuristic: treat the application tags themselves as tasks, de-duplicated,
    // joined by comma+space. This ensures the section remains visible even without
    // enrichment. If a preserved (enriched) value exists it will overwrite this in
    // mergePreservingEnriched below.
    const generatedTasksString = Array.from(new Set(applicationTags.map(t => String(t))))
      .sort((a, b) => a.localeCompare(b))
      .join(', ');
    const base = {
      id: p.id,
      category: p.category,
      name: p.patternName,
      mediaType: inferMediaType(p),
      description: p.description || '',
      template: tpl,
      application: applicationTags,
      // Always provide a tasks string fallback; enrichment (if any) can override.
      applicationTasksString: generatedTasksString || null,
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
      },
      knowledgeIntent: null
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

module.exports = { normalize, repairMojibakeString };
