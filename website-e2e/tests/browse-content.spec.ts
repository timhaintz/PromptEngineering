import { expect, test } from '@playwright/test';

test.describe('browse and content pages', () => {
  test('categories page lists category tiles and opens a category detail page', async ({ page }) => {
    await page.goto('./categories/');

    await expect(page.getByRole('heading', { level: 1, name: /Categories/i })).toBeVisible();
    await page.getByRole('link', { name: /Argument/i }).first().click();

    await expect(page).toHaveURL(/\/category\/argument\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /^Argument$/ })).toBeVisible();
  });

  test('taxonomy page shows logic groups and category links', async ({ page }) => {
    await page.goto('./taxonomy/');

    await expect(page.getByRole('heading', { level: 1, name: /PP Taxonomy/i })).toBeVisible();
    await expect(page.getByText(/Across Logic/i)).toBeVisible();
    await expect(page.getByRole('link', { name: /^Argument$/ })).toBeVisible();
  });

  test('papers page opens an internal paper detail page', async ({ page }) => {
    await page.goto('./papers/');

    await expect(page.getByRole('heading', { level: 1, name: /^Papers$/ })).toBeVisible();
    await page.getByRole('link').filter({ hasText: /Patterns:/i }).first().click();

    await expect(page).toHaveURL(/\/papers\/.+/);
    await expect(page.getByRole('link', { name: /Back to Papers/i })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /Patterns \(/i })).toBeVisible();
  });

  test('examples page filters examples and exposes parent navigation links', async ({ page }) => {
    await page.goto('./examples/');

    await expect(page.getByRole('heading', { level: 1, name: /All Prompt Examples/i })).toBeVisible();
    await expect(page.getByRole('search', { name: /Filter examples/i })).toBeVisible();

    await page.getByRole('textbox', { name: /Search examples/i }).fill('security');
    await page.getByRole('button', { name: /^Filter$/ }).click();

    await expect(page).toHaveURL(/\/examples\/?\?q=security/);
    await expect(page.getByText(/for query “security”/i)).toBeVisible();
    await expect(page.getByRole('link', { name: /Go to example in paper/i }).first()).toBeVisible();
  });
});
