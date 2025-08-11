/**
 * Similarity Matrix - Utilities for creating and managing similarity matrices
 * 
 * Provides functionality for generating, visualizing, and manipulating
 * similarity matrices with efficient storage and retrieval.
 */

import { EmbeddingVector, cosineSimilarity } from './similarity-engine';

export interface SimilarityMatrixEntry {
  i: number;
  j: number;
  similarity: number;
  idA: string;
  idB: string;
}

export interface SimilarityMatrixOptions {
  threshold?: number;
  sparse?: boolean;
  symmetric?: boolean;
}

export interface MatrixStatistics {
  totalPairs: number;
  nonZeroPairs: number;
  averageSimilarity: number;
  maxSimilarity: number;
  minSimilarity: number;
  sparsity: number;
}

/**
 * Sparse similarity matrix implementation for memory efficiency
 */
export class SimilarityMatrix {
  private embeddings: EmbeddingVector[];
  private matrix: Map<string, number> = new Map();
  private options: Required<SimilarityMatrixOptions>;

  constructor(
    embeddings: EmbeddingVector[],
    options: SimilarityMatrixOptions = {}
  ) {
    this.embeddings = [...embeddings];
    this.options = {
      threshold: options.threshold ?? 0.1,
      sparse: options.sparse ?? true,
      symmetric: options.symmetric ?? true
    };

    this.buildMatrix();
  }

  private buildMatrix(): void {
    this.matrix.clear();
    const n = this.embeddings.length;

    for (let i = 0; i < n; i++) {
      const endJ = this.options.symmetric ? i + 1 : n;
      
      for (let j = this.options.symmetric ? 0 : 0; j < endJ; j++) {
        if (i === j) {
          this.setEntry(i, j, 1.0); // Self-similarity
          continue;
        }

        const similarity = cosineSimilarity(
          this.embeddings[i].embedding,
          this.embeddings[j].embedding
        );

        if (!this.options.sparse || similarity >= this.options.threshold) {
          this.setEntry(i, j, similarity);
          
          if (this.options.symmetric && i !== j) {
            this.setEntry(j, i, similarity);
          }
        }
      }
    }
  }

  private getKey(i: number, j: number): string {
    return `${i},${j}`;
  }

  private setEntry(i: number, j: number, value: number): void {
    this.matrix.set(this.getKey(i, j), value);
  }

  /**
   * Get similarity between two embeddings by index
   */
  getSimilarity(i: number, j: number): number {
    return this.matrix.get(this.getKey(i, j)) ?? 0;
  }

  /**
   * Get similarity between two embeddings by ID
   */
  getSimilarityById(idA: string, idB: string): number {
    const indexA = this.embeddings.findIndex(emb => emb.id === idA);
    const indexB = this.embeddings.findIndex(emb => emb.id === idB);
    
    if (indexA === -1 || indexB === -1) {
      return 0;
    }

    return this.getSimilarity(indexA, indexB);
  }

  /**
   * Get all similarities for a specific embedding
   */
  getRow(index: number): SimilarityMatrixEntry[] {
    const entries: SimilarityMatrixEntry[] = [];
    
    for (let j = 0; j < this.embeddings.length; j++) {
      const similarity = this.getSimilarity(index, j);
      if (similarity > 0 || !this.options.sparse) {
        entries.push({
          i: index,
          j,
          similarity,
          idA: this.embeddings[index].id,
          idB: this.embeddings[j].id
        });
      }
    }

    return entries.sort((a, b) => b.similarity - a.similarity);
  }

  /**
   * Get all similarities for a specific embedding by ID
   */
  getRowById(id: string): SimilarityMatrixEntry[] {
    const index = this.embeddings.findIndex(emb => emb.id === id);
    if (index === -1) {
      return [];
    }
    return this.getRow(index);
  }

  /**
   * Get top K most similar pairs
   */
  getTopPairs(k: number = 10): SimilarityMatrixEntry[] {
    const pairs: SimilarityMatrixEntry[] = [];
    
    for (const [key, similarity] of this.matrix.entries()) {
      const [i, j] = key.split(',').map(Number);
      
      // Skip self-similarities and duplicates if symmetric
      if (i === j) continue;
      if (this.options.symmetric && i > j) continue;
      
      pairs.push({
        i,
        j,
        similarity,
        idA: this.embeddings[i].id,
        idB: this.embeddings[j].id
      });
    }

    return pairs
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, k);
  }

  /**
   * Get matrix statistics
   */
  getStatistics(): MatrixStatistics {
    const n = this.embeddings.length;
    const totalPairs = this.options.symmetric ? (n * (n - 1)) / 2 : n * n - n;
    const nonZeroPairs = this.matrix.size - n; // Exclude self-similarities
    
    const similarities = Array.from(this.matrix.values())
      .filter(sim => sim < 1.0); // Exclude self-similarities
    
    const sum = similarities.reduce((acc, sim) => acc + sim, 0);
    const averageSimilarity = similarities.length > 0 ? sum / similarities.length : 0;
    const maxSimilarity = similarities.length > 0 ? Math.max(...similarities) : 0;
    const minSimilarity = similarities.length > 0 ? Math.min(...similarities) : 0;
    const sparsity = 1 - (nonZeroPairs / totalPairs);

    return {
      totalPairs,
      nonZeroPairs,
      averageSimilarity,
      maxSimilarity,
      minSimilarity,
      sparsity
    };
  }

  /**
   * Export matrix as dense 2D array
   */
  toDenseMatrix(): number[][] {
    const n = this.embeddings.length;
    const matrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        matrix[i][j] = this.getSimilarity(i, j);
      }
    }

    return matrix;
  }

  /**
   * Export matrix as sparse format for JSON serialization
   */
  toSparseFormat(): {
    embeddings: string[];
    entries: SimilarityMatrixEntry[];
    statistics: MatrixStatistics;
  } {
    const entries: SimilarityMatrixEntry[] = [];
    
    for (const [key, similarity] of this.matrix.entries()) {
      const [i, j] = key.split(',').map(Number);
      entries.push({
        i,
        j,
        similarity,
        idA: this.embeddings[i].id,
        idB: this.embeddings[j].id
      });
    }

    return {
      embeddings: this.embeddings.map(emb => emb.id),
      entries,
      statistics: this.getStatistics()
    };
  }

  /**
   * Get embedding metadata
   */
  getEmbeddingInfo(index: number): EmbeddingVector | undefined {
    return this.embeddings[index];
  }

  /**
   * Get total number of embeddings
   */
  size(): number {
    return this.embeddings.length;
  }

  /**
   * Update threshold and rebuild sparse matrix
   */
  updateThreshold(threshold: number): void {
    this.options.threshold = threshold;
    this.buildMatrix();
  }
}
