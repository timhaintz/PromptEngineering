"use client";
import React from 'react';
import { usePreferences } from '../hooks/usePreferences';

export default function ReadabilityControls() {
  const { fontScale, increaseFont, decreaseFont, canIncrease, canDecrease, widthMode, toggleWidth, theme, setTheme } = usePreferences();
  return (
    <div className="flex items-center gap-2 text-xs border rounded px-2 py-1 bg-white shadow-sm sticky top-4 z-20" aria-label="Readability controls">
      <div className="flex items-center gap-1" role="group" aria-label="Font size">
        <button
          type="button"
          className="px-2 py-1 rounded border bg-gray-50 hover:bg-gray-100 disabled:opacity-40"
          onClick={decreaseFont}
          disabled={!canDecrease}
        >A−</button>
        <span aria-live="polite" className="px-1 select-none">{fontScale === 0 ? 'Base' : fontScale > 0 ? `+${fontScale}` : `${fontScale}`}</span>
        <button
          type="button"
          className="px-2 py-1 rounded border bg-gray-50 hover:bg-gray-100 disabled:opacity-40"
          onClick={increaseFont}
          disabled={!canIncrease}
        >A+</button>
      </div>
      <div className="h-4 w-px bg-gray-300" />
      <button
        type="button"
        onClick={toggleWidth}
        className="px-2 py-1 rounded border bg-gray-50 hover:bg-gray-100"
        aria-pressed={widthMode === 'relaxed' ? 'true' : 'false'}
      >{widthMode === 'relaxed' ? 'Narrow Width' : 'Relax Width'}</button>
      <div className="h-4 w-px bg-gray-300" />
      <label className="sr-only" htmlFor="theme-select">Theme</label>
      <select
        id="theme-select"
        className="px-1 py-1 border rounded bg-gray-50 text-xs"
        value={theme}
        onChange={e => setTheme(e.target.value as any)}
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="hc">High Contrast</option>
      </select>
    </div>
  );
}
