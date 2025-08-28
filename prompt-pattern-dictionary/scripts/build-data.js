/**
 * Data processing script for Prompt Pattern Dictionary
 * Transforms promptpatterns.json into optimized formats for the web application
 */

const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const { promisify } = require('util');

// File paths
const SOURCE_FILE = path.join(__dirname, '../../promptpatterns.json');
const OUTPUT_DIR = path.join(__dirname, '../public/data');
const PATTERNS_FILE = path.join(OUTPUT_DIR, 'patterns.json');
const CATEGORIES_FILE = path.join(OUTPUT_DIR, 'pattern-categories.json');
const SEARCH_INDEX_FILE = path.join(OUTPUT_DIR, 'search-index.json');
const STATS_FILE = path.join(OUTPUT_DIR, 'stats.json');
const PYTHON_SCRIPT = path.join(__dirname, 'generate-pattern-categories.py');
const EMBEDDING_SCRIPT = path.join(__dirname, 'generate-embeddings-similarity.py');
const SEMANTIC_ANALYSIS_SCRIPT = path.join(__dirname, 'run-semantic-analysis.py');
const NORMALIZE_SCRIPT = path.join(__dirname, 'transform-normalized-pp.js');
const ENRICH_SCRIPT = path.join(__dirname, 'enrich-normalized-pp.py');

// Repo root (two levels up from this scripts folder)
const REPO_ROOT = path.join(__dirname, '..', '..');

/**
 * Choose how to run Python scripts:
 * - Prefer the currently activated Python ("python" on PATH). The user activates env at repo root.
 * - Only use `uv run` when explicitly requested via USE_UV=1.
 * - Optionally fall back to repo venv python if present and python command is unavailable (rare).
 */
function getPythonInvoker() {
  // Explicit opt-in to uv
  if (String(process.env.USE_UV).toLowerCase() === '1' || String(process.env.USE_UV).toLowerCase() === 'true') {
    return { command: 'uv', preArgs: ['run'] };
  }

  // Default: use the activated environment's python
  // This assumes the user ran the activation script in the shell invoking npm.
  const pythonOnPath = spawnSync('python', ['--version'], { stdio: 'ignore' });
  if (pythonOnPath.status === 0) {
    return { command: 'python', preArgs: [] };
  }

  // Fallback: repo venv if available
  const venvPythonPath = path.join(REPO_ROOT, 'venv', 'Scripts', 'python.exe');
  if (fs.existsSync(venvPythonPath)) {
    return { command: venvPythonPath, preArgs: [] };
  }

  // Last resort: try "py -3" on Windows or plain python
  if (process.platform === 'win32') {
    const py3 = spawnSync('py', ['-3', '--version'], { stdio: 'ignore' });
    if (py3.status === 0) return { command: 'py', preArgs: ['-3'] };
  }
  return { command: 'python', preArgs: [] };
}

/**
 * Check if embeddings already exist
 */
function checkExistingEmbeddings() {
  const embeddingDir = path.join(OUTPUT_DIR, 'embeddings');
  const embeddingIndexFile = path.join(OUTPUT_DIR, 'embedding-index.json');
  
  if (!fs.existsSync(embeddingDir) || !fs.existsSync(embeddingIndexFile)) {
    return false;
  }
  
  // Check if we have at least some embedding files
  const embeddingFiles = fs.readdirSync(embeddingDir).filter(file => file.endsWith('.json'));
  
  if (embeddingFiles.length === 0) {
    return false;
  }
  
  console.log(`✅ Found ${embeddingFiles.length} existing embedding files`);
  return true;
}

/**
 * Run Python script to generate embeddings using Azure OpenAI
 */
