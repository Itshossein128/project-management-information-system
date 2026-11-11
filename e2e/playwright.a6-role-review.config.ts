import { defineConfig, devices } from "@playwright/test";

if (!process.env.A6_P1_E2E_FIXTURES || !process.env.A6_P1_E2E_API || !process.env.A6_P1_E2E_WEB) {
  throw new Error("Use the isolated A6 runner with seed-role-review.py.");
}

export default defineConfig({
  testDir: "./tests",
  testMatch: ["a6-role-review.e2e.spec.ts", "a6-p6-manager-path.e2e.spec.ts"],
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 180_000,
  expect: { timeout: 10_000 },
  reporter: [["list"], ["json", { outputFile: "../test-results/a6-role-review/results.json" }]],
  outputDir: "../test-results/a6-role-review/artifacts",
  use: {
    ...devices["Desktop Chrome"], baseURL: process.env.A6_P1_E2E_WEB,
    actionTimeout: 15_000, navigationTimeout: 30_000,
    trace: "retain-on-failure", screenshot: "only-on-failure",
  },
});
