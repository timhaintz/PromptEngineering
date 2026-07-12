import { expect, test } from '@playwright/test';

test.describe('homepage and global navigation', () => {
  test('homepage renders the primary entry points', async ({ page }) => {
    await page.goto('./');

    await expect(page).toHaveTitle(/Ballarat AI Prompt Taxonomy/i);
    await expect(page.getByRole('heading', { level: 1, name: /Ballarat AI Prompt Taxonomy/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Browse Patterns/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Start with the Guide/i })).toBeVisible();
    await expect(page.getByRole('search', { name: /Prompt pattern search/i })).toBeVisible();
  });

  test('global navigation reaches logic layers', async ({ page }) => {
    await page.goto('./');

    const logicLink = page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Logic' });
    if (!(await logicLink.isVisible())) {
      await page.getByRole('button', { name: 'Menu' }).click();
    }
    await logicLink.click();

    await expect(page).toHaveURL(/\/logic\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /Logic Layers/i })).toBeVisible();
  });

  test('responsible use page renders its policy guidance', async ({ page }) => {
    await page.goto('./responsible-use/');

    await expect(page.getByRole('heading', { level: 1, name: /^Responsible Use$/i })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /Research inclusion is not endorsement/i })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /Before you apply a pattern/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Report privately/i })).toBeVisible();
  });
});
