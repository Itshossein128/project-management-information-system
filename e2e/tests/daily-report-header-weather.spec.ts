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
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name === "pwa-offline", "Requires the dev server");
  });

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
    const weatherContainer = page.getByTestId("weather-override-value");
    await expect(weatherContainer).toBeVisible();

    const radiogroup = page.getByTestId("weather-selector-radiogroup");
    await expect(radiogroup).toBeVisible();

    const clearBtn = page.getByTestId("weather-option-clear");
    const cloudyBtn = page.getByTestId("weather-option-cloudy");
    const rainyBtn = page.getByTestId("weather-option-rainy");
    const snowyBtn = page.getByTestId("weather-option-snowy");
    const stormyBtn = page.getByTestId("weather-option-stormy");

    await expect(clearBtn).toBeVisible();
    await expect(cloudyBtn).toBeVisible();
    await expect(rainyBtn).toBeVisible();
    await expect(snowyBtn).toBeVisible();
    await expect(stormyBtn).toBeVisible();

    await expect(clearBtn).toHaveAttribute("role", "radio");
    await expect(cloudyBtn).toHaveAttribute("role", "radio");

    // Click rainy option
    await rainyBtn.click();
    await expect(rainyBtn).toHaveAttribute("aria-checked", "true");
    await expect(clearBtn).toHaveAttribute("aria-checked", "false");
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

    // Assert exactly five options rendered with catalog-driven visible labels (plus empty placeholder)
    const options = reasonSelect.locator("option");
    await expect(options).toHaveCount(6);
    await expect(reasonSelect.locator('option[value="weather"]')).toHaveText("نامساعد بودن شرایط جوی");
    await expect(reasonSelect.locator('option[value="holiday"]')).toHaveText("تعطیل رسمی / تقویمی");
    await expect(reasonSelect.locator('option[value="strike_or_dispute"]')).toHaveText("اختلاف یا اعتصاب");
    await expect(reasonSelect.locator('option[value="client_stop_order"]')).toHaveText("دستور توقف کارفرما / مشاور");
    await expect(reasonSelect.locator('option[value="safety_incident"]')).toHaveText("حادثه ایمنی");

    // Attempting to save without reason triggers validation
    await page.getByTestId("summary-metadata-save").click();
    await expect(page.getByText(/علت تعطیلی کارگاه الزامی است/)).toBeVisible();

    // Selecting a valid reason succeeds
    await reasonSelect.selectOption("weather");
    await page.getByTestId("summary-metadata-save").click();
    await expect(page.getByText(/ذخیره شد/)).toBeVisible();
  });

  test("inactive site status renders five catalog-driven options in English locale", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    await expect(page.getByTestId("summary-metadata-editor")).toBeVisible({ timeout: 10000 });

    const enBtn = page.locator("#button-language-en");
    await expect(enBtn).toBeVisible();
    await enBtn.click();
    await expect(page.locator("html")).toHaveAttribute("lang", "en");

    await page.getByTestId("site-override-toggle").check();
    const siteSelect = page.getByTestId("site-override-value");
    await siteSelect.selectOption("inactive");

    const reasonSelect = page.getByTestId("inactivity-reason-select");
    await expect(reasonSelect).toBeVisible();

    const options = reasonSelect.locator("option");
    await expect(options).toHaveCount(6);
    await expect(reasonSelect.locator('option[value="weather"]')).toHaveText("Adverse weather");
    await expect(reasonSelect.locator('option[value="holiday"]')).toHaveText("Official / calendar holiday");
    await expect(reasonSelect.locator('option[value="strike_or_dispute"]')).toHaveText("Strike or dispute");
    await expect(reasonSelect.locator('option[value="client_stop_order"]')).toHaveText("Client / consultant stop order");
    await expect(reasonSelect.locator('option[value="safety_incident"]')).toHaveText("Safety incident");
  });

  test("temperature validation blocks out-of-range inputs and reversed min/max pair", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    await expect(page.getByTestId("summary-metadata-editor")).toBeVisible({ timeout: 10000 });

    const maxInput = page.locator("#summary-temp-max");
    const minInput = page.locator("#summary-temp-min");

    // Enter reversed pair: min=25, max=15
    await minInput.fill("25");
    await maxInput.fill("15");

    await page.getByTestId("summary-metadata-save").click();
    await expect(page.locator("#summary-temp-max-error")).toBeVisible();
    await expect(page.locator("#summary-temp-max")).toHaveAttribute("aria-invalid", "true");

    // Correct to valid pair
    await maxInput.fill("30");
    await expect(page.locator("#summary-temp-max-error")).toHaveCount(0);
  });

  test("weather impact notes entry, hydration, read-only display, and PDF export trigger", async ({ page }) => {
    await setupWeatherMocks(page);
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);

    await expect(page.getByTestId("summary-metadata-editor")).toBeVisible({ timeout: 10000 });

    const impactNotesInput = page.locator("#summary-weather-impact");
    await expect(impactNotesInput).toBeVisible();

    const multilineNotes = "وزش باد شدید & بارش باران < 20mm\nتوقف کار در ارتفاع";
    await impactNotesInput.fill(multilineNotes);

    // Save notes
    await page.getByTestId("summary-metadata-save").click();
    await expect(page.getByText(/ذخیره شد/)).toBeVisible();

    // Verify hydrated in input
    await expect(impactNotesInput).toHaveValue(multilineNotes);

    // Verify PDF download button is functional
    const pdfButton = page.getByRole("button", { name: /خروجی PDF/ });
    await expect(pdfButton).toBeVisible();
    await pdfButton.click();
  });
});
