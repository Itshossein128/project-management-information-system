/**
 * FLOW: Budget upsert, actual cost, variance, cost pool allocate (Sprint 7)
 * MODULE: Budget & Cost Control
 * ROLES: admin
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
  createActualCostViaApi,
  createBudgetViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

test.describe("Sprint 7 — Budget & Cost Control", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("costs page KPIs, budget upsert, actual, variance, pool allocate", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "Cost Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "A1",
      name: "Cost Activity",
      wbsId,
      totalQuantity: 100,
    });

    await page.goto(`${base}/costs`);
    await expect(page.getByRole("heading", { name: /کنترل هزینه/i })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("costs-kpi-grid")).toBeVisible();
    await expect(page.getByText("تعهدات")).toBeVisible();
    await expect(page.getByText("بودجه کل (BAC)")).toBeVisible();

    // Budget upsert via grid
    await expect(page.getByTestId("budget-grid")).toBeVisible();
    await expect(page.getByTestId("budget-cell-1-labor")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("budget-cell-1-labor").click();
    const budgetInput = page.getByTestId("budget-input-1-labor");
    await expect(budgetInput).toBeVisible();
    await budgetInput.fill("1000000");
    await budgetInput.press("Enter");
    await page.getByTestId("budget-save-btn").click();
    await expect(page.getByTestId("budget-cell-1-labor")).toContainText(/۱|1/, {
      timeout: 10_000,
    });

    // Actual cost via API (Jalali date picker is flaky under headless); verify in UI
    await createActualCostViaApi(page, base, {
      amount: 250_000,
      wbsId,
      costCategory: "labor",
      description: "E2E UI actual",
    });
    await page.getByTestId("costs-tab-actual").click();
    await expect(page.getByTestId("actual-costs-tab")).toBeVisible();
    await expect(page.getByText("E2E UI actual")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("actual-cost-add-btn").first()).toBeVisible();

    // Seed activity-level budget for pool allocate
    await createBudgetViaApi(page, base, {
      wbsId,
      activityId,
      costCategory: "site_overhead",
      budgetAmount: 500_000,
    });

    // Variance tab shows rows
    await page.getByTestId("costs-tab-variance").click();
    await expect(page.getByTestId("variance-tab")).toBeVisible();
    await expect(page.getByRole("cell", { name: /Cost Root/ })).toBeVisible({
      timeout: 15_000,
    });

    // Cost pool create + manual allocate
    await page.getByTestId("costs-tab-pools").click();
    await expect(page.getByTestId("cost-pool-tab")).toBeVisible();
    await page.getByTestId("cost-pool-new-btn").first().click();
    await expect(page.getByTestId("cost-pool-create-form")).toBeVisible();
    await page.getByTestId("cost-pool-name-input").fill("E2E Pool");
    await page.getByTestId("cost-pool-category").selectOption("site_overhead");
    await page.getByTestId("cost-pool-amount-input").fill("80000");
    await page.getByTestId("cost-pool-create-btn").click();
    await expect(page.getByText("E2E Pool")).toBeVisible({ timeout: 10_000 });

    await page.getByRole("button", { name: "تخصیص" }).first().click();
    await expect(page.getByTestId("cost-pool-allocation-wizard")).toBeVisible();
    await expect(page.getByTestId("cost-pool-auto-allocate")).toBeVisible();
    await page.getByTestId("cost-pool-allocate-activity").selectOption(activityId);
    await page.getByTestId("cost-pool-allocate-amount").fill("30000");
    const allocateRespPromise = page.waitForResponse(
      (r) =>
        r.url().includes("/allocate/") &&
        !r.url().includes("auto-allocate") &&
        r.request().method() === "POST",
      { timeout: 20_000 },
    );
    await page.getByTestId("cost-pool-allocate-confirm").click({ force: true });
    const allocateResp = await allocateRespPromise;
    expect(allocateResp.ok(), await allocateResp.text()).toBeTruthy();
    await expect(page.getByTestId("cost-pool-allocation-wizard")).toHaveCount(0, {
      timeout: 15_000,
    });
    await expect(page.getByRole("cell", { name: "E2E Pool" })).toBeVisible();
    await expect(page.getByText(/تخصیص جزئی|کامل/)).toBeVisible({ timeout: 10_000 });
  });
});
