/**
 * Similarity Engine - Core embedding similarity calculations
 * 
 * Provides efficient cosine similarity calculations for embeddings with
 * caching and batch processing capabilities.
 */

export interface EmbeddingVector {
  id: string;
  embedding: number[];
  metadata?: Record<string, unknown>;
}

export interface SimilarityResult {
  id: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface SimilarityOptions {
  threshold?: number;
  topK?: number;
  includeMetadata?: boolean;
}

/**
 * Calculate cosine similarity between two embedding vectors
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error('Vectors must have the same length');
  }

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  normA = Math.sqrt(normA);
  normB = Math.sqrt(normB);

  if (normA === 0 || normB === 0) {
    return 0;
  }

  return dotProduct / (normA * normB);
}

/**
 * Find most similar embeddings to a query vector
 */
export function findSimilar(
  queryEmbedding: number[],
  embeddings: EmbeddingVector[],
  options: SimilarityOptions = {}
): SimilarityResult[] {
  const {
    threshold = 0.0,
    topK = 10,
    includeMetadata = true
  } = options;

  const similarities: SimilarityResult[] = embeddings
    .map(item => ({
      id: item.id,
      score: cosineSimilarity(queryEmbedding, item.embedding),
      metadata: includeMetadata ? item.metadata : undefined
    }))
    .filter(result => result.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  return similarities;
}

/**
 * Calculate similarity matrix between all embeddings
 */
export function calculateSimilarityMatrix(
  embeddings: EmbeddingVector[],
  options: SimilarityOptions = {}
): number[][] {
  const { threshold = 0.0 } = options;
  const matrix: number[][] = [];

  for (let i = 0; i < embeddings.length; i++) {
    matrix[i] = [];
    for (let j = 0; j < embeddings.length; j++) {
      if (i === j) {
        matrix[i][j] = 1.0; // Self-similarity
      } else {
        const similarity = cosineSimilarity(
          embeddings[i].embedding,
          embeddings[j].embedding
        );
        matrix[i][j] = similarity >= threshold ? similarity : 0;
      }
    }
  }

  return matrix;
}

/**
 * Batch similarity calculation with performance optimization
 */
export class SimilarityEngine {
  private embeddings: Map<string, EmbeddingVector> = new Map();
  private similarityCache: Map<string, SimilarityResult[]> = new Map();

  constructor(embeddings: EmbeddingVector[] = []) {
    this.loadEmbeddings(embeddings);
  }

  loadEmbeddings(embeddings: EmbeddingVector[]): void {
    this.embeddings.clear();
    this.similarityCache.clear();
    
    for (const embedding of embeddings) {
      this.embeddings.set(embedding.id, embedding);
    }
  }

  addEmbedding(embedding: EmbeddingVector): void {
    this.embeddings.set(embedding.id, embedding);
    // Clear cache when new embeddings are added
    this.similarityCache.clear();
  }

  removeEmbedding(id: string): boolean {
    const removed = this.embeddings.delete(id);
    if (removed) {
      this.similarityCache.clear();
    }
    return removed;
  }

  findSimilar(
    queryId: string,
    options: SimilarityOptions = {}
  ): SimilarityResult[] {
    const cacheKey = `${queryId}_${JSON.stringify(options)}`;
    
    if (this.similarityCache.has(cacheKey)) {
      return this.similarityCache.get(cacheKey)!;
    }

    const queryEmbedding = this.embeddings.get(queryId);
    if (!queryEmbedding) {
      throw new Error(`Embedding not found for ID: ${queryId}`);
    }

    const allEmbeddings = Array.from(this.embeddings.values())
      .filter(emb => emb.id !== queryId); // Exclude self

    const results = findSimilar(queryEmbedding.embedding, allEmbeddings, options);
    
    this.similarityCache.set(cacheKey, results);
    return results;
  }

  findSimilarByVector(
    queryEmbedding: number[],
    options: SimilarityOptions = {}
  ): SimilarityResult[] {
    const allEmbeddings = Array.from(this.embeddings.values());
    return findSimilar(queryEmbedding, allEmbeddings, options);
  }

  getEmbedding(id: string): EmbeddingVector | undefined {
    return this.embeddings.get(id);
  }

  getAllEmbeddings(): EmbeddingVector[] {
    return Array.from(this.embeddings.values());
  }

  getEmbeddingCount(): number {
    return this.embeddings.size;
  }

  clearCache(): void {
    this.similarityCache.clear();
  }
}
