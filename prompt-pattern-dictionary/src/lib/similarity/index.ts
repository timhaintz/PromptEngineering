/**
 * Cosine Similarity and Pattern Comparison Utilities
 * 
 * Provides client-side similarity calculations for the Ballarat AI Prompt Dictionary.
 * Implements real-time pattern comparison using pre-computed embeddings.
 * 
 * Features:
 * - Cosine similarity calculations
 * - Pattern comparison matrices
 * - Clustering and statistical analysis
 * - Efficient embedding loading and caching
 */

// Export new modular similarity components
export * from './similarity-engine';
export * from './similarity-matrix';
export * from './similarity-network';

import type { 
  EmbeddingStorage, 
  EmbeddingIndex, 
  PatternComparison, 
  ClusterGroup,
  HeatmapCell,
  ScatterPoint,
  NetworkNode,
  SimilaritySearchResult
} from '../types/pattern';

/**
 * Calculate cosine similarity between two embedding vectors
 */
export function cosineSimilarity(vectorA: number[], vectorB: number[]): number {
  if (vectorA.length !== vectorB.length) {
    throw new Error('Vectors must have the same length');
  }

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < vectorA.length; i++) {
    dotProduct += vectorA[i] * vectorB[i];
    normA += vectorA[i] * vectorA[i];
    normB += vectorB[i] * vectorB[i];
  }

  const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
  
  if (magnitude === 0) {
    return 0;
  }

  return dotProduct / magnitude;
}

/**
 * Calculate similarity matrix between multiple patterns
 */
export function calculateSimilarityMatrix(embeddings: number[][]): number[][] {
  const n = embeddings.length;
  const matrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) {
        matrix[i][j] = 1.0; // Perfect similarity with itself
      } else if (i < j) {
        // Calculate similarity only for upper triangle
        const similarity = cosineSimilarity(embeddings[i], embeddings[j]);
        matrix[i][j] = similarity;
        matrix[j][i] = similarity; // Mirror to lower triangle
      }
    }
  }

  return matrix;
}

/**
 * Embedding cache for efficient loading
 */
class EmbeddingCache {
  private cache = new Map<string, EmbeddingStorage>();
  private index: EmbeddingIndex | null = null;

  async getEmbeddingIndex(): Promise<EmbeddingIndex> {
    if (!this.index) {
      const response = await fetch('/data/embedding-index.json');
      if (!response.ok) {
        throw new Error('Failed to load embedding index');
      }
      this.index = await response.json();
    }
    return this.index!;
  }

  async getPaperEmbeddings(paperId: string): Promise<EmbeddingStorage> {
    if (!this.cache.has(paperId)) {
      const response = await fetch(`/data/embeddings/paper-${paperId}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load embeddings for paper ${paperId}`);
      }
      const data = await response.json();
      this.cache.set(paperId, data);
    }
    return this.cache.get(paperId)!;
  }

  async getPatternEmbedding(patternId: string): Promise<number[] | null> {
    try {
      const index = await this.getEmbeddingIndex();
      const paperId = index.patternToPaper[patternId];
      
      if (!paperId) {
        console.warn(`Pattern ${patternId} not found in embedding index`);
        return null;
      }

      const paperEmbeddings = await this.getPaperEmbeddings(paperId);
      const patternEmbedding = paperEmbeddings.patterns[patternId];
      
      return patternEmbedding ? patternEmbedding.embedding : null;
    } catch (error) {
      console.error(`Error loading embedding for pattern ${patternId}:`, error);
      return null;
    }
  }

  async getMultiplePatternEmbeddings(patternIds: string[]): Promise<Map<string, number[]>> {
    const embeddings = new Map<string, number[]>();
    
    // Group patterns by paper for efficient loading
    const index = await this.getEmbeddingIndex();
    const paperGroups = new Map<string, string[]>();
    
    for (const patternId of patternIds) {
      const paperId = index.patternToPaper[patternId];
      if (paperId) {
        if (!paperGroups.has(paperId)) {
          paperGroups.set(paperId, []);
        }
        paperGroups.get(paperId)!.push(patternId);
      }
    }

    // Load embeddings by paper
    for (const [paperId, patterns] of paperGroups) {
      try {
        const paperEmbeddings = await this.getPaperEmbeddings(paperId);
        
        for (const patternId of patterns) {
          const patternEmbedding = paperEmbeddings.patterns[patternId];
          if (patternEmbedding) {
            embeddings.set(patternId, patternEmbedding.embedding);
          }
        }
      } catch (error) {
        console.error(`Error loading embeddings for paper ${paperId}:`, error);
      }
    }

    return embeddings;
  }

  clearCache(): void {
    this.cache.clear();
    this.index = null;
  }
}

