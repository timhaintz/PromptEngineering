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
