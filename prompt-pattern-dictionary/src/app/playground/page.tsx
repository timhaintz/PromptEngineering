/**
 * Similarity Playground Page
 * 
 * Interactive page for real-time pattern discovery using natural language
 * input and semantic similarity matching.
 */

import { SimilarityPlayground } from '@/components/comparison';
import { Metadata } from 'next';
import Link from 'next/link';
import PageShell from '@/components/layout/PageShell';

export const metadata: Metadata = {
  title: 'Similarity Playground - Prompt Pattern Dictionary',
  description: 'Find relevant prompt patterns by describing your task in natural language using semantic search.',
};

export default function PlaygroundPage() {
  return (
    <PageShell variant="wide" noContainer>
      {/* Header */}
      <div className="surface-card border-b rounded-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Similarity Playground
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Discover relevant patterns by describing your prompt goals
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/comparison"
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Pattern Comparison
              </a>
              <Link
                href="/"
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Dictionary
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SimilarityPlayground />
      </div>

      {/* Usage Tips */}
      <div className="mt-16 surface-card border-t rounded-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center bg-blue-100 rounded-lg mb-4">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Describe Your Task</h3>
              <p className="text-gray-600 text-sm">
                Enter a natural description of what you want to accomplish with your prompt
              </p>
            </div>
            
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center bg-green-100 rounded-lg mb-4">
                <svg className="h-6 w-6 text-green-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Get Matched Patterns</h3>
              <p className="text-gray-600 text-sm">
                Receive ranked results based on semantic similarity to your description
              </p>
            </div>
            
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center bg-purple-100 rounded-lg mb-4">
                <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Explore & Compare</h3>
              <p className="text-gray-600 text-sm">
                Dive deeper into patterns and compare multiple approaches
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
