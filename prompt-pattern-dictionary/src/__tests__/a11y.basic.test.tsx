// @jest-environment jsdom
/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { jest, describe, it, expect, beforeAll } from '@jest/globals';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import '@testing-library/jest-dom';

// Mock next/navigation for client components that expect App Router context
jest.mock('next/navigation', () => {
  return {
    useSearchParams: () => new URLSearchParams(''),
    useRouter: () => ({
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    }),
  };
});


// Stub IntersectionObserver to silence act() warnings originating from Next <Link /> prefetch logic
beforeAll(() => {
  if (!(global as any).IntersectionObserver) {
    class IO {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
    ;(global as any).IntersectionObserver = IO as any;
  }
});

import LogicPage from '@/app/logic/page';
import PatternsPage from '@/app/patterns/page';
// Defer importing SearchPage until after mocks are established to avoid resolving
// the real navigation module before our jest.mock takes effect.
let SearchPage: any;
beforeAll(async () => {
  // Dynamic import after mocks
  const mod = await import('@/app/search/page');
  SearchPage = mod.default ?? mod;
});

expect.extend(toHaveNoViolations);

describe('Accessibility smoke tests', () => {
  it('Logic page has no critical a11y violations', async () => {
    const ui = await LogicPage();
    const { container } = render(ui as any);
    const results = await axe(container, { rules: { 'color-contrast': { enabled: false } } });
    expect(results).toHaveNoViolations();
  });

  it('Patterns page has no critical a11y violations', async () => {
    const ui = await PatternsPage({ searchParams: {} } as any);
    const { container } = render(ui as any);
    const results = await axe(container, { rules: { 'color-contrast': { enabled: false } } });
    expect(results).toHaveNoViolations();
  }, 15000);

  it('Search page has no critical a11y violations', async () => {
    const { container } = render(<SearchPage />);
    const results = await axe(container, { rules: { 'color-contrast': { enabled: false } } });
    expect(results).toHaveNoViolations();
  }, 15000);
});
