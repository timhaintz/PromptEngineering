/**
 * Heatmap Component (scaffold)
 *
 * Reusable heatmap to render PRD HeatmapCell[] in an accessible grid with
 * row/column headers. Minimal styling and a simple similarity->color mapping
 * when a cell.color isn't provided.
 */

'use client';

import React from 'react';
import type { HeatmapCell } from '@/lib/types/pattern';

export interface HeatmapProps {
  cells: HeatmapCell[];
  xLabels: string[]; // columns
  yLabels: string[]; // rows
  onCellClick?: (cell: HeatmapCell) => void;
  className?: string;
  title?: string;
}

function colorForSimilarity(similarity: number): string {
  // Tailwind classes fallbacks if no color is provided on the cell
  if (similarity >= 0.8) return 'bg-green-500';
  if (similarity >= 0.6) return 'bg-yellow-500';
  if (similarity >= 0.3) return 'bg-orange-500';
  return 'bg-red-500';
}

function opacityBucket(similarity: number): string {
  if (similarity >= 0.9) return 'opacity-100';
  if (similarity >= 0.75) return 'opacity-80';
  if (similarity >= 0.6) return 'text-slate-600';
  if (similarity >= 0.45) return 'opacity-60';
  if (similarity >= 0.3) return 'opacity-50';
  if (similarity >= 0.15) return 'opacity-40';
  return 'opacity-30';
}

export default function Heatmap({
  cells,
  xLabels,
  yLabels,
  onCellClick,
  className = '',
  title = 'Similarity Heatmap',
}: HeatmapProps) {
  // Build an index for quick lookup by (x,y)
  const sizeX = xLabels.length;
  const sizeY = yLabels.length;

  const grid: (HeatmapCell | undefined)[][] = Array.from({ length: sizeY }, () =>
    Array.from({ length: sizeX }, () => undefined)
  );

  for (const cell of cells) {
    if (
      typeof cell.x === 'number' &&
      typeof cell.y === 'number' &&
      cell.x >= 0 &&
      cell.y >= 0 &&
      cell.x < sizeX &&
      cell.y < sizeY
    ) {
      grid[cell.y][cell.x] = cell;
    }
  }

  const formatPct = (s: number) => `${(s * 100).toFixed(1)}%`;

  return (
    <div className={`bg-white rounded-lg shadow-md p-4 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">Click a cell to inspect a pair.</p>
      </div>

      {/* Legend */}
      <div className="mb-3 flex items-center space-x-4 text-xs">
        <span className="text-gray-600">Similarity:</span>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span>Low (&lt;30%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-orange-500 rounded"></div>
          <span>Medium (30-60%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-500 rounded"></div>
          <span>High (60-80%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span>Very High (&gt;80%)</span>
        </div>
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Column headers */}
          <div className="flex">
            <div className="w-32 h-8"></div>
            {xLabels.map((label, i) => (
              <div
                key={`x-${i}`}
                className="w-16 h-8 flex items-center justify-center text-[10px] font-medium text-gray-700 border-b border-gray-200"
                title={label}
              >
                <span className="transform -rotate-45 origin-center truncate w-12">{label}</span>
              </div>
            ))}
          </div>

          {/* Rows */}
          {grid.map((row, y) => (
            <div key={`row-${y}`} className="flex">
              {/* Row header */}
              <div
                className="w-32 h-10 flex items-center px-2 text-xs font-medium text-gray-700 border-r border-gray-200 bg-gray-50"
                title={yLabels[y]}
              >
                <span className="truncate">{yLabels[y]}</span>
              </div>

              {row.map((cell, x) => {
                const similarity = cell?.similarity ?? (y === x ? 1 : 0);
                const isDiagonal = y === x;
                const colorClass = cell?.color || (isDiagonal ? 'bg-gray-100' : colorForSimilarity(similarity));
                const opacityClass = isDiagonal ? '' : opacityBucket(similarity);
                const label = isDiagonal
                  ? `Self: ${formatPct(1)}`
                  : `${yLabels[y]} ↔ ${xLabels[x]}: ${formatPct(similarity)}`;
                const content = isDiagonal ? '100%' : formatPct(similarity);
                return (
                  <button
                    key={`cell-${x}-${y}`}
                    type="button"
                    className={`w-16 h-10 border border-gray-200 flex items-center justify-center text-[10px] font-semibold text-white ${colorClass} ${opacityClass}`}
                    title={label}
                    aria-label={label}
                    onClick={() => cell && onCellClick?.(cell)}
                  >
                    {content}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
