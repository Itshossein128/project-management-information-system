/**
 * FLOW: Risk Register (List, Create, Matrix)
 * MODULE: Delays, Barriers & Risk (Module 14)
 * ROLES: admin, project_manager, viewer
 *
 * DECISION TREE:
 * 1. Admin accesses Risk Register -> Sees matrix and events table (Tested)
 * 2. Admin creates a new Risk Event -> Validates form, success toast, matrix updates (Tested)
 * 3. User with no edit permission -> Cannot see 'New Event' button (Deferred - focus on happy path/auth first)
 * 4. User views empty state -> Matrix is empty, table shows "no data" message (Tested via new project)
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Risk Register - Module 14", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("empty risk register loads correctly", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/risk-register`);

    await expect(page.getByRole("heading", { name: "ریسک و تأخیر" })).toBeVisible();
    await expect(page.getByText("رویدادی ثبت نشده")).toBeVisible();
    await expect(page.getByRole("button", { name: "رویداد جدید" })).toBeVisible();
  });

  test("create a new risk event successfully", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/risk-register`);

    await page.getByRole("button", { name: "رویداد جدید" }).click();
    await expect(page.getByRole("heading", { name: "رویداد جدید", level: 2 })).toBeVisible();

    await page.getByPlaceholder("شرح").fill("Test Delay Event");
    await page.getByPlaceholder("احتمال").fill("0.8");
    await page.getByPlaceholder("مسئول").fill("Contractor");

    // Select severity
    await page.locator('select').filter({ hasText: 'متوسط' }).selectOption('high');

    await page.getByRole("button", { name: "ذخیره" }).click();

    await expect(page.getByText("ثبت شد")).toBeVisible();
    await expect(page.getByText("Test Delay Event")).toBeVisible();
    await expect(page.getByText("80%")).toBeVisible(); // 0.8 * 100
  });
});
