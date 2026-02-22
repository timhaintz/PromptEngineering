# Prompt Pattern Dictionary — Project Structure

> Last verified: July 2025. If you add a route, component, or script please update this file.

## Root Structure

```
prompt-pattern-dictionary/
├── .github/
│   └── ISSUE_TEMPLATE/
│       ├── ai_assist_correction.yml
│       └── responsible_use_report.yml
├── .vscode/
│   └── tasks.json
├── docs/                                    # Project documentation
│   ├── ACCESSIBILITY.md                     # WCAG mapping, audit log, regression checklist
│   ├── FOLDER_STRUCTURE.md                  # This file
│   ├── PHASE2_IMPLEMENTATION_SUMMARY.md     # Phase 2 delivery notes
│   ├── PRD.md                               # Product Requirements Document (canonical)
│   ├── telemetry.md                         # Telemetry event schema (draft)
│   └── THEMING.md                           # Theming & design tokens (canonical)
├── public/
│   ├── data/                                # Processed data files (see Data Pipeline below)
│   │   ├── embeddings/                      # Per-paper embedding JSON (paper-0…72, minus 32 & 45)
│   │   ├── category-embeddings.json
│   │   ├── embedding-index.json
│   │   ├── embedding-stats.json
│   │   ├── normalized-patterns.json
│   │   ├── pattern-categories.json
│   │   ├── pattern-categories-flat.json
│   │   ├── patterns.json
│   │   ├── search-index.json
│   │   ├── semantic-assignments.json
│   │   ├── similar-examples.json
│   │   ├── similar-patterns.json
│   │   ├── similarity-analysis.json
│   │   └── stats.json
│   └── *.svg                                # Static assets (file.svg, globe.svg, next.svg, etc.)
├── scripts/                                 # Build & utility scripts (Node + Python)
│   ├── build-data.js                        # Main data build orchestrator
│   ├── transform-normalized-pp.js           # Normalize patterns → normalized-patterns.json
│   ├── generate-semantic-categories.js      # Semantic category assignments
│   ├── coerce-application-arrays.js         # DEPRECATED — use build-data.js --coerce-application-arrays
│   ├── contrast-audit.cjs                   # Automated contrast audit (npm run a11y:contrast)
│   ├── contrast_audit.js                    # Legacy copy — prefer contrast-audit.cjs
│   ├── orientation_redundancy_scan.js       # Orientation content duplication checker
│   ├── enrich-normalized-pp.py              # GPT-5 enrichment pipeline
│   ├── generate-embeddings-similarity.py    # Pattern embedding + similarity generation
│   ├── generate-example-embeddings.py       # Example-level embedding generation
│   ├── generate-category-embeddings.py      # Category embedding generation
│   ├── generate-pattern-categories.py       # Hierarchical category builder
│   ├── analyze-semantic-similarity.py       # Semantic similarity analysis
│   ├── run-semantic-analysis.py             # Orchestrates semantic analysis
│   ├── backfill_knowledge_intent.py         # Knowledge intent quadrant classifier
│   ├── backfill_domain_example_categories.py
│   ├── domain_example_classifier.py
│   ├── knowledge_intent_classifier.py
│   └── peil_prompt_reference.py             # PEIL prompt generation reference
├── src/                                     # Application source code
│   └── (see below)
├── tests/                                   # Playwright & integration tests
│   ├── a11y/
│   │   └── accessibility.spec.ts            # axe-core e2e accessibility tests
│   └── themePersistence.test.tsx             # Theme storage persistence test
├── types/                                   # Root-level type declarations
│   └── jest-axe.d.ts                        # jest-axe type augmentation
├── tmp/                                     # Ephemeral caches (gitignored)
│
├── .gitignore
├── eslint.config.mjs                        # ESLint flat config
├── jest.config.cjs                          # Jest configuration
├── jest.setup.ts                            # Jest setup (jest-axe, etc.)
├── next.config.ts                           # Next.js config (static export, basePath)
├── package.json
├── playwright.config.ts                     # Playwright config for a11y tests
├── postcss.config.mjs                       # PostCSS config (Tailwind v4 plugin)
├── tsconfig.json                            # TypeScript configuration
├── README.md                                # Project overview & quick start
├── ACCESSIBILITY.md                         # Root-level accessibility notes
├── SECURITY.md                              # Security policy
└── THEMING.md                               # Root-level theming notes
```

## `src/` — Application Source

### `src/app/` — Next.js App Router Pages

