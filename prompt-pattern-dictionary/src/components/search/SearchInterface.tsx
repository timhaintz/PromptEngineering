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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    }
  };

  const handleQuickSearch = (term: string) => {
    setSearchTerm(term);
    router.push(`/search?q=${encodeURIComponent(term)}`);
  };

  return (
    <section aria-label="Search prompt patterns" className={`max-w-4xl mx-auto mb-16 ${className}`}>
      <div className="bg-surface-1 rounded-xl shadow-lg p-8 border border-muted">
        <h2 className="text-2xl font-semibold text-primary mb-6 text-center">
          Search Prompt Patterns
        </h2>

        {/* Search Bar */}
        <form
          role="search"
          aria-label="Prompt pattern search"
          onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
          className="relative mb-6"
        >
          <label htmlFor="pattern-search" className="sr-only">Search prompt patterns</label>
          <input
            id="pattern-search"
            type="text"
            placeholder="Search for patterns, categories, or techniques..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full px-6 py-4 text-lg bg-surface-2 text-primary placeholder:text-tertiary border border-muted rounded-lg focus-ring outline-none"
            aria-describedby="search-hint"
            autoComplete="off"
          />
          <button
            type="submit"
            onClick={handleSearch}
            className="absolute right-3 top-1/2 -translate-y-1/2 bg-blue-800 text-white px-6 py-2 rounded-lg hover:bg-blue-700 focus-ring transition-colors"
          >
            Search
          </button>
        </form>

        {/* Quick Search Suggestions */}
        <div className="text-center" aria-labelledby="popular-searches-heading">
          <p id="popular-searches-heading" className="text-secondary mb-4">Popular searches:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {['jailbreak', 'persona', 'template', 'security', 'output customization', 'fact check'].map((term) => (
              <button
                key={term}
                type="button"
                onClick={() => handleQuickSearch(term)}
                className="px-4 py-2 bg-surface-2 text-secondary border border-muted rounded-full hover:bg-surface-hover hover:text-primary focus-ring transition-colors text-sm"
              >
                {term}
              </button>
            ))}
          </div>
          <p id="search-hint" className="mt-4 text-xs text-tertiary">Press Enter or select a suggestion to run the search.</p>
        </div>
      </div>
    </section>
  );
}
