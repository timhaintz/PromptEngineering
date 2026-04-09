import { expect, test } from '@playwright/test';

test.describe('orientation hub', () => {
  test('hub presents role map and quick paths without leftover phase labels', async ({ page }) => {
    await page.goto('./orientation/hub/');

    await expect(page.getByRole('heading', { level: 1, name: /Orientation Hub/i })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /^Role → Intent Map$/ })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /^Quick Paths$/ })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: /^Role → Intent Map$/ })).not.toContainText(/P1b/i);
    await expect(page.getByRole('heading', { level: 2, name: /^Quick Paths$/ })).not.toContainText(/P1/i);
  });

  test('researcher intent link opens the similarity preview guidance', async ({ page }) => {
    await page.goto('./orientation/hub/');

    await page.getByRole('link', { name: /Researchers quick intent link/i }).click();

    await expect(page).toHaveURL(/\/orientation\/similarity-preview\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /Similarity Preview/i })).toBeVisible();
  });

  test('quick path for evaluation opens quality and evaluation guidance', async ({ page }) => {
    await page.goto('./orientation/hub/');

    await page.getByRole('link', { name: /Go to Evaluate Prompt Quality/i }).click();

    await expect(page).toHaveURL(/\/orientation\/quality-evaluation\/?$/);
    await expect(page.getByRole('heading', { level: 1, name: /Quality & Evaluation/i })).toBeVisible();
  });
});
