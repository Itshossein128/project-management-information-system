/**
 * FLOW: Inactive Site Activity Conflict Guard (Spec 031 / User Story 2)
 * MODULE: Daily Reports
 * ROLES: editor, admin
 */

import { expect, test, type Page } from "@playwright/test";
import { session } from "../helpers/navigation";

const projectId = "55555555-5555-4555-8555-555555555555";
const reportId = "66666666-6666-4666-8666-666666666666";
const base = `/api/v1/projects/${projectId}`;

const project = {
  project_id: projectId,
  id: projectId,
  project_name: "Inactivity Guard Project",
  name: "Inactivity Guard Project",
  project_code: "IGP",
  slug: "igp",
  status: "active",
  currency: "IRR",
};

function createReport(siteStatus: "active" | "inactive") {
  return {
    report_id: reportId,
    id: reportId,
    project_id: projectId,
    report_date: "1405/06/27", // Jalali formatted for edit page
    day_of_week: "جمعه",
    shift: "full",
    work_front: "جبهه ۱",
    location_notes: "بلوک مرکزی",
    weather_condition: "clear",
    weather_condition_label: "صاف",
    temp_max: "28.0",
    temp_min: "16.0",
    site_status: siteStatus,
    site_status_label: siteStatus === "inactive" ? "غیرفعال" : "فعال",
    inactivity_reason: siteStatus === "inactive" ? "holiday" : null,
    inactivity_reason_label: siteStatus === "inactive" ? "تعطیل رسمی / تقویمی" : null,
    weather_impact_notes: "",
    general_notes: "روز تعطیل",
    management_opinion: "",
    weather_override: false,
    site_status_override: false,
    is_auto_summary: false,
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
}

async function setupGuardMocks(page: Page, initialReport: ReturnType<typeof createReport>) {
  const postedActivities: any[] = [];
  const currentReport = { ...initialReport };

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
      return route.fulfill({ json: currentReport });
    }

    if (path === `${base}/daily-reports/${reportId}/`) {
      return route.fulfill({ json: currentReport });
    }

    if (path.endsWith("/activities/")) {
      if (method === "POST") {
        const data = route.request().postDataJSON();
        postedActivities.push(data);
        const newRow = {
          id: `act-${postedActivities.length}`,
          ...data,
        };
        currentReport.activities = [...currentReport.activities, newRow] as any;
        return route.fulfill({ status: 201, json: newRow });
      }
      return route.fulfill({ json: { results: currentReport.activities } });
    }

    if (path.endsWith("/members/")) {
      return route.fulfill({ json: [] });
    }

    if (path.endsWith("/activities-lite/") || path.endsWith("/subcontractors/")) {
      return route.fulfill({ json: { results: [] } });
    }

    return route.fulfill({ json: { results: [] } });
  });

  return { postedActivities, currentReport };
}

