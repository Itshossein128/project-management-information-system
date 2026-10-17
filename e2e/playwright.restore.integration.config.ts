import { defineConfig, devices } from "@playwright/test";
import { resolve } from "node:path";

const root = resolve(__dirname, "..");

// Real API/PostgreSQL required on :8000; no intercepted restore responses.
export default defineConfig({
  testDir: "./tests",
  testMatch: "project-archive-restore.integration.spec.ts",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { outputFolder: `${root}/playwright-report/project-archive-restore-integration`, open: "never" }],
    ["json", { outputFile: `${root}/test-results/project-archive-restore-integration.json` }],
  ],
  outputDir: `${root}/test-results/project-archive-restore-integration`,
  use: {
    channel: process.env.RESTORE_BROWSER_CHANNEL === "chrome" ? "chrome" : undefined,
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
