# Product Requirements Document: Prompt Pattern Dictionary & Search Interface

## Executive Summary

We are developing a comprehensive, dictionary-style search interface for prompt patterns and examples extracted from cybersecurity and prompt engineering research papers. This will be a GitHub-hosted web application that provides an intuitive, searchable database of prompt patterns similar to the Oxford English Dictionary (OED) experience, but focused on prompt engineering patterns for cybersecurity applications.

## Product Vision

Create the definitive reference tool for cybersecurity prompt engineering patterns - a searchable, discoverable, and educational resource that serves as both a learning platform and practical reference guide for prompt engineers, researchers, and cybersecurity professionals.

## Background & Context

- **Data Source**: `promptpatterns.json` - A curated database of prompt patterns extracted from 72+ research papers
- **Current Structure**: Hierarchical JSON with Papers → Categories → Patterns → Examples
- **Index System**: Each prompt has a unique index (e.g., "1-0-2-0" for Paper 1, Category 0, Pattern 2, Example 0)
- **Target Repository**: https://github.com/timhaintz/PromptEngineering4Cybersecurity (currently private)

## Target Users

### Primary Users
- **Prompt Engineers**: Professionals designing and optimizing prompts for LLMs
- **Cybersecurity Researchers**: Academic and industry researchers working with AI/ML in security
- **Security Practitioners**: SOC analysts, penetration testers, security engineers using AI tools

### Secondary Users
- **Students**: Learning prompt engineering and cybersecurity concepts
- **Developers**: Building AI-powered security tools
- **Compliance Teams**: Understanding AI safety and security patterns

## Core Features & Requirements

### 1. Search & Discovery

#### 1.1 Advanced Search Functionality
- **Free-text search** across pattern names, descriptions, and example prompts
- **Category filtering** (Input Semantics, Output Customization, Jailbreaking, etc.)
- **Paper source filtering** by author, publication date, or research paper
- **Fuzzy search** for partial matches and typos
- **Search suggestions** and auto-complete
- **Boolean search** operators (AND, OR, NOT)

#### 1.2 Browse & Navigation
- **Category-based browsing** with expandable tree structure
- **Research paper index** with paper details and all associated patterns
- **Tag-based navigation** for related patterns
- **"Related Patterns"** suggestions based on content similarity
- **Recently viewed** patterns history

### 2. Dictionary-Style Interface

#### 2.1 Pattern Entry Display
- **Pattern name** as primary heading
- **Pronunciation guide** for complex terms (if applicable)
- **Definition/Description** with clear, concise explanation
- **Category classification** and subcategories
- **Etymology** (source paper, authors, publication date)
- **Usage examples** with syntax highlighting
- **Cross-references** to related patterns
- **Security implications** and warnings where relevant

#### 2.2 Example Management
- **Multiple examples** per pattern with individual indexing
- **Code/prompt formatting** with syntax highlighting
- **Copy-to-clipboard** functionality
- **Example variations** and modifications
- **Context explanations** for complex examples

### 3. Content Organization

#### 3.1 Hierarchical Structure
```
Research Paper
├── Paper Metadata (Title, Authors, APA Reference, URL, Date Added)
├── Categories
│   ├── Category Name
│   ├── Pattern Collection
│   │   ├── Pattern Name
│   │   ├── Pattern Description
│   │   └── Example Prompts
│   │       ├── Example 1
│   │       ├── Example 2
│   │       └── Example N
```

#### 3.2 Indexing System
- **Maintain existing index format**: `{paperId}-{categoryIndex}-{patternIndex}-{exampleIndex}`
- **Permalink structure**: `/pattern/{index}` or `/pattern/{paper}/{category}/{pattern}`
- **Canonical URLs** for each pattern and example

### 4. User Experience Features

#### 4.1 Reading Experience
- **Responsive design** optimized for desktop and mobile
- **Dark/Light mode** toggle
- **Font size adjustment** for accessibility
- **Print-friendly** views
- **Bookmark functionality** for favorite patterns
- **Reading progress** tracking

##### 4.1.1 Accessibility & Readability Expansion (Added)

Adopt a site-wide accessibility program (WCAG 2.2 AA + selected AAA) with these commitments:

