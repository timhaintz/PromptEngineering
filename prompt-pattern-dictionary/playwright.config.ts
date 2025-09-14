import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/a11y',
  outputDir: 'test-results/a11y',
  timeout: 30000,
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'off'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
});
