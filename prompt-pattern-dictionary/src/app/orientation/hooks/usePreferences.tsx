"use client";
import { useCallback, useEffect, useState } from 'react';

interface PrefState {
  fontScale: number; // -1,0,1,2
  widthMode: 'default' | 'relaxed';
  theme: 'light' | 'dark' | 'high-contrast' | 'system';
}

const KEY = 'orientation:readability:v1';

function load(): PrefState {
  if (typeof window === 'undefined') return { fontScale: 0, widthMode: 'default', theme: 'system' };
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { fontScale: 0, widthMode: 'default', theme: 'system' };
  const parsed: Partial<PrefState> & { theme?: string } = JSON.parse(raw);
    // Backward compatibility: migrate legacy 'hc' to 'high-contrast'
    let tempTheme: string | undefined = parsed.theme;
    if (tempTheme === 'hc') tempTheme = 'high-contrast';
    const allowed = new Set(['light','dark','high-contrast','system']);
    const theme: PrefState['theme'] = allowed.has(tempTheme || '') ? (tempTheme as PrefState['theme']) : 'system';
    return {
      fontScale: Math.min(2, Math.max(-1, parsed.fontScale ?? 0)),
      widthMode: parsed.widthMode === 'relaxed' ? 'relaxed' : 'default',
      theme
    };
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
