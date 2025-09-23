/**
 * Enhanced TypeScript interfaces for patterns with dual categorization
 */

export interface SemanticCategorization {
  category: string;
  confidence: number;
  top_alternatives: Array<{
    category: string;
    similarity: number;
  }>;
}

export interface EnhancedExample {
  id: string;
  content: string;
  index: number;
  semantic_categorization?: SemanticCategorization;
}

export interface EnhancedPattern {
  id: string;
  patternName: string;
  description: string;
  examples: EnhancedExample[];
  category: string; // Original paper category
  original_paper_category?: string; // Preserved original category
  semantic_categorization?: SemanticCategorization; // New semantic category
  paper: {
    apaReference: string;
    title?: string;
    authors?: string[];
    url?: string;
  };
  tags: string[];
  searchableContent: string;
}

export interface CategoryFilter {
  type: 'original' | 'semantic' | 'example';
  category: string;
}

export interface SearchFilters {
  query: string;
  categoryFilters: CategoryFilter[];
  confidenceThreshold: number;
  showMismatchesOnly: boolean;
}

export interface CategoryDistribution {
  original: Record<string, number>;
  semantic: Record<string, number>;
  examples: Record<string, number>;
}

export interface PatternStatistics {
  totalPatterns: number;
  categorizedPatterns: number;
  categoryChanges: number;
  exampleMismatches: number;
  averageConfidence: number;
}

// Normalized Prompt Pattern schema (docs/PRD.md)
export interface NormalizedPromptPattern {
  id: string;
  category: string;
  name: string;
  mediaType: 'text' | 'image' | 'audio' | 'video' | 'multimodal';
  description?: string;
  template?: {
    role?: string;
    context?: string;
    action?: string;
    format?: string;
    response?: string;
  };
  // In data, application can be a single narrative string (preferred) or legacy array of tags
  application?: string | string[];
  // New: concise actionable tasks (comma+space separated), optional
  applicationTasksString?: string;
  dependentLLM?: string | null;
  turn?: 'single' | 'multi';
  promptExamples: string[];
  related?: Array<{ category: string; similarity: number }>;
  reference: {
    title: string;
    authors: string[];
    url: string;
    apa?: string;
  };
}
