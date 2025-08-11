/**
 * Similarity Network - Graph-based similarity analysis
 * 
 * Provides functionality for creating and analyzing similarity networks
 * where nodes are embeddings and edges represent similarity relationships.
 */

import { EmbeddingVector } from './similarity-engine';
import { SimilarityMatrix } from './similarity-matrix';

export interface NetworkNode {
  id: string;
  label?: string;
  metadata?: Record<string, unknown>;
  embedding?: number[];
  // Visual properties
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  cluster?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  // Visual properties
  width?: number;
  color?: string;
}

export interface NetworkLayout {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  clusters?: NetworkCluster[];
}

export interface NetworkCluster {
  id: number;
  nodes: string[];
  centroid?: NetworkNode;
  avgSimilarity?: number;
  color?: string;
}

export interface NetworkOptions {
  similarityThreshold?: number;
  maxEdges?: number;
  includeWeakConnections?: boolean;
  layoutAlgorithm?: 'force' | 'circular' | 'grid';
  clusteringEnabled?: boolean;
  clusterThreshold?: number;
}

/**
 * Network-based similarity analysis and visualization
 */
export class SimilarityNetwork {
  private embeddings: Map<string, EmbeddingVector> = new Map();
  private similarityMatrix?: SimilarityMatrix;
  private options: Required<NetworkOptions>;

  constructor(
    embeddings: EmbeddingVector[] = [],
    options: NetworkOptions = {}
  ) {
    this.options = {
      similarityThreshold: options.similarityThreshold ?? 0.3,
      maxEdges: options.maxEdges ?? 1000,
      includeWeakConnections: options.includeWeakConnections ?? false,
      layoutAlgorithm: options.layoutAlgorithm ?? 'force',
      clusteringEnabled: options.clusteringEnabled ?? true,
      clusterThreshold: options.clusterThreshold ?? 0.5
    };

    this.loadEmbeddings(embeddings);
  }

  loadEmbeddings(embeddings: EmbeddingVector[]): void {
    this.embeddings.clear();
    
    for (const embedding of embeddings) {
      this.embeddings.set(embedding.id, embedding);
    }

    if (embeddings.length > 0) {
      this.similarityMatrix = new SimilarityMatrix(embeddings, {
        threshold: this.options.similarityThreshold,
        sparse: true,
        symmetric: true
      });
    }
  }

  /**
   * Generate network layout from similarity data
   */
  generateNetwork(): NetworkLayout {
    if (!this.similarityMatrix) {
      return { nodes: [], edges: [] };
    }

    const nodes = this.createNodes();
    const edges = this.createEdges();
    const layout = this.applyLayout(nodes, edges);
    
    if (this.options.clusteringEnabled) {
      const clusters = this.detectClusters(layout.nodes, layout.edges);
      return { ...layout, clusters };
    }

    return layout;
  }

  private createNodes(): NetworkNode[] {
    const embeddings = Array.from(this.embeddings.values());
    
  return embeddings.map((embedding) => ({
      id: embedding.id,
      label: this.extractLabel(embedding),
      metadata: embedding.metadata,
      embedding: embedding.embedding,
      size: this.calculateNodeSize(embedding),
      color: this.assignNodeColor(embedding)
    }));
  }

  private createEdges(): NetworkEdge[] {
    if (!this.similarityMatrix) return [];

    const topPairs = this.similarityMatrix.getTopPairs(this.options.maxEdges);
    
    return topPairs
      .filter(pair => pair.similarity >= this.options.similarityThreshold)
      .map(pair => ({
        source: pair.idA,
        target: pair.idB,
        weight: pair.similarity,
        width: this.calculateEdgeWidth(pair.similarity),
        color: this.assignEdgeColor(pair.similarity)
      }));
  }

