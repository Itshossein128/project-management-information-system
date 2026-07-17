import { expect, test } from "@playwright/test";

/**
 * Sprint 12 smoke: economic dashboard tabs and Monte Carlo.
 */
test.describe("Sprint 12 — Economic Engine", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/mobile|phone|username/i).fill("+10000000001");
    await page.getByLabel(/password/i).fill("devpass123");
    await page.getByRole("button", { name: /sign in|login|ورود/i }).click();
    await page.waitForURL(/\/(home|projects)/);
  });

  async function firstProjectId(page: import("@playwright/test").Page) {
    await page.goto("/projects");
    const firstProject = page.locator('a[href*="/projects/"]').first();
    const href = await firstProject.getAttribute("href");
    if (!href) return null;
    return href.split("/")[2];
  }

  test("economic page loads overview profit layers", async ({ page }) => {
    const projectId = await firstProjectId(page);
    if (!projectId) {
      test.skip();
      return;
    }
    await page.goto(`/projects/${projectId}/economic`);
    await expect(page.getByRole("heading", { name: /تحلیل اقتصادی/i })).toBeVisible();
    await expect(page.getByTestId("economic-overview")).toBeVisible();
    await expect(page.getByText("سود حسابداری")).toBeVisible();
    await expect(page.getByText("سرمایه در گردش")).toBeVisible();
  });

  test("forecast tab loads EVM panel", async ({ page }) => {
    const projectId = await firstProjectId(page);
    if (!projectId) {
      test.skip();
      return;
    }
    await page.goto(`/projects/${projectId}/economic`);
    await page.getByRole("button", { name: /پیش‌بینی EVM/i }).click();
    await expect(page.getByTestId("economic-forecast")).toBeVisible();
  });

  test("monte carlo tab shows run button", async ({ page }) => {
    const projectId = await firstProjectId(page);
    if (!projectId) {
      test.skip();
      return;
    }
    await page.goto(`/projects/${projectId}/economic`);
    await page.getByRole("button", { name: /مونت‌کارلو/i }).click();
    await expect(page.getByTestId("monte-carlo-panel")).toBeVisible();
    await expect(page.getByTestId("run-simulation")).toBeVisible();
  });
});
