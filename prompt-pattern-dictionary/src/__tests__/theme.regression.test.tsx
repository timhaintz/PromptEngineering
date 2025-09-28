import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import pages (server components) – for simplicity test a couple representative ones.
import LogicPage from '@/app/logic/page';
import PatternsPage from '@/app/patterns/page';
import SearchPage from '@/app/search/page';

// Helper: force document to dark theme before each render
beforeEach(() => {
  document.documentElement.setAttribute('data-theme', 'dark');
});

describe('Dark theme regression', () => {
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
});
