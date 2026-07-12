/**
 * FLOW: Offline indicator visible (Sprint 5)
 * MODULE: Offline Sync
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Offline sync — Sprint 5 smoke", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("project shell shows connectivity indicator after login", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.locator("body")).toBeVisible();
    const indicator = page.getByTestId("offline-indicator");
    await expect(indicator).toBeVisible({ timeout: 15_000 });
    await expect(indicator).toContainText(/آنلاین|offline|online/i);
  });
});
