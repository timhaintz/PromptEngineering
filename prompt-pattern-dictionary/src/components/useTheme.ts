"use client";
import { useEffect, useState, useCallback } from "react";

export type ThemeMode = "light" | "dark" | "high-contrast" | "system";
const STORAGE_KEY = "pe-theme";

function getSystemPref(): Exclude<ThemeMode, 'high-contrast' | 'system'> {
  if (typeof window === "undefined") return "light";
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
}

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode | null>(null);
  const [effective, setEffective] = useState<Exclude<ThemeMode,'system'>>("light");

  const resolveEffective = useCallback((m: ThemeMode | null): Exclude<ThemeMode,'system'> => {
    if (!m || m === 'system') return getSystemPref();
    if (m === 'high-contrast') return 'high-contrast';
    return m; // light or dark
  }, []);

  const applyDom = useCallback((eff: Exclude<ThemeMode,'system'>) => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', eff);
    }
  }, []);

  const setTheme = useCallback((next: ThemeMode) => {
    setMode(next);
    try { window.localStorage.setItem(STORAGE_KEY, next); } catch {}
    const eff = resolveEffective(next);
    setEffective(eff);
    applyDom(eff);
  }, [applyDom, resolveEffective]);

  // Initialize + system listener when in system mode
  useEffect(() => {
    if (typeof window === 'undefined') return;
    let stored: ThemeMode | null = null;
    try { stored = window.localStorage.getItem(STORAGE_KEY) as ThemeMode | null; } catch {}
    const initialMode: ThemeMode = stored || 'system';
    setMode(initialMode);
    const eff = resolveEffective(initialMode);
    setEffective(eff);
    applyDom(eff);
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    const listener = () => {
      setEffective(prev => {
        if ((stored || initialMode) === 'system') {
          const eff2 = resolveEffective('system');
          applyDom(eff2);
          return eff2;
        }
        return prev;
      });
    };
    mql.addEventListener('change', listener);
    return () => mql.removeEventListener('change', listener);
  }, [applyDom, resolveEffective]);

  return { theme: mode, effectiveTheme: effective, setTheme };
}
