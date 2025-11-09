import fs from 'fs';
import path from 'path';

// Simple audit: ensure key high-contrast token selectors and variable usages exist.
// This does not measure actual contrast ratios; it guards presence for P4 groundwork.

describe('High-Contrast token audit', () => {
  const tokensPath = path.join(__dirname, '..', 'styles', 'tokens.css');
  const themePath = path.join(__dirname, '..', 'styles', 'theme.css');
  const tokens = fs.readFileSync(tokensPath, 'utf8');
  const theme = fs.readFileSync(themePath, 'utf8');

  const requiredSelectors = ["[data-theme='high-contrast']", "html[data-theme='high-contrast']"];
  const requiredVariables = [
    '--surface-1', '--text-primary', '--text-secondary', '--accent', '--accent-fg', '--border-strong'
  ];

  it('includes high-contrast selectors in tokens.css and theme.css', () => {
    requiredSelectors.forEach(sel => {
      expect(tokens.includes(sel) || theme.includes(sel)).toBe(true);
    });
  });

  it('references required token variables in high-contrast styles', () => {
    requiredVariables.forEach(v => {
      const regex = new RegExp(v.replace(/[-]/g, '[-]'), 'i');
      expect(regex.test(tokens) || regex.test(theme)).toBe(true);
    });
  });
});
