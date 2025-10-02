// Global jest setup for polyfills used across tests
import { jest } from '@jest/globals';
import { TextEncoder, TextDecoder } from 'util';

jest.mock('next/navigation', () => {
  const actual = jest.requireActual('next/navigation') as Record<string, unknown>;
  return {
    ...actual,
    useRouter: () => ({
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(() => Promise.resolve()),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }),
    useSearchParams: () => new URLSearchParams(),
  };
});
(global as any).TextEncoder = (global as any).TextEncoder || TextEncoder;
(global as any).TextDecoder = (global as any).TextDecoder || TextDecoder;

// Basic fetch stub (can be overridden per test)
if (!(global as any).fetch) {
  (global as any).fetch = jest.fn(async () => ({ ok: true, json: async () => ([])}));
}
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string): MediaQueryList => ({
    matches: query.includes('(prefers-color-scheme: dark)') ? false : false,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {}, // deprecated but included for libs expecting it
    removeListener: () => {},
    dispatchEvent: () => false
  })
});

// Optional: provide a noop ResizeObserver for components relying on it
// @ts-ignore
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Silence jsdom canvas getContext not implemented warnings encountered during axe color contrast scanning
// jsdom defines getContext but throws; replace with benign stub.
(HTMLCanvasElement.prototype as any).getContext = () => null;
