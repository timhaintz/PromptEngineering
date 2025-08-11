/**
 * Similarity Network Component
 * 
 * Displays patterns as nodes in a network graph with edges representing
 * similarity relationships. Uses D3.js-style force simulation for layout.
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import type { PatternComparison, NetworkNode, NetworkEdge } from '@/lib/types/pattern';

interface SimilarityNetworkProps {
  comparison: PatternComparison;
  threshold?: number; // Minimum similarity to show edge
  onNodeClick?: (patternId: string) => void;
  className?: string;
}

export default function SimilarityNetwork({
  comparison,
  threshold = 0.3,
  onNodeClick,
  className = ''
}: SimilarityNetworkProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // 'visualization' reserved for future enhancements
  const { patterns, similarityMatrix } = comparison;

  // Get pattern display label (use full ID for consistency)
  const getPatternName = (patternId: string): string => {
    return patternId;
  };

  // Create nodes and edges from comparison data
  const createNetworkData = () => {
  const nodes: NetworkNode[] = patterns.map((patternId) => ({
      id: patternId,
      label: getPatternName(patternId),
      category: 'unknown', // In real implementation, get from pattern metadata
      x: Math.random() * 400 + 50,
      y: Math.random() * 300 + 50,
      connections: []
    }));

    const edges: NetworkEdge[] = [];
    
    for (let i = 0; i < patterns.length; i++) {
      for (let j = i + 1; j < patterns.length; j++) {
        const similarity = similarityMatrix[i][j];
        if (similarity >= threshold) {
          edges.push({
            source: patterns[i],
            target: patterns[j],
            weight: similarity
          });
          // Update connection counts
          const sourceNode = nodes[i];
          const targetNode = nodes[j];
          sourceNode.connections.push({
            targetId: patterns[j],
            similarity,
            weight: similarity
          });
          targetNode.connections.push({
            targetId: patterns[i],
            similarity,
            weight: similarity
          });
        }
      }
    }

    return { nodes, edges };
  };

  const { nodes, edges } = createNetworkData();

  const getNodeRadius = (connections: number): number => {
    return Math.max(8, Math.min(20, 8 + connections * 2));
  };

  const getNodeColor = (connections: number): string => {
    if (connections >= 5) return '#10b981'; // green-500
    if (connections >= 3) return '#f59e0b'; // amber-500
    if (connections >= 1) return '#ef4444'; // red-500
    return '#6b7280'; // gray-500
  };

  const getEdgeWidth = (weight: number): number => {
    return Math.max(1, weight * 3);
  };

  const getEdgeOpacity = (weight: number): number => {
    return Math.max(0.3, weight);
  };

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = svgRef.current;
    const rect = svg.getBoundingClientRect();
    
    // Simple force simulation logic
    const simulateForces = () => {
      const iterations = 100;
      const attraction = 0.01;
      const repulsion = 200;
      
      for (let iter = 0; iter < iterations; iter++) {
        // Repulsion between all nodes
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const nodeI = nodes[i];
            const nodeJ = nodes[j];
            
            if (!nodeI.x || !nodeI.y || !nodeJ.x || !nodeJ.y) continue;
            
            const dx = nodeJ.x - nodeI.x;
            const dy = nodeJ.y - nodeI.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
              const force = repulsion / (distance * distance);
              const fx = (dx / distance) * force;
              const fy = (dy / distance) * force;
              
              nodeI.x! -= fx;
              nodeI.y! -= fy;
              nodeJ.x! += fx;
              nodeJ.y! += fy;
            }
          }
        }
        
        // Attraction along edges
        edges.forEach(edge => {
          const sourceNode = nodes.find(n => n.id === edge.source);
          const targetNode = nodes.find(n => n.id === edge.target);
          
          if (sourceNode && targetNode && sourceNode.x && sourceNode.y && targetNode.x && targetNode.y) {
            const dx = targetNode.x - sourceNode.x;
            const dy = targetNode.y - sourceNode.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
              const force = attraction * edge.weight;
              const fx = (dx / distance) * force * distance;
              const fy = (dy / distance) * force * distance;
              
              sourceNode.x! += fx;
              sourceNode.y! += fy;
              targetNode.x! -= fx;
              targetNode.y! -= fy;
            }
          }
        });
        
        // Keep nodes within bounds
        nodes.forEach(node => {
          const margin = 30;
          if (node.x !== undefined && node.y !== undefined) {
            node.x = Math.max(margin, Math.min(rect.width - margin, node.x));
            node.y = Math.max(margin, Math.min(rect.height - margin, node.y));
          }
        });
      }
    };

    simulateForces();
  }, [nodes, edges, threshold]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId === selectedNode ? null : nodeId);
    if (onNodeClick) {
      onNodeClick(nodeId);
    }
  };

  const isNodeHighlighted = (nodeId: string): boolean => {
    if (!hoveredNode && !selectedNode) return false;
    if (hoveredNode === nodeId || selectedNode === nodeId) return true;
    
    // Highlight connected nodes
    const targetNode = hoveredNode || selectedNode;
    return edges.some(edge => 
      (edge.source === targetNode && edge.target === nodeId) ||
      (edge.target === targetNode && edge.source === nodeId)
    );
  };

  const isEdgeHighlighted = (edge: NetworkEdge): boolean => {
    if (!hoveredNode && !selectedNode) return false;
    const targetNode = hoveredNode || selectedNode;
    return edge.source === targetNode || edge.target === targetNode;
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Similarity Network
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Patterns connected by similarity relationships. Larger nodes have more connections.
          Threshold: {(threshold * 100).toFixed(0)}%
        </p>
        
        {/* Controls */}
        <div className="flex items-center space-x-4 mb-4">
          <label className="flex items-center space-x-2 text-sm">
            <span className="text-gray-600">Similarity Threshold:</span>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.1"
              value={threshold}
              onChange={(e) => {
                // In a real implementation, this would update the parent component
                console.log('Threshold changed:', e.target.value);
              }}
              className="w-20"
              aria-label="Similarity threshold"
            />
            <span className="font-medium">{(threshold * 100).toFixed(0)}%</span>
          </label>
        </div>
      </div>

      {/* Network Visualization */}
      <div className="relative">
        <svg
          ref={svgRef}
          width="100%"
          height="400"
          viewBox="0 0 500 400"
          className="border border-gray-200 rounded-lg bg-gray-50"
        >
          {/* Edges */}
          {edges.map((edge, index) => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;
            
            const isHighlighted = isEdgeHighlighted(edge);
            
            return (
              <line
                key={`edge-${index}`}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke={isHighlighted ? '#3b82f6' : '#9ca3af'}
                strokeWidth={getEdgeWidth(edge.weight)}
                opacity={isHighlighted ? 0.8 : getEdgeOpacity(edge.weight)}
                className="transition-all duration-200"
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const isHighlighted = isNodeHighlighted(node.id);
            const isSelected = selectedNode === node.id;
            
            return (
              <g key={node.id}>
                {/* Node circle */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={getNodeRadius(node.connections.length)}
                  fill={isSelected ? '#3b82f6' : getNodeColor(node.connections.length)}
                  stroke={isHighlighted ? '#1d4ed8' : '#ffffff'}
                  strokeWidth={isHighlighted ? 3 : 2}
                  className="cursor-pointer transition-all duration-200"
                  onMouseEnter={() => setHoveredNode(node.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onClick={() => handleNodeClick(node.id)}
                />
                
                {/* Node label */}
                <text
                  x={node.x}
                  y={(node.y || 0) + getNodeRadius(node.connections.length) + 15}
                  textAnchor="middle"
                  fontSize="10"
                  fill={isHighlighted ? '#1d4ed8' : '#374151'}
                  className="pointer-events-none font-medium"
                >
                  {node.label}
                </text>
                
                {/* Connection count */}
                <text
                  x={node.x}
                  y={(node.y || 0) + 3}
                  textAnchor="middle"
                  fontSize="8"
                  fill="white"
                  className="pointer-events-none font-bold"
                >
                  {node.connections.length}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover tooltip */}
        {hoveredNode && (
          <div className="absolute top-4 left-4 bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm z-10">
            <div className="font-medium flex items-center gap-2">
              <span>Pattern</span>
              <span className="inline-flex items-center rounded bg-gray-800 text-white px-2 py-0.5 text-[10px] font-semibold border border-gray-700" title={`ID: ${getPatternName(hoveredNode)}`}>
                ID: {getPatternName(hoveredNode)}
              </span>
            </div>
            <div className="text-gray-300">
              {nodes.find(n => n.id === hoveredNode)?.connections.length || 0} connections
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Node Colors</h4>
          <div className="space-y-2 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>High connectivity (5+ connections)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-amber-500 rounded-full"></div>
              <span>Medium connectivity (3-4 connections)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <span>Low connectivity (1-2 connections)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
              <span>Isolated (no connections)</span>
            </div>
          </div>
        </div>
        
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Statistics</h4>
          <div className="space-y-1 text-xs">
            <div>Total patterns: {nodes.length}</div>
            <div>Connections shown: {edges.length}</div>
            <div>Most connected: {Math.max(...nodes.map(n => n.connections.length), 0)} links</div>
            <div>Average connections: {(edges.length * 2 / nodes.length).toFixed(1)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
