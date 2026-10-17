import { defineConfig, devices } from "@playwright/test";
import { resolve } from "node:path";

const root = resolve(__dirname, "..");

// This suite only needs the frontend: API responses are intercepted per test.
export default defineConfig({
  testDir: "./tests",
  testMatch: "project-activation-feedback.spec.ts",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 2,
  reporter: [
    ["list"],
    ["html", { outputFolder: `${root}/playwright-report/project-activation`, open: "never" }],
    ["json", { outputFile: `${root}/test-results/project-activation.json` }],
  ],
  outputDir: `${root}/test-results/project-activation`,
  use: {
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium-desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chrome", use: { ...devices["Pixel 5"] } },
  ],
  webServer: {
    command: "pnpm dev:web --host 127.0.0.1 --port 5173",
    cwd: root,
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
