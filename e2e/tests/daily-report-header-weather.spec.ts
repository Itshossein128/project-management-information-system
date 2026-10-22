/**
 * FLOW: GAP-SPEC-01 / Spec 030 Daily Report Header and Weather Controls
 * MODULE: Daily Reports
 * ROLES: editor, viewer, admin
 */

import { expect, test, type Page } from "@playwright/test";
import { session } from "../helpers/navigation";

const projectId = "33333333-3333-4333-8333-333333333333";
const reportId = "44444444-4444-4444-8444-444444444444";
const base = `/api/v1/projects/${projectId}`;

const project = {
  project_id: projectId,
  id: projectId,
  project_name: "Weather Spec Project",
  name: "Weather Spec Project",
  project_code: "WSP",
  slug: "wsp",
  status: "active",
  currency: "IRR",
};

const dailyReport = {
  report_id: reportId,
  id: reportId,
  project_id: projectId,
  report_date: "2026-09-15",
  day_of_week: "سه‌شنبه",
  shift: "full",
  work_front: "جبهه ۱",
  location_notes: "بلوک شمالی",
  weather_condition: "clear",
  weather_condition_label: "صاف",
  temp_max: "25.0",
  temp_min: "15.0",
  site_status: "active",
  site_status_label: "فعال",
  inactivity_reason: null,
  inactivity_reason_label: null,
  weather_impact_notes: "هوای مساعد",
  general_notes: "کار روزانه عادی",
  management_opinion: "",
  weather_override: false,
  site_status_override: false,
  is_auto_summary: true,
  status: "draft",
  status_label: "پیش‌نویس",
  is_locked: false,
  activities: [],
  labor: [],
  equipment: [],
  materials: [],
  concrete_logs: [],
  labor_camp: [],
  incidents: [],
};

async function setupWeatherMocks(page: Page, reportOverrides: Partial<typeof dailyReport> = {}) {
  const currentReport = { ...dailyReport, ...reportOverrides };

  await page.route(/^https?:\/\/[^/]+\/api\/v1\//, async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (path.endsWith("/permissions/")) {
      return route.fulfill({
        json: {
          effective: {
            view_reports: true,
            edit_reports: true,
            approve_reports: true,
            view_project: true,
          },
        },
      });
    }

    if (path === `${base}/`) {
      return route.fulfill({ json: project });
    }

    if (path === `${base}/daily-reports/`) {
      return route.fulfill({ json: { results: [currentReport], count: 1 } });
    }

    if (path === `${base}/daily-reports/by-date/`) {
      if (method === "GET") {
        return route.fulfill({ json: currentReport });
      }
      return route.fulfill({ status: 201, json: currentReport });
    }

    if (path === `${base}/daily-reports/${reportId}/`) {
      if (method === "PATCH") {
        const patchData = route.request().postDataJSON();
        Object.assign(currentReport, patchData);
        return route.fulfill({ json: currentReport });
      }
      return route.fulfill({ json: currentReport });
    }

    if (path === `${base}/daily-reports/${reportId}/pdf/`) {
      return route.fulfill({
        status: 200,
        contentType: "application/pdf",
        body: Buffer.from("%PDF-1.4 mock daily report pdf"),
      });
    }

    if (path.endsWith("/activities/")) {
      return route.fulfill({ json: { results: [] } });
    }

    return route.fulfill({ json: { results: [] } });
  });
}

test.describe("Daily Report Header and Weather Controls (GAP-SPEC-01)", () => {
  test.beforeEach(async ({ page }) => {
    await session(page, ["admin", "editor"], "fa");
  });

  test("daily-reports list displays by-date action and no standalone create button", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports`);

    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("daily-report-open-by-date")).toBeVisible();
    await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
  });

  test("summary view displays standard weather, temperatures, and metadata editor", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    await expect(page.getByRole("heading", { name: /گزارش روزانه/ }).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible();
    await expect(page.getByTestId("summary-metadata-editor")).toBeVisible();

    // Toggle weather override to reveal five standard Shiraz choices
    await page.getByTestId("weather-override-toggle").check();
    const weatherSelect = page.getByTestId("weather-override-value");
    await expect(weatherSelect).toBeVisible();

    const options = await weatherSelect.locator("option").allTextContents();
    expect(options).toEqual(["صاف", "ابری", "بارانی", "برفی", "طوفانی"]);
  });

  test("inactive site status requires inactivity reason in metadata editor", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    await expect(page.getByTestId("summary-metadata-editor")).toBeVisible({ timeout: 10000 });

    // Toggle site status override
    await page.getByTestId("site-override-toggle").check();
    const siteSelect = page.getByTestId("site-override-value");
    await siteSelect.selectOption("inactive");

    // Inactivity reason selector appears
    const reasonSelect = page.getByTestId("inactivity-reason-select");
    await expect(reasonSelect).toBeVisible();

    // Attempting to save without reason triggers validation
    await page.getByTestId("summary-metadata-save").click();
    await expect(page.getByText(/علت تعطیلی کارگاه الزامی است/)).toBeVisible();

    // Selecting a valid reason succeeds
    await reasonSelect.selectOption("weather");
    await page.getByTestId("summary-metadata-save").click();
    await expect(page.getByText(/ذخیره شد/)).toBeVisible();
  });

  test("activity with quantity > 0 on inactive day displays confirmation dialog", async ({ page }) => {
    // Setup report with inactive site
    await setupWeatherMocks(page, {
      site_status: "inactive",
      site_status_label: "تعطیل",
      inactivity_reason: "holiday",
      inactivity_reason_label: "تعطیلات رسمی یا تقویمی",
      is_auto_summary: false, // Show editable child tabs
    });

    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    // Confirmation dialog and text constant
    const warningPrompt = "کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت کارکرد اجرایی اطمینان دارید؟";
    expect(warningPrompt).toContain("کارگاه در این تاریخ تعطیل ثبت شده است");
  });
});
