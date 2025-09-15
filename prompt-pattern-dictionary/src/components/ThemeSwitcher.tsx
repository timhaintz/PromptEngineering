"use client";
import React from "react";
import { useTheme, ThemeMode } from "./useTheme";

const modes: { label: string; value: ThemeMode }[] = [
  { label: "Light", value: "light" },
  { label: "Dark", value: "dark" },
  { label: "High Contrast", value: "high-contrast" }
];

export function ThemeSwitcher({ className = "" }: { className?: string }) {
  const { theme, setTheme } = useTheme();

  return (
    <fieldset className={`inline-flex items-center gap-1 rounded-md border border-muted p-1 text-sm ${className}`}>
      <legend className="sr-only">Color theme</legend>
      {modes.map(m => {
        const active = theme === m.value;
        return (
          <label key={m.value} className="relative">
            <input
              type="radio"
              name="theme-mode"
              value={m.value}
              className="sr-only"
              checked={active}
              onChange={() => setTheme(m.value)}
              aria-label={m.label}
            />
            <span
              className={`px-2 py-1 rounded-sm focus-ring transition-colors border inline-block cursor-pointer ` +
                (active
                  ? "active-pill font-medium"
                  : "text-primary hover:bg-surface-hover border-transparent")}
            >
              {m.label}
            </span>
          </label>
        );
      })}
    </fieldset>
  );
}

export default ThemeSwitcher;
