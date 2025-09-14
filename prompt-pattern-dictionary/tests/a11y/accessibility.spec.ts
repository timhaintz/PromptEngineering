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

test.describe('Accessibility (axe-core)', () => {
  for (const route of ROUTES) {
    test(`route ${route} should have no serious or critical violations`, async ({ page, baseURL }) => {
      await page.goto(route);
      // Wait for network to settle a bit
      await page.waitForLoadState('networkidle');
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();
      const violations = accessibilityScanResults.violations.filter(v => ['serious', 'critical'].includes(v.impact || ''));            
      if (violations.length) {
        console.log(`Violations for ${route}:`);
        for (const v of violations) {
          console.log(`- ${v.id}: ${v.description}`);
          v.nodes.slice(0, 5).forEach(n => console.log(`  * ${n.html}`));
        }
      }
      expect.soft(violations).toEqual([]);
    });
  }
});
