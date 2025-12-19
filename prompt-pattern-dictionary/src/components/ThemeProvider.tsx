"use client";
import React, { createContext, useContext, useEffect, useCallback, useReducer, useState, ReactNode } from 'react';

export type ThemeChoice = "light" | "dark" | "high-contrast" | "system";
export type ResolvedTheme = "light" | "dark" | "high-contrast";

interface ThemeContextValue {
  theme: ThemeChoice;          // user choice (may be 'system')
  resolvedTheme: ResolvedTheme;// applied theme after resolving 'system'
  setTheme: (m: ThemeChoice) => void;
  toggleDark: () => void;      // convenience: cycle light/dark when not high-contrast
  isSystem: boolean;           // theme === 'system'
  highContrastAuto: boolean;   // true if high contrast came from system while in 'system'
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
  const allowSystemHighContrast = true; // default chosen path

  const [theme, setThemeChoice] = useState<ThemeChoice>(() => {
    if (typeof window === 'undefined') return 'system';
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as ThemeChoice | null;
      if (stored === 'light' || stored === 'dark' || stored === 'high-contrast' || stored === 'system') {
        return stored;
      }
    } catch {}
    return 'system';
  });

  // Used to re-render when system preferences change.
  const [, forceSystemUpdate] = useReducer((x: number) => x + 1, 0);

  const resolvedTheme = resolveTheme(theme, allowSystemHighContrast);
  const highContrastAuto = theme === 'system' && resolvedTheme === 'high-contrast' && systemForcedColors();

  const setTheme = useCallback((next: ThemeChoice) => {
    setThemeChoice(next);
    try { localStorage.setItem(STORAGE_KEY, next); } catch {}
    try { window.dispatchEvent(new CustomEvent('pe-theme-change', { detail: { theme: next } })); } catch {}
  }, []);

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

  // Apply theme attributes to the document.
  useEffect(() => {
    if (typeof document === 'undefined') return;
    document.documentElement.setAttribute('data-theme', resolvedTheme);
    document.documentElement.setAttribute('data-theme-mode', theme);
    document.documentElement.setAttribute('data-theme-resolved', resolvedTheme);
    document.documentElement.setAttribute('data-theme-ready', 'true');
  }, [theme, resolvedTheme]);

  // Listeners for system theme changes + storage sync.
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;

    const bump = () => {
      if (theme === 'system') forceSystemUpdate();
    };

    const mqlColor = window.matchMedia('(prefers-color-scheme: dark)');
    mqlColor.addEventListener('change', bump);

    let mqlForced: MediaQueryList | null = null;
    try { mqlForced = window.matchMedia('(forced-colors: active)'); } catch {}
    mqlForced?.addEventListener('change', bump);

    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        const incoming = e.newValue as ThemeChoice;
        setThemeChoice(incoming);
      }
    };
    window.addEventListener('storage', onStorage);

    return () => {
      mqlColor.removeEventListener('change', bump);
      mqlForced?.removeEventListener('change', bump);
      window.removeEventListener('storage', onStorage);
    };
  }, [theme]);

  const value: ThemeContextValue = {
    theme,
    resolvedTheme,
    setTheme,
    toggleDark,
    isSystem: theme === 'system',
    highContrastAuto,
  };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useThemeContext() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useThemeContext must be used within ThemeProvider');
  return ctx;
}
