/**
 * TypeScript definitions for the Prompt Pattern Dictionary
 * Based on the structure of promptpatterns.json
 */

// Main data structure from promptpatterns.json
export interface PromptPatternsData {
  Papers: Paper[];
}

export interface Paper {
  paperId: string;
  title: string;
  authors: string[];
  year?: number;
  url?: string;
  apaReference?: string;
  dateAdded: string;
  categories: Category[];
}

export interface Category {
  categoryName: string;
  patterns: Pattern[];
}

export interface Pattern {
  patternName: string;
  description?: string;
  examples: string[];
}

// Processed data structures for the application
export interface ProcessedPattern {
  id: string; // Format: "paperId-categoryIndex-patternIndex"
  patternName: string;
  description?: string;
  examples: ProcessedExample[];
  category: string;
  paper: {
    id: string;
    title: string;
    authors: string[];
    year?: number;
    url?: string;
    apaReference?: string;
  };
  tags: string[];
  searchableContent: string; // Combined text for search indexing
  // New embedding-related fields
  embedding?: number[];
  similarityScores?: {
    [categorySlug: string]: number;
  };
  primaryCategory?: string;
  secondaryCategories?: string[];
  confidenceScore?: number;
  autoAssigned?: boolean;
}

export interface ProcessedExample {
  id: string; // Format: "paperId-categoryIndex-patternIndex-exampleIndex"
  content: string;
  index: number;
}

export interface PatternCategory {
  name: string;
  slug: string;
  description?: string;
  patternCount: number;
  patterns: ProcessedPattern[];
}

export interface SearchResult {
  pattern: ProcessedPattern;
  score: number;
  matchedFields: string[];
  snippet?: string;
}

export interface SearchFilters {
  categories?: string[];
  papers?: string[];
  authors?: string[];
  tags?: string[];
  hasExamples?: boolean;
}

export interface SearchQuery {
  text: string;
  filters: SearchFilters;
  sortBy: 'relevance' | 'alphabetical' | 'date';
  limit?: number;
  offset?: number;
}

// Navigation and UI types
export interface BreadcrumbItem {
  label: string;
  href: string;
}

export interface RelatedPattern {
  id: string;
  patternName: string;
  category: string;
  similarity: number;
}

// API response types
export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: SearchQuery;
  facets: {
    categories: { name: string; count: number }[];
    papers: { name: string; count: number }[];
    authors: { name: string; count: number }[];
  };
}

export interface PatternDetailResponse {
  pattern: ProcessedPattern;
  related: RelatedPattern[];
  breadcrumbs: BreadcrumbItem[];
}

// Utility types
export type PatternIndex = `${string}-${number}-${number}`;
export type ExampleIndex = `${string}-${number}-${number}-${number}`;

export interface DataProcessingStats {
  totalPapers: number;
  totalCategories: number;
  totalPatterns: number;
  totalExamples: number;
  lastProcessed: string;
}

// Security and content moderation
export enum SecurityLevel {
  SAFE = 'safe',
  WARNING = 'warning', 
  DANGEROUS = 'dangerous'
}

export interface ContentWarning {
  level: SecurityLevel;
  message: string;
  reason: string;
}

// Embedding and Similarity Types (from PRD)
export interface CategoryEmbedding {
  categorySlug: string;
  categoryName: string;
  definitionEmbedding: number[];
  exampleEmbeddings: number[];
  averageEmbedding: number[];
  patternCount: number;
  averageConfidence: number;
}

export interface SimilarityMatrix {
  patternId: string;
  similarities: {
    [categorySlug: string]: {
      score: number;
      rank: number;
      confidence: 'high' | 'medium' | 'low';
    };
  };
  primaryAssignment: {
    category: string;
    score: number;
    confidence: string;
  };
  tags: string[];
}

// Pattern Comparison Feature Interfaces
export interface PatternComparison {
  comparisonId: string;
  timestamp: string;
  patterns: string[]; // Array of pattern IDs
  userPrompt?: string; // Optional user-provided prompt
  similarityMatrix: number[][]; // NxN matrix of similarities
  statistics: {
    averageSimilarity: number;
    maxSimilarity: number;
    minSimilarity: number;
    clusters: ClusterGroup[];
  };
  visualization: {
    heatmapData: HeatmapCell[];
    scatterPlotData: ScatterPoint[];
    networkData: NetworkNode[];
  };
}

export interface ClusterGroup {
  id: string;
  patternIds: string[];
  centroid: number[];
  averageIntraClusterSimilarity: number;
  mostRepresentativePattern: string;
}

export interface HeatmapCell {
  x: number;
  y: number;
  similarity: number;
  patternIds: [string, string];
  color: string;
}

export interface ScatterPoint {
  x: number;
  y: number;
  patternId: string;
  label: string;
  category: string;
  similarity?: number; // Similarity to user prompt if applicable
}

export interface NetworkNode {
  id: string;
  label: string;
  category: string;
  x?: number; // Position for visualization
  y?: number; // Position for visualization
  connections: {
    targetId: string;
    similarity: number;
    weight: number;
  }[];
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface SimilaritySearchResult {
  patternId: string;
  patternName: string;
  similarity: number;
  category: string;
  excerpt: string;
  confidence: 'high' | 'medium' | 'low';
  sourceTitle: string;
  authors: string[];
}

// Embedding Storage Schema (Paper-based chunking)
export interface EmbeddingStorage {
  metadata: {
    model: string;
    dimensions: number;
    generatedAt: string;
    totalPatterns: number;
    totalExamples: number;
    papers: string[]; // List of paper IDs in this chunk
  };
  patterns: {
    [patternId: string]: {
      embedding: number[];
      hash: string;
      lastUpdated: string;
      paperId: string; // First number in index (e.g., "1703", "2102")
    };
  };
  examples: {
    [exampleId: string]: {
      embedding: number[];
      hash: string;
      lastUpdated: string;
      patternId: string;
      paperId: string; // Same as parent pattern
    };
  };
}

export interface EmbeddingIndex {
  metadata: {
    generatedAt: string;
    totalPapers: number;
    embeddingModel: string;
    totalApiCalls: number;
    totalTokensUsed: number;
  };
  papers: {
    [paperId: string]: {
      file: string;
      patternCount: number;
      exampleCount: number;
      lastUpdated: string;
    };
  };
  patternToPaper: {
    [patternId: string]: string;
  };
  exampleToPaper: {
    [exampleId: string]: string;
  };
}
