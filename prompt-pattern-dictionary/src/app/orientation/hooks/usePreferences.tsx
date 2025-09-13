"use client";
import { useCallback, useEffect, useState } from 'react';

interface PrefState {
  fontScale: number; // -1,0,1,2
  widthMode: 'default' | 'relaxed';
}

const KEY = 'orientation:readability:v1';

function load(): PrefState {
  if (typeof window === 'undefined') return { fontScale: 0, widthMode: 'default' };
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { fontScale: 0, widthMode: 'default' };
    const parsed = JSON.parse(raw) as PrefState;
    return { fontScale: Math.min(2, Math.max(-1, parsed.fontScale)), widthMode: parsed.widthMode === 'relaxed' ? 'relaxed' : 'default' };
  } catch {
    return { fontScale: 0, widthMode: 'default' };
  }
}

export function usePreferences() {
  const [state, setState] = useState<PrefState>(() => load());

  useEffect(() => {
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.dataset.fontScale = String(state.fontScale);
      root.dataset.widthMode = state.widthMode;
    }
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(KEY, JSON.stringify(state));
    }
  }, [state]);

  const increaseFont = useCallback(() => setState(s => s.fontScale >= 2 ? s : { ...s, fontScale: s.fontScale + 1 }), []);
  const decreaseFont = useCallback(() => setState(s => s.fontScale <= -1 ? s : { ...s, fontScale: s.fontScale - 1 }), []);
  const toggleWidth = useCallback(() => setState(s => ({ ...s, widthMode: s.widthMode === 'default' ? 'relaxed' : 'default' })), []);

  return {
    fontScale: state.fontScale,
    increaseFont,
    decreaseFont,
    canIncrease: state.fontScale < 2,
    canDecrease: state.fontScale > -1,
    widthMode: state.widthMode,
    toggleWidth,
  };
}