test.describe("Inactive Site Activity Confirmation Guard", () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name === "pwa-offline", "Requires the dev server");
  });

  test.beforeEach(async ({ page }) => {
    await session(page, ["admin", "editor"], "fa");
  });

  test("inactive report + positive quantity prompts dialog with approved Persian copy; confirm saves row", async ({ page }) => {
    const { postedActivities } = await setupGuardMocks(page, createReport("inactive"));
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/edit`);

    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 10000 });

    // Add activity row
    await page.getByTestId("grid-add-row-btn").first().click();

    const row = page.locator("tbody tr").first();
    await expect(row).toBeVisible();

    // Fill quantity with positive number (15) - quantity is 2nd number input in the row
    const qtyInput = row.locator('input[type="number"]').nth(1);
    await qtyInput.fill("15");

    // Click Save
    const saveBtn = row.locator('button[title="ذخیره"]');
    await saveBtn.click();

    // Inactive-activity confirmation dialog appears
    const dialog = page.getByTestId("inactive-activity-confirm-dialog");
    await expect(dialog).toBeVisible();

    // Assert approved Persian copy verbatim
    await expect(dialog).toContainText(
      "کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟",
    );

    // Confirm save
    const confirmBtn = page.getByTestId("inactive-activity-confirm-btn");
    await confirmBtn.click();

    // Dialog closes and row is persisted via API
    await expect(dialog).toHaveCount(0);
    await expect.poll(() => postedActivities.length).toBe(1);
    expect(postedActivities[0].quantity).toBe(15);
  });

  test("inactive report + positive quantity cancel aborts save and retains in-progress entry", async ({ page }) => {
    const { postedActivities } = await setupGuardMocks(page, createReport("inactive"));
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/edit`);

    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 10000 });

    await page.getByTestId("grid-add-row-btn").first().click();
    const row = page.locator("tbody tr").first();
    await expect(row).toBeVisible();

    const qtyInput = row.locator('input[type="number"]').nth(1);
    await qtyInput.fill("20");

    const saveBtn = row.locator('button[title="ذخیره"]');
    await saveBtn.click();

    const dialog = page.getByTestId("inactive-activity-confirm-dialog");
    await expect(dialog).toBeVisible();

    // Click cancel
    const cancelBtn = page.getByTestId("inactive-activity-cancel-btn");
    await cancelBtn.click();

    await expect(dialog).toHaveCount(0);

    // No POST was made
    expect(postedActivities.length).toBe(0);

    // Input still retains in-progress value
    await expect(qtyInput).toHaveValue("20");
  });

  test("inactive report + zero quantity saves without confirmation dialog", async ({ page }) => {
    const { postedActivities } = await setupGuardMocks(page, createReport("inactive"));
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/edit`);

    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 10000 });

    await page.getByTestId("grid-add-row-btn").first().click();
    const row = page.locator("tbody tr").first();
    await expect(row).toBeVisible();

    const qtyInput = row.locator('input[type="number"]').nth(1);
    await qtyInput.fill("0");

    const saveBtn = row.locator('button[title="ذخیره"]');
    await saveBtn.click();

    // Dialog never appears
    await expect(page.getByTestId("inactive-activity-confirm-dialog")).toHaveCount(0);

    // Row is saved directly
    await expect.poll(() => postedActivities.length).toBe(1);
    expect(postedActivities[0].quantity).toBe(0);
  });

  test("active report + positive quantity saves without confirmation dialog", async ({ page }) => {
    const { postedActivities } = await setupGuardMocks(page, createReport("active"));
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/edit`);

    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 10000 });

    await page.getByTestId("grid-add-row-btn").first().click();
    const row = page.locator("tbody tr").first();
    await expect(row).toBeVisible();

    const qtyInput = row.locator('input[type="number"]').nth(1);
    await qtyInput.fill("50");

    const saveBtn = row.locator('button[title="ذخیره"]');
    await saveBtn.click();

    // Dialog never appears
    await expect(page.getByTestId("inactive-activity-confirm-dialog")).toHaveCount(0);

    await expect.poll(() => postedActivities.length).toBe(1);
    expect(postedActivities[0].quantity).toBe(50);
  });

  test("dialog chrome and body in English locale match approved English text and catalog keys", async ({ page }) => {
    await setupGuardMocks(page, createReport("inactive"));
    await page.goto(`/projects/${projectId}/daily-reports/${reportId}/edit`);

    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 10000 });

    const enBtn = page.locator("#button-language-en");
    await expect(enBtn).toBeVisible();
    await enBtn.click();
    await expect(page.locator("html")).toHaveAttribute("lang", "en");

    await page.getByTestId("grid-add-row-btn").first().click();
    const row = page.locator("tbody tr").first();
    await expect(row).toBeVisible();

    const qtyInput = row.locator('input[type="number"]').nth(1);
    await qtyInput.fill("12");

    const saveBtn = row.locator('button[title="ذخیره"], button[title="Save"], button[aria-label="ذخیره"], button[aria-label="Save"]');
    await saveBtn.click();

    const dialog = page.getByTestId("inactive-activity-confirm-dialog");
    await expect(dialog).toBeVisible();

    // Check English body text
    await expect(dialog).toContainText(
      "The site is marked inactive on this date; are you sure you want to record execution activity with positive volume?",
    );

    // Check English buttons
    await expect(page.getByTestId("inactive-activity-cancel-btn")).toHaveText("Cancel");
    await expect(page.getByTestId("inactive-activity-confirm-btn")).toHaveText("Confirm and save");
  });
});
