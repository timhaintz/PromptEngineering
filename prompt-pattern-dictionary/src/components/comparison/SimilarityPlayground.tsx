/**
 * Similarity Playground Component
 * 
 * Interactive interface for users to input prompts and find the most
 * similar patterns in real-time using semantic embeddings.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { findSimilarPatternsFromText } from '@/lib/similarity';
import type { SimilaritySearchResult } from '@/lib/types/pattern';

interface SimilarityPlaygroundProps {
  className?: string;
}

export default function SimilarityPlayground({ className = '' }: SimilarityPlaygroundProps) {
  const [userPrompt, setUserPrompt] = useState('');
  const [searchResults, setSearchResults] = useState<SimilaritySearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threshold, setThreshold] = useState(0.5);
  const [maxResults, setMaxResults] = useState(10);

  // Debounced search function
  const debouncedSearch = useCallback(
    async (prompt: string) => {
      if (!prompt.trim() || prompt.length < 10) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      setError(null);

      try {
        const results = await findSimilarPatternsFromText(prompt, {
          threshold,
          maxResults,
          includeExcerpts: true
        });
        setSearchResults(results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed');
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    },
    [threshold, maxResults]
  );

  // Debounce the search with useEffect
  useEffect(() => {
    const timer = setTimeout(() => {
      debouncedSearch(userPrompt);
    }, 500);

    return () => clearTimeout(timer);
  }, [userPrompt, debouncedSearch]);

  const getConfidenceColor = (confidence: 'high' | 'medium' | 'low') => {
    switch (confidence) {
  case 'high': return 'text-green-700 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSimilarityBarWidthClass = (similarity: number) => {
    const pct = Math.max(5, Math.min(100, Math.round(similarity * 100)));
    // Map to Tailwind width buckets using supported fractions or arbitrary percentage values
    if (pct >= 95) return 'w-[95%]';
    if (pct >= 90) return 'w-[90%]';
    if (pct >= 80) return 'w-4/5';
    if (pct >= 70) return 'w-[70%]';
    if (pct >= 66) return 'w-2/3';
    if (pct >= 60) return 'w-3/5';
    if (pct >= 50) return 'w-1/2';
    if (pct >= 40) return 'w-2/5';
    if (pct >= 33) return 'w-1/3';
    if (pct >= 25) return 'w-1/4';
    if (pct >= 20) return 'w-1/5';
    if (pct >= 10) return 'w-[10%]';
    return 'w-[5%]';
  };

  const handleExamplePrompt = (example: string) => {
    setUserPrompt(example);
  };

  const examplePrompts = [
    "Write a creative story about a robot learning to paint",
    "Explain quantum computing in simple terms for a 10-year-old",
    "Analyze the pros and cons of remote work",
    "Generate a marketing strategy for a sustainable fashion brand",
    "Debug this Python code that's giving me syntax errors"
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Similarity Playground
        </h2>
        <p className="text-gray-600">
          Enter your prompt to find the most similar patterns in our database using semantic search.
          This helps you discover relevant prompt engineering techniques for your use case.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="space-y-4">
          {/* Prompt Input */}
          <div>
            <label htmlFor="user-prompt" className="block text-sm font-medium text-gray-700 mb-2">
              Your Prompt or Task Description
            </label>
            <textarea
              id="user-prompt"
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="Describe what you want to accomplish with your prompt... (minimum 10 characters)"
              className="w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={4}
              aria-label="Enter your prompt or task description"
            />
            <div className="mt-1 text-sm text-gray-500">
              {userPrompt.length} characters {userPrompt.length < 10 && '(minimum 10 required)'}
            </div>
          </div>

          {/* Search Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="similarity-threshold" className="block text-sm font-medium text-gray-700 mb-1">
                Similarity Threshold: {(threshold * 100).toFixed(0)}%
              </label>
              <input
                id="similarity-threshold"
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full"
                aria-label="Similarity threshold percentage"
              />
              <div className="text-xs text-gray-500 mt-1">
                Higher values = more similar patterns only
              </div>
            </div>

            <div>
              <label htmlFor="max-results" className="block text-sm font-medium text-gray-700 mb-1">
                Max Results: {maxResults}
              </label>
              <input
                id="max-results"
                type="range"
                min="5"
                max="50"
                step="5"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="w-full"
                aria-label="Maximum number of results"
              />
              <div className="text-xs text-gray-500 mt-1">
                Number of patterns to return
              </div>
            </div>
          </div>
        </div>

        {/* Example Prompts */}
        <div className="mt-6 border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Try These Examples:</h4>
          <div className="flex flex-wrap gap-2">
            {examplePrompts.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExamplePrompt(example)}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                aria-label={`Use example prompt: ${example}`}
              >
                {example.slice(0, 40)}...
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Similar Patterns
            </h3>
            {isSearching && (
              <div className="flex items-center text-sm text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Searching...
              </div>
            )}
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {/* Error State */}
          {error && (
            <div className="p-6 bg-red-50">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* No Results */}
          {!isSearching && !error && userPrompt.length >= 10 && searchResults.length === 0 && (
            <div className="p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">No similar patterns found</h3>
              <p className="mt-2 text-gray-600">
                Try lowering the similarity threshold or using different keywords.
              </p>
            </div>
          )}

          {/* Empty State */}
          {userPrompt.length < 10 && !isSearching && (
            <div className="p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Start typing to search</h3>
              <p className="mt-2 text-gray-600">
                Enter at least 10 characters to find similar prompt patterns.
              </p>
            </div>
          )}

          {/* Results List */}
          {searchResults.map((result, index) => (
            <div key={result.patternId} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center flex-wrap gap-2 mb-2">
                    <h4 className="text-lg font-medium text-gray-900">
                      {result.patternName}
                    </h4>
                    {/* Pattern ID badge */}
                    <span className="inline-flex items-center rounded bg-gray-100 text-gray-800 px-2 py-0.5 text-[10px] font-semibold border border-gray-200">
                      ID: {result.patternId}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(result.confidence)}`}>
                      {result.confidence} confidence
                    </span>
                    <span className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
                      {result.category}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-3">
                    {result.excerpt}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      From: {result.sourceTitle}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-700">
                        {(result.similarity * 100).toFixed(1)}% similar
                      </span>
                    </div>
                  </div>

                  {/* Similarity Bar */}
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`bg-blue-600 h-2 rounded-full transition-all duration-300 ${getSimilarityBarWidthClass(result.similarity)}`}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="ml-6 flex-shrink-0">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">
                      #{index + 1}
                    </div>
                    <div className="text-xs text-gray-500">
                      Rank
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Results Summary */}
        {searchResults.length > 0 && (
          <div className="p-4 bg-gray-50 border-t">
            <div className="text-sm text-gray-600 text-center">
              Found {searchResults.length} similar pattern{searchResults.length !== 1 ? 's' : ''} 
              {' '}above {(threshold * 100).toFixed(0)}% similarity threshold
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
