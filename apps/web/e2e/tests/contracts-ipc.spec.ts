/**
 * FLOW: Contracts list and navigation (Sprint 8)
 * MODULE: Contracts & IPC
 * ROLES: admin (project_manager)
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Contracts — Sprint 8 smoke", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("contracts list page loads from project navigation", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByRole("heading", { name: /پروژه|project/i })).toBeVisible({
      timeout: 15_000,
    });

    const firstProjectLink = page.locator('a[href*="/projects/"]').first();
    const href = await firstProjectLink.getAttribute("href");
    test.skip(!href || !href.includes("/projects/"), "No projects in dev database");

    await firstProjectLink.click();
    await page.goto(`${href}/contracts`);
    await expect(page.getByRole("heading", { name: "قراردادها" })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByRole("button", { name: "قراردادها" })).toBeVisible();
    await expect(page.getByRole("button", { name: "صدور موقت" })).toBeVisible();
  });

  test("new contract form route renders", async ({ page }) => {
    await page.goto("/projects");
    const firstProjectLink = page.locator('a[href*="/projects/"]').first();
    const href = await firstProjectLink.getAttribute("href");
    test.skip(!href, "No projects in dev database");

    await page.goto(`${href}/contracts/new`);
    await expect(page.getByRole("heading", { name: "قرارداد جدید" })).toBeVisible({
      timeout: 15_000,
    });
  });
});
