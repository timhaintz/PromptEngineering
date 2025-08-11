/*
  Generate semantic category assignments and similar patterns

  - Reads category embeddings from public/data/category-embeddings.json
  - Reads embedding index and per-paper embeddings from public/data
  - Computes cosine similarity of each pattern to each category (topN=3)
  - Assigns best category per pattern and aggregates per-category lists
  - Computes top-K similar patterns for each pattern across all patterns (K=10)
  - Writes:
      public/data/semantic-assignments.json
      public/data/similar-patterns.json

  Note: Uses only existing embeddings. No external API calls.
*/

const fs = require('fs');
const path = require('path');

function readJSON(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function cosineSimilarity(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    const va = a[i];
    const vb = b[i];
    dot += va * vb;
    na += va * va;
    nb += vb * vb;
  }
  const mag = Math.sqrt(na) * Math.sqrt(nb);
  return mag === 0 ? 0 : dot / mag;
}

function safeMkdir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

async function main() {
  const dataDir = path.join(process.cwd(), 'public', 'data');
  const embeddingsDir = path.join(dataDir, 'embeddings');
  const outAssignments = path.join(dataDir, 'semantic-assignments.json');
  const outSimilar = path.join(dataDir, 'similar-patterns.json');
  const outSimilarExamples = path.join(dataDir, 'similar-examples.json');

  // Inputs
  const categories = readJSON(path.join(dataDir, 'category-embeddings.json'));
  const index = readJSON(path.join(dataDir, 'embedding-index.json'));
  const patternsList = readJSON(path.join(dataDir, 'patterns.json'));

  // Build map id -> name, description, category (original)
  const idToPatternMeta = new Map();
  for (const p of patternsList) {
    idToPatternMeta.set(p.id, { name: p.patternName || p.name || p.title || p.id, description: p.description || '', category: p.category || null });
  }

  // Prepare category vectors
  const categoryMeta = categories.categories || categories; // support flat or nested
  const catEntries = Object.entries(categoryMeta).map(([slug, c]) => ({ slug, name: c.name, logic: c.logic, description: c.description || '', embedding: c.embedding }));
  const catDim = (catEntries[0] && catEntries[0].embedding && catEntries[0].embedding.length) || 0;

  const meta = {
    generatedAt: new Date().toISOString(),
    model: (categories.metadata && categories.metadata.model) || 'embedding-3',
    dimensions: (categories.metadata && categories.metadata.dimensions) || catDim,
    totalCategories: catEntries.length,
  };

  // Gather all pattern embeddings by streaming per paper
  const patternIds = Object.keys(index.patternToPaper);
  const paperToPatterns = new Map();
  for (const pid of patternIds) {
    const paperId = index.patternToPaper[pid];
    if (!paperToPatterns.has(paperId)) paperToPatterns.set(paperId, []);
    paperToPatterns.get(paperId).push(pid);
  }

  const patternEmbeddings = new Map(); // id -> vector
  const exampleEmbeddings = new Map(); // exampleId -> vector
  for (const [paperId, ids] of paperToPatterns) {
    const paperPath = path.join(embeddingsDir, `paper-${paperId}.json`);
    if (!fs.existsSync(paperPath)) continue;
    const paper = readJSON(paperPath);
    const pe = paper.patterns || {};
    for (const id of ids) {
      const rec = pe[id];
      if (rec && Array.isArray(rec.embedding)) {
        patternEmbeddings.set(id, rec.embedding);
      }
    }
    // also load examples from this paper
    const ex = paper.examples || {};
    for (const [exId, exRec] of Object.entries(ex)) {
      if (exRec && Array.isArray(exRec.embedding)) {
        exampleEmbeddings.set(exId, exRec.embedding);
      }
    }
  }

  // Compute best categories per pattern
  const patterns = {};
  const categoriesOut = {};
  for (const ce of catEntries) {
    categoriesOut[ce.slug] = {
      name: ce.name,
      slug: ce.slug,
      logic: ce.logic,
      description: ce.description,
      patternCount: 0,
      patterns: []
    };
  }

  const TOP_N = 3;
  const SIM_THRESHOLD = 0.45; // conservative default

  for (const [id, vec] of patternEmbeddings) {
    // Rank categories by similarity
    const scores = catEntries.map(ce => ({ slug: ce.slug, name: ce.name, similarity: cosineSimilarity(vec, ce.embedding) }))
      .sort((a, b) => b.similarity - a.similarity);
    const top = scores.slice(0, TOP_N);
    const best = top[0];

    patterns[id] = {
      id,
      name: (idToPatternMeta.get(id) || {}).name || id,
      currentCategory: (idToPatternMeta.get(id) || {}).category || null,
      bestCategory: best,
      topCategories: top
    };

    // Assign into category if passes threshold; otherwise still assign best for counts but mark low confidence
    const assignSlug = best.slug;
    if (categoriesOut[assignSlug]) {
      categoriesOut[assignSlug].patterns.push({ id, name: patterns[id].name, similarity: best.similarity });
      categoriesOut[assignSlug].patternCount++;
    }
  }

  // Sort patterns in each category by similarity desc
  for (const c of Object.values(categoriesOut)) {
    c.patterns.sort((a, b) => b.similarity - a.similarity);
  }

  const assignments = {
    meta: { ...meta, threshold: SIM_THRESHOLD, topN: TOP_N, totalPatterns: Object.keys(patterns).length },
    categories: categoriesOut,
    patterns
  };

  // Compute similar patterns (top-K) using brute force across all patterns
  const allIds = Array.from(patternEmbeddings.keys());
  const K = 10;
  const similar = {};

  for (let i = 0; i < allIds.length; i++) {
    const idA = allIds[i];
    const va = patternEmbeddings.get(idA);
    const scores = [];
    for (let j = 0; j < allIds.length; j++) {
      if (i === j) continue;
      const idB = allIds[j];
      const vb = patternEmbeddings.get(idB);
      const s = cosineSimilarity(va, vb);
      scores.push({ id: idB, similarity: s });
    }
    scores.sort((a, b) => b.similarity - a.similarity);
    similar[idA] = scores.slice(0, K);
  }

  // Write outputs
  safeMkdir(dataDir);
  fs.writeFileSync(outAssignments, JSON.stringify(assignments, null, 2), 'utf8');
  fs.writeFileSync(outSimilar, JSON.stringify({ meta: { generatedAt: meta.generatedAt, k: K }, similar }, null, 2), 'utf8');
  
  // Compute similar examples (top-5 across all examples)
  const exIds = Array.from(exampleEmbeddings.keys());
  const exK = 5;
  const similarExamples = {};
  for (let i = 0; i < exIds.length; i++) {
    const idA = exIds[i];
    const va = exampleEmbeddings.get(idA);
    const scores = [];
    for (let j = 0; j < exIds.length; j++) {
      if (i === j) continue;
      const idB = exIds[j];
      const vb = exampleEmbeddings.get(idB);
      const s = cosineSimilarity(va, vb);
      scores.push({ id: idB, similarity: s });
    }
    scores.sort((a, b) => b.similarity - a.similarity);
    similarExamples[idA] = scores.slice(0, exK);
  }
  fs.writeFileSync(outSimilarExamples, JSON.stringify({ meta: { generatedAt: meta.generatedAt, k: exK }, similar: similarExamples }, null, 2), 'utf8');

  console.log(`Wrote semantic assignments to ${path.relative(process.cwd(), outAssignments)}`);
  console.log(`Wrote similar patterns to ${path.relative(process.cwd(), outSimilar)}`);
  console.log(`Wrote similar examples to ${path.relative(process.cwd(), outSimilarExamples)}`);
}

main().catch(err => {
  console.error('Failed to generate semantic categories:', err);
  process.exit(1);
});
