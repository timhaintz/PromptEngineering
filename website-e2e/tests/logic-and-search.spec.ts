import { expect, test } from '@playwright/test';

test.describe('logic layers and search', () => {
  test('logic page links through to the Argument category', async ({ page }) => {
    await page.goto('/logic/');

    await expect(page.getByRole('heading', { level: 1, name: /Logic Layers/i })).toBeVisible();
    await page.getByRole('link', { name: /Argument/i }).first().click();

    await expect(page).toHaveURL(/\/category\/argument\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /^Argument$/ })).toBeVisible();
  });

  test('homepage search redirects into the dedicated search page', async ({ page }) => {
    await page.goto('/');

    await page.getByLabel(/Search prompt patterns/i).fill('security');
    await page.getByRole('button', { name: /^Search$/ }).click();

    await expect(page).toHaveURL(/\/search\/?\?q=security/);
    await expect(page.getByRole('heading', { level: 1, name: /^Search$/ })).toBeVisible();
    await expect(page.getByLabel('Search text')).toHaveValue('security');
  });

  test('search page exposes core filter controls', async ({ page }) => {
    await page.goto('/search/?q=security&type=pattern');

    await expect(page.getByRole('heading', { level: 1, name: /^Search$/ })).toBeVisible();
    await expect(page.getByLabel('Search text')).toHaveValue('security');
    await expect(page.getByLabel('Search type')).toHaveValue('pattern');
    await expect(page.getByLabel('Category type')).toHaveValue('original');
    await expect(page.getByRole('button', { name: /Clear all/i })).toBeVisible();
  });
});
