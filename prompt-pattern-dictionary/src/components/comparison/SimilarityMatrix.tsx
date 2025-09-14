/**
 * Similarity Matrix Component
 * 
 * Displays a visual similarity matrix with color-coded cells showing
 * pairwise similarities between selected patterns. Includes interactive
 * hover effects and click actions.
 */

'use client';

import { useState } from 'react';
import type { PatternComparison } from '@/lib/types/pattern';
import Heatmap from '@/components/visualization/Heatmap';

interface SimilarityMatrixProps {
  comparison: PatternComparison;
  onCellClick?: (patternIds: [string, string], similarity: number) => void;
  className?: string;
}

export default function SimilarityMatrix({
  comparison,
  onCellClick,
  className = ''
}: SimilarityMatrixProps) {
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null);

  // 'visualization' reserved for future heatmap/scatter views
  const { patterns, similarityMatrix } = comparison;

  // Get pattern display label (full ID for consistent indexing UX)
  const getPatternName = (patternId: string): string => {
    return patternId;
  };

  const formatSimilarity = (similarity: number): string => {
    return (similarity * 100).toFixed(1) + '%';
  };

  const getSimilarityColor = (similarity: number): string => {
    if (similarity >= 0.8) return 'bg-green-500';
    if (similarity >= 0.6) return 'bg-yellow-500';
    if (similarity >= 0.3) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getSimilarityIntensity = (similarity: number): number => {
    // Return opacity value between 0.2 and 1.0
    return 0.2 + (similarity * 0.8);
  };

  const getOpacityClass = (similarity: number): string => {
    // Bucket opacity into Tailwind classes to avoid inline styles
    if (similarity >= 0.9) return 'opacity-100';
    if (similarity >= 0.75) return 'opacity-80';
  if (similarity >= 0.6) return 'text-slate-600';
    if (similarity >= 0.45) return 'opacity-60';
    if (similarity >= 0.3) return 'opacity-50';
    if (similarity >= 0.15) return 'opacity-40';
    return 'opacity-30';
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Similarity Matrix
        </h3>
        <p className="text-sm text-gray-600">
          Pairwise similarity scores between selected patterns. Darker colors indicate higher similarity.
        </p>
      </div>

      {/* Legend */}
      <div className="mb-4 flex items-center space-x-4 text-sm">
        <span className="text-gray-600">Similarity:</span>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span>Low (&lt;30%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-orange-500 rounded"></div>
          <span>Medium (30-60%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-yellow-500 rounded"></div>
          <span>High (60-80%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Very High (&gt;80%)</span>
        </div>
      </div>

      {/* Matrix */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Column Headers */}
          <div className="flex">
            <div className="w-32 h-8"></div> {/* Empty corner */}
            {patterns.map((patternId, index) => (
              <div
                key={`header-${index}`}
                className="w-20 h-8 flex items-center justify-center text-xs font-medium text-gray-700 border-b border-gray-200"
                title={getPatternName(patternId)}
              >
                <span className="transform -rotate-45 origin-center truncate w-16">
                  P{index + 1}
                </span>
              </div>
            ))}
          </div>

          {/* Matrix Rows */}
          {patterns.map((rowPatternId, rowIndex) => (
            <div key={`row-${rowIndex}`} className="flex">
              {/* Row Header */}
              <div
                className="w-32 h-12 flex items-center px-2 text-xs font-medium text-gray-700 border-r border-gray-200 bg-gray-50"
                title={`ID: ${getPatternName(rowPatternId)}`}
              >
                <div className="flex items-center gap-1 min-w-0">
                  <span className="shrink-0">P{rowIndex + 1}:</span>
                  <span className="inline-flex items-center rounded bg-gray-100 text-gray-800 px-2 py-0.5 text-[10px] font-semibold border border-gray-200 truncate" title={`ID: ${getPatternName(rowPatternId)}`}>
                    ID: {getPatternName(rowPatternId)}
                  </span>
                </div>
              </div>

              {/* Matrix Cells */}
              {patterns.map((colPatternId, colIndex) => {
                const similarity = similarityMatrix[rowIndex][colIndex];
                const isHovered = hoveredCell?.x === colIndex && hoveredCell?.y === rowIndex;
                const isDiagonal = rowIndex === colIndex;

        return (
                  <div
                    key={`cell-${rowIndex}-${colIndex}`}
          className={`w-20 h-12 border border-gray-200 cursor-pointer transition-all duration-200 relative ${
                      isHovered ? 'ring-2 ring-blue-500 z-10' : ''
          } ${isDiagonal ? 'bg-gray-100' : getSimilarityColor(similarity)} ${isDiagonal ? '' : getOpacityClass(similarity)}`}
                    data-opacity={isDiagonal ? '1' : getSimilarityIntensity(similarity)}
                    onMouseEnter={() => setHoveredCell({ x: colIndex, y: rowIndex })}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => {
                      if (!isDiagonal && onCellClick) {
                        onCellClick([rowPatternId, colPatternId], similarity);
                      }
                    }}
                    title={
                      isDiagonal
                        ? `Self-similarity: 100%`
                        : `Similarity between P${rowIndex + 1} and P${colIndex + 1}: ${formatSimilarity(similarity)}`
                    }
                  >
                    <div className="w-full h-full flex items-center justify-center text-xs font-medium text-white">
                      {isDiagonal ? '100%' : formatSimilarity(similarity)}
                    </div>

                    {/* Hover tooltip */}
                    {isHovered && !isDiagonal && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-20 whitespace-nowrap">
                        <div className="font-medium">Similarity: {formatSimilarity(similarity)}</div>
                        <div className="text-gray-300 flex items-center gap-1">
                          <span className="inline-flex items-center rounded bg-gray-800 text-white px-2 py-0.5 text-[10px] font-semibold border border-gray-700">ID: {getPatternName(rowPatternId)}</span>
                          <span>↔</span>
                          <span className="inline-flex items-center rounded bg-gray-800 text-white px-2 py-0.5 text-[10px] font-semibold border border-gray-700">ID: {getPatternName(colPatternId)}</span>
                        </div>
                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-600">Average Similarity</div>
          <div className="text-xl font-bold text-gray-900">
            {formatSimilarity(comparison.statistics.averageSimilarity)}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-600">Highest Similarity</div>
          <div className="text-xl font-bold text-green-700">
            {formatSimilarity(comparison.statistics.maxSimilarity)}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-600">Lowest Similarity</div>
          <div className="text-xl font-bold text-red-600">
            {formatSimilarity(comparison.statistics.minSimilarity)}
          </div>
        </div>
      </div>

      {/* Pattern Legend */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Pattern Reference</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          {patterns.map((patternId, index) => (
            <div key={`legend-${index}`} className="flex items-center space-x-2">
              <span className="font-medium text-gray-600 w-8">P{index + 1}:</span>
              <span className="text-gray-800 truncate" title={getPatternName(patternId)}>
                {getPatternName(patternId)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Heatmap Preview (scaffold) */}
      {comparison.visualization?.heatmapData?.length ? (
        <div className="mt-8">
          <Heatmap
            cells={comparison.visualization.heatmapData}
            xLabels={patterns.map((_, i) => `P${i + 1}`)}
            yLabels={patterns.map((_, i) => `P${i + 1}`)}
            onCellClick={(cell) => {
              if (!onCellClick) return;
              const [idA, idB] = cell.patternIds;
              onCellClick([idA, idB], cell.similarity);
            }}
          />
        </div>
      ) : null}
    </div>
  );
}
