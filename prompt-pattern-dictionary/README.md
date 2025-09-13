# Prompt Pattern Dictionary

A comprehensive, searchable dictionary of prompt engineering patterns for cybersecurity applications. This project provides an OED-style interface for discovering and learning prompt patterns extracted from research papers.

## 🎯 Project Overview

This is a Next.js-based web application that transforms academic research on prompt engineering into an accessible, searchable dictionary. It serves as the definitive reference tool for cybersecurity prompt engineering patterns.

For the normalized Prompt Pattern schema and mapping details, see the Product Requirements Document (Prompt Pattern Schema section): docs/PRD.md.

### Key Features

- **Dictionary-Style Interface**: Clean, professional layout inspired by the Oxford English Dictionary
- **Advanced Search**: Full-text search with category filtering and fuzzy matching
- **Research Paper Integration**: Direct links to source papers with proper attribution
- **Pattern Categories**: Organized by Input Semantics, Output Customization, Security Testing, etc.
- **Copy-to-Clipboard**: Easy copying of prompt examples
- **Responsive Design**: Optimized for desktop and mobile devices
- **AI-Assisted Enrichment (Optional)**: Fill missing pattern fields with Azure OpenAI (GPT-5) and display an “AI-assisted” badge with disclaimer

### Recent UI/UX Updates

- **Unified Pattern View**: A shared PatternDetail component renders patterns identically on both paper pages and category pages.
	- Collapsible Template and Prompt Examples; defaults are compact and persist per pattern via localStorage
	- Example rows keep their ID badges; Template is shown as preformatted text when expanded
- **Similarity Surfacing**:
	- Per-example “Similar Examples” chips with IDs and similarity scores; links deep into the canonical paper example anchors
	- Fallback when example-level data is missing uses “Similar Patterns” mapped to each pattern’s first example
	- “Similar Patterns” section is collapsible and hidden by default on both paper and category pages
- **Deep-Linking & Permalinks**: All pattern/example links resolve to /papers routes using stable anchors
	- Patterns: `#p-{categoryIndex}-{patternIndex}`
	- Examples: `#e-{categoryIndex}-{patternIndex}-{exampleIndex}`
	- Category pages show an inline “Paper: Title” link next to the Permalink for quick source navigation
- **Matrix Semantics**: Matrix counts now reflect semantic similarity category assignments with robust fallback to original taxonomy when needed
- **Search UX**: Results categorized by type with filters, clean blank initial state, “Clear all,” and URL state persistence
- **Accessibility**: Improved contrast and chevron-based toggles with appropriate ARIA controls
 - **How to apply**: A concise 1–2 sentence usage summary is shown inline under Application when available; generated via optional enrichment.
 - **Orientation Layout (OED-Inspired)**: Refactored Orientation page to a two-column grid with a sticky numbered side navigation (desktop) and chip navigation (mobile), mirroring reference dictionary usage guides.
 - **Cheat Sheet Page**: Added `/orientation/cheatsheet` printable condensed reference (5-Key template, lifecycle, evaluation metrics, anti‑patterns, responsible use).
 - **Accessibility & Responsible Use Section**: Dedicated section consolidating inclusive design, bias monitoring, provenance, and escalation guidance.
 - **Sticky Side Navigation**: IntersectionObserver-driven highlight state with scroll offset margin for unobscured anchored headings.
 - **Numbered Sections & Skip Link**: Added ordered heading numbering for cognitive mapping plus a skip-to-content link for keyboard and screen reader efficiency.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/timhaintz/PromptEngineering4Cybersecurity.git

# Navigate to the project
cd PromptEngineering4Cybersecurity/prompt-pattern-dictionary

# Install dependencies
npm install

# Process the source data
npm run build-data

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dictionary.

### Start in production

To run the site in production mode (optimized build):

```bash
# Build the app (includes data processing & semantic artifacts)
npm run build

# Start the production server
npm run start
```

## 📁 Project Structure

