"use client";
import { useEffect, useState, useCallback } from "react";

export type ThemeMode = "light" | "dark" | "high-contrast";
const STORAGE_KEY = "pe-theme";

function getSystemPref(): ThemeMode {
  if (typeof window === "undefined") return "light";
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
}

export function useTheme() {
  const [theme, setTheme] = useState<ThemeMode | null>(null);

  // Initialize
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
      const initial = stored || getSystemPref();
      applyTheme(initial);
    } catch {
      applyTheme(getSystemPref());
    }
  }, []);

  const applyTheme = useCallback((mode: ThemeMode) => {
    setTheme(mode);
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", mode === "high-contrast" ? "high-contrast" : mode);
    }
    try { window.localStorage.setItem(STORAGE_KEY, mode); } catch {}
  }, []);

  return { theme, setTheme: applyTheme };
}
