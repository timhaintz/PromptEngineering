import { defineConfig, devices } from '@playwright/test';

const raw = process.env.PLAYWRIGHT_BASE_URL ?? 'https://www.timhaintz.com.au/PromptEngineering';
const baseURL = raw.endsWith('/') ? raw : `${raw}/`;

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }]
  ],
  timeout: 30_000,
  expect: {
    timeout: 10_000
  },
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    navigationTimeout: 20_000,
    actionTimeout: 10_000
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome']
      }
    }
  ]
});
