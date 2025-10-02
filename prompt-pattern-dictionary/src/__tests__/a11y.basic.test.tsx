// @jest-environment jsdom
/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { jest, describe, it, expect, beforeAll } from '@jest/globals';
import { render, act } from '@testing-library/react';
import { axe } from 'jest-axe';
import 'jest-axe/extend-expect';
import '@testing-library/jest-dom';

// Mock next/navigation for client components that expect App Router context
jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(''),
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock next/link to a simple anchor to avoid prefetch + IntersectionObserver side-effects that cause act warnings
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...rest }: any) => <a href={typeof href === 'string' ? href : '#'} {...rest}>{children}</a>,
}));


// Stub IntersectionObserver to silence act() warnings originating from Next <Link /> prefetch logic
beforeAll(() => {
  // Stub IntersectionObserver
  if (!(global as any).IntersectionObserver) {
    class IO {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
    ;(global as any).IntersectionObserver = IO as any;
  }
  // Stub fetch so server component data loaders in SearchPage don't throw
  if (!(global as any).fetch) {
    (global as any).fetch = jest.fn(async () => ({ ok: true, json: async () => ([])}));
  }
  // Stub canvas getContext to silence jsdom "not implemented" during axe color-contrast scanning
  if (!(HTMLCanvasElement.prototype as any).getContext) {
    (HTMLCanvasElement.prototype as any).getContext = () => null;
  }
});

// Small helper to allow effects + async state updates to settle before running axe
async function flushAsyncEffects() {
  // One macro-task tick
  await act(async () => {
    await new Promise(res => setTimeout(res, 0));
  });
}

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

// jest-axe matcher already registered via extend-expect import

describe('Accessibility smoke tests', () => {
  it('Logic page has no critical a11y violations', async () => {
    const ui = await LogicPage();
    const { container } = render(ui as any);
    await flushAsyncEffects();
  const results = await axe(container, { rules: { 'color-contrast': { enabled: true } } });
  expect(results).toHaveNoViolations();
  });

  it('Patterns page has no critical a11y violations', async () => {
    const ui = await PatternsPage();
    const { container } = render(ui as any);
    await flushAsyncEffects();
  const results = await axe(container, { rules: { 'color-contrast': { enabled: true } } });
  expect(results).toHaveNoViolations();
  }, 15000);

  it('Search page has no critical a11y violations', async () => {
    const { container } = render(<SearchPage />);
    await flushAsyncEffects();
  const results = await axe(container, { rules: { 'color-contrast': { enabled: true } } });
  expect(results).toHaveNoViolations();
  }, 15000);
});
