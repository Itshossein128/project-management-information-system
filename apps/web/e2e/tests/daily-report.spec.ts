/**
 * FLOW: Daily report auto-summary and approval workflow
 * MODULE: Daily Reports
 */

import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
  createDailyReportViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

const API_BASE = "http://127.0.0.1:8000/api";

async function authHeaders(page: Page): Promise<Record<string, string>> {
  const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  if (!access) throw new Error("authHeaders requires loginAs first");
  return {
    Authorization: `Bearer ${access}`,
    "Content-Type": "application/json",
  };
}

test.describe("Daily reports — auto summary", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("list has no new-report button for any role", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
    await expect(page.getByTestId("daily-report-open-by-date")).toBeVisible();

    await loginAs(page, E2E_USERS.visitor);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
  });

  test("daily reports list page loads with by-date control", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /گزارش.*روزانه/i })).toBeVisible();
    await expect(page.getByTestId("daily-report-open-by-date")).toBeVisible();
  });

  test("/daily-reports/new redirects away from blank create form", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports/new`);
    await expect(page).toHaveURL(new RegExp(`${base}/daily-reports/?$`));
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-form")).toHaveCount(0);
  });

  test("submit and approve workflow updates status on summary view", async ({ page }) => {
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

    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("approval-status-bar")).toBeVisible();
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);

    await page.getByTestId("report-submit-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/ارسال|submitted/i, {
      timeout: 15_000,
    });

    await page.getByTestId("report-approve-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|تأیید|approved|locked/i, {
      timeout: 15_000,
    });
    await expect(page.getByTestId("approval-status-bar")).toContainText(/قفل/);
  });

  test("gap closure smoke: specialty seed, by-date, approve, versions", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Gaps Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-G1",
      name: "Gaps Activity",
      wbsId,
      totalQuantity: 50,
    });
    const headers = await authHeaders(page);
    const reportDate = "1404/05/01";

    const subRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/sub-reports/`, {
      headers,
      data: {
        report_date: reportDate,
        discipline: "civil",
        weather_condition: "clear",
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            crew_name: "Crew",
            worker_count: 2,
            activity_ref: activityId,
            activity_description: "Gaps Activity",
            unit: "m3",
            quantity: 12,
          },
        ],
        labor_entries: [
          {
            labor_category: "direct",
            job_title: "کارگر",
            present_count: 3,
            leave_count: 1,
          },
        ],
        material_entries: [
          {
            material_description: "سیمان",
            quantity: 2,
            unit: "کیسه",
            notes: "انبار A",
          },
        ],
      },
    });
    expect(subRes.ok()).toBeTruthy();
    const sub = (await subRes.json()) as { id: string };
    const submitSub = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/sub-reports/${sub.id}/submit/`,
      { headers },
    );
    expect(submitSub.ok()).toBeTruthy();

    const ensureRes = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/?date=${encodeURIComponent(reportDate)}`,
      { headers },
    );
    expect(ensureRes.ok()).toBeTruthy();
    const ensured = (await ensureRes.json()) as { report_id?: string; id?: string };
    const reportId = ensured.report_id ?? ensured.id!;

    await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: { work_front: "جبهه شرقی" },
    });

    const submitRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/submit/`,
      { headers },
    );
    expect(submitRes.ok()).toBeTruthy();
    const approveRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/approve/`,
      { headers },
    );
    expect(approveRes.ok()).toBeTruthy();

    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|locked|تأیید|approved/i);
    await expect(page.getByTestId("report-correction-btn")).toBeVisible();

    await page.getByTestId("report-versions-btn").click();
    await expect(page.getByTestId("report-versions-panel")).toBeVisible();
    await expect(page.getByTestId("report-versions-panel")).toContainText(/نسخه/);
  });
});
