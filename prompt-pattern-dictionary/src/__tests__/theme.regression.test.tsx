/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import pages (server components) – for simplicity test a couple representative ones.
import LogicPage from '@/app/logic/page';
import PatternsPage from '@/app/patterns/page';
import SearchPage from '@/app/search/page';
import CategoriesPage from '@/app/categories/page';
import PapersPage from '@/app/papers/page';

// Helper: force document to dark theme before each render
beforeEach(() => {
  document.documentElement.setAttribute('data-theme', 'dark');
});

describe('Dark theme regression', () => {
  it('Dark theme tokens match expected refined palette', () => {
    const style = getComputedStyle(document.documentElement);
    const tokens: Record<string,string> = {
      '--color-bg-base': style.getPropertyValue('--color-bg-base').trim(),
      '--color-surface-1': style.getPropertyValue('--color-surface-1').trim(),
      '--color-surface-2': style.getPropertyValue('--color-surface-2').trim(),
      '--color-surface-hover': style.getPropertyValue('--color-surface-hover').trim(),
      '--color-border-muted': style.getPropertyValue('--color-border-muted').trim(),
      '--color-border-strong': style.getPropertyValue('--color-border-strong').trim(),
      '--color-text-primary': style.getPropertyValue('--color-text-primary').trim(),
      '--color-text-secondary': style.getPropertyValue('--color-text-secondary').trim(),
      '--color-text-muted': style.getPropertyValue('--color-text-muted').trim(),
      '--color-accent': style.getPropertyValue('--color-accent').trim(),
      '--color-accent-hover': style.getPropertyValue('--color-accent-hover').trim(),
      '--color-accent-active-bg': style.getPropertyValue('--color-accent-active-bg').trim(),
      '--color-focus-ring': style.getPropertyValue('--color-focus-ring').trim(),
      '--color-focus-ring-outer': style.getPropertyValue('--color-focus-ring-outer').trim(),
    };
    expect(tokens).toEqual({
      '--color-bg-base': '#14181E',
      '--color-surface-1': '#1B2027',
      '--color-surface-2': '#232A33',
      '--color-surface-hover': '#2B3540',
      '--color-border-muted': '#313C47',
      '--color-border-strong': '#526170',
      '--color-text-primary': '#E9EDF2',
      '--color-text-secondary': '#BAC5D1',
      '--color-text-muted': '#8392A1',
      '--color-accent': '#2E6FE0',
      '--color-accent-hover': '#4D8CF0',
      '--color-accent-active-bg': 'rgba(46, 111, 224, 0.10)',
      '--color-focus-ring': '#F5F9FF',
      '--color-focus-ring-outer': '#2E6FE0',
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
    const ui = await PatternsPage({ searchParams: Promise.resolve({}) } as any);
    const { container } = render(ui as any);
    // Ensure the shell exists
    const shell = container.querySelector('.min-h-screen');
    expect(shell).toBeTruthy();
    // Ensure surface-card classes exist
    expect(container.querySelector('.surface-card')).toBeTruthy();
  });

  it('Search page uses PageShell and utilities', () => {
    const { container } = render(<SearchPage />);
    expect(container.querySelector('.min-h-screen')).toBeTruthy();
    expect(container.querySelector('.surface-card')).toBeTruthy();
    // Inputs should have input-base
    expect(container.querySelector('.input-base')).toBeTruthy();
  });

  it('Categories page uses PageShell and surface cards', async () => {
    const ui = await CategoriesPage();
    const { container } = render(ui as any);
    expect(container.querySelector('.min-h-screen')).toBeTruthy();
    expect(container.querySelector('.surface-card')).toBeTruthy();
  });

  it('Papers page uses PageShell and surface cards', async () => {
    const ui = await PapersPage();
    const { container } = render(ui as any);
    expect(container.querySelector('.min-h-screen')).toBeTruthy();
    expect(container.querySelector('.surface-card')).toBeTruthy();
  });
});
