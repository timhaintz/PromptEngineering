/**
 * Search Interface Component
 * 
 * Main search functionality for the homepage
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface SearchInterfaceProps {
  className?: string;
}

export default function SearchInterface({ className = '' }: SearchInterfaceProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const router = useRouter();

  const handleSearch = () => {
    if (searchTerm.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleQuickSearch = (term: string) => {
    setSearchTerm(term);
    router.push(`/search?q=${encodeURIComponent(term)}`);
  };

  return (
    <div className={`max-w-4xl mx-auto mb-16 ${className}`}>
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Search Prompt Patterns
        </h2>
        
        {/* Search Bar */}
        <div className="relative mb-6">
          <input
            type="text"
            placeholder="Search for patterns, categories, or techniques..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full px-6 py-4 text-lg text-gray-900 placeholder-gray-500 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
          <button 
            onClick={handleSearch}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
        
        {/* Quick Search Suggestions */}
        <div className="text-center">
          <p className="text-gray-600 mb-4">Popular searches:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {['jailbreak', 'persona', 'template', 'security', 'output customization', 'fact check'].map((term) => (
              <button
                key={term}
                onClick={() => handleQuickSearch(term)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors text-sm"
              >
                {term}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