```
prompt-pattern-dictionary/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable React components
│   ├── lib/             # Utilities and data processing
│   └── types/           # TypeScript definitions
├── public/
│   └── data/            # Processed pattern data
├── scripts/             # Build and data processing scripts
└── docs/                # Project documentation
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start the production server (after `npm run build`)
- `npm run build-data` - Process source JSON into optimized format
- `npm run lint` - Run ESLint
- `npm test` - Run tests

### Data Processing

The application processes `../promptpatterns.json` to create:
- Individual pattern pages
- Search indexes
- Category listings
- Cross-references

#### Data Files and Semantics

Processed artifacts in `public/data/` include:

- `normalized-patterns.json`: Normalized attributes per pattern (mediaType, dependentLLM, application, turn, template)
	- When enrichment is enabled, may also include: `usageSummary`, `aiAssisted`, `aiAssistedFields`, `aiAssistedModel`, `aiAssistedAt`
- `semantic-assignments.json`: Best semantic category assignments and scores used to compute matrix counts
- `similar-examples.json`: Example-level similarity edges with top-k matches and scores
- `similar-patterns.json`: Pattern-level similarity edges with top-k matches and scores
- `stats.json`: Summary counts and last processing timestamp

Notes:
- Deep-links are canonicalized to `/papers/{paperId}` anchors for both patterns and examples
- When example-level similar data is absent, the UI falls back to similar patterns and links to the first example of each similar pattern

### Optional AI Enrichment (GPT-5)

You can optionally enrich normalized pattern data using Azure OpenAI (GPT-5) to infer missing fields like Template (Role, Context, Action, Format, Response), Application tags, Dependent LLM (only when explicitly cited), Turn, and a concise 1–2 sentence Usage Summary explaining how to apply the pattern.

- What it does:
	- Updates `public/data/normalized-patterns.json`
	- Adds metadata: `aiAssisted`, `aiAssistedFields`, `aiAssistedModel`, `aiAssistedAt`
	- Pattern pages show an “AI-assisted” badge and a small disclaimer noting fields may be incorrect

- Scope to fields:

You can restrict enrichment to only certain fields using `--enrich-fields` with a comma-separated list. Allowed values: `template,application,dependentLLM,turn,usageSummary`.

- How to run (npm):

```bash
# Add -- after the script name to pass flags through npm
npm run build-data -- --enrich

# Limit enrichment to first 25 patterns
npm run build-data -- --enrich --enrich-limit 25

# Enrich only template and application fields
npm run build-data -- --enrich --enrich-fields template,application
```

- How to run (Node directly):

```bash
node scripts/build-data.js --enrich
node scripts/build-data.js --enrich --enrich-limit 25
node scripts/build-data.js --enrich --enrich-fields template,application,usageSummary
```

- Using uv for Python steps (Windows PowerShell):

The build auto-detects uv and prefers `uv run` for Python scripts (embeddings, categorization, enrichment). To force uv explicitly in PowerShell:

```powershell
$env:USE_UV = "1"
node .\scripts\build-data.js --enrich --enrich-fields template --enrich-limit 5
```

- GPT-5 temperature behavior:

Azure GPT-5 deployments accept only the default temperature. The enrichment pipeline does not set `temperature` explicitly for GPT-5 (and will retry without it if the service rejects the parameter), so you won’t see 400 errors about unsupported temperature values.

- Requirements:
	- Azure environment variables for endpoints/models must be set according to your `azure_models.py` registration
	- Authentication uses Azure Identity’s Interactive Browser Credential with secure token caching; you may be prompted to sign in via browser
	- No embeddings are regenerated by this step

## 📚 Documentation

- [Product Requirements Document](docs/PRD.md)
- [Folder Structure Guide](docs/FOLDER_STRUCTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🌐 Deployment

This project is configured for deployment to GitHub Pages:

```bash
npm run build
npm run export
```

The static files will be generated in the `out/` directory, ready for GitHub Pages hosting.

### Deep-Linking Behavior (Static Export)

When exporting statically, deep links of the form `/papers/{paperId}#p-{c}-{p}` and `/papers/{paperId}#e-{c}-{p}-{e}` continue to resolve correctly in the generated `out/` bundle. Category-page links always route to the canonical paper anchor to avoid dead links.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Research papers and authors whose work is cataloged in this dictionary
- The prompt engineering and cybersecurity communities
- Contributors to the open-source ecosystem

## 📞 Support

For questions or support, please open an issue in the GitHub repository.
