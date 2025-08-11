/**
 * Pattern Selector Component
 * 
 * Allows users to select 2-10 patterns for comparison from search results
 * or category browsing. Provides checkbox-based selection with validation.
 */

'use client';

import { useState, useEffect } from 'react';
import type { ProcessedPattern } from '@/lib/types/pattern';

interface PatternSelectorProps {
  patterns: ProcessedPattern[];
  selectedPatterns: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  maxSelections?: number;
  minSelections?: number;
}

export default function PatternSelector({
  patterns,
  selectedPatterns,
  onSelectionChange,
  maxSelections = 10,
  minSelections = 2
}: PatternSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPatterns, setFilteredPatterns] = useState(patterns);

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredPatterns(patterns);
    } else {
      const filtered = patterns.filter(pattern =>
        pattern.patternName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pattern.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pattern.paper.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPatterns(filtered);
    }
  }, [searchTerm, patterns]);

  const handlePatternToggle = (patternId: string) => {
    const isSelected = selectedPatterns.includes(patternId);
    let newSelection: string[];

    if (isSelected) {
      // Remove pattern
      newSelection = selectedPatterns.filter(id => id !== patternId);
    } else {
      // Add pattern if within limits
      if (selectedPatterns.length >= maxSelections) {
        return; // Don't add if at max
      }
      newSelection = [...selectedPatterns, patternId];
    }

    onSelectionChange(newSelection);
  };

  const canCompare = selectedPatterns.length >= minSelections;
  const reachedMax = selectedPatterns.length >= maxSelections;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">
          Select Patterns to Compare
        </h3>
        <div className="text-sm text-gray-600">
          {selectedPatterns.length} of {maxSelections} selected
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search patterns, categories, or papers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <svg
          className="absolute right-3 top-2.5 h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Selection Status */}
      {selectedPatterns.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg
                className="h-5 w-5 text-blue-500 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-blue-800 font-medium">
                {selectedPatterns.length} patterns selected
              </span>
            </div>
            {canCompare && (
              <span className="text-green-600 text-sm font-medium">
                Ready to compare!
              </span>
            )}
          </div>
          {!canCompare && (
            <p className="text-blue-600 text-sm mt-1">
              Select at least {minSelections} patterns to enable comparison
            </p>
          )}
        </div>
      )}

      {/* Pattern List */}
      <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
        {filteredPatterns.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"
              />
            </svg>
            <p>No patterns found matching your search</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredPatterns.map((pattern) => {
              const isSelected = selectedPatterns.includes(pattern.id);
              const isDisabled = !isSelected && reachedMax;

              return (
                <div
                  key={pattern.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${
                    isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={() => !isDisabled && handlePatternToggle(pattern.id)}
                >
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => !isDisabled && handlePatternToggle(pattern.id)}
                      disabled={isDisabled}
                      aria-label={`Select ${pattern.patternName} for comparison`}
                      className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {pattern.patternName}
                          </h4>
                          {/* Pattern ID badge */}
                          <span className="shrink-0 text-[10px] font-medium bg-gray-100 text-gray-800 px-2 py-0.5 rounded border border-gray-200">
                            ID: {pattern.id}
                          </span>
                        </div>
                        <span className="text-xs text-gray-500 ml-2">
                          {pattern.examples.length} examples
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {pattern.category}
                      </p>
                      <p className="text-xs text-gray-500 mt-1 truncate">
                        {pattern.paper.title} • {pattern.paper.authors.join(', ')}
                      </p>
                      {pattern.description && (
                        <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                          {pattern.description}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selection Summary */}
      {selectedPatterns.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Selected Patterns:
          </h4>
          <div className="flex flex-wrap gap-2">
            {selectedPatterns.map((patternId) => {
              const pattern = patterns.find(p => p.id === patternId);
              if (!pattern) return null;

              return (
                <span
                  key={patternId}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {pattern.patternName}
                  <span className="ml-2 text-[10px] font-medium bg-white/70 text-blue-800 px-2 py-0.5 rounded border border-blue-200">
                    ID: {pattern.id}
                  </span>
                  <button
                    onClick={() => handlePatternToggle(patternId)}
                    aria-label={`Remove ${pattern.patternName} from selection`}
                    className="ml-2 inline-flex items-center justify-center w-4 h-4 text-blue-400 hover:text-blue-600"
                  >
                    <svg
                      className="w-3 h-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