  private applyLayout(nodes: NetworkNode[], edges: NetworkEdge[]): NetworkLayout {
    const layoutNodes = [...nodes];

    switch (this.options.layoutAlgorithm) {
      case 'force':
        this.applyForceLayout(layoutNodes, edges);
        break;
      case 'circular':
        this.applyCircularLayout(layoutNodes);
        break;
      case 'grid':
        this.applyGridLayout(layoutNodes);
        break;
    }

    return { nodes: layoutNodes, edges };
  }

  private applyForceLayout(nodes: NetworkNode[], edges: NetworkEdge[]): void {
    // Simple force-directed layout algorithm
  const width = 800;
  const height = 600;

    // Initialize positions randomly
    nodes.forEach(node => {
      node.x = Math.random() * width;
      node.y = Math.random() * height;
    });

    // Run simulation steps
    const iterations = 100;
    const k = Math.sqrt((width * height) / nodes.length);
    
    for (let iter = 0; iter < iterations; iter++) {
      // Calculate repulsive forces
      nodes.forEach(nodeA => {
        let fx = 0, fy = 0;
        
        nodes.forEach(nodeB => {
          if (nodeA.id !== nodeB.id) {
            const dx = nodeA.x! - nodeB.x!;
            const dy = nodeA.y! - nodeB.y!;
            const distance = Math.sqrt(dx * dx + dy * dy) || 0.01;
            const force = k * k / distance;
            
            fx += (dx / distance) * force;
            fy += (dy / distance) * force;
          }
        });

        nodeA.x = Math.max(0, Math.min(width, nodeA.x! + fx * 0.01));
        nodeA.y = Math.max(0, Math.min(height, nodeA.y! + fy * 0.01));
      });

      // Calculate attractive forces from edges
      edges.forEach(edge => {
        const nodeA = nodes.find(n => n.id === edge.source);
        const nodeB = nodes.find(n => n.id === edge.target);
        
        if (nodeA && nodeB) {
          const dx = nodeB.x! - nodeA.x!;
          const dy = nodeB.y! - nodeA.y!;
          const distance = Math.sqrt(dx * dx + dy * dy) || 0.01;
          const force = (distance * distance) / k * edge.weight;
          
          const fx = (dx / distance) * force * 0.01;
          const fy = (dy / distance) * force * 0.01;
          
          nodeA.x = Math.max(0, Math.min(width, nodeA.x! + fx));
          nodeA.y = Math.max(0, Math.min(height, nodeA.y! + fy));
          nodeB.x = Math.max(0, Math.min(width, nodeB.x! - fx));
          nodeB.y = Math.max(0, Math.min(height, nodeB.y! - fy));
        }
      });
    }
  }

