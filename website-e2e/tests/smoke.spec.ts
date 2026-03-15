import { expect, test } from '@playwright/test';

test.describe('homepage and global navigation', () => {
  test('homepage renders the primary entry points', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/Ballarat AI Prompt Dictionary/i);
    await expect(page.getByRole('heading', { level: 1, name: /Ballarat AI Prompt Dictionary/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Browse Patterns/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Orientation \/ Getting Started/i })).toBeVisible();
    await expect(page.getByRole('search', { name: /Prompt pattern search/i })).toBeVisible();
  });

  test('global navigation reaches logic layers', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('navigation', { name: /Global navigation/i }).getByRole('link', { name: 'Logic' }).click();

    await expect(page).toHaveURL(/\/logic\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /Logic Layers/i })).toBeVisible();
  });

  test('responsible use page renders its main heading', async ({ page }) => {
    await page.goto('/responsible-use/');

    await expect(page.getByRole('heading', { level: 1, name: /Responsible Use & Ethical Guidelines/i })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /Core Principles/i })).toBeVisible();
  });
});
