'use client';

import React, { useState } from 'react';

interface CopyButtonProps {
  text: string;
  liveRegionId?: string;
  className?: string;
  ariaLabel?: string;
  children?: React.ReactNode;
}

export default function CopyButton({ text, liveRegionId, className, ariaLabel, children }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') return;
    
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      
      // Update external live region if provided and exists
      if (liveRegionId) {
        const liveRegion = document.getElementById(liveRegionId);
        if (liveRegion) {
           liveRegion.textContent = 'Copied snippet to clipboard';
           setTimeout(() => {
               if (liveRegion) liveRegion.textContent = '';
           }, 3000);
        }
      }

      // Reset internal state
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <button
      type="button"
      aria-label={ariaLabel || "Copy snippet"}
      className={className}
      onClick={handleCopy}
    >
      {children || (copied ? 'Copied!' : 'Copy')}
    </button>
  );
}
