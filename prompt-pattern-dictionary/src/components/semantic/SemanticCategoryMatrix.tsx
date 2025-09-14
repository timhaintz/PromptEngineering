/**
 * Semantic Category Matrix Component
 * 
 * Displays the dual categorization matrix with filtering and visualization
 */

'use client';

import { useState, useMemo } from 'react';
import { EnhancedPattern } from '@/types/patterns';

interface SemanticMatrixProps {
  patterns: EnhancedPattern[];
  className?: string;
}

export default function SemanticCategoryMatrix({ patterns, className = '' }: SemanticMatrixProps) {
  const [viewMode, setViewMode] = useState<'patterns' | 'examples' | 'matrix'>('matrix');
  const [selectedOriginalCategory, setSelectedOriginalCategory] = useState<string>('all');
  const [selectedSemanticCategory, setSelectedSemanticCategory] = useState<string>('all');
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0);
  const [showMismatchesOnly, setShowMismatchesOnly] = useState<boolean>(false);

  // Calculate category distributions and statistics
  const statistics = useMemo(() => {
    const categorizedPatterns = patterns.filter(p => p.semantic_categorization);
    
    const originalCategories = new Set(patterns.map(p => p.category || p.original_paper_category));
    const semanticCategories = new Set(categorizedPatterns.map(p => p.semantic_categorization!.category));
    
    const categoryChanges = categorizedPatterns.filter(p => 
      p.original_paper_category !== p.semantic_categorization!.category
    ).length;
    
    let exampleMismatches = 0;
    categorizedPatterns.forEach(pattern => {
      const patternCategory = pattern.semantic_categorization!.category;
      pattern.examples?.forEach(example => {
        if (example.semantic_categorization && 
            example.semantic_categorization.category !== patternCategory) {
          exampleMismatches++;
        }
      });
    });
    
    const avgConfidence = categorizedPatterns.length > 0 ? 
      categorizedPatterns.reduce((sum, p) => sum + p.semantic_categorization!.confidence, 0) / categorizedPatterns.length : 0;

    return {
      totalPatterns: patterns.length,
      categorizedPatterns: categorizedPatterns.length,
      originalCategoriesCount: originalCategories.size,
      semanticCategoriesCount: semanticCategories.size,
      categoryChanges,
      exampleMismatches,
      averageConfidence: avgConfidence,
      originalCategories: Array.from(originalCategories).sort(),
      semanticCategories: Array.from(semanticCategories).sort()
    };
  }, [patterns]);

  // Create category transition matrix
  const transitionMatrix = useMemo(() => {
    const matrix: Record<string, Record<string, number>> = {};
    
    patterns.forEach(pattern => {
      if (pattern.semantic_categorization && pattern.original_paper_category) {
        const original = pattern.original_paper_category;
        const semantic = pattern.semantic_categorization.category;
        
        if (!matrix[original]) matrix[original] = {};
        if (!matrix[original][semantic]) matrix[original][semantic] = 0;
        matrix[original][semantic]++;
      }
    });
    
    return matrix;
  }, [patterns]);

  // Filter patterns based on current selections
  const filteredPatterns = useMemo(() => {
    return patterns.filter(pattern => {
      // Original category filter
      if (selectedOriginalCategory !== 'all' && 
          pattern.original_paper_category !== selectedOriginalCategory) {
        return false;
      }
      
      // Semantic category filter
      if (selectedSemanticCategory !== 'all' && 
          pattern.semantic_categorization?.category !== selectedSemanticCategory) {
        return false;
      }
      
      // Confidence threshold
      if (pattern.semantic_categorization && 
          pattern.semantic_categorization.confidence < confidenceThreshold) {
        return false;
      }
      
      // Show mismatches only
      if (showMismatchesOnly && pattern.semantic_categorization && 
          pattern.original_paper_category === pattern.semantic_categorization.category) {
        return false;
      }
      
      return true;
    });
  }, [patterns, selectedOriginalCategory, selectedSemanticCategory, confidenceThreshold, showMismatchesOnly]);

  const renderStatisticsPanel = () => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">Categorization Statistics</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{statistics.totalPatterns}</div>
          <div className="text-sm text-gray-600">Total Patterns</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-700">{statistics.categoryChanges}</div>
          <div className="text-sm text-gray-600">Category Changes</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{statistics.exampleMismatches}</div>
          <div className="text-sm text-gray-600">Example Mismatches</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">{(statistics.averageConfidence * 100).toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Avg Confidence</div>
        </div>
      </div>
      
      <div className="text-sm text-gray-600">
        <strong>Coverage:</strong> {statistics.categorizedPatterns}/{statistics.totalPatterns} patterns ({((statistics.categorizedPatterns / statistics.totalPatterns) * 100).toFixed(1)}%)
        <br />
        <strong>Category Migration:</strong> {((statistics.categoryChanges / statistics.categorizedPatterns) * 100).toFixed(1)}% of patterns changed categories
      </div>
    </div>
  );

  const renderControlPanel = () => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">Filters & Controls</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {/* View Mode */}
        <div>
          <label htmlFor="view-mode" className="block text-sm font-medium text-gray-700 mb-2">View Mode</label>
          <select
            id="view-mode"
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value as 'patterns' | 'examples' | 'matrix')}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="matrix">Transition Matrix</option>
            <option value="patterns">Pattern View</option>
            <option value="examples">Example View</option>
          </select>
        </div>
        
        {/* Original Category Filter */}
        <div>
          <label htmlFor="original-category" className="block text-sm font-medium text-gray-700 mb-2">Original Category</label>
          <select
            id="original-category"
            value={selectedOriginalCategory}
            onChange={(e) => setSelectedOriginalCategory(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Categories</option>
            {statistics.originalCategories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
        
        {/* Semantic Category Filter */}
        <div>
          <label htmlFor="semantic-category" className="block text-sm font-medium text-gray-700 mb-2">Semantic Category</label>
          <select
            id="semantic-category"
            value={selectedSemanticCategory}
            onChange={(e) => setSelectedSemanticCategory(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Categories</option>
            {statistics.semanticCategories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
        
        {/* Confidence Threshold */}
        <div>
          <label htmlFor="min-confidence" className="block text-sm font-medium text-gray-700 mb-2">
            Min Confidence: {(confidenceThreshold * 100).toFixed(0)}%
          </label>
          <input
            id="min-confidence"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
      
      <div className="flex items-center">
        <input
          type="checkbox"
          id="show-mismatches"
          checked={showMismatchesOnly}
          onChange={(e) => setShowMismatchesOnly(e.target.checked)}
          className="mr-2"
        />
        <label htmlFor="show-mismatches" className="text-sm text-gray-700">
          Show only category changes
        </label>
      </div>
    </div>
  );

  const renderTransitionMatrix = () => {
    const topTransitions = Object.entries(transitionMatrix)
      .flatMap(([original, semanticCounts]) =>
        Object.entries(semanticCounts).map(([semantic, count]) => ({
          original,
          semantic,
          count,
          isChange: original !== semantic
        }))
      )
      .sort((a, b) => b.count - a.count)
      .slice(0, 20);

    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Top Category Transitions</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Original Category</th>
                <th className="text-left py-2">Semantic Category</th>
                <th className="text-right py-2">Count</th>
                <th className="text-center py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {topTransitions.map((transition, idx) => (
                <tr key={idx} className="border-b">
                  <td className="py-2 text-blue-600">{transition.original}</td>
                  <td className="py-2 text-green-700">{transition.semantic}</td>
                  <td className="py-2 text-right font-medium">{transition.count}</td>
                  <td className="py-2 text-center">
                    {transition.isChange ? (
                      <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">
                        Changed
                      </span>
                    ) : (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                        Same
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderPatternView = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">
        Patterns ({filteredPatterns.length})
      </h3>
      
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {filteredPatterns.slice(0, 50).map(pattern => (
          <div key={pattern.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2 flex-wrap">
                <h4 className="font-medium text-gray-900">{pattern.patternName}</h4>
                {/* Pattern ID badge */}
                <span className="text-[10px] font-medium bg-gray-100 text-gray-800 px-2 py-0.5 rounded border border-gray-200">
                  ID: {pattern.id}
                </span>
              </div>
              {pattern.semantic_categorization && (
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {(pattern.semantic_categorization.confidence * 100).toFixed(1)}%
                </span>
              )}
            </div>
            
            <div className="flex gap-2 text-sm">
              <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded">
                Original: {pattern.original_paper_category || pattern.category}
              </span>
              {pattern.semantic_categorization && (
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                  Semantic: {pattern.semantic_categorization.category}
                </span>
              )}
            </div>
            
            {/* Example full-index badges (first 5) */}
            {pattern.examples && pattern.examples.length > 0 && (
              <div className="mt-2 flex items-center flex-wrap gap-1 text-[10px] text-gray-700">
                <span className="mr-1 text-gray-600">Examples:</span>
                {pattern.examples.slice(0, 5).map(ex => (
                  <span key={ex.id}
                        className="inline-flex items-center bg-gray-100 text-gray-800 px-2 py-0.5 rounded border border-gray-200">
                    {pattern.id}-{ex.index}
                  </span>
                ))}
                {pattern.examples.length > 5 && (
                  <span className="text-gray-500 ml-1">+{pattern.examples.length - 5} more</span>
                )}
              </div>
            )}

            {/* Show example mismatches */}
            {pattern.examples && pattern.semantic_categorization && (
              <div className="mt-2 text-xs text-gray-600">
                {pattern.examples.filter(ex => 
                  ex.semantic_categorization?.category !== pattern.semantic_categorization!.category
                ).length} example(s) with different categories
              </div>
            )}
          </div>
        ))}
        
        {filteredPatterns.length > 50 && (
          <div className="text-center text-gray-600 text-sm">
            Showing first 50 of {filteredPatterns.length} patterns
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {renderStatisticsPanel()}
      {renderControlPanel()}
      
      {viewMode === 'matrix' && renderTransitionMatrix()}
      {viewMode === 'patterns' && renderPatternView()}
      {viewMode === 'examples' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Example Analysis</h3>
          <p className="text-gray-600">Example-level analysis view coming soon...</p>
        </div>
      )}
    </div>
  );
}
