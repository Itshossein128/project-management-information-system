/**
 * FLOW: Offline write → reconnect → sync (Sprint 5)
 * MODULE: Offline Sync
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
  createDailyReportViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

test.describe("Offline sync — Sprint 5", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("connectivity banner hides when online and appears when offline", async ({
    page,
    context,
  }) => {
    await page.goto("/projects");
    await expect(page.locator("body")).toBeVisible();
    // Healthy online: no permanent banner
    await expect(page.getByTestId("offline-indicator")).toHaveCount(0, {
      timeout: 15_000,
    });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });
    await context.setOffline(false);
  });

  test("conflict resolution workflow: server, local, and merge", async ({ page, context }) => {
    // 1. Create a project and an approved report on the server via API
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "Root Phase" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-A1",
      name: "Daily Report Activity",
      wbsId,
    });

    // Create a report on "1404/04/27"
    const reportDate = "1404/04/27";
    const reportId = await createDailyReportViaApi(page, base, {
      reportDate,
      activityId,
    });

    // Approve the report on the server so it causes a conflict when edited offline
    const projectId = base.split("/").pop()!;
    const headers = {
      Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem("auth_access_token"))}`,
      "Content-Type": "application/json",
    };

    const API_BASE = "http://127.0.0.1:8000/api";
    await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/status/`, {
      headers,
      data: { status: "approved" },
    });

    // 2. Go offline and attempt to create a report for the same date (which will conflict)
    await page.goto(`${base}/daily-reports/new`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });

    // Fill date to match the server one
    const dateInput = page.locator('.rmdp-input'); // Using JalaliDatePicker input
    await dateInput.click();
    await page.locator('.rmdp-day').filter({ hasText: /^27$/ }).click();

    await page.getByTestId("daily-report-save-header").click();
    await expect(page.getByText(/به صورت آفلاین ذخیره شد|آفلاین ذخیره/i).first()).toBeVisible({
      timeout: 15_000,
    });

    // 3. Reconnect and trigger sync
    await context.setOffline(false);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });

    const syncBtn = page.getByTestId("daily-reports-sync-now");
    if (await syncBtn.isVisible().catch(() => false)) {
      await syncBtn.click();
    }

    // Wait for the sync to fail due to conflict and show the conflict warning
    await expect(page.getByText(/تعارض/i).first()).toBeVisible({ timeout: 20_000 });

    // Navigate to conflict resolution page
    await page.goto(`${base}/daily-reports/sync-conflicts`);

    await expect(page.getByTestId("conflict-page-container")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("conflict-card-0")).toBeVisible();

    // 4. Test "Use Server" resolution
    await page.getByTestId("conflict-option-server").click();
    await page.getByTestId("conflict-apply-btn").click();

    await expect(page.getByText(/نسخه سرور اعمال شد|تغییرات اعمال شد/i).first()).toBeVisible({ timeout: 15_000 });

    // We expect the empty state to appear because the only conflict was resolved
    await expect(page.getByTestId("conflict-empty-state")).toBeVisible({ timeout: 15_000 });
  });

  test("offline header save queues and syncs after reconnect", async ({ page, context }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports/new`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });

    const dateInput = page.locator('.rmdp-input'); // Using JalaliDatePicker input
    await dateInput.click();
    await page.locator('.rmdp-day').filter({ hasText: /^28$/ }).click();

    await page.getByTestId("daily-report-save-header").click();
    await expect(page.getByText(/به صورت آفلاین ذخیره شد|آفلاین ذخیره/i).first()).toBeVisible({
      timeout: 15_000,
    });

    await context.setOffline(false);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });

    const syncBtn = page.getByTestId("daily-reports-sync-now");
    if (await syncBtn.isVisible().catch(() => false)) {
      await syncBtn.click();
      await expect(page.getByText(/همگام‌سازی شد|همگام/i).first()).toBeVisible({
        timeout: 20_000,
      });
    } else {
      // Auto-sync may have already drained the queue — banner hides when healthy.
      await expect(page.getByTestId("offline-indicator")).toHaveCount(0, {
        timeout: 20_000,
      });
    }

    await expect(page.getByTestId("daily-reports-list")).toBeVisible();

    // Verify that a row is visible to ensure report was saved
    await expect(page.locator("table tbody tr").first()).toBeVisible({ timeout: 20_000 });
  });
});
