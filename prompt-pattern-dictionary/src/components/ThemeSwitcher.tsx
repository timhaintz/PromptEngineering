"use client";
import React, { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { useThemeContext } from "./ThemeProvider";
import type { ThemeChoice } from "./ThemeProvider";

const MODES: { label: string; value: ThemeChoice; short: string; icon: React.ReactElement }[] = [
  {
    label: "System (Auto)",
    value: "system",
    short: "Sys",
    icon: <svg aria-hidden className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8"/></svg>
  },
  {
    label: "Light",
    value: "light",
    short: "Light",
    icon: <svg aria-hidden className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 18a6 6 0 100-12 6 6 0 000 12zm0-16a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm0 18a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm10-7a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM6 12a1 1 0 01-1 1H4a1 1 0 110-2h1a1 1 0 011 1zm11.657 5.657a1 1 0 011.414 0l.707.707a1 1 0 01-1.414 1.414l-.707-.707a1 1 0 010-1.414zM5.929 6.343a1 1 0 010-1.414L6.636 4.22a1 1 0 111.414 1.414L7.343 6.343A1 1 0 015.93 6.343zm12.142-1.414a1 1 0 010 1.414L17.364 6.343a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM6.343 17.657a1 1 0 010 1.414l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 0z"/></svg>
  },
  {
    label: "Dark",
    value: "dark",
    short: "Dark",
    icon: <svg aria-hidden className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.79A9 9 0 0111.21 3 7 7 0 0012 17a7 7 0 009-4.21z"/></svg>
  },
  {
    label: "High Contrast",
    value: "high-contrast",
    short: "HC",
    icon: <svg aria-hidden className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 100 20V2z"/><path d="M12 2v20a10 10 0 000-20z" fill="currentColor" fillOpacity="0.35"/></svg>
  }
];

export function ThemeSwitcher({ className = "" }: { className?: string }) {
  const { theme, setTheme } = useThemeContext();
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [mounted, setMounted] = useState(false);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const radioRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const current = MODES.find(m => m.value === theme) || MODES[0];

  const openPanel = () => setOpen(true);
  const closePanel = () => { setOpen(false); triggerRef.current?.focus(); };

  useEffect(() => {
    setMounted(true);
  }, []);

  // Track viewport size for mobile overlay behaviour
  useEffect(() => {
  if (typeof window === 'undefined') return;
    const update = () => setIsMobile(window.innerWidth < 768);
    update();
    window.addEventListener('resize', update);
    return () => {
      window.removeEventListener('resize', update);
    };
  }, []);

  // Prevent background scroll when mobile sheet is open
  useEffect(() => {
    if (!isMobile || !open || typeof document === 'undefined') return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [isMobile, open]);

  // Close on outside / escape
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closePanel();
      if (['ArrowDown','ArrowUp','Home','End'].includes(e.key)) {
        e.preventDefault();
  const currentIndex = MODES.findIndex(m => m.value === theme) || 0;
        let targetIndex = currentIndex;
        if (e.key === 'ArrowDown') targetIndex = (currentIndex + 1) % MODES.length;
        if (e.key === 'ArrowUp') targetIndex = (currentIndex - 1 + MODES.length) % MODES.length;
        if (e.key === 'Home') targetIndex = 0;
        if (e.key === 'End') targetIndex = MODES.length - 1;
        const btn = radioRefs.current[targetIndex];
        btn?.focus();
      }
    };
    const onPointerDown = (e: PointerEvent) => {
      if (!panelRef.current) return;
      if (!panelRef.current.contains(e.target as Node) && !triggerRef.current?.contains(e.target as Node)) {
        closePanel();
      }
    };
    window.addEventListener('keydown', onKey);
    window.addEventListener('pointerdown', onPointerDown);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('pointerdown', onPointerDown);
    };
  }, [open, theme]);

  const select = (value: ThemeChoice) => {
    // Apply theme but keep panel open to allow rapid comparison unless same value clicked
    const wasSame = value === theme;
    setTheme(value);
    if (wasSame) closePanel();
  };

  const panelContent = (
    <>
      {MODES.map((m, idx) => {
        const active = theme === m.value;
        if (active) {
          return (
            <button
              key={m.value}
              ref={el => { radioRefs.current[idx] = el; }}
              role="radio"
              aria-checked="true"
              tabIndex={0}
              onClick={() => select(m.value)}
              onKeyDown={e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); select(m.value); } }}
              className="w-full text-left flex items-center gap-2 px-2 py-1 rounded-md text-sm focus-ring transition-colors active-pill font-medium"
            >
              <span className="shrink-0">{m.icon}</span>
              <span className="flex-1">{m.label}</span>
              <span aria-hidden className="text-xs">✓</span>
              <span className="sr-only">(Active)</span>
            </button>
          );
        }
        return (
          <button
            key={m.value}
            ref={el => { radioRefs.current[idx] = el; }}
            role="radio"
            aria-checked="false"
            tabIndex={-1}
            onClick={() => select(m.value)}
            onKeyDown={e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); select(m.value); } }}
            className="w-full text-left flex items-center gap-2 px-2 py-1 rounded-md text-sm focus-ring transition-colors text-secondary hover:bg-surface-hover"
          >
            <span className="shrink-0">{m.icon}</span>
            <span className="flex-1">{m.label}</span>
          </button>
        );
      })}
      <div className="pt-1 mt-1 border-t border-muted text-[10px] px-2 text-secondary">
        <span className="block">Arrow keys navigate • Stored locally</span>
      </div>
    </>
  );

  return (
    <div className={`relative ${className}`}>
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="dialog"
        {...(open ? { 'aria-expanded': 'true' } : {})}
        aria-label={`Theme: ${current.label}. ${open ? 'Close selector' : 'Open theme selector'}`}
        onClick={() => (open ? closePanel() : openPanel())}
        className="inline-flex items-center gap-1 rounded-md border border-muted bg-surface-2 px-2.5 py-1.5 text-sm text-secondary shadow-sm hover:bg-surface-hover focus-ring"
      >
        {current.icon}
      </button>
      {open && !isMobile && (
        <div
          ref={panelRef}
          role="radiogroup"
          aria-label="Color theme"
          className="absolute right-0 mt-2 w-48 rounded-md border border-muted bg-surface-1 shadow-lg p-1 z-50"
        >
          {panelContent}
        </div>
      )}
      {open && isMobile && mounted && typeof document !== 'undefined'
        ? createPortal(
            <div className="fixed inset-0 z-[100] pointer-events-auto">
              <div
                className="absolute inset-0 bg-surface-1/60 backdrop-blur-sm"
                aria-hidden="true"
                onClick={closePanel}
              />
              <div className="absolute inset-x-3 top-20" role="dialog" aria-modal="true">
                <div
                  ref={panelRef}
                  role="radiogroup"
                  aria-label="Color theme"
                  className="rounded-xl border border-muted bg-surface-1 shadow-2xl p-1"
                >
                  {panelContent}
                </div>
              </div>
            </div>,
            document.body
          )
        : null}
    </div>
  );
}

export default ThemeSwitcher;