// Global embedding cache instance
export const embeddingCache = new EmbeddingCache();

/**
 * Compare multiple patterns and generate comprehensive comparison data
 */
export async function comparePatterns(
  patternIds: string[],
  userPrompt?: string
): Promise<PatternComparison> {
  if (patternIds.length < 2) {
    throw new Error('At least 2 patterns are required for comparison');
  }

  if (patternIds.length > 10) {
    throw new Error('Maximum 10 patterns allowed for comparison');
  }

  // Load embeddings for all patterns
  const embeddings = await embeddingCache.getMultiplePatternEmbeddings(patternIds);
  
  // Filter out patterns that couldn't be loaded
  const validPatternIds = patternIds.filter(id => embeddings.has(id));
  const embeddingVectors = validPatternIds.map(id => embeddings.get(id)!);

  if (validPatternIds.length < 2) {
    throw new Error('Not enough valid embeddings found for comparison');
  }

  // Calculate similarity matrix
  const similarityMatrix = calculateSimilarityMatrix(embeddingVectors);
  
  // Calculate statistics
  const flatSimilarities = [];
  for (let i = 0; i < similarityMatrix.length; i++) {
    for (let j = i + 1; j < similarityMatrix[i].length; j++) {
      flatSimilarities.push(similarityMatrix[i][j]);
    }
  }

  const averageSimilarity = flatSimilarities.reduce((a, b) => a + b, 0) / flatSimilarities.length;
  const maxSimilarity = Math.max(...flatSimilarities);
  const minSimilarity = Math.min(...flatSimilarities);

  // Generate clusters (simple k-means with k=2 for now)
  const clusters = generateClusters(embeddingVectors, validPatternIds, 2);

  // Generate visualization data
  const heatmapData = generateHeatmapData(similarityMatrix, validPatternIds);
  const scatterPlotData = generateScatterPlotData(embeddingVectors, validPatternIds);
  const networkData = generateNetworkData(similarityMatrix, validPatternIds);

  const comparison: PatternComparison = {
    comparisonId: `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    patterns: validPatternIds,
    userPrompt,
    similarityMatrix,
    statistics: {
      averageSimilarity,
      maxSimilarity,
      minSimilarity,
      clusters
    },
    visualization: {
      heatmapData,
      scatterPlotData,
      networkData
    }
  };

  return comparison;
}

/**
 * Generate clusters using simple k-means clustering
 */
function generateClusters(
  embeddings: number[][],
  patternIds: string[],
  k: number
): ClusterGroup[] {
  if (embeddings.length <= k) {
    // If we have fewer or equal patterns than clusters, each pattern is its own cluster
    return embeddings.map((embedding, index) => ({
      id: `cluster_${index}`,
      patternIds: [patternIds[index]],
      centroid: embedding,
      averageIntraClusterSimilarity: 1.0,
      mostRepresentativePattern: patternIds[index]
    }));
  }

  // Simple k-means implementation
  // Initialize centroids randomly
  const centroids: number[][] = [];
  const dimension = embeddings[0].length;
  
  for (let i = 0; i < k; i++) {
    const randomIndex = Math.floor(Math.random() * embeddings.length);
    centroids.push([...embeddings[randomIndex]]);
  }

  const assignments = new Array(embeddings.length).fill(0);
  let hasChanged = true;
  const maxIterations = 10;
  let iteration = 0;

  while (hasChanged && iteration < maxIterations) {
    hasChanged = false;
    
    // Assign each point to nearest centroid
    for (let i = 0; i < embeddings.length; i++) {
      let bestCluster = 0;
      let bestSimilarity = cosineSimilarity(embeddings[i], centroids[0]);
      
      for (let j = 1; j < k; j++) {
        const similarity = cosineSimilarity(embeddings[i], centroids[j]);
        if (similarity > bestSimilarity) {
          bestSimilarity = similarity;
          bestCluster = j;
        }
      }
      
      if (assignments[i] !== bestCluster) {
        assignments[i] = bestCluster;
        hasChanged = true;
      }
    }

    // Update centroids
    for (let j = 0; j < k; j++) {
      const clusterPoints = embeddings.filter((_, i) => assignments[i] === j);
      if (clusterPoints.length > 0) {
        for (let d = 0; d < dimension; d++) {
          centroids[j][d] = clusterPoints.reduce((sum, point) => sum + point[d], 0) / clusterPoints.length;
        }
      }
    }
    
    iteration++;
  }

  // Create cluster groups
  const clusters: ClusterGroup[] = [];
  for (let j = 0; j < k; j++) {
    const clusterPatternIds = patternIds.filter((_, i) => assignments[i] === j);
    const clusterEmbeddings = embeddings.filter((_, i) => assignments[i] === j);
    
    if (clusterPatternIds.length === 0) continue;

    // Calculate average intra-cluster similarity
    let totalSimilarity = 0;
    let pairCount = 0;
    for (let i = 0; i < clusterEmbeddings.length; i++) {
      for (let l = i + 1; l < clusterEmbeddings.length; l++) {
        totalSimilarity += cosineSimilarity(clusterEmbeddings[i], clusterEmbeddings[l]);
        pairCount++;
      }
    }
    const averageIntraClusterSimilarity = pairCount > 0 ? totalSimilarity / pairCount : 1.0;

    // Find most representative pattern (closest to centroid)
    let bestPatternIndex = 0;
    let bestSimilarity = cosineSimilarity(clusterEmbeddings[0], centroids[j]);
    for (let i = 1; i < clusterEmbeddings.length; i++) {
      const similarity = cosineSimilarity(clusterEmbeddings[i], centroids[j]);
      if (similarity > bestSimilarity) {
        bestSimilarity = similarity;
        bestPatternIndex = i;
      }
    }

    clusters.push({
      id: `cluster_${j}`,
      patternIds: clusterPatternIds,
      centroid: centroids[j],
      averageIntraClusterSimilarity,
      mostRepresentativePattern: clusterPatternIds[bestPatternIndex]
    });
  }

  return clusters;
}

/**
 * Generate heatmap visualization data
 */
function generateHeatmapData(
  similarityMatrix: number[][],
  patternIds: string[]
): HeatmapCell[] {
  const cells: HeatmapCell[] = [];
  
  for (let i = 0; i < similarityMatrix.length; i++) {
    for (let j = 0; j < similarityMatrix[i].length; j++) {
      const similarity = similarityMatrix[i][j];
      
      // Generate color based on similarity (green-yellow-red scale)
      let color: string;
      if (similarity >= 0.8) {
        color = '#22c55e'; // Green - high similarity
      } else if (similarity >= 0.6) {
        color = '#eab308'; // Yellow - medium similarity  
      } else if (similarity >= 0.3) {
        color = '#f97316'; // Orange - low similarity
      } else {
        color = '#ef4444'; // Red - very low similarity
      }
      
      cells.push({
        x: i,
        y: j,
        similarity,
        patternIds: [patternIds[i], patternIds[j]],
        color
      });
    }
  }
  
  return cells;
}

/**
 * Generate scatter plot data using PCA for dimensionality reduction
 */
function generateScatterPlotData(
  embeddings: number[][],
  patternIds: string[]
): ScatterPoint[] {
  // Simple 2D projection using first two dimensions for now
  // In a real implementation, you'd want to use PCA or t-SNE
  return embeddings.map((embedding, index) => ({
    x: embedding[0] || 0,
    y: embedding[1] || 0,
    patternId: patternIds[index],
    label: patternIds[index],
    category: 'unknown' // Would be populated from pattern data
  }));
}

/**
 * Generate network graph data
 */
function generateNetworkData(
  similarityMatrix: number[][],
  patternIds: string[],
  threshold: number = 0.5
): NetworkNode[] {
  const nodes: NetworkNode[] = patternIds.map((patternId) => ({
    id: patternId,
    label: patternId,
    category: 'unknown', // Would be populated from pattern data
    connections: []
  }));

  // Add connections based on similarity threshold
  for (let i = 0; i < similarityMatrix.length; i++) {
    for (let j = i + 1; j < similarityMatrix[i].length; j++) {
      const similarity = similarityMatrix[i][j];
      
      if (similarity >= threshold) {
        // Add bidirectional connections
        nodes[i].connections.push({
          targetId: patternIds[j],
          similarity,
          weight: similarity
        });
        
        nodes[j].connections.push({
          targetId: patternIds[i],
          similarity,
          weight: similarity
        });
      }
    }
  }

  return nodes;
}

/**
 * Find patterns most similar to a given text (for playground feature)
 */
export async function findSimilarPatterns(
  embedding: number[],
  threshold: number = 0.5,
  limit: number = 10
): Promise<Array<{ patternId: string; similarity: number }>> {
  const index = await embeddingCache.getEmbeddingIndex();
  const results: Array<{ patternId: string; similarity: number }> = [];

  // Load all patterns and calculate similarities
  for (const [paperId] of Object.entries(index.papers)) {
    try {
      const paperEmbeddings = await embeddingCache.getPaperEmbeddings(paperId);
      
      for (const [patternId, patternEmbedding] of Object.entries(paperEmbeddings.patterns)) {
        const similarity = cosineSimilarity(embedding, patternEmbedding.embedding);
        
        if (similarity >= threshold) {
          results.push({ patternId, similarity });
        }
      }
    } catch (error) {
      console.error(`Error processing paper ${paperId}:`, error);
    }
  }

  // Sort by similarity and limit results
  return results
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, limit);
}

/**
 * Find similar patterns based on user input text
 * Generates embedding from text then finds similar patterns
 */
export async function findSimilarPatternsFromText(
  userText: string,
  options: {
    threshold?: number;
    maxResults?: number;
    includeExcerpts?: boolean;
  } = {}
): Promise<SimilaritySearchResult[]> {
  const { threshold = 0.5, maxResults = 10 } = options;
  
  try {
    // TODO: In production, generate embedding from userText using Azure OpenAI
    // For now, return mock results based on text content
    const mockResults: SimilaritySearchResult[] = [
      {
        patternId: 'mock-pattern-1',
        patternName: 'Few-Shot Learning',
        similarity: 0.85,
        category: 'prompting',
        excerpt: 'Provide examples to guide the model toward better performance on specific tasks...',
        confidence: 'high' as const,
        sourceTitle: 'Prompt Engineering Patterns',
        authors: ['Mock Author A', 'Mock Author B']
      },
      {
        patternId: 'mock-pattern-2',
        patternName: 'Chain-of-Thought',
        similarity: 0.72,
        category: 'reasoning',
        excerpt: 'Step-by-step reasoning process that improves complex problem solving capabilities...',
        confidence: 'medium' as const,
        sourceTitle: 'Advanced Prompting Techniques',
        authors: ['Mock Author C', 'Mock Author D']
      },
      {
        patternId: 'mock-pattern-3',
        patternName: 'Zero-Shot Learning',
        similarity: 0.65,
        category: 'prompting',
        excerpt: 'Task completion without explicit examples, relying on model knowledge...',
        confidence: 'medium' as const,
        sourceTitle: 'Foundation Model Capabilities',
        authors: ['Mock Author E']
      }
    ];

    // Simulate similarity based on text content
    const textLower = userText.toLowerCase();
    const adjustedResults = mockResults.map(result => {
      let similarity = result.similarity;
      
      // Simple keyword matching to adjust similarity
      if (textLower.includes('example') || textLower.includes('few shot')) {
        if (result.patternName === 'Few-Shot Learning') similarity = Math.min(0.95, similarity + 0.1);
      }
      if (textLower.includes('reasoning') || textLower.includes('step') || textLower.includes('think')) {
        if (result.patternName === 'Chain-of-Thought') similarity = Math.min(0.95, similarity + 0.1);
      }
      if (textLower.includes('no example') || textLower.includes('zero shot')) {
        if (result.patternName === 'Zero-Shot Learning') similarity = Math.min(0.95, similarity + 0.1);
      }

      return { ...result, similarity, confidence: getConfidenceLevel(similarity) };
    });

    // Filter by threshold and limit results
    return adjustedResults
      .filter(result => result.similarity >= threshold)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, maxResults);
      
  } catch (error) {
    console.error('Error finding similar patterns:', error);
    throw new Error('Failed to find similar patterns');
  }
}

/**
 * Utility function to get confidence level based on similarity score
 */
export function getConfidenceLevel(similarity: number): 'high' | 'medium' | 'low' {
  if (similarity >= 0.7) return 'high';
  if (similarity >= 0.5) return 'medium';
  return 'low';
}