```
src/app/
├── layout.tsx                               # Root layout (ThemeProvider, TopNav, pre-hydration script)
├── page.tsx                                 # Homepage
├── globals.css                              # Global CSS (Tailwind directives, tokens import)
├── favicon.ico
│
├── categories/page.tsx                      # All categories listing
├── category/[slug]/page.tsx                 # Individual category page
├── comparison/page.tsx                      # Pattern comparison dashboard
├── examples/page.tsx                        # Examples browser
├── logic/page.tsx                           # Logic categories view
├── matrix/page.tsx                          # Similarity matrix page
├── paper/[paperId]/page.tsx                 # Single paper redirect
├── papers/page.tsx                          # All papers listing
├── papers/[paperId]/page.tsx                # Individual paper page
├── pattern/[paperId]/page.tsx               # Paper pattern overview
├── pattern/[paperId]/[catIdx]/[patIdx]/page.tsx  # Individual pattern page
├── patterns/page.tsx                        # All patterns browser
├── playground/page.tsx                      # Similarity playground (stub)
├── responsible-use/page.tsx                 # Responsible use guidelines
├── search/page.tsx                          # Search interface
├── semantic/page.tsx                        # Semantic category explorer
├── taxonomy/page.tsx                        # Taxonomy overview
│
└── orientation/                             # Orientation hub (multi-page)
    ├── layout.tsx                           # Orientation layout (side nav)
    ├── page.tsx                             # Orientation landing
    ├── data/sections.tsx                    # Section content data (1300+ lines)
    ├── hooks/usePreferences.tsx             # User preference hook
    ├── utils/readingTime.ts                 # Reading time calculator
    ├── components/                          # Orientation-specific components
    │   ├── ClientDecisionTree.tsx
    │   ├── CopyButton.tsx
    │   ├── DecisionTreeWidget.tsx
    │   ├── LegacyHashRedirect.tsx
    │   ├── OrientationNav.tsx
    │   ├── QuickPathsPanel.tsx
    │   ├── ReadingTimeBadge.tsx
    │   └── SectionPager.tsx
    └── [slug]/page.tsx                      # 18 sub-pages:
        # about, accessibility-responsible-use, adaptation, all,
        # anti-patterns, cheatsheet, choosing-patterns, combining-patterns,
        # faq, feedback, glossary, hub, learning-path, lifecycle,
        # next-steps, pattern-anatomy, quality-evaluation, quick-start,
        # search-similarity, similarity-preview, what-is-a-pattern
```

### `src/components/` — Reusable React Components

```
src/components/
├── comparison/                              # Pattern comparison UI
│   ├── index.ts                             # Barrel export
│   ├── ComparisonDashboard.tsx              # Main comparison dashboard
│   ├── PatternSelector.tsx                  # Pattern multi-select
│   ├── SimilarityMatrix.tsx                 # Matrix heatmap view
│   ├── SimilarityNetwork.tsx                # Force-directed network graph
│   └── SimilarityPlayground.tsx             # Playground text → similarity
├── diagram/
│   └── MermaidDiagram.tsx                   # Mermaid diagram renderer
├── examples/
│   └── ExamplesBrowser.tsx                  # Examples list/grid browser
├── layout/
│   └── PageShell.tsx                        # Standard page wrapper (width variants)
├── navigation/
│   ├── Breadcrumbs.tsx                      # Breadcrumb trail
│   ├── OrientationSideNav.tsx               # Orientation sticky sidebar
│   ├── OrientationTOC.tsx                   # Table of contents (scrollspy)
│   └── TopNav.tsx                           # Global top navigation bar
├── papers/
│   ├── PapersGrid.tsx                       # Papers grid/list view
│   └── PatternDetail.tsx                    # Shared pattern detail component
├── patterns/
│   └── PatternsBrowser.tsx                  # Patterns list browser
├── search/
│   └── SearchInterface.tsx                  # Homepage/search page search UI
├── semantic/
│   └── SemanticCategoryMatrix.tsx           # Semantic category matrix view
├── ui/                                      # Atomic UI primitives
│   ├── Badge.tsx
│   ├── Card.tsx
│   ├── PageHeader.tsx
│   ├── Spinner.tsx
│   ├── StatChip.tsx
│   └── Tile.tsx
├── visualization/
│   └── Heatmap.tsx                          # Recharts-based heatmap component
├── ProvenanceBadge.tsx                      # AI-assisted provenance badge
├── ThemeProvider.tsx                         # Centralized theme state manager
└── ThemeSwitcher.tsx                        # Light/Dark/System toggle
```

### `src/lib/` — Business Logic & Utilities

```
src/lib/
├── data/
│   ├── categories.ts                        # Category data loading helpers
│   └── papers.ts                            # Paper data loading helpers
├── search/
│   └── booleanQuery.ts                      # Boolean query parser
├── similarity/
│   ├── index.ts                             # Barrel: cosine similarity, compare, search, cache
│   ├── similarity-engine.ts                 # Core embedding calculations + SimilarityEngine class
│   ├── similarity-matrix.ts                 # Sparse matrix implementation + SimilarityMatrix class
│   └── similarity-network.ts                # Graph analysis + SimilarityNetwork class
└── types/
    └── pattern.ts                           # Core TypeScript types (Paper, Pattern, Example,
                                             #   embeddings, comparison, visualization)
```

