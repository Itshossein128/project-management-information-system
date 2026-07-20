/**
 * FLOW: Add actual cost form validation (Sprint 7)
 * MODULE: Finance / Cost Control
 * ROLES: view_costs, edit_costs
 * DECISION TREE:
 *   - Add actual cost (validation fail -> save button disabled)
 * BRANCHES TESTED: 1
 * BRANCHES DEFERRED: 14
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Finance — Budget & Cost (Validation)", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("add cost form validation requires amount and date", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/costs`);

    // Navigate to actual costs tab
    await page.getByTestId("costs-tab-actual").click();
    await page.getByTestId("actual-cost-add-btn").first().click();
    await expect(page.getByRole("dialog", { name: "ثبت هزینه جدید" })).toBeVisible();

    // The save button should be disabled initially (no date, no amount)
    await expect(page.getByRole("button", { name: "ذخیره" })).toBeDisabled();

    // Fill only date
    await page.locator('.rmdp-input').click();
    await page.locator('.rmdp-day').filter({ hasText: /^20$/ }).click();
    await expect(page.getByRole("button", { name: "ذخیره" })).toBeDisabled();

    // Fill only amount (clear date)
    await page.locator('.rmdp-input').fill(""); // Clear date by emptying input
    await page.locator('.rmdp-input').press('Enter');
    await page.locator('input[type="number"]').fill("5000");
    await expect(page.getByRole("button", { name: "ذخیره" })).toBeDisabled();

    // Fill both
    await page.locator('.rmdp-input').click();
    await page.locator('.rmdp-day').filter({ hasText: /^20$/ }).click();
    await expect(page.getByRole("button", { name: "ذخیره" })).toBeEnabled();
  });
});
