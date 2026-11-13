import { defineConfig } from '@playwright/test';

if (!process.env.A7P6_BROWSER_FIXTURES) {
  throw new Error('Isolated P6 browser fixtures (A7P6_BROWSER_FIXTURES) are required');
}

export default defineConfig({
  testDir: './tests',
  testMatch: 'a7-p6-delivery-acceptance.spec.ts',
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 120_000,
  reporter: 'list',
  outputDir: '../test-results/a7-p6',
  use: {
    baseURL: 'http://127.0.0.1:15173',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