  private applyCircularLayout(nodes: NetworkNode[]): void {
    const centerX = 400;
    const centerY = 300;
    const radius = 200;
    
    nodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length;
      node.x = centerX + radius * Math.cos(angle);
      node.y = centerY + radius * Math.sin(angle);
    });
  }

  private applyGridLayout(nodes: NetworkNode[]): void {
    const cols = Math.ceil(Math.sqrt(nodes.length));
    const cellWidth = 800 / cols;
    const cellHeight = 600 / Math.ceil(nodes.length / cols);
    
    nodes.forEach((node, index) => {
      const row = Math.floor(index / cols);
      const col = index % cols;
      node.x = col * cellWidth + cellWidth / 2;
      node.y = row * cellHeight + cellHeight / 2;
    });
  }

  private detectClusters(nodes: NetworkNode[], edges: NetworkEdge[]): NetworkCluster[] {
    // Simple clustering based on connected components with high similarity
    const clusters: NetworkCluster[] = [];
    const visited = new Set<string>();
    let clusterId = 0;

    const adjacencyList = new Map<string, string[]>();
    
    // Build adjacency list for high-similarity edges
    edges
      .filter(edge => edge.weight >= this.options.clusterThreshold)
      .forEach(edge => {
        if (!adjacencyList.has(edge.source)) {
          adjacencyList.set(edge.source, []);
        }
        if (!adjacencyList.has(edge.target)) {
          adjacencyList.set(edge.target, []);
        }
        adjacencyList.get(edge.source)!.push(edge.target);
        adjacencyList.get(edge.target)!.push(edge.source);
      });

    // DFS to find connected components
    const dfs = (nodeId: string, cluster: string[]): void => {
      visited.add(nodeId);
      cluster.push(nodeId);
      
      const neighbors = adjacencyList.get(nodeId) || [];
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          dfs(neighbor, cluster);
        }
      }
    };

    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        const clusterNodes: string[] = [];
        dfs(node.id, clusterNodes);
        
        if (clusterNodes.length > 1) {
          clusters.push({
            id: clusterId++,
            nodes: clusterNodes,
            color: this.generateClusterColor(clusterId)
          });
        }
      }
    });

    // Assign cluster colors to nodes
    clusters.forEach(cluster => {
      cluster.nodes.forEach(nodeId => {
        const node = nodes.find(n => n.id === nodeId);
        if (node) {
          node.cluster = cluster.id;
          node.color = cluster.color;
        }
      });
    });

    return clusters;
  }

  private extractLabel(embedding: EmbeddingVector): string {
    // Extract meaningful label from metadata or ID
    if (embedding.metadata?.name) {
      return String(embedding.metadata.name);
    }
    if (embedding.metadata?.title) {
      return String(embedding.metadata.title);
    }
    return embedding.id.split('-').pop() || embedding.id;
  }

  private calculateNodeSize(embedding: EmbeddingVector): number {
    // Base size with optional scaling based on metadata
    let size = 10;
    
    if (embedding.metadata?.importance) {
      size *= Number(embedding.metadata.importance);
    }
    
    return Math.max(5, Math.min(30, size));
  }

  private assignNodeColor(embedding: EmbeddingVector): string {
    // Default color scheme
    const colors = [
      '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
      '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
    ];
    
    if (embedding.metadata?.category) {
      const categoryHash = this.hashString(String(embedding.metadata.category));
      return colors[categoryHash % colors.length];
    }
    
    const idHash = this.hashString(embedding.id);
    return colors[idHash % colors.length];
  }

  private calculateEdgeWidth(similarity: number): number {
    return Math.max(1, similarity * 5);
  }

  private assignEdgeColor(similarity: number): string {
    // Color gradient from weak to strong similarity
    if (similarity >= 0.8) return '#10b981'; // Strong - green
    if (similarity >= 0.6) return '#f59e0b'; // Medium - yellow
    if (similarity >= 0.4) return '#ef4444'; // Weak - red
    return '#9ca3af'; // Very weak - gray
  }

  private generateClusterColor(clusterId: number): string {
    const colors = [
      '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
      '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
    ];
    return colors[clusterId % colors.length];
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Get network statistics
   */
  getNetworkStatistics(): {
    nodeCount: number;
    edgeCount: number;
    avgDegree: number;
    clusterCount: number;
    density: number;
  } {
    const layout = this.generateNetwork();
    const nodeCount = layout.nodes.length;
    const edgeCount = layout.edges.length;
    const avgDegree = nodeCount > 0 ? (2 * edgeCount) / nodeCount : 0;
    const maxEdges = nodeCount * (nodeCount - 1) / 2;
    const density = maxEdges > 0 ? edgeCount / maxEdges : 0;
    
    return {
      nodeCount,
      edgeCount,
      avgDegree,
      clusterCount: layout.clusters?.length || 0,
      density
    };
  }

  /**
   * Update network options and regenerate
   */
  updateOptions(newOptions: Partial<NetworkOptions>): void {
    this.options = { ...this.options, ...newOptions };
    
    if (newOptions.similarityThreshold && this.similarityMatrix) {
      this.similarityMatrix.updateThreshold(newOptions.similarityThreshold);
    }
  }
}