async function generateEmbeddings(forceRegenerate = false) {
  // Check if embeddings already exist (unless force regenerate is requested)
  if (!forceRegenerate && checkExistingEmbeddings()) {
    console.log('🔄 Embeddings already exist, skipping generation...');
    console.log('💡 Use --force-embeddings flag to regenerate embeddings');
    return;
  }
  
  return new Promise((resolve, reject) => {
    console.log('🔮 Generating embeddings with Azure OpenAI...');
    const inv = getPythonInvoker();
    const python = spawn(inv.command, [...inv.preArgs, EMBEDDING_SCRIPT], {
      cwd: path.dirname(EMBEDDING_SCRIPT),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Embedding generation completed successfully');
        if (stdout) console.log(stdout);
        resolve();
      } else {
        console.error('⚠️  Embedding generation had issues but continuing build...');
        if (stderr) console.error(stderr);
        // Don't reject - continue build without embeddings following Azure best practices
        console.log('📝 Build continuing without embeddings - check embedding_generation.log for details');
        resolve();
      }
    });

    python.on('error', (error) => {
      console.error('⚠️  Failed to start embedding generation, continuing without embeddings:', error);
      // Don't reject - graceful degradation following Azure best practices
      resolve();
    });
  });
}

/**
 * Run semantic similarity analysis using Python script
 */
async function runSemanticAnalysis() {
  console.log('🔮 Running semantic similarity analysis...');
  
  return new Promise((resolve, reject) => {
  const inv = getPythonInvoker();
  const pythonProcess = spawn(inv.command, [...inv.preArgs, SEMANTIC_ANALYSIS_SCRIPT], {
      stdio: 'inherit',
      cwd: path.dirname(SEMANTIC_ANALYSIS_SCRIPT)
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Semantic analysis completed successfully');
        resolve();
      } else {
        console.log('⚠️  Semantic analysis had issues but continuing...');
        resolve(); // Don't fail the build if semantic analysis fails
      }
    });
    
    pythonProcess.on('error', (error) => {
      console.log('⚠️  Semantic analysis error but continuing build...');
      console.log('💡 Ensure Azure OpenAI credentials are properly configured for semantic analysis');
      resolve(); // Don't fail the build if semantic analysis fails
    });
  });
}

/**
 * Run Python script to generate hierarchical pattern categories
 */
async function generateHierarchicalCategories() {
  return new Promise((resolve, reject) => {
    console.log('🐍 Generating hierarchical pattern categories with Python script...');
  const inv = getPythonInvoker();
  const python = spawn(inv.command, [...inv.preArgs, PYTHON_SCRIPT], {
      cwd: path.dirname(PYTHON_SCRIPT),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Python script completed successfully');
        if (stdout) console.log(stdout);
        resolve();
      } else {
        console.error('❌ Python script failed with code:', code);
        if (stderr) console.error(stderr);
        reject(new Error(`Python script failed with code ${code}: ${stderr}`));
      }
    });

    python.on('error', (error) => {
      console.error('❌ Failed to start Python script:', error);
      reject(error);
    });
  });
}

/**
 * Main data processing function
 */
