"use client";
import React, { createContext, useContext, useEffect, useCallback, useState, ReactNode, useRef } from 'react';

export type ThemeChoice = "light" | "dark" | "high-contrast" | "system";
export type ResolvedTheme = "light" | "dark" | "high-contrast";

interface ThemeContextValue {
  theme: ThemeChoice;          // user choice (may be 'system')
  resolvedTheme: ResolvedTheme;// applied theme after resolving 'system'
  setTheme: (m: ThemeChoice) => void;
  toggleDark: () => void;      // convenience: cycle light/dark when not high-contrast
  isSystem: boolean;           // theme === 'system'
  highContrastAuto: boolean;   // true if high contrast came from system while in 'system'
  ready: boolean;              // hydration complete
}

const ThemeContext = createContext<ThemeContextValue | null>(null);
const STORAGE_KEY = 'pe-theme';

// Detect forced-colors (Windows High Contrast) if supported
function systemForcedColors(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return false;
  try { return window.matchMedia('(forced-colors: active)').matches; } catch { return false; }
}

function getSystemPrefBase(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function resolveTheme(choice: ThemeChoice, allowSystemHighContrast: boolean): ResolvedTheme {
  if (choice === 'high-contrast') return 'high-contrast';
  if (choice === 'system') {
    if (allowSystemHighContrast && systemForcedColors()) return 'high-contrast';
    return getSystemPrefBase();
  }
  return choice; // light or dark
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeChoice] = useState<ThemeChoice>('system');
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('light');
  const [highContrastAuto, setHighContrastAuto] = useState(false);
  const [ready, setReady] = useState(false);
  const allowSystemHighContrast = true; // default chosen path
  const mountedRef = useRef(false);

  const apply = useCallback((choice: ThemeChoice) => {
    const eff = resolveTheme(choice, allowSystemHighContrast);
    setResolvedTheme(eff);
    const autoHC = choice === 'system' && eff === 'high-contrast' && systemForcedColors();
    setHighContrastAuto(autoHC);
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', eff);
      document.documentElement.setAttribute('data-theme-mode', choice);
      document.documentElement.setAttribute('data-theme-resolved', eff);
      document.documentElement.setAttribute('data-theme-ready', 'true');
    }
  }, [allowSystemHighContrast]);

  const setTheme = useCallback((next: ThemeChoice) => {
    setThemeChoice(next);
    try { localStorage.setItem(STORAGE_KEY, next); } catch {}
    apply(next);
    try { window.dispatchEvent(new CustomEvent('pe-theme-change', { detail: { theme: next } })); } catch {}
  }, [apply]);

  const toggleDark = useCallback(() => {
    const current = theme;
    let next: ThemeChoice;
    if (current === 'light') next = 'dark';
    else if (current === 'dark') next = 'light';
    else if (current === 'high-contrast') next = resolvedTheme === 'dark' ? 'light' : 'dark';
    else { // system
      next = resolvedTheme === 'dark' ? 'light' : 'dark';
    }
    setTheme(next);
  }, [theme, resolvedTheme, setTheme]);

  // Initialization & listeners
  useEffect(() => {
    if (mountedRef.current) return; // ensure runs once
    mountedRef.current = true;
    let stored: ThemeChoice | null = null;
    try { stored = localStorage.getItem(STORAGE_KEY) as ThemeChoice | null; } catch {}
    const initial = stored || 'system';
    setThemeChoice(initial);
    apply(initial);
    setReady(true);

    // System dark/light listener
    const mqlColor = window.matchMedia('(prefers-color-scheme: dark)');
    const onColorChange = () => {
      if (initial === 'system' || theme === 'system') {
        apply('system');
      }
    };
    mqlColor.addEventListener('change', onColorChange);

    // Forced-colors listener (high contrast)
    let mqlForced: MediaQueryList | null = null;
    try { mqlForced = window.matchMedia('(forced-colors: active)'); } catch {}
    const onForced = () => {
      if (theme === 'system') apply('system');
    };
    mqlForced?.addEventListener('change', onForced);

    // Storage sync
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        const incoming = e.newValue as ThemeChoice;
        setThemeChoice(incoming);
        apply(incoming);
      }
    };
    window.addEventListener('storage', onStorage);

    return () => {
      mqlColor.removeEventListener('change', onColorChange);
      mqlForced?.removeEventListener('change', onForced);
      window.removeEventListener('storage', onStorage);
    };
  }, [apply, theme]);

  const value: ThemeContextValue = {
    theme,
    resolvedTheme,
    setTheme,
    toggleDark,
    isSystem: theme === 'system',
    highContrastAuto,
    ready,
  };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useThemeContext() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useThemeContext must be used within ThemeProvider');
  return ctx;
}
