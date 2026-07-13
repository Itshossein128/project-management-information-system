import { expect, test } from "@playwright/test";

/**
 * Sprint 10 smoke: materials balance, equipment utilization, HR leave list.
 */
test.describe("Sprint 10 — Resources smoke", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/mobile|phone|username/i).fill("+10000000001");
    await page.getByLabel(/password/i).fill("devpass123");
    await page.getByRole("button", { name: /sign in|login|ورود/i }).click();
    await page.waitForURL(/\/(home|projects)/);
  });

  test("material balance page loads with balance tab", async ({ page }) => {
    await page.goto("/projects");
    const firstProject = page.locator('a[href*="/projects/"]').first();
    const href = await firstProject.getAttribute("href");
    if (!href) {
      test.skip();
      return;
    }
    const projectId = href.split("/")[2];
    await page.goto(`/projects/${projectId}/material-balance`);
    await expect(page.getByRole("heading", { name: /بالانس مصالح/i })).toBeVisible();
    await expect(page.getByText("بالانس")).toBeVisible();
  });

  test("equipment utilization page loads summary cards", async ({ page }) => {
    await page.goto("/projects");
    const firstProject = page.locator('a[href*="/projects/"]').first();
    const href = await firstProject.getAttribute("href");
    if (!href) {
      test.skip();
      return;
    }
    const projectId = href.split("/")[2];
    await page.goto(`/projects/${projectId}/equipment-utilization`);
    await expect(page.getByRole("heading", { name: /بهره‌وری ماشین‌آلات/i })).toBeVisible();
  });

  test("leave requests page loads", async ({ page }) => {
    await page.goto("/projects");
    const firstProject = page.locator('a[href*="/projects/"]').first();
    const href = await firstProject.getAttribute("href");
    if (!href) {
      test.skip();
      return;
    }
    const projectId = href.split("/")[2];
    await page.goto(`/projects/${projectId}/leave-requests`);
    await expect(page.getByRole("heading", { name: /مرخصی/i })).toBeVisible();
  });
});
