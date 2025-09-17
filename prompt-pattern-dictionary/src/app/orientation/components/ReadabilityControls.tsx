"use client";
import React from 'react';
import { usePreferences } from '../hooks/usePreferences';

export default function ReadabilityControls() {
  const { fontScale, increaseFont, decreaseFont, canIncrease, canDecrease, widthMode, toggleWidth, theme, setTheme } = usePreferences();
  return (
    <div className="flex items-center gap-2 text-xs border border-muted rounded px-2 py-1 bg-surface-1 shadow-sm sticky top-4 z-20 text-secondary" aria-label="Readability controls">
      <div className="flex items-center gap-1" role="group" aria-label="Font size">
        <button
          type="button"
          className="px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover disabled:opacity-40 text-primary"
          onClick={decreaseFont}
          disabled={!canDecrease}
        >A−</button>
        <span aria-live="polite" className="px-1 select-none">{fontScale === 0 ? 'Base' : fontScale > 0 ? `+${fontScale}` : `${fontScale}`}</span>
        <button
          type="button"
          className="px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover disabled:opacity-40 text-primary"
          onClick={increaseFont}
          disabled={!canIncrease}
        >A+</button>
      </div>
      <div className="h-4 w-px bg-surface-2" />
      <button
        type="button"
        onClick={toggleWidth}
        className="px-2 py-1 rounded border border-muted bg-surface-2 hover:bg-surface-hover text-primary"
        data-state={widthMode}
        aria-label={widthMode === 'relaxed' ? 'Switch to narrow width' : 'Relax content width'}
      >{widthMode === 'relaxed' ? 'Narrow Width' : 'Relax Width'}</button>
      <div className="h-4 w-px bg-surface-2" />
      <label className="sr-only" htmlFor="theme-select">Theme</label>
      <select
        id="theme-select"
        className="px-1 py-1 border border-muted rounded bg-surface-2 text-xs text-primary hover:bg-surface-hover"
        value={theme}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
          const val = e.target.value;
          if (val === 'system' || val === 'light' || val === 'dark' || val === 'high-contrast') {
            setTheme(val);
          }
        }}
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="high-contrast">High Contrast</option>
      </select>
    </div>
  );
}
