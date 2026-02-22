// @jest-environment jsdom
/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Smoke tests for pages that were previously untested.
 * 
 * These verify basic rendering without crashes. Server components that read
 * from public/data/ files work because Jest runs in Node.js where fs is available.
 */
import React from 'react';
import { jest, describe, it, expect, beforeAll } from '@jest/globals';
import { render, act } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock next/navigation for client components
jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(''),
  usePathname: () => '/',
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock next/link to a simple anchor
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...rest }: any) =>
    <a href={typeof href === 'string' ? href : '#'} {...rest}>{children}</a>,
}));

beforeAll(() => {
  // Stub IntersectionObserver
  if (!(global as any).IntersectionObserver) {
    class IO {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
    (global as any).IntersectionObserver = IO as any;
  }
  // Stub fetch for components that lazy-load data
  if (!(global as any).fetch) {
    (global as any).fetch = jest.fn(async () => ({
      ok: true,
      json: async () => ([]),
    }));
  }
  // Stub canvas getContext
  if (!(HTMLCanvasElement.prototype as any).getContext) {
    (HTMLCanvasElement.prototype as any).getContext = () => null;
  }
});

async function flushAsyncEffects() {
  await act(async () => {
    await new Promise(res => setTimeout(res, 0));
  });
}

// --- Presentational pages (no fs reads) ---

describe('Comparison page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/comparison/page');
    const Page = mod.default;
    const { container } = render(<Page />);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 15000);
});

describe('Playground page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/playground/page');
    const Page = mod.default;
    const { container } = render(<Page />);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 15000);
});

describe('Responsible Use page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/responsible-use/page');
    const Page = mod.default;
    const ui = typeof Page === 'function' ? <Page /> : Page;
    const { container } = render(ui as any);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 15000);
});

// --- Server components that read from public/data/ ---

describe('Taxonomy page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/taxonomy/page');
    const Page = mod.default;
    const ui = await (Page as any)();
    const { container } = render(ui as any);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 30000);
});

describe('Examples page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/examples/page');
    const Page = mod.default;
    // examples/page.tsx is sync but reads fs at module level
    const { container } = render(<Page />);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 30000);
});

describe('Semantic page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/semantic/page');
    const Page = mod.default;
    const ui = await (Page as any)();
    const { container } = render(ui as any);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 30000);
});

describe('Matrix page', () => {
  it('renders without crashing', async () => {
    const mod = await import('@/app/matrix/page');
    const Page = mod.default;
    const ui = await (Page as any)();
    const { container } = render(ui as any);
    await flushAsyncEffects();
    expect(container.querySelector('h1')).toBeTruthy();
  }, 30000);
});
