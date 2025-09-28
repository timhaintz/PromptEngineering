/**
 * Semantic Analysis Page
 * 
 * Displays the dual categorization matrix and analysis tools
 */

import { Suspense } from 'react';
import fs from 'fs';
import path from 'path';
import SemanticCategoryMatrix from '@/components/semantic/SemanticCategoryMatrix';
import { EnhancedPattern } from '@/types/patterns';
import PageShell from '@/components/layout/PageShell';

async function getPatternsData(): Promise<EnhancedPattern[]> {
  const filePath = path.join(process.cwd(), 'public', 'data', 'patterns.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

export default async function SemanticAnalysisPage() {
  const patterns = await getPatternsData();
  
  return (
    <PageShell>
      <div className="space-y-12">
        {/* Header */}
  <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Semantic Category Analysis
          </h1>
          <p className="text-lg text-gray-600 max-w-4xl">
            Explore how patterns are categorized using AI-powered semantic similarity analysis. 
            This dual categorization system reveals both original paper categories and semantically-derived universal categories, 
            providing insights into pattern relationships and example variations.
          </p>
        </div>

        {/* Key Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="surface-card p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Dual Categorization
            </h3>
            <p className="text-gray-600 text-sm">
              Compare original paper categories with AI-derived semantic categories to discover new pattern relationships.
            </p>
          </div>
          
          <div className="surface-card p-6">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Example Analysis
            </h3>
            <p className="text-gray-600 text-sm">
              Explore how individual examples within patterns may represent different semantic concepts than their parent pattern.
            </p>
          </div>
          
          <div className="surface-card p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Confidence Scoring
            </h3>
            <p className="text-gray-600 text-sm">
              Filter and analyze patterns based on semantic similarity confidence scores to ensure quality insights.
            </p>
          </div>
        </div>

        {/* Semantic Matrix Component */}
        <Suspense fallback={
          <div className="surface-card p-8">
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading semantic analysis...</span>
            </div>
          </div>
        }>
          <SemanticCategoryMatrix patterns={patterns} />
        </Suspense>

        {/* Usage Guide */}
  <div className="surface-card p-6 mt-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">How to Use This Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">🔍 Discover Patterns</h3>
              <ul className="text-sm text-gray-600 space-y-1 mb-4">
                <li>• Use the transition matrix to see how categories evolved</li>
                <li>• Filter by confidence to find high-quality categorizations</li>
                <li>• Look for patterns where examples differ from their parent pattern</li>
              </ul>
              
              <h3 className="text-lg font-medium text-gray-900 mb-2">📊 Understand Changes</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• High category changes indicate semantic improvements</li>
                <li>• Example mismatches reveal nuanced pattern variations</li>
                <li>• Confidence scores help validate categorization quality</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">🎯 Filter Effectively</h3>
              <ul className="text-sm text-gray-600 space-y-1 mb-4">
                <li>• Combine original and semantic category filters</li>
                <li>• Adjust confidence threshold for precision</li>
                <li>• Enable &quot;Show only changes&quot; for migration analysis</li>
              </ul>
              
              <h3 className="text-lg font-medium text-gray-900 mb-2">🔬 Research Applications</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Validate pattern taxonomy decisions</li>
                <li>• Discover cross-domain pattern relationships</li>
                <li>• Identify patterns for specific use cases</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
