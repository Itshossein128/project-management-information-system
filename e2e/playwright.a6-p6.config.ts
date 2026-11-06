import { defineConfig, devices } from "@playwright/test";

if (!process.env.A6_P1_E2E_FIXTURES || !process.env.A6_P1_E2E_API || !process.env.A6_P1_E2E_WEB) {
  throw new Error("A6-P6 browser check reuses the isolated seeded stack; see e2e/a6-p1/run.py.");
}

export default defineConfig({
  testDir: "./tests",
  testMatch: "a6-p6-manager-path.e2e.spec.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  outputDir: "../test-results/a6-p6-manager",
  use: {
    ...devices["Desktop Chrome"],
    baseURL: process.env.A6_P1_E2E_WEB,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