### Other `src/` Directories

```
src/styles/
├── theme.css                                # Semantic utility classes (surface-card, input-base, etc.)
└── tokens.css                               # Design token primitives per theme mode

src/types/
└── patterns.ts                              # Enhanced pattern types (semantic categorization,
                                             #   NormalizedPromptPattern, search filters)

src/utils/
└── paths.ts                                 # Base path utilities for GitHub Pages

src/__tests__/
├── a11y.basic.test.tsx                      # Basic accessibility smoke tests
├── a11y.orientation.test.tsx                # Orientation page a11y tests
├── bannedClasses.test.ts                    # Banned Tailwind class detection
├── contrast.tokens.test.ts                  # Token contrast ratio validation
├── data.integrity.test.ts                   # Data file schema validation
├── highContrastTokens.test.tsx              # High-contrast theme token tests
├── legacy.variables.ban.test.ts             # Legacy --color-* variable ban
├── similarityPreview.snapshot.test.tsx       # Similarity preview snapshot
├── similarityPreview.test.tsx               # Similarity preview unit tests
├── theme.regression.test.tsx                # Theme persistence regression tests
└── __snapshots__/
    └── similarityPreview.snapshot.test.tsx.snap
```

## Key Directory Explanations

### `/src/app/` — Next.js App Router

Uses the App Router with file-based routing. Dynamic segments (`[paperId]`, `[slug]`) generate static pages at build time via `generateStaticParams`. The project uses `output: "export"` in `next.config.ts` for fully static deployment — there are no API routes.

### `/src/components/` — Component Architecture

- **comparison/**: Multi-pattern comparison and playground UI (currently mocked data)
- **papers/**: `PatternDetail.tsx` is the shared pattern rendering component used by both paper and category pages
- **navigation/**: Global nav, breadcrumbs, and orientation-specific side navigation
- **ui/**: Atomic primitives shared across the application
- **visualization/**: Data visualization components (Heatmap via Recharts)

### `/src/lib/similarity/` — Similarity Library

The barrel `index.ts` re-exports from submodules and provides the main API:
- `comparePatterns()` — multi-pattern comparison with embeddings
- `findSimilarPatternsFromText()` — text → similar patterns (currently returns mock data)
- `embeddingCache` — lazy-loading embedding cache

The submodules (`similarity-engine.ts`, `similarity-matrix.ts`, `similarity-network.ts`) provide class-based implementations used internally.

### `/public/data/` — Processed Data

Generated by `npm run build-data`. Only commit changes when the upstream `promptpatterns.json` changes — timestamp-only rebuilds should not be committed.

> **Pipeline-only files**: `search-index.json` and `pattern-categories-flat.json` are generated by the build pipeline but not currently consumed by the UI. They exist for future use and external tooling. `similarity-analysis.json` is consumed by `transform-normalized-pp.js` as an intermediate pipeline artifact.

### `/scripts/` — Build Automation

- **Node.js**: `build-data.js` orchestrates the pipeline; `transform-normalized-pp.js` and `generate-semantic-categories.js` run as sub-steps.
- **Python**: Embedding generation, enrichment (GPT-5), classification, and analysis scripts. Require Azure OpenAI credentials.

## Data Pipeline

```
promptpatterns.json (source)
    │
    ▼
build-data.js                    → patterns.json, search-index.json, stats.json,
                                    pattern-categories.json, pattern-categories-flat.json
    │
    ▼
transform-normalized-pp.js       → normalized-patterns.json
    │
    ▼
generate-semantic-categories.js  → semantic-assignments.json
    │
    ▼
next build                       → out/ (static export)
```

Optional steps (require Azure credentials):
- `generate-embeddings-similarity.py` → `embeddings/`, `embedding-index.json`
- `enrich-normalized-pp.py --enrich` → updates `normalized-patterns.json` with AI metadata

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 with App Router (`output: "export"`) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS v4 (via `@tailwindcss/postcss`) — no `tailwind.config.js` |
| Theming | Semantic design tokens (`tokens.css` + `theme.css`), ThemeProvider |
| Search | Client-side search over pre-built JSON indexes |
| Embeddings | Azure OpenAI `text-embedding-3-large` (3072 dimensions) |
| Unit Tests | Jest + jest-axe (accessibility) |
| E2E Tests | Playwright + @axe-core/playwright |
| Build Output | Static `out/` directory for GitHub Pages |

## Development Workflow

1. Clone the repository
2. `npm install`
3. `npm run build-data` — process source JSON into `public/data/`
4. `npm run dev` — start development server at `localhost:3000`
5. `npm run build` — full production build (data + Next.js static export)
6. `npm run preview` — serve existing `out/` without rebuilding
