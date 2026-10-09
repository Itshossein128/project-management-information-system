/**
 * FLOW: Daily report create and approval workflow (Sprint 4)
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

test.describe("Daily reports — Sprint 4", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("visitor cannot see new report button", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await loginAs(page, E2E_USERS.visitor);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
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
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|تأیید|approved|locked/i, {
      timeout: 15_000,
    });
    await expect(page.getByTestId("approval-status-bar")).toContainText(/قفل/);
  });

  test("gap closure smoke: work front, versions, correction, materials recon", async ({ page }) => {
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

    const createRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/`, {
      headers,
      data: {
        report_date: "1404/05/01",
        shift: "full",
        site_status: "active",
        weather_condition: "sunny",
        work_front: "جبهه شرقی",
      },
    });
    expect(createRes.ok()).toBeTruthy();
    const created = (await createRes.json()) as { report_id?: string; id?: string };
    const reportId = created.report_id ?? created.id!;

    const activityRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/activities/`,
      {
        headers,
        data: {
          activity_ref: activityId,
          activity_description: "Gaps Activity",
          shift: "shift_1",
          quantity: 12,
          quantity_measured: true,
          unit: "m3",
          responsible_name: "سرپرست الف",
        },
      },
    );
    expect(activityRes.ok()).toBeTruthy();

    await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/labor/`, {
      headers,
      data: {
        labor_category: "direct",
        job_title: "کارگر",
        shift_1_count: 3,
        absence_count: 1,
      },
    });
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/materials/`,
      {
        headers,
        data: {
          material_description: "سیمان",
          transaction_type: "return",
          quantity: 2,
          unit: "کیسه",
          consumption_location: "انبار A",
        },
      },
    );
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/incidents/`,
      {
        headers,
        data: {
          incident_type: "barrier",
          description: "مانع دسترسی به جبهه",
          corrective_action: "مسیر جایگزین",
          follow_up_owner_name: "ناظر ب",
          due_date: "1403/07/13",
        },
      },
    );

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

    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|locked/i);
    await expect(page.getByTestId("report-correction-btn")).toBeVisible();

    await page.getByTestId("report-versions-btn").click();
    await expect(page.getByTestId("report-versions-panel")).toBeVisible();
    await expect(page.getByTestId("report-versions-panel")).toContainText(/نسخه/);

    await page.getByTestId("report-tab-materials").click();
    await expect(page.getByTestId("materials-reconciliation-panel")).toBeVisible({ timeout: 10_000 });
  });
});
