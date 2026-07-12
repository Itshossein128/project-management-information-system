/**
 * FLOW: Daily report create and list (Sprint 4)
 * MODULE: Daily Reports
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Daily reports — Sprint 4 smoke", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("daily reports list page loads", async ({ page }) => {
    await page.goto("/projects");
    const firstProjectLink = page.locator('a[href*="/projects/"]').first();
    const href = await firstProjectLink.getAttribute("href");
    test.skip(!href, "No projects in dev database");

    await page.goto(`${href}/daily-reports`);
    await expect(page.getByRole("heading", { name: /گزارش.*روزانه|daily/i })).toBeVisible({
      timeout: 15_000,
    });
  });

  test("new daily report form route renders", async ({ page }) => {
    await page.goto("/projects");
    const firstProjectLink = page.locator('a[href*="/projects/"]').first();
    const href = await firstProjectLink.getAttribute("href");
    test.skip(!href, "No projects in dev database");

    await page.goto(`${href}/daily-reports/new`);
    await expect(page.getByRole("button", { name: /فعالیت|نیروی انسانی/i }).first()).toBeVisible({
      timeout: 15_000,
    });
  });
});
