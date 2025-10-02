/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { render, act } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import pages (server components) – for simplicity test a couple representative ones.
// Mock navigation hooks to avoid App Router invariant errors
jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(''),
  useRouter: () => ({ push: jest.fn(), replace: jest.fn(), prefetch: jest.fn() }),
}));

import fs from 'fs';
import path from 'path';
import LogicPage from '@/app/logic/page';
import PatternsPage from '@/app/patterns/page';
import SearchPage from '@/app/search/page';
import CategoriesPage from '@/app/categories/page';
import PapersPage from '@/app/papers/page';

function injectTokens() {
  if (document.getElementById('test-tokens')) return;
  const css = fs.readFileSync(path.join(process.cwd(), 'src', 'styles', 'tokens.css'), 'utf8');
  const style = document.createElement('style');
  style.id = 'test-tokens';
  style.textContent = css;
  document.head.appendChild(style);
}

// Helper: force document to dark theme before each render
beforeEach(() => {
  document.documentElement.setAttribute('data-theme', 'dark');
  // Provide fetch stub for data-loading server components invoked in test environment
  if (!(global as any).fetch) {
    (global as any).fetch = jest.fn(async () => ({ ok: true, json: async () => ([])}));
  }
});

describe('Dark theme regression', () => {
  it('Dark theme tokens match expected refined palette', () => {
    injectTokens();
    const style = getComputedStyle(document.documentElement);
    const tokens: Record<string,string> = {
      '--surface-1': style.getPropertyValue('--surface-1').trim(),
      '--surface-2': style.getPropertyValue('--surface-2').trim(),
      '--surface-card': style.getPropertyValue('--surface-card').trim(),
      '--surface-hover': style.getPropertyValue('--surface-hover').trim(),
      '--border-default': style.getPropertyValue('--border-default').trim(),
      '--border-strong': style.getPropertyValue('--border-strong').trim(),
      '--text-primary': style.getPropertyValue('--text-primary').trim(),
      '--text-secondary': style.getPropertyValue('--text-secondary').trim(),
      '--text-muted': style.getPropertyValue('--text-muted').trim(),
      '--accent': style.getPropertyValue('--accent').trim(),
      '--accent-hover': style.getPropertyValue('--accent-hover').trim(),
      '--accent-active-bg': style.getPropertyValue('--accent-active-bg').trim(),
      '--focus-ring': style.getPropertyValue('--focus-ring').trim(),
      '--focus-ring-outer': style.getPropertyValue('--focus-ring-outer').trim(),
    };
    expect(tokens).toEqual({
      '--surface-1': '#0e141a',
      '--surface-2': '#16202a',
      '--surface-card': '#18222d',
      '--surface-hover': '#22303d',
      '--border-default': '#27323d',
      '--border-strong': '#35424f',
      '--text-primary': '#f2f6f9',
      '--text-secondary': '#dde6ee',
      '--text-muted': '#9aa8b5',
      '--accent': '#3b82f6',
      '--accent-hover': '#4d8cf0',
  '--accent-active-bg': 'rgba(59,130,246,0.16)',
      '--focus-ring': '#f5f9ff',
      '--focus-ring-outer': '#2e6fe0',
    });
  });
  it('Logic page should not render legacy light wrappers', async () => {
    const ui = await LogicPage();
    const { container } = render(ui as any);
    // Assert no raw light gradient or legacy classes at top-level
    expect(container.querySelector('[class*="bg-gradient"]')).toBeNull();
    // Accept some bg-white only inside svg, but not as page wrapper
    const wrappers = Array.from(container.querySelectorAll('.bg-white'));
    const offending = wrappers.filter(w => w.classList.contains('min-h-screen'));
    expect(offending.length).toBe(0);
  });

  it('Patterns page uses PageShell and token utilities', async () => {
    const ui = await PatternsPage();
    const { container } = render(ui as any);
    // Ensure the shell exists
    const shell = container.querySelector('.min-h-screen');
    expect(shell).toBeTruthy();
    // Ensure surface-card classes exist
    expect(container.querySelector('.surface-card')).toBeTruthy();
  });

  it('Search page renders within PageShell (shell presence assertion)', async () => {
    let container: HTMLElement;
    await act(async () => {
      const r = render(<SearchPage />);
      container = r.container;
      // allow pending async effects
      await new Promise(res => setTimeout(res, 0));
    });
    expect(container!.querySelector('.min-h-screen')).toBeTruthy();
  });

  it('Categories page renders within PageShell', async () => {
    const ui = await CategoriesPage();
    const { container } = render(ui as any);
    expect(container.querySelector('.min-h-screen')).toBeTruthy();
  });

  it('Papers page uses PageShell and surface cards', async () => {
    const ui = await PapersPage();
    const { container } = render(ui as any);
    expect(container.querySelector('.min-h-screen')).toBeTruthy();
    expect(container.querySelector('.surface-card')).toBeTruthy();
  });
});
