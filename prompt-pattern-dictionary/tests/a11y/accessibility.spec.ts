import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const ROUTES = [
  '/',
  '/search',
  '/orientation/quick-start',
  '/orientation/cheatsheet',
  '/patterns',
  '/categories'
];

const THEMES: Array<'light' | 'dark' | 'high-contrast'> = ['light', 'dark', 'high-contrast'];

test.describe('Accessibility (axe-core) across themes', () => {
  for (const route of ROUTES) {
    for (const theme of THEMES) {
      test(`${route} theme=${theme} has no serious/critical violations`, async ({ page }) => {
        await page.goto(route);
        await page.waitForLoadState('domcontentloaded');
        // Apply theme before potential dynamic content settles
        await page.evaluate(t => {
          document.documentElement.setAttribute('data-theme', t);
        }, theme);
        // Small wait for repaint and any CSS var dependent hydration
        await page.waitForTimeout(50);
        await page.waitForLoadState('networkidle');
        const accessibilityScanResults = await new AxeBuilder({ page })
          .withTags(['wcag2a', 'wcag2aa'])
          .analyze();
        const violations = accessibilityScanResults.violations.filter(v => ['serious', 'critical'].includes(v.impact || ''));
        if (violations.length) {
          console.log(`Violations for ${route} (theme=${theme}):`);
          for (const v of violations) {
            console.log(`- ${v.id}: ${v.description}`);
            v.nodes.slice(0, 5).forEach(n => console.log(`  * ${n.html}`));
          }
        }
        expect.soft(violations).toEqual([]);
      });
    }
  }
});
