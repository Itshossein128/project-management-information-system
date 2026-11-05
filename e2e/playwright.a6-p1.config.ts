import { defineConfig, devices } from "@playwright/test";

if (!process.env.A6_P1_E2E_FIXTURES || !process.env.A6_P1_E2E_API || !process.env.A6_P1_E2E_WEB) {
  throw new Error("A6-P1 real E2E requires an isolated seeded database, API and web URLs; see e2e/a6-p1/README.md.");
}
export default defineConfig({
  testDir: "./tests",
  testMatch: "a6-p1-real.e2e.spec.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  outputDir: "../test-results/a6-p1-real",
  use: { ...devices["Desktop Chrome"], baseURL: process.env.A6_P1_E2E_WEB, trace: "retain-on-failure", screenshot: "only-on-failure" },
});