async function processData(options = {}) {
  console.log('🔄 Starting data processing...');

  // Check if source file exists
  if (!fs.existsSync(SOURCE_FILE)) {
    throw new Error(`Source file not found: ${SOURCE_FILE}`);
  }

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Generate embeddings first (before categorization) following Azure best practices
  await generateEmbeddings(options.forceEmbeddings);

  // Generate hierarchical pattern categories using Python script
  await generateHierarchicalCategories();

  // Read and parse source data
  const rawData = fs.readFileSync(SOURCE_FILE, 'utf-8');
  const sourceData = JSON.parse(rawData);

  console.log(`📖 Loaded ${sourceData.Source.Titles.length} papers from source file`);

  // Process patterns
  const { patterns, categories, stats } = processPatterns(sourceData);

  // Generate search index
  const searchIndex = generateSearchIndex(patterns);

  // Write output files (but don't overwrite the hierarchical categories file)
  fs.writeFileSync(PATTERNS_FILE, JSON.stringify(patterns, null, 2));
  // Note: pattern-categories.json is now generated by the Python script
  fs.writeFileSync(SEARCH_INDEX_FILE, JSON.stringify(searchIndex, null, 2));
  fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2));

  console.log('✅ Data processing complete!');
  console.log(`📊 Processed ${stats.totalPatterns} patterns from ${stats.totalPapers} papers`);
  console.log(`📁 Output files written to ${OUTPUT_DIR}`);

  // Run normalization step to produce normalized-patterns.json
  try {
    console.log('🧩 Generating normalized-patterns.json...');
    const nodeCmd = process.execPath; // current Node executable
    await new Promise((resolve) => {
      const cp = spawn(nodeCmd, [NORMALIZE_SCRIPT], {
        cwd: path.dirname(NORMALIZE_SCRIPT),
        stdio: 'inherit',
        env: { ...process.env, PRESERVE_ENRICHED: process.env.PRESERVE_ENRICHED ?? '1' }
      });
      cp.on('close', () => resolve());
      cp.on('error', () => resolve());
    });
  } catch (e) {
    console.log('⚠️  Normalization step failed, continuing without normalized-patterns.json');
  }

  // Run semantic analysis if requested
  if (options.runSemanticAnalysis) {
    console.log('\n🔍 Running semantic similarity analysis...');
    await runSemanticAnalysis();
  }

  // Optional enrichment step using Azure OpenAI (gpt-5)
  if (options.enrich) {
    console.log('\n🧠 Running optional AI enrichment (gpt-5) ...');
    const inv = getPythonInvoker();
    await new Promise((resolve) => {
      const args = [...inv.preArgs, ENRICH_SCRIPT];
      if (options.enrichLimit) {
        args.push('--limit', String(options.enrichLimit));
      }
      if (options.enrichIds && options.enrichIds.length > 0) {
        args.push('--ids', options.enrichIds.join(','));
      }
      if (options.enrichFields && options.enrichFields.length > 0) {
        args.push('--enrich-fields', options.enrichFields.join(','));
      }
      if (options.enrichForce) {
        args.push('--enrich-force');
      }
      if (options.enrichForceFields && options.enrichForceFields.length > 0) {
        args.push('--enrich-force-fields', options.enrichForceFields.join(','));
      }
      if (options.enrichNoFallback) {
        args.push('--no-fallback');
      }
      const cp = spawn(inv.command, args, {
        cwd: path.dirname(ENRICH_SCRIPT),
        stdio: 'inherit'
      });
      cp.on('close', () => resolve());
      cp.on('error', () => resolve());
    });
  }
}

/**
 * Process papers into flat pattern structure
 */
function processPatterns(data) {
  const patterns = [];
  const categoryMap = new Map();
  
  let totalPatterns = 0;
  let totalExamples = 0;
  let totalCategories = 0;

  data.Source.Titles.forEach((paper, paperIndex) => {
    paper.CategoriesAndPatterns.forEach((category, categoryIndex) => {
      totalCategories++;
      
      category.PromptPatterns.forEach((pattern, patternIndex) => {
        totalPatterns++;
        
        // Generate unique ID
        const patternId = `${paperIndex}-${categoryIndex}-${patternIndex}`;
        
        // Process examples
        const processedExamples = pattern.ExamplePrompts.map((example, exampleIndex) => {
          totalExamples++;
          return {
            id: `${patternId}-${exampleIndex}`,
            content: example,
            index: exampleIndex
          };
        });

        // Create processed pattern
        const processedPattern = {
          id: patternId,
          patternName: pattern.PatternName,
          description: pattern.Description || '',
          examples: processedExamples,
          category: category.PatternCategory,
          paper: {
            id: paperIndex.toString(),
            title: paper.Title,
            authors: paper.Authors || [],
            year: paper.Year,
            url: paper.URLReference,
            apaReference: paper.APAReference
          },
          tags: generateTags(pattern, category, paper),
          searchableContent: createSearchableContent(pattern, category, paper)
        };

        patterns.push(processedPattern);

        // Group by category
        if (!categoryMap.has(category.PatternCategory)) {
          categoryMap.set(category.PatternCategory, []);
        }
        categoryMap.get(category.PatternCategory).push(processedPattern);
      });
    });
  });

  // Create category objects
  const categories = Array.from(categoryMap.entries()).map(([name, patterns]) => ({
    name,
    slug: slugify(name),
    patternCount: patterns.length,
    patterns: patterns.sort((a, b) => a.patternName.localeCompare(b.patternName))
  }));

  const stats = {
    totalPapers: data.Source.Titles.length,
    totalCategories,
    totalPatterns,
    totalExamples,
    lastProcessed: new Date().toISOString()
  };

  return { patterns, categories, stats };
}

/**
 * Generate searchable tags for a pattern
 */