- System font stack for performance: `system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`.
- Three distinct display modes: Light, Dark, High-Contrast (HC ≥7:1 text contrast) with user toggle & persistence.
- Readability controls: font size scaling (S/M/L), width mode (narrow/prose), theme selection; respect `prefers-color-scheme` & `prefers-reduced-motion`.
- Prose line length constrained to ~70–75ch for orientation & docs content.
- Unified focus outline (2px) and multiple skip links (Main, Section Nav, Search).
- Accessible disclosures for collapsibles (`<button aria-expanded>` + `aria-controls`).
- Live regions for copy success, search result count, preference change announcements.
- AI provenance badges link to explanation; footer carries disclaimer.
- CI axe-core scan on core pages; build fails on critical/serious violations.
- `docs/ACCESSIBILITY.md` tracks WCAG mapping, exceptions, audit logs.
- Hybrid Orientation: multi-page `/orientation/{slug}` + all-in-one; legacy hash anchors redirected.

Acceptance (Phase 1): Lighthouse Accessibility ≥95 (home/search/pattern) and zero critical/serious axe issues.

##### 4.1.2 Global Footer (Added)

Add OED-style footer with grouped links (About, Using the Dictionary, Accessibility & Responsible Use, Data & Provenance, Contribute, License & Legal), build/version metadata, and AI-assisted disclaimer. Mobile: collapsible groups.

#### 4.2 Interactive Elements
- **Interactive examples** where users can modify prompts
- **Copy examples** with attribution
- **Share functionality** (direct links, social media)
- **Comment system** for community feedback (future consideration)
- **Rating system** for pattern usefulness

### 5. Technical Architecture

#### 5.1 Frontend
- **Framework**: React.js or Vue.js for interactive components
- **Static Site Generator**: Next.js, Gatsby, or VitePress for optimal performance
- **Styling**: Tailwind CSS or styled-components for responsive design
- **Search**: Client-side search with Lunr.js or Flexsearch
- **Hosting**: GitHub Pages with custom domain
 - **Design Tokens (Added)**: Central token layer for typography, spacing, color roles, focus ring, radii; exposed via Tailwind config & CSS vars.
 - **Theme Infra (Added)**: `<html data-theme>` attribute switching (light|dark|hc); low-cost JS bundle (<5KB gzipped) for persistence only.

#### 5.2 Data Management
- **Source Data**: `promptpatterns.json` as single source of truth
- **Build Process**: Automated generation of search indexes and static pages
- **Content Validation**: Schema validation for data integrity
- **Version Control**: Git-based content management

#### 5.3 Performance Requirements
- **Page Load Time**: < 3 seconds for initial load
- **Search Response**: < 500ms for search results
- **Mobile Performance**: Lighthouse score > 90
- **Offline Capability**: Service worker for cached content

## Detailed User Stories

### As a Prompt Engineer
- I want to search for "jailbreaking" patterns so I can understand security vulnerabilities
- I want to browse patterns by category so I can discover new techniques
- I want to copy example prompts so I can modify them for my use case
- I want to see related patterns so I can explore variations

### As a Cybersecurity Researcher
- I want to filter patterns by research paper so I can cite sources correctly
- I want to see the full academic context so I can understand the research background
- I want to export citations so I can include them in my papers
- I want to track pattern evolution across different papers

### As a Security Practitioner
- I want to quickly find defensive patterns so I can protect my systems
- I want to understand attack patterns so I can build better defenses
- I want practical examples so I can implement solutions immediately
- I want security warnings so I can use patterns safely

## Success Metrics

### Usage Metrics
- **Monthly Active Users**: Target 1,000+ within 6 months
- **Search Queries**: Track most common searches
- **Page Views**: Monitor most accessed patterns
- **Session Duration**: Average 5+ minutes indicating deep engagement

### Quality Metrics
- **Search Success Rate**: >85% of searches yield relevant results
- **User Satisfaction**: Survey-based feedback >4/5 stars
- **Content Coverage**: Index 100% of available patterns
- **Update Frequency**: New content added monthly

### Technical Metrics
- **Site Performance**: Lighthouse scores >90 across all categories
- **Uptime**: 99.9% availability
- **Mobile Usage**: 40%+ of traffic from mobile devices
- **Search Performance**: Sub-500ms response times

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up repository structure and development environment
- [ ] Design information architecture and URL structure
- [ ] Create basic page templates and navigation
- [ ] Implement core search functionality
- [ ] Build pattern display components

### Phase 2: Content & Search (Weeks 5-8)
- [ ] Process `promptpatterns.json` into searchable format
- [ ] Implement advanced search filters and categories
- [ ] Create individual pattern pages with full details
- [ ] Add cross-references and related pattern suggestions
- [ ] Implement responsive design and mobile optimization

### Phase 3: Enhancement (Weeks 9-12)
- [ ] Add interactive features (copy, share, bookmark)
- [ ] Implement accessibility features
- [ ] Add analytics and user tracking
- [ ] Optimize performance and SEO
- [ ] User testing and feedback implementation

