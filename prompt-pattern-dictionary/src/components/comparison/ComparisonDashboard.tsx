/**
 * Comparison Dashboard Component
 * 
 * Main dashboard for pattern comparison features. Combines pattern selection,
 * similarity matrix, network visualization, and export functionality.
 */

'use client';

import { useState, useEffect } from 'react';
import { comparePatterns } from '@/lib/similarity';
import type { PatternComparison } from '@/lib/types/pattern';
import PatternSelector from './PatternSelector';
import SimilarityMatrix from './SimilarityMatrix';
import SimilarityNetwork from './SimilarityNetwork';

interface ComparisonDashboardProps {
  className?: string;
}

export default function ComparisonDashboard({ className = '' }: ComparisonDashboardProps) {
  const [selectedPatterns, setSelectedPatterns] = useState<string[]>([]);
  const [comparison, setComparison] = useState<PatternComparison | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'matrix' | 'network'>('matrix');

  // Mock patterns for development - in production, this would come from props or context
  const mockPatterns = [
    {
      id: 'pattern-1',
      patternName: 'Few-Shot Learning',
      category: 'prompting',
      description: 'Provide examples to guide the model',
      examples: [],
      paper: { id: 'paper-1', title: 'Mock Paper', authors: [] },
      tags: ['examples', 'learning'],
      searchableContent: 'few shot learning examples'
    },
    {
      id: 'pattern-2', 
      patternName: 'Chain-of-Thought',
      category: 'reasoning',
      description: 'Step-by-step reasoning process',
      examples: [],
      paper: { id: 'paper-2', title: 'Mock Paper 2', authors: [] },
      tags: ['reasoning', 'steps'],
      searchableContent: 'chain of thought reasoning'
    }
  ];

  // Perform comparison when patterns change
  useEffect(() => {
    const performComparison = async () => {
      if (selectedPatterns.length < 2) {
        setComparison(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await comparePatterns(selectedPatterns);
        setComparison(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to compare patterns');
        setComparison(null);
      } finally {
        setIsLoading(false);
      }
    };

    performComparison();
  }, [selectedPatterns]);

  const handleExportData = () => {
    if (!comparison) return;

    const exportData = {
      timestamp: new Date().toISOString(),
      patterns: comparison.patterns,
      similarityMatrix: comparison.similarityMatrix,
      statistics: comparison.statistics,
      metadata: {
        totalPatterns: comparison.patterns.length,
        comparisonCount: comparison.patterns.length * (comparison.patterns.length - 1) / 2,
        exportedBy: 'PromptPattern Dictionary'
      }
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pattern-comparison-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!comparison) return;

    const csvRows = ['Pattern 1,Pattern 2,Similarity Score'];
    
    for (let i = 0; i < comparison.patterns.length; i++) {
      for (let j = i + 1; j < comparison.patterns.length; j++) {
        const pattern1 = comparison.patterns[i];
        const pattern2 = comparison.patterns[j];
        const similarity = comparison.similarityMatrix[i][j];
        csvRows.push(`"${pattern1}","${pattern2}",${similarity}`);
      }
    }

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pattern-similarities-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCellClick = (patternIds: [string, string], similarity: number) => {
    console.log('Cell clicked:', patternIds, similarity);
    // In a real implementation, this could open a detailed comparison view
  };

  const handleNodeClick = (patternId: string) => {
    console.log('Node clicked:', patternId);
    // In a real implementation, this could highlight the pattern or show details
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Pattern Comparison Dashboard
        </h2>
        <p className="text-gray-600">
          Select 2-10 patterns to analyze their similarities and relationships using semantic embeddings.
        </p>
      </div>

      {/* Pattern Selection */}
      <PatternSelector
        patterns={mockPatterns}
        selectedPatterns={selectedPatterns}
        onSelectionChange={setSelectedPatterns}
        maxSelections={10}
      />

      {/* Results Section */}
      {selectedPatterns.length >= 2 && (
        <div className="space-y-6">
          {/* Controls */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Comparison Results
                </h3>
                
                {/* View Toggle */}
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setActiveView('matrix')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      activeView === 'matrix'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    aria-label="Show similarity matrix view"
                  >
                    Matrix View
                  </button>
                  <button
                    onClick={() => setActiveView('network')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      activeView === 'network'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    aria-label="Show network graph view"
                  >
                    Network View
                  </button>
                </div>
              </div>

              {/* Export Controls */}
              {comparison && (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleExportCSV}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                    aria-label="Export similarity data as CSV"
                  >
                    Export CSV
                  </button>
                  <button
                    onClick={handleExportData}
                    className="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
                    aria-label="Export comparison data as JSON"
                  >
                    Export JSON
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="bg-white rounded-lg shadow-md p-12">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Computing similarities...</span>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Comparison Failed
                  </h3>
                  <p className="text-sm text-red-700 mt-1">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Visualization */}
          {comparison && !isLoading && (
            <div>
              {activeView === 'matrix' ? (
                <SimilarityMatrix
                  comparison={comparison}
                  onCellClick={handleCellClick}
                />
              ) : (
                <SimilarityNetwork
                  comparison={comparison}
                  onNodeClick={handleNodeClick}
                  threshold={0.3}
                />
              )}
            </div>
          )}

          {/* Summary Statistics */}
          {comparison && !isLoading && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                Analysis Summary
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {comparison.patterns.length}
                  </div>
                  <div className="text-sm text-gray-600">Patterns Compared</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-700">
                    {(comparison.statistics.averageSimilarity * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Average Similarity</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {(comparison.statistics.maxSimilarity * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Highest Similarity</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {(comparison.statistics.minSimilarity * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Lowest Similarity</div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>Interpretation:</strong> Higher similarity scores indicate patterns that share similar 
                  semantic content and purpose. Scores above 80% suggest very similar patterns that might be 
                  variants or specializations of each other. Scores below 30% indicate distinct patterns 
                  serving different purposes.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {selectedPatterns.length === 0 && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <div className="max-w-md mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Start by selecting patterns
            </h3>
            <p className="mt-2 text-gray-600">
              Choose at least 2 patterns from the selector above to begin comparing their similarities.
            </p>
          </div>
        </div>
      )}

      {/* Single Selection State */}
      {selectedPatterns.length === 1 && (
        <div className="bg-blue-50 rounded-lg p-8 text-center">
          <div className="max-w-md mx-auto">
            <svg className="mx-auto h-12 w-12 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-blue-900">
              Select one more pattern
            </h3>
            <p className="mt-2 text-blue-700">
              You need at least 2 patterns to perform similarity analysis. 
              Add one more pattern to get started.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
