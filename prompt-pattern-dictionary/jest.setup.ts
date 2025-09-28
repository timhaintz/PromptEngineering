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
