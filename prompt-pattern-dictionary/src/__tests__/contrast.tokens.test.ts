/**
 * Basic contrast ratio validation for core text tokens against primary surfaces.
 * This is a lightweight guard (not exhaustive WCAG audit) to catch accidental
 * low-contrast regressions when adjusting tokens.
 */
import { JSDOM } from 'jsdom';
import { TextEncoder, TextDecoder } from 'util';
import fs from 'fs';
import path from 'path';

// Strongly typed polyfill attachment (avoid 'any')
const g: typeof globalThis & { TextEncoder?: typeof TextEncoder; TextDecoder?: typeof TextDecoder } = globalThis;
if (!g.TextEncoder) g.TextEncoder = TextEncoder;
if (!g.TextDecoder) g.TextDecoder = TextDecoder;

function luminance(hex: string): number {
  hex = hex.replace('#', '').trim();
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  const r = parseInt(hex.slice(0, 2), 16) / 255;
  const g = parseInt(hex.slice(2, 4), 16) / 255;
  const b = parseInt(hex.slice(4, 6), 16) / 255;
  const toLin = (c: number) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const R = toLin(r), G = toLin(g), B = toLin(b);
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

function contrast(hex1: string, hex2: string): number {
  const L1 = luminance(hex1);
  const L2 = luminance(hex2);
  const light = Math.max(L1, L2);
  const dark = Math.min(L1, L2);
  return (light + 0.05) / (dark + 0.05);
}

function extractComputedTokens(themeAttr?: string) {
  const htmlAttr = themeAttr ? ` data-theme="${themeAttr}"` : '';
  const dom = new JSDOM(`<!doctype html><html${htmlAttr}><head></head><body></body></html>`);
  const { window } = dom;
  // Inject tokens.css only (imports theme.css which imports tokens)
  const styleEl = window.document.createElement('style');
  // NOTE: embedding minimal subset (these tests rely on JSDOM executing CSS variable cascade).
  const tokensPath = path.join(__dirname, '..', 'styles', 'tokens.css');
  styleEl.textContent = fs.readFileSync(tokensPath, 'utf8');
  window.document.head.appendChild(styleEl);
  const cs = window.getComputedStyle(window.document.documentElement);
  const read = (name: string) => cs.getPropertyValue(name).trim();
  return {
    surface1: read('--surface-1'),
    surfaceCard: read('--surface-card'),
    textPrimary: read('--text-primary'),
    textSecondary: read('--text-secondary'),
    textMuted: read('--text-muted'),
  };
}

describe('semantic token contrast (light/dark)', () => {
  const MIN_PRIMARY = 4.5; // target AA for normal text
  const MIN_SECONDARY = 3.8; // allow slightly lower but still > 3:1
  const MIN_MUTED = 3.0; // metadata threshold

  test('light mode core text ratios', () => {
    const t = extractComputedTokens();
    expect(contrast(t.textPrimary, t.surface1)).toBeGreaterThanOrEqual(MIN_PRIMARY);
    expect(contrast(t.textSecondary, t.surface1)).toBeGreaterThanOrEqual(MIN_SECONDARY);
    expect(contrast(t.textMuted, t.surface1)).toBeGreaterThanOrEqual(MIN_MUTED);
  });

  test('dark mode core text ratios', () => {
    const t = extractComputedTokens('dark');
    expect(contrast(t.textPrimary, t.surface1)).toBeGreaterThanOrEqual(MIN_PRIMARY);
    expect(contrast(t.textSecondary, t.surface1)).toBeGreaterThanOrEqual(MIN_SECONDARY);
    expect(contrast(t.textMuted, t.surface1)).toBeGreaterThanOrEqual(MIN_MUTED);
  });
});