### Phase 4: Launch & Iteration (Weeks 13-16)
- [ ] Beta testing with select users
- [ ] Bug fixes and performance optimization
- [ ] Documentation and help content
- [ ] Public launch and marketing
- [ ] Community feedback integration

## Technical Specifications

### Data Schema
```typescript
interface PromptPattern {
  id: string; // e.g., "1-0-2-0"
  patternName: string;
  category: string;
  description?: string;
  examples: string[];
  sourceTitle: string;
  authors: string[];
  url: string;
  dateAdded: string;
  tags: string[];
  securityLevel?: 'safe' | 'warning' | 'dangerous';
}
```

## Normalized Prompt Pattern Display (Detail Page)

Each Prompt Pattern page renders the following fields in order when available:

1. ID
2. Category
3. Name
4. Media Type (one of: "Text Only", "Text2Audio", "Text2Image", "Text2Video", "Audio2Text", "Image2Text", "Video2Text")
5. Description
6. Template
  - Role
  - Context
  - Action
  - Format
  - Response
7. Application (tags/labels)
8. Dependent LLM (or N/A)
9. Turn (Single/Multi)
10. Prompt Examples (with stable anchors: #example-{paperId}-{categoryIndex}-{patternIndex}-{exampleIndex})
11. Related PPs (IDs as links)
12. Reference (Title, Authors, URL; APA if available)

Data sourcing: The build process writes `public/data/normalized-patterns.json` via `scripts/transform-normalized-pp.js`, integrating heuristics for Media Type, Template decomposition, and Turn inference, and using `similar-patterns.json` for Related PPs. Embeddings are not regenerated for this step.

### Optional AI Enrichment
- The build supports an optional AI enrichment step using GPT-5 to infer missing fields (Template, Application, Dependent LLM, Turn).
- Invoke with `--enrich` (and optionally `--enrich-limit <n>`). Enriched patterns include:
  - `aiAssisted: true`
  - `aiAssistedFields: [...]`
  - `aiAssistedModel`
  - `aiAssistedAt`
- The Pattern Detail page shows an “AI-assisted” badge and a disclaimer that AI-inferred fields may be incorrect.
 - Example:
   - `node prompt-pattern-dictionary/scripts/build-data.js --enrich`
   - `npm run build-data --prefix prompt-pattern-dictionary -- --enrich --enrich-limit 50`

### URL Structure
- Homepage: `/`
- Search: `/search?q={query}&category={category}`
- Pattern: `/pattern/{paperId}/{categoryIndex}/{patternIndex}`
- Example: `/pattern/{paperId}/{categoryIndex}/{patternIndex}/example/{exampleIndex}`
- Category: `/category/{categoryName}`
- Paper: `/paper/{paperId}`

### Search Index Structure
```javascript
{
  patterns: [
    {
      id: "1-0-2-0",
      title: "Change Request Simulation",
      content: "My software system architecture is X...",
      category: "Requirements Elicitation",
      paper: "ChatGPT Prompt Patterns for Improving Code Quality...",
      authors: ["Jules White", "Sam Hays"],
      tags: ["simulation", "requirements", "software-design"]
    }
  ]
}
```

## Risk Assessment & Mitigation

### Technical Risks
- **Risk**: Large JSON file performance issues
- **Mitigation**: Implement lazy loading and chunked data processing

- **Risk**: Search performance degradation with growth
- **Mitigation**: Consider server-side search for large datasets

### Content Risks
- **Risk**: Copyright issues with research paper content
- **Mitigation**: Ensure fair use compliance, provide proper attribution

- **Risk**: Dangerous prompt patterns misuse
- **Mitigation**: Add warnings, implement content moderation guidelines

### User Experience Risks
- **Risk**: Complex academic content overwhelming users
- **Mitigation**: Add beginner-friendly explanations and tutorials

## Future Enhancements

### Version 2.0 Features
- User accounts and personal collections
- Community contributions and pattern submissions
- API for programmatic access
- Machine learning for pattern recommendation
- Integration with popular prompt engineering tools

### Long-term Vision
- Multi-language support
- Video tutorials and interactive learning
- Real-time collaboration features
- Integration with LLM providers for testing
- Academic partnership program

## Conclusion

This prompt pattern dictionary will serve as the definitive reference for cybersecurity prompt engineering, combining academic rigor with practical usability. By creating an OED-style interface with modern search capabilities, we'll provide immense value to the prompt engineering and cybersecurity communities while establishing a foundation for future research and collaboration.

The phased approach ensures we can deliver value quickly while iterating based on user feedback. The focus on performance, accessibility, and user experience will make this tool indispensable for professionals working at the intersection of AI and cybersecurity.
