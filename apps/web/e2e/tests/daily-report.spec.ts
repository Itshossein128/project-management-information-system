/**
 * FLOW: Daily report create and approval workflow (Sprint 4)
 * MODULE: Daily Reports
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
  createDailyReportViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

test.describe("Daily reports — Sprint 4", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("daily reports list page loads", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /گزارش.*روزانه/i })).toBeVisible();
    await expect(page.getByTestId("daily-report-new-btn")).toBeVisible();
  });

  test("new daily report form route renders tabs", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports/new`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-tab-activities")).toBeVisible();
    await expect(page.getByTestId("report-tab-labor")).toBeVisible();
    await expect(page.getByTestId("daily-report-save-header")).toBeVisible();
  });

  test("submit and approve workflow updates status", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-A1",
      name: "Daily Report Activity",
      wbsId,
      totalQuantity: 100,
    });
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Daily Report Activity",
      quantity: 25,
    });

    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("approval-status-bar")).toBeVisible();
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);

    await page.getByTestId("report-submit-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/ارسال|submitted/i, {
      timeout: 15_000,
    });

    await page.getByTestId("report-approve-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/تأیید|approved/i, {
      timeout: 15_000,
    });
  });
});
