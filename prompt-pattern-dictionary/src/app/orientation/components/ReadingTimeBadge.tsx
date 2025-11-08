import React from 'react';
import { readingTimeFromWords } from '../utils/readingTime';

interface ReadingTimeBadgeProps { words?: number; className?: string; }

export function ReadingTimeBadge({ words = 0, className = '' }: ReadingTimeBadgeProps) {
  const time = readingTimeFromWords(words);
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-surface-2 text-secondary border border-muted select-none ${className}`}
      aria-label={`Estimated reading time: ${time}`}
    >
      <svg aria-hidden="true" width="12" height="12" viewBox="0 0 24 24" className="opacity-70"><path fill="currentColor" d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm1 11a1 1 0 0 1-2 0V7a1 1 0 0 1 2 0v4h3a1 1 0 0 1 0 2Z"/></svg>
      {time}
    </span>
  );
}
