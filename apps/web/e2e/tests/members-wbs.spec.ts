/**
 * FLOW: Members & WBS page smoke (Sprint 2)
 * MODULE: Project Foundation
 * ROLES: admin
 */

import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

async function firstProjectHref(page: Page) {
  await page.goto("/projects");
  const firstProjectLink = page.locator('a[href*="/projects/"]').first();
  const href = await firstProjectLink.getAttribute("href");
  return href;
}

test.describe("Members & WBS — Sprint 2 smoke", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("project members page loads", async ({ page }) => {
    const href = await firstProjectHref(page);
    test.skip(!href, "No projects in dev database");

    await page.goto(`${href}/settings/members`);
    await expect(
      page.getByRole("heading", { name: /مدیریت اعضا|اعضا|members/i }).first(),
    ).toBeVisible({ timeout: 15_000 });
  });

  test("project WBS page loads", async ({ page }) => {
    const href = await firstProjectHref(page);
    test.skip(!href, "No projects in dev database");

    await page.goto(`${href}/wbs`);
    await expect(
      page.getByRole("heading", { name: /ساختار شکست کار|WBS/i }).first(),
    ).toBeVisible({ timeout: 15_000 });
  });
});