function generateTags(pattern, category, paper) {
  const tags = new Set();
  
  // Add category as tag
  tags.add(category.PatternCategory.toLowerCase());
  
  // Add pattern name words
  pattern.PatternName.split(/\s+/).forEach((word) => {
    if (word.length > 2) {
      tags.add(word.toLowerCase());
    }
  });
  
  // Add year if available
  if (paper.Year) {
    tags.add(paper.Year.toString());
  }
  
  // Add common prompt engineering terms
  const commonTerms = ['prompt', 'pattern', 'llm', 'ai', 'security', 'jailbreak', 'bypass'];
  const patternText = (pattern.PatternName + ' ' + (pattern.Description || '')).toLowerCase();
  
  commonTerms.forEach(term => {
    if (patternText.includes(term)) {
      tags.add(term);
    }
  });
  
  return Array.from(tags);
}

/**
 * Create searchable content string
 */
function createSearchableContent(pattern, category, paper) {
  const parts = [
    pattern.PatternName,
    pattern.Description || '',
    category.PatternCategory,
    paper.Title,
    (paper.Authors || []).join(' '),
    ...pattern.ExamplePrompts
  ];
  
  return parts.filter(Boolean).join(' ').toLowerCase();
}

/**
 * Generate search index optimized for client-side search
 */
function generateSearchIndex(patterns) {
  return patterns.map(pattern => ({
    id: pattern.id,
    title: pattern.patternName,
    content: pattern.searchableContent,
    category: pattern.category,
    paper: pattern.paper.title,
    authors: pattern.paper.authors,
    tags: pattern.tags,
    hasExamples: pattern.examples.length > 0
  }));
}

/**
 * Convert string to URL-friendly slug
 */
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Error handling wrapper
 */
async function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    const options = {
      forceEmbeddings: args.includes('--force-embeddings'),
      runSemanticAnalysis: args.includes('--semantic-analysis'),
      enrich: args.includes('--enrich'),
      enrichLimit: (() => {
        const idx = args.indexOf('--enrich-limit');
        if (idx !== -1 && args[idx + 1]) return parseInt(args[idx + 1], 10);
        return undefined;
      })(),
      enrichFields: (() => {
        const idx = args.indexOf('--enrich-fields');
        if (idx !== -1 && args[idx + 1]) {
          return args[idx + 1].split(',').map(s => s.trim()).filter(Boolean);
        }
        return undefined;
      })(),
      enrichIds: (() => {
        const idx = args.indexOf('--enrich-ids');
        if (idx !== -1 && args[idx + 1]) {
          return args[idx + 1].split(',').map(s => s.trim()).filter(Boolean);
        }
        return undefined;
      })(),
      enrichForce: args.includes('--enrich-force') || args.includes('--force'),
      enrichForceFields: (() => {
        const idx = args.indexOf('--enrich-force-fields');
        if (idx !== -1 && args[idx + 1]) {
          return args[idx + 1].split(',').map(s => s.trim()).filter(Boolean);
        }
        return undefined;
      })(),
      enrichNoFallback: args.includes('--enrich-no-fallback')
    };

    if (args.includes('--help') || args.includes('-h')) {
      console.log('📖 Usage: node build-data.js [options]');
      console.log('');
      console.log('Options:');
      console.log('  --force-embeddings     Regenerate embeddings even if they already exist');
      console.log('  --semantic-analysis    Run semantic similarity analysis after data processing');
  console.log('  --enrich               Run optional AI enrichment (gpt-5) to suggest missing fields');
  console.log('  --enrich-limit <n>     Limit number of patterns to enrich in this run');
  console.log('  --enrich-ids <csv>     Comma-separated list of pattern IDs to enrich (e.g., 0-1-0,3-2-1)');
  console.log('  --enrich-fields <csv>  Comma-separated list of fields to enrich (template,application,dependentLLM,turn,usageSummary)');
  console.log('  --enrich-force        Force enrichment even if fields already populated');
  console.log('  --enrich-force-fields <csv>  Force enrichment for specific fields (e.g., application,usageSummary)');
  console.log('  --enrich-no-fallback  Do not write fallback messages on errors/content filter; leave fields unchanged');
  console.log('  --help, -h            Show this help message');
      process.exit(0);
    }

    await processData(options);
    process.exit(0);
  } catch (error) {
    console.error('❌ Error processing data:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { processData };
