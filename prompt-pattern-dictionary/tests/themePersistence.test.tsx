import React from 'react';
import { render, act } from '@testing-library/react';
import { ThemeProvider, useThemeContext } from '@/components/ThemeProvider';

function Consumer() {
  const { theme, resolvedTheme, setTheme } = useThemeContext();
  return (
    <div>
      <span data-testid="mode">{theme}</span>
      <span data-testid="effective">{resolvedTheme}</span>
      <button onClick={() => setTheme('dark')}>dark</button>
      <button onClick={() => setTheme('light')}>light</button>
    </div>
  );
}

describe('Theme persistence', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-theme-mode');
  });

  it('applies stored theme on mount', () => {
    localStorage.setItem('pe-theme', 'dark');
    render(<ThemeProvider><Consumer /></ThemeProvider>);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('persists chosen theme selection and updates resolved attribute', () => {
    const { getByText } = render(<ThemeProvider><Consumer /></ThemeProvider>);
    act(() => { getByText('dark').click(); });
    expect(localStorage.getItem('pe-theme')).toBe('dark');
    // resolved stored on attribute
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme-resolved')).toBe('dark');
  });
});
