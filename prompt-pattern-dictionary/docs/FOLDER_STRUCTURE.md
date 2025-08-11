# Prompt Pattern Dictionary - Project Structure

This document outlines the recommended folder structure for the Prompt Pattern Dictionary project, a GitHub-hosted Next.js application.

## Root Structure

```
prompt-pattern-dictionary/                    # Main project folder
├── README.md                                # Project overview and setup instructions
├── package.json                             # Node.js dependencies and scripts
├── package-lock.json                        # Locked dependency versions
├── next.config.js                           # Next.js configuration
├── tailwind.config.js                       # Tailwind CSS configuration
├── tsconfig.json                            # TypeScript configuration
├── .gitignore                               # Git ignore rules
├── .env.local                               # Environment variables (local)
├── .env.example                             # Environment variables template
├── .github/                                 # GitHub workflows and configurations
│   ├── workflows/                           # CI/CD workflows
│   │   ├── deploy.yml                       # Deployment to GitHub Pages
│   │   ├── test.yml                         # Automated testing
│   │   └── build.yml                        # Build verification
│   └── ISSUE_TEMPLATE/                      # Issue templates
│       ├── bug_report.md
│       └── feature_request.md
├── docs/                                    # Project documentation
│   ├── PRD.md                              # Product Requirements Document
│   ├── API.md                              # API documentation
│   ├── DEPLOYMENT.md                       # Deployment guide
│   ├── CONTRIBUTING.md                     # Contribution guidelines
│   └── ARCHITECTURE.md                     # Technical architecture
├── src/                                     # Source code
│   ├── app/                                # Next.js App Router
│   │   ├── layout.tsx                      # Root layout
│   │   ├── page.tsx                        # Homepage
│   │   ├── globals.css                     # Global styles
│   │   ├── search/                         # Search functionality
│   │   │   └── page.tsx                    # Search results page
│   │   ├── pattern/                        # Pattern pages
│   │   │   └── [...slug]/                  # Dynamic pattern routes
│   │   │       └── page.tsx               # Individual pattern page
│   │   ├── category/                       # Category pages
│   │   │   └── [category]/                 # Dynamic category routes
│   │   │       └── page.tsx               # Category listing page
│   │   ├── paper/                          # Research paper pages
│   │   │   └── [paperId]/                  # Dynamic paper routes
│   │   │       └── page.tsx               # Paper details page
│   │   └── api/                            # API routes (if needed)
│   │       └── search/
│   │           └── route.ts               # Search API endpoint
│   ├── components/                         # Reusable React components
│   │   ├── ui/                            # Basic UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Modal.tsx
│   │   ├── search/                        # Search-related components
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   └── SearchSuggestions.tsx
│   │   ├── pattern/                       # Pattern-related components
│   │   │   ├── PatternCard.tsx
│   │   │   ├── PatternDetail.tsx
│   │   │   ├── PatternExample.tsx
│   │   │   └── RelatedPatterns.tsx
│   │   ├── navigation/                    # Navigation components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Breadcrumbs.tsx
│   │   └── layout/                        # Layout components
│   │       ├── PageLayout.tsx
│   │       ├── ContentWrapper.tsx
│   │       └── ThemeProvider.tsx
│   ├── lib/                               # Utility libraries and functions
│   │   ├── data/                          # Data processing utilities
│   │   │   ├── processPatterns.ts         # Process promptpatterns.json
│   │   │   ├── searchIndex.ts             # Search index generation
│   │   │   └── dataValidation.ts          # Data validation schemas
│   │   ├── search/                        # Search functionality
│   │   │   ├── searchEngine.ts            # Main search logic
│   │   │   ├── filters.ts                 # Search filters
│   │   │   └── indexBuilder.ts            # Search index builder
│   │   ├── utils/                         # General utilities
│   │   │   ├── formatting.ts              # Text formatting utilities
│   │   │   ├── urlHelpers.ts              # URL generation helpers
│   │   │   ├── constants.ts               # Application constants
│   │   │   └── helpers.ts                 # General helper functions
│   │   └── types/                         # TypeScript type definitions
│   │       ├── pattern.ts                 # Pattern data types
│   │       ├── search.ts                  # Search-related types
│   │       └── api.ts                     # API response types
│   ├── styles/                            # Additional stylesheets
│   │   ├── components.css                 # Component-specific styles
│   │   └── utilities.css                  # Utility classes
│   └── hooks/                             # Custom React hooks
│       ├── useSearch.ts                   # Search functionality hook
│       ├── useLocalStorage.ts             # Local storage hook
│       └── useTheme.ts                    # Theme management hook
├── public/                                # Static assets
│   ├── favicon.ico                        # Site favicon
│   ├── manifest.json                      # PWA manifest
│   ├── robots.txt                         # Search engine instructions
│   ├── sitemap.xml                        # Site map for SEO
│   ├── images/                            # Image assets
│   │   ├── logo.svg                       # Site logo
│   │   └── icons/                         # Icon files
│   └── data/                              # Processed data files
│       ├── patterns.json                  # Processed pattern data
│       ├── search-index.json              # Pre-built search index
│       └── pattern-categories.json        # Category metadata
├── scripts/                               # Build and utility scripts
│   ├── build-data.js                      # Enhanced data processing script
│   ├── generate-pattern-categories.py     # Hierarchical categories (existing)
│   ├── generate-embeddings-similarity.py  # NEW: Embedding & similarity processing
│   ├── generate-sitemap.js                # Sitemap generation
│   ├── validate-data.js                   # Data validation script
│   └── deploy.sh                          # Deployment script
├── tests/                                 # Test files
│   ├── __mocks__/                         # Mock files for testing
│   ├── components/                        # Component tests
│   │   ├── SearchBar.test.tsx
│   │   └── PatternCard.test.tsx
│   ├── lib/                               # Library function tests
│   │   ├── searchEngine.test.ts
│   │   └── dataProcessing.test.ts
│   ├── pages/                             # Page tests
│   │   └── search.test.tsx
│   ├── setup.ts                           # Test setup configuration
│   └── utils.ts                           # Test utilities
└── dist/                                  # Build output (generated)
    ├── _next/                             # Next.js build files
    ├── static/                            # Static assets
    └── index.html                         # Generated HTML files
```

