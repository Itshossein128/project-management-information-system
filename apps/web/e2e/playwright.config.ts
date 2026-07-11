import { defineConfig, devices } from "@playwright/test";

const WEB_PORT = 5173;
const API_URL = "http://127.0.0.1:8000/api";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { outputFolder: "./reports", open: "never" }]],
  use: {
    baseURL: `http://127.0.0.1:${WEB_PORT}`,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium-desktop",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
  webServer: [
    {
      command: "pnpm --filter api dev",
      url: "http://127.0.0.1:8000/api/schema/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      cwd: "../../..",
    },
    {
      command: "pnpm --filter web dev --host 127.0.0.1 --port 5173",
      url: "http://127.0.0.1:5173/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      cwd: "../../..",
    },
  ],
});
