"use client";
import React, { createContext, useContext, useEffect, useCallback, useState, ReactNode } from 'react';

export type ThemeMode = "light" | "dark" | "high-contrast" | "system";
interface ThemeContextValue {
  mode: ThemeMode;               // chosen mode (may be 'system')
  effective: Exclude<ThemeMode,'system'>; // applied theme
  setMode: (m: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);
const STORAGE_KEY = 'pe-theme';
const STORAGE_KEY_EFFECTIVE = 'pe-theme-effective';

function getSystemPref(): Exclude<ThemeMode,'high-contrast' | 'system'> {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>('system');
  const [effective, setEffective] = useState<Exclude<ThemeMode,'system'>>('light');

  const resolveEffective = useCallback((m: ThemeMode) => {
    if (m === 'system') return getSystemPref();
    if (m === 'high-contrast') return 'high-contrast';
    return m; // light | dark
  }, []);

  const apply = useCallback((m: ThemeMode) => {
    const eff = resolveEffective(m);
    setEffective(eff);
    try { localStorage.setItem(STORAGE_KEY_EFFECTIVE, eff); } catch {}
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', eff);
      document.documentElement.setAttribute('data-theme-mode', m);
    }
  }, [resolveEffective]);

  const setMode = useCallback((m: ThemeMode) => {
    setModeState(m);
    try { localStorage.setItem(STORAGE_KEY, m); } catch {}
    apply(m);
    // Broadcast to other tabs & listeners
    try { window.dispatchEvent(new CustomEvent('pe-theme-change', { detail: { mode: m } })); } catch {}
  }, [apply]);

  // Init
  useEffect(() => {
    let stored: ThemeMode | null = null;
    try { stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null; } catch {}
    const initial = stored || 'system';
    setModeState(initial);
    apply(initial);

    // System preference listener
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      setEffective(prev => {
        if (initial === 'system' || mode === 'system') {
          const eff2 = resolveEffective('system');
            if (typeof document !== 'undefined') {
              document.documentElement.setAttribute('data-theme', eff2);
            }
          return eff2;
        }
        return prev;
      });
    };
    mql.addEventListener('change', onChange);

    // Cross-tab storage sync
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        const incoming = e.newValue as ThemeMode;
        setModeState(incoming);
        apply(incoming);
      }
    };
    window.addEventListener('storage', onStorage);

    // Custom event (intra-tab) listeners from other code
    const onCustom = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail && detail.mode) {
        setModeState(detail.mode as ThemeMode);
        apply(detail.mode as ThemeMode);
      }
    };
    window.addEventListener('pe-theme-change', onCustom as EventListener);

    return () => {
      mql.removeEventListener('change', onChange);
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('pe-theme-change', onCustom as EventListener);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value: ThemeContextValue = { mode, effective, setMode };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useThemeContext() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useThemeContext must be used within ThemeProvider');
  return ctx;
}
