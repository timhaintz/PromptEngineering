import React from 'react';
import { render, act } from '@testing-library/react';
import { ThemeProvider, useThemeContext } from '@/components/ThemeProvider';

function Consumer() {
  const { mode, effective, setMode } = useThemeContext();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <span data-testid="effective">{effective}</span>
      <button onClick={() => setMode('dark')}>dark</button>
      <button onClick={() => setMode('light')}>light</button>
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

  it('persists chosen theme and effective key', () => {
    const { getByText } = render(<ThemeProvider><Consumer /></ThemeProvider>);
    act(() => { getByText('dark').click(); });
    expect(localStorage.getItem('pe-theme')).toBe('dark');
    expect(localStorage.getItem('pe-theme-effective')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