## Key Directory Explanations

### `/src/app/` - Next.js App Router
- Uses the new App Router for better performance and developer experience
- File-based routing with dynamic segments for patterns, categories, and papers
- Supports layouts, loading states, and error boundaries

### `/src/components/` - Component Architecture
- **ui/**: Basic, reusable UI components following atomic design principles
- **search/**: Search-specific components with complex state management
- **pattern/**: Pattern display and interaction components
- **navigation/**: Site navigation and wayfinding components
- **layout/**: Page structure and theming components

### `/src/lib/` - Business Logic
- **data/**: Data processing and validation for the source JSON
- **search/**: Search engine implementation and indexing
- **utils/**: Shared utilities and helper functions
- **types/**: TypeScript definitions for type safety

### `/public/data/` - Processed Data
- Contains processed versions of the source `promptpatterns.json`
- Pre-built search indexes for fast client-side search
- Generated during build process for optimal performance

### `/scripts/` - Build Automation
- Data processing scripts to transform source JSON
- Build-time optimizations and validations
- Deployment automation for GitHub Pages

## Development Workflow

### Initial Setup
1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm run build-data` to process the source JSON file
4. Run `npm run dev` to start the development server

### Build Process
1. **Data Processing**: Transform `../promptpatterns.json` into optimized formats
2. **Search Index**: Generate client-side search indexes
3. **Static Generation**: Pre-render all pattern and category pages
4. **Optimization**: Minimize and optimize assets for production

### Deployment
- Automated deployment to GitHub Pages via GitHub Actions
- Static site generation for optimal performance
- Custom domain support with proper DNS configuration

## Technology Stack

- **Framework**: Next.js 13+ with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for responsive design
- **Search**: Lunr.js or Flexsearch for client-side search + semantic search
- **Embeddings**: Azure OpenAI text-embedding-3-large (3072 dimensions)
- **Vector Storage**: JSON flat files with cosine similarity
- **Testing**: Jest and React Testing Library
- **Build**: Node.js + Python scripts for data processing
- **Hosting**: GitHub Pages with GitHub Actions

## Benefits of This Structure

1. **Scalability**: Clear separation of concerns allows for easy expansion
2. **Performance**: Static generation and client-side search for speed
3. **Maintainability**: Well-organized code with clear responsibilities
4. **SEO**: Static pages with proper metadata for search engines
5. **Developer Experience**: Modern tooling with hot reload and TypeScript
6. **Production Ready**: Automated testing, building, and deployment

This structure provides a solid foundation for building a professional, performant, and maintainable prompt pattern dictionary that can serve the cybersecurity and prompt engineering communities effectively.
