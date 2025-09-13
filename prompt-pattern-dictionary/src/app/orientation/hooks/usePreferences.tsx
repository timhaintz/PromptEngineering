"use client";
import { useCallback, useEffect, useState } from 'react';

interface PrefState {
  fontScale: number; // -1,0,1,2
  widthMode: 'default' | 'relaxed';
  theme: 'light' | 'dark' | 'hc' | 'system';
}

const KEY = 'orientation:readability:v1';

function load(): PrefState {
  if (typeof window === 'undefined') return { fontScale: 0, widthMode: 'default', theme: 'system' };
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { fontScale: 0, widthMode: 'default', theme: 'system' };
    const parsed = JSON.parse(raw) as PrefState;
    return { fontScale: Math.min(2, Math.max(-1, parsed.fontScale)), widthMode: parsed.widthMode === 'relaxed' ? 'relaxed' : 'default', theme: ['light','dark','hc','system'].includes(parsed.theme) ? parsed.theme : 'system' };
  } catch {
    return { fontScale: 0, widthMode: 'default', theme: 'system' };
  }
}

export function usePreferences() {
  const [state, setState] = useState<PrefState>(() => load());

  useEffect(() => {
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.dataset.fontScale = String(state.fontScale);
      root.dataset.widthMode = state.widthMode;
      // Theme resolution: system -> relies on prefers-color-scheme, so remove explicit data-theme
      if (state.theme === 'system') {
        root.removeAttribute('data-theme');
      } else {
        root.setAttribute('data-theme', state.theme);
      }
    }
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(KEY, JSON.stringify(state));
    }
  }, [state]);

  const increaseFont = useCallback(() => setState(s => s.fontScale >= 2 ? s : { ...s, fontScale: s.fontScale + 1 }), []);
  const decreaseFont = useCallback(() => setState(s => s.fontScale <= -1 ? s : { ...s, fontScale: s.fontScale - 1 }), []);
  const toggleWidth = useCallback(() => setState(s => ({ ...s, widthMode: s.widthMode === 'default' ? 'relaxed' : 'default' })), []);
  const setTheme = useCallback((theme: PrefState['theme']) => setState(s => ({ ...s, theme })), []);

  return {
    fontScale: state.fontScale,
    increaseFont,
    decreaseFont,
    canIncrease: state.fontScale < 2,
    canDecrease: state.fontScale > -1,
    widthMode: state.widthMode,
    toggleWidth,
    theme: state.theme,
    setTheme,
  };
}
