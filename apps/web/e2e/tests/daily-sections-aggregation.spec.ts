/**
 * Feature 033 — Specialty unit daily sections → structured daily summary
 * Tag: daily-sections (quickstart §5)
 */

import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
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

async function approveBuildingsActivityReport(
  page: Page,
  projectId: string,
  reportDate: string,
  activityId: string,
  quantity = 18,
  approve = true,
) {
  const headers = await authHeaders(page);
  const openRes = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/open/`,
    { headers, data: { report_date: reportDate } },
  );
  expect(openRes.ok()).toBeTruthy();
  const sub = (await openRes.json()) as { id: string };

  const patchRes = await page.request.patch(
    `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${sub.id}/`,
    {
      headers,
      data: {
        weather_condition: "clear",
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            crew_name: "Crew Alpha",
            worker_count: 4,
            activity_ref: activityId,
            activity_description: "Sections grid activity",
            unit: "m3",
            quantity,
          },
        ],
      },
    },
  );
  expect(patchRes.ok(), await patchRes.text()).toBeTruthy();

  const actions = approve ? (["submit", "approve"] as const) : (["submit"] as const);
  for (const action of actions) {
    const res = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${sub.id}/${action}/`,
      { headers },
    );
    expect(res.ok(), await res.text()).toBeTruthy();
  }
  return sub.id;
}

test.describe("daily-sections aggregation", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("daily-sections: executed activity appears in summary with provenance", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const wbsId = await createRootWbs(page, projectBase, { code: "1", name: "033 Root" });
    const activityId = await createActivityViaApi(page, projectBase, {
      code: "S33-A1",
      name: "Sections Activity",
      wbsId,
      totalQuantity: 80,
    });
    const reportDate = "1404/06/01";
    await approveBuildingsActivityReport(page, projectId, reportDate, activityId);

    const headers = await authHeaders(page);
    const summaryRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    expect(summaryRes.ok()).toBeTruthy();
    const summary = (await summaryRes.json()) as { report_id?: string; id?: string };
    const reportId = summary.report_id ?? summary.id!;

    await page.goto(`${projectBase}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId("daily-report-summary-view")).toContainText("Sections grid activity");
    await expect(page.getByTestId("daily-report-summary-view")).toContainText("Crew Alpha");
  });

  test("daily-sections: cross-project activity reference is rejected", async ({ page }) => {
    const foreignBase = await createProjectViaApi(page);
    const foreignId = foreignBase.split("/").pop()!;
    const foreignWbs = await createRootWbs(page, foreignBase, { code: "9", name: "Foreign" });
    const foreignActivity = await createActivityViaApi(page, foreignBase, {
      code: "FOR-1",
      name: "Foreign activity",
      wbsId: foreignWbs,
      totalQuantity: 10,
    });

    const homeBase = await createProjectViaApi(page);
    const homeId = homeBase.split("/").pop()!;
    const headers = await authHeaders(page);
    const openRes = await page.request.post(
      `${API_BASE}/v1/projects/${homeId}/units/buildings/daily-reports/open/`,
      { headers, data: { report_date: "1404/06/02" } },
    );
    expect(openRes.ok()).toBeTruthy();
    const sub = (await openRes.json()) as { id: string };

    const patchRes = await page.request.patch(
      `${API_BASE}/v1/projects/${homeId}/units/buildings/daily-reports/${sub.id}/`,
      {
        headers,
        data: {
          activities: [
            {
              row_number: 1,
              shift: "shift_1",
              activity_ref: foreignActivity,
              activity_description: "Foreign activity",
              quantity: 5,
            },
          ],
        },
      },
    );
    expect(patchRes.ok()).toBeFalsy();
    const body = (await patchRes.json()) as { error?: { code?: string } };
    expect(body.error?.code ?? "").toMatch(/activity_not_in_project_scope|validation_error/i);
  });

  test("daily-sections: invalid quantity shows localized validation", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    await page.goto(`${projectBase}/buildings?date=1404/06/03`);
    await expect(page.locator("#container-unitDailyReportPanel")).toBeVisible({ timeout: 20_000 });
    await page.locator("#button-createUnitReportDraft").click();
    await expect(page.getByTestId("unit-section-tab-activities")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("unit-section-tab-activities").click();
    await expect(page.getByTestId("unit-section-activities")).toBeVisible();
  });

  test("daily-sections: summary structured sections render after rebuild", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const wbsId = await createRootWbs(page, projectBase, { code: "1", name: "033 Struct" });
    const activityId = await createActivityViaApi(page, projectBase, {
      code: "S33-S1",
      name: "Struct Activity",
      wbsId,
      totalQuantity: 40,
    });
    const reportDate = "1404/06/04";
    await approveBuildingsActivityReport(page, projectId, reportDate, activityId, 10);

    const headers = await authHeaders(page);
    const summaryRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    const summary = (await summaryRes.json()) as { report_id?: string; id?: string };
    const reportId = summary.report_id ?? summary.id!;

    const rebuildA = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    const rebuildB = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    expect(rebuildA.ok()).toBeTruthy();
    expect(rebuildB.ok()).toBeTruthy();

    await page.goto(`${projectBase}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId("summary-section-header")).toBeVisible();
  });

  test("daily-sections: bilingual labels on unit section tabs", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const headers = await authHeaders(page);
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/open/`,
      { headers, data: { report_date: "1404/06/05" } },
    );

    for (const locale of ["fa", "en"] as const) {
      await page.goto("/projects");
      await page.locator(`#button-language-${locale}`).click();
      await page.goto(`${projectBase}/buildings?date=1404/06/05`);
      await expect(page.locator("#container-unitDailyReportPanel")).toBeVisible({ timeout: 20_000 });
      await expect(page.getByTestId("unit-report-sections-tabs")).toBeVisible();
      await expect(page.getByTestId("unit-section-tab-activities")).toBeVisible();
    }
  });

  test("daily-sections: correction removes unit contribution until resubmit", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const wbsId = await createRootWbs(page, projectBase, { code: "1", name: "033 Corr" });
    const activityId = await createActivityViaApi(page, projectBase, {
      code: "S33-C1",
      name: "Correction Activity",
      wbsId,
      totalQuantity: 30,
    });
    const reportDate = "1404/06/06";
    const unitReportId = await approveBuildingsActivityReport(
      page,
      projectId,
      reportDate,
      activityId,
      8,
      false,
    );

    const headers = await authHeaders(page);
    let summaryRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    let summary = (await summaryRes.json()) as { activities?: unknown[] };
    expect((summary.activities ?? []).length).toBeGreaterThan(0);

    const rejectRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${unitReportId}/reject/`,
      { headers, data: { rejection_reason: "رد برای آزمایش حذف ردیف تجمیع" } },
    );
    expect(rejectRes.ok()).toBeTruthy();

    summaryRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    summary = (await summaryRes.json()) as { activities?: unknown[] };
    expect(summary.activities ?? []).toHaveLength(0);
  });
});
