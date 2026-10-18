/**
 * FLOW: Offline indicator + sync conflicts (Sprint 5 / auto-summary)
 * MODULE: Offline Sync
 *
 * Blank project daily-report create is retired; offline tests must not open
 * `/daily-reports/new` or enqueue blank POST /daily-reports/.
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
    await expect(page.getByTestId("offline-indicator")).toHaveCount(0, {
      timeout: 15_000,
    });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });
    await context.setOffline(false);
  });

  test("list has no blank create; sync-conflicts route loads", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
    await expect(page.getByTestId("daily-report-open-by-date")).toBeVisible();

    await page.goto(`${base}/daily-reports/new`);
    await expect(page).toHaveURL(new RegExp(`${base}/daily-reports/?$`));

    await page.goto(`${base}/sync-conflicts`);
    await expect(page.locator("[data-testid='conflict-page-container']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("specialty-seeded summary is viewable; conflicts page after approve", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "Root Phase" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-A1",
      name: "Daily Report Activity",
      wbsId,
    });

    const reportDate = "1404/04/27";
    const reportId = await createDailyReportViaApi(page, base, {
      reportDate,
      activityId,
    });

    const projectId = base.split("/").pop()!;
    const headers = {
      Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem("auth_access_token"))}`,
      "Content-Type": "application/json",
    };
    const API_BASE = "http://127.0.0.1:8000/api";
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/status/`,
      { headers, data: { status: "approved" } },
    );

    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({
      timeout: 15_000,
    });

    await page.goto(`${base}/daily-reports/sync-conflicts`);
    await expect(page.getByTestId("conflict-page-container")).toBeVisible({
      timeout: 15_000,
    });
  });
});
