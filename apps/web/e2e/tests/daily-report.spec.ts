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

const assertCautionStyle = async (badge: ReturnType<Page["locator"]>, dark: boolean) => {
  const style = await badge.evaluate((el, isDark) => {
    const probe = document.createElement("span");
    probe.style.color = `var(--palette-warning-${isDark ? "400" : "500"})`;
    probe.style.backgroundColor = "var(--muted)";
    document.body.append(probe);
    const cs = getComputedStyle(el);
    const expected = getComputedStyle(probe);
    const result = {
      shadow: cs.boxShadow,
      background: cs.backgroundColor,
      warning: expected.color,
      neutral: expected.backgroundColor,
      fontSize: parseFloat(cs.fontSize),
    };
    probe.remove();
    return result;
  }, dark);
  expect(style.shadow).toContain("inset");
  expect(style.shadow).toContain(style.warning);
  expect(style.background).toBe(style.neutral);
  expect(style.background).not.toBe("rgba(0, 0, 0, 0)");
  expect(style.fontSize).toBeLessThanOrEqual(12);
};

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

  test("daily report lifecycle: correction cancellation and version history", async ({ page }) => {
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

    const openRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/open/`, {
      headers,
      data: {
        report_date: reportDate,
      },
    });
    expect(openRes.ok()).toBeTruthy();
    const sub = (await openRes.json()) as { id: string };

    const updateRes = await page.request.patch(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${sub.id}/`,
      {
        headers,
        data: {
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
              transaction_type: "receipt",
              warehouse_document_reference: "REC-001",
              material_description: "سیمان",
              quantity: 2,
              unit: "کیسه",
              notes: "انبار A",
            },
          ],
        },
      },
    );
    expect(updateRes.ok()).toBeTruthy();

    const submitSub = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${sub.id}/submit/`,
      { headers },
    );
    expect(submitSub.ok()).toBeTruthy();

    const approveSub = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${sub.id}/approve/`,
      { headers },
    );
    expect(approveSub.ok()).toBeTruthy();

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
    const versionsPanel = page.getByTestId("report-versions-panel");
    await expect(versionsPanel).toBeVisible();
    await expect(versionsPanel).toContainText(/نسخه|Version/i);
    await expect(versionsPanel).toContainText("Admin");
    await expect(versionsPanel).toContainText(/ثبت اولیه|Initial submission/);
    await expect(versionsPanel).toContainText(/تأیید:\s*(?:۱۴۰\d|\d{4})|Approved:/i);
    await page.getByTestId("report-versions-btn").click();

    await page.getByTestId("report-correction-btn").click();
    await page.getByTestId("report-correction-reason").fill("اصلاح برای پوشش آزمون چرخه عمر گزارش");
    await page.getByTestId("report-correction-confirm-btn").click();
    await expect(page).toHaveURL(new RegExp(`/daily-reports/.+/edit`));
    const cancelDraftUrl = page.url();
    const cancelDraftId = cancelDraftUrl.match(/daily-reports\/([^/]+)\/edit/)?.[1]!;

    let cancelledDraftRequested = false;
    const requestListener = (req: import("@playwright/test").Request) => {
      if (req.url().includes(`/daily-reports/${cancelDraftId}/`)) {
        cancelledDraftRequested = true;
      }
    };

    await expect(page.getByTestId("report-correction-cancel-btn")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("report-correction-cancel-btn").click();
    await expect(page.getByTestId("report-correction-cancel-confirmation")).toBeVisible();

    page.on("request", requestListener);
    await page.getByTestId("report-correction-cancel-confirm-btn").click();
    await expect(page).toHaveURL(new RegExp(`/daily-reports/${reportId}/view`));
    page.off("request", requestListener);

    expect(cancelledDraftRequested).toBe(false);
    await expect(page.getByTestId("report-correction-cancel-btn")).toHaveCount(0);

    // T038: Full approved correction cycle with enriched version history lineage
    await page.getByTestId("report-correction-btn").click();
    await page.getByTestId("report-correction-reason").fill("اصلاح نهایی برای ثبت نسخه دوم");
    await page.getByTestId("report-correction-confirm-btn").click();
    await expect(page).toHaveURL(new RegExp(`/daily-reports/.+/edit`));
    const v2EditUrl = page.url();
    const v2ReportId = v2EditUrl.match(/daily-reports\/([^/]+)\/edit/)?.[1]!;

    // T036: Assert lineage metadata while v2 is still an unapproved draft
    await page.getByTestId("report-versions-btn").click();
    const draftV2History = page.getByTestId("report-versions-panel");
    await expect(draftV2History).toBeVisible();
    await expect(draftV2History).toContainText(/نسخه 2|Version 2/i, { timeout: 15_000 });
    await expect(draftV2History).toContainText("Admin");
    await expect(draftV2History).toContainText("اصلاح نهایی برای ثبت نسخه دوم");
    await expect(draftV2History).toContainText(/ثبت اولیه|Initial submission/);
    await expect(draftV2History).toContainText(/تأیید:\s*ثبت‌نشده|Approved:\s*Not available/);
    await expect(draftV2History).toContainText(/تأیید:\s*(?:۱۴۰\d|\d{4})|Approved:/i);
    await page.getByTestId("report-versions-btn").click();

    await page.getByTestId("report-submit-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/ارسال|submitted/i, { timeout: 15_000 });

    await page.getByTestId("report-approve-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|locked|تأیید|approved/i, { timeout: 15_000 });

    await page.getByTestId("report-versions-btn").click();
    const vHistoryPanel = page.getByTestId("report-versions-panel");
    await expect(vHistoryPanel).toBeVisible();
    await expect(vHistoryPanel).toContainText(/نسخه 2|Version 2/i, { timeout: 15_000 });
    await expect(vHistoryPanel).toContainText("Admin");
    await expect(vHistoryPanel).toContainText("اصلاح نهایی برای ثبت نسخه دوم");
    await expect(vHistoryPanel).toContainText(/ثبت اولیه|Initial submission/);
    await expect(vHistoryPanel).toContainText(/نسخه فعلی|جاری|Current version/);
    await expect(vHistoryPanel).toContainText(/تأیید:\s*(?:۱۴۰\d|\d{4})|Approved:/i);

    // Navigate to v1 read-only historical view
    await page.getByTestId("report-version-open-1").click();
    await expect(page).toHaveURL(new RegExp(`/daily-reports/${reportId}/view`));
    await expect(page.getByTestId("report-status-badge")).toContainText(/قفل|locked|تأیید|approved/i);
    await expect(page.getByTestId("report-correction-cancel-btn")).toHaveCount(0);
  });

  test("daily report lifecycle: draft v1 has no correction cancel control", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Draft Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-D1",
      name: "Draft Activity",
      wbsId,
      totalQuantity: 10,
    });
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Draft Activity",
      quantity: 5,
    });
    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-correction-cancel-btn")).toHaveCount(0);
  });

  test("daily report lifecycle: unset and zero quantity presentation", async ({ page }) => {
    const SCREENS_DIR = "../../specs/036-validation-codes-unset-semantics/screenshots";
    test.setTimeout(120_000);
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Qty Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-Q1",
      name: "Qty Activity",
      wbsId,
      totalQuantity: 20,
    });
    const headers = await authHeaders(page);
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Qty Activity",
      quantity: 0,
    });

    // Full coverage of the three-state matrix (spec 036 quantity-ui contract):
    // 1 measured false + null (unset), 2 measured true + zero (numeric),
    // 3 measured true + null (unset), 4 measured false + legacy numeric (unset),
    // 5 measured true + positive (numeric).
    await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: {
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Unset",
            unit: "m3",
            quantity: null,
            quantity_measured: false,
          },
          {
            row_number: 2,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Zero",
            unit: "m3",
            quantity: 0,
            quantity_measured: true,
          },
          {
            row_number: 3,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Measured Null",
            unit: "m3",
            quantity: null,
            quantity_measured: true,
          },
          {
            row_number: 4,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Legacy False Numeric",
            unit: "m3",
            // Supported writes normalize not-measured rows to a null quantity;
            // the legacy numeric shape is injected below via a read-response
            // fixture (rendering evidence only).
            quantity: null,
            quantity_measured: false,
          },
          {
            row_number: 5,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Positive",
            unit: "m3",
            quantity: 12.5,
            quantity_measured: true,
          },
        ],
      },
    });

    const rowFor = (scope: ReturnType<Page["getByTestId"]>, name: string) => scope.locator("tr", { hasText: name });
    // Edit-grid rows carry the description as an input value, not text;
    // match by display value via inputValue() (hasText cannot see input values).
    const editRowFor = async (name: string): Promise<ReturnType<Page["locator"]>> => {
      const rows = page.locator("tbody tr");
      const rowCount = await rows.count();
      for (let i = 0; i < rowCount; i++) {
        const row = rows.nth(i);
        if ((await row.locator("input[list]").first().inputValue()) === name) return row;
      }
      throw new Error(`Edit-grid row not found: ${name}`);
    };
    const UNSET_FA = "ثبت‌نشده";
    const UNSET_EN = "Unset";

    const checkSummaryCells = async (scope: ReturnType<Page["locator"]>, unsetText: string) => {
      const unsetRows = ["Qty Activity Unset", "Qty Activity Measured Null", "Qty Activity Legacy False Numeric"];
      for (const name of unsetRows) {
        const row = rowFor(scope, name);
        await expect(row.getByTestId("unset-quantity-badge")).toBeVisible();
        await expect(row.getByTestId("unset-quantity-badge")).toHaveText(unsetText);
      }
      // Positive numeric: no badge, numeric value retained.
      const positiveRow = rowFor(scope, "Qty Activity Positive");
      await expect(positiveRow.getByTestId("unset-quantity-badge")).toHaveCount(0);
      await expect(positiveRow.locator("td").nth(7)).toHaveText(/^12\.5(?:0+)?$/);
      // Explicit zero: no badge, recognizably numeric zero.
      const zeroRow = rowFor(scope, "Qty Activity Zero");
      await expect(zeroRow.getByTestId("unset-quantity-badge")).toHaveCount(0);
      await expect(zeroRow.locator("td").nth(7)).toHaveText(/^0(?:\.0+)?$/);
    };

    // Persian: exact per-cell labels.
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    const summaryView = page.getByTestId("daily-report-summary-view");
    await checkSummaryCells(summaryView, UNSET_FA);
    await assertCautionStyle(summaryView.getByTestId("unset-quantity-badge").first(), false);
    await page.screenshot({ path: `${SCREENS_DIR}/summary-fa-light.png`, fullPage: true });

    // Edit form badge + keyboard editing regression on numeric inputs.
    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    const unsetEditRow = page.locator("tbody tr").first();
    await expect(unsetEditRow.getByTestId("activity-quantity-editable")).toBeVisible();
    await expect(unsetEditRow.getByTestId("activity-quantity-editable").getByTestId("unset-quantity-badge")).toHaveText(UNSET_FA);

    const zeroEditRow = await editRowFor("Qty Activity Zero");
    await expect(zeroEditRow.getByTestId("activity-quantity-editable")).toHaveCount(0);
    const zeroInput = zeroEditRow.locator('input[type="number"]').last();
    await expect(zeroInput).toHaveValue(/^0(\.0+)?$/);
    await zeroInput.click();
    await page.keyboard.press("ControlOrMeta+a");
    await page.keyboard.type("7");
    await expect(zeroInput).toHaveValue(/^7(\.0+)?$/);
    await page.keyboard.press("ControlOrMeta+a");
    await page.keyboard.type("0");
    await expect(page.getByTestId("activity-quantity-readonly")).toHaveCount(0);

    // English: exact labels change, data does not.
    await page.evaluate(() => {
      localStorage.setItem("app-language", "en");
      localStorage.setItem("i18nextLng", "en");
    });
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    await checkSummaryCells(page.getByTestId("daily-report-summary-view"), UNSET_EN);
    await page.screenshot({ path: `${SCREENS_DIR}/summary-en-light.png`, fullPage: true });

    // Dark theme check + screenshot.
    await page.evaluate(() => {
      localStorage.setItem("app-language", "fa");
      localStorage.setItem("i18nextLng", "fa");
      localStorage.setItem("app-theme", "dark");
    });
    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    const darkBadge = (await editRowFor("Qty Activity Measured Null")).getByTestId("unset-quantity-badge");
    const darkBadgeStyle = await darkBadge.evaluate((el) => {
      const cs = window.getComputedStyle(el);
      return { boxShadow: cs.boxShadow };
    });
    expect(darkBadgeStyle.boxShadow).toMatch(/inset/);
    await page.screenshot({ path: `${SCREENS_DIR}/summary-fa-dark-edit.png`, fullPage: true });

    // Narrow viewport variant.
    await page.setViewportSize({ width: 420, height: 900 });
    await page.reload();
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await page.screenshot({ path: `${SCREENS_DIR}/summary-fa-dark-narrow.png`, fullPage: true });
    await page.setViewportSize({ width: 1280, height: 720 });

    // Drop the measured-null row so the real approval flow can pass, then
    // submit + approve through the real API.
    const repairRes = await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: {
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Unset",
            unit: "m3",
            quantity: null,
            quantity_measured: false,
          },
          {
            row_number: 2,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Zero",
            unit: "m3",
            quantity: 0,
            quantity_measured: true,
          },
          {
            row_number: 4,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Legacy False Numeric",
            unit: "m3",
            quantity: null,
            quantity_measured: false,
          },
          {
            row_number: 5,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Qty Activity Positive",
            unit: "m3",
            quantity: 12.5,
            quantity_measured: true,
          },
        ],
      },
    });
    expect(repairRes.ok()).toBeTruthy();
    const submitRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/submit/`, { headers });
    expect(submitRes.ok()).toBeTruthy();
    const approveRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/approve/`, { headers });
    expect(approveRes.ok()).toBeTruthy();

    // Read-response fixture for the legacy state that supported writes normalize
    // (measured false + numeric quantity). Rendering evidence only.
    const realReport = (await (
      await page.request.get(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, { headers })
    ).json()) as { activities: Array<{ activity_description: string; quantity?: string | number | null }> };
    const legacyFixture = JSON.parse(JSON.stringify(realReport));
    const legacyRow = legacyFixture.activities.find(
      (a: { activity_description: string }) => a.activity_description === "Qty Activity Legacy False Numeric",
    );
    expect(legacyRow).toBeTruthy();
    legacyRow.quantity = "5.0000";
    await page.route(`**/api/v1/projects/*/daily-reports/${reportId}/`, async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(legacyFixture) });
        return;
      }
      await route.continue();
    });

    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    // Read-only fixture matrix includes unsupported legacy combinations. GET
    // interception proves rendering only; the real report remains unchanged.
    const template = legacyFixture.activities[0];
    const cases = [
      { name: "Measured Null", quantity: null, measured: true, unset: true },
      { name: "Not Measured Null", quantity: null, measured: false, unset: true },
      { name: "Legacy False Zero", quantity: "0.0000", measured: false, unset: true },
      { name: "Legacy False Positive", quantity: "5.0000", measured: false, unset: true },
      { name: "Numeric Zero", quantity: 0, measured: true, unset: false },
      { name: "String Zero", quantity: "0.00", measured: true, unset: false },
      { name: "Positive", quantity: "12.5000", measured: true, unset: false },
    ];
    legacyFixture.activities = cases.map((item, index) => ({
      ...template, id: `fixture-${index}`, row_number: index + 1,
      activity_description: item.name, quantity: item.quantity, quantity_measured: item.measured,
    }));
    for (const locale of ["fa", "en"]) {
      for (const theme of ["light", "dark"]) {
        for (const width of [1280, 420]) {
          await page.setViewportSize({ width, height: 900 });
          await page.evaluate(({ locale, theme }) => {
            localStorage.setItem("i18nextLng", locale);
            localStorage.setItem("app-language", locale);
            localStorage.setItem("app-theme", theme);
          }, { locale, theme });
          const label = locale === "fa" ? UNSET_FA : UNSET_EN;
          for (const surface of ["view", "edit"]) {
            await page.goto(`${base}/daily-reports/${reportId}/${surface}`);
            await expect(page.getByTestId(surface === "view" ? "daily-report-summary-view" : "daily-report-form")).toBeVisible();
            for (const item of cases) {
              const cell = surface === "view"
                ? page.getByTestId("summary-activities").locator("tr").filter({ has: page.getByRole("cell", { name: new RegExp(`(?:^|— )${item.name}$`) }) }).locator("td").nth(7)
                : (await editRowFor(item.name)).getByTestId("activity-quantity-readonly");
              if (item.unset) {
                await expect(cell.getByTestId("unset-quantity-badge")).toHaveText(label);
                await assertCautionStyle(cell.getByTestId("unset-quantity-badge"), theme === "dark");
              } else {
                await expect(cell.getByTestId("unset-quantity-badge")).toHaveCount(0);
                await expect(cell).toHaveText(String(item.quantity));
              }
            }
            const quantityCell = surface === "view"
              ? page.getByTestId("summary-activities").locator("tbody tr").first().locator("td").nth(7)
              : page.getByTestId("activity-quantity-readonly").first();
            await quantityCell.scrollIntoViewIfNeeded();
            const table = surface === "view"
              ? page.getByTestId("summary-activities")
              : page.locator("table").filter({ has: page.getByTestId("activity-quantity-readonly") }).locator("..");
            await table.screenshot({ path: `${SCREENS_DIR}/quantity-${surface}-${locale}-${theme}-${width}.png` });
          }
        }
      }
    }
    const persisted = await (await page.request.get(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, { headers })).json();
    expect(persisted).toEqual(realReport);

  });

  test("daily report summary: general activity quantity unset vs zero (no measured flag)", async ({ page }) => {
    test.setTimeout(90_000);
    const SCREENS_DIR = "../../specs/036-validation-codes-unset-semantics/screenshots";
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Gen Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-GN1",
      name: "Gen Activity",
      wbsId,
      totalQuantity: 10,
    });
    const headers = await authHeaders(page);

    // Seed one null-quantity and one zero-quantity general activity via two
    // distinct specialty-unit reports (aggregated into one daily summary).
    const unitConfigs: Array<{ unit: "buildings" | "mechanical"; description: string; quantity: number | null }> = [
      { unit: "buildings", description: "General Null Qty", quantity: null },
      { unit: "mechanical", description: "General Zero Qty", quantity: 0 },
    ];
    for (const cfg of unitConfigs) {
      const openRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/units/${cfg.unit}/daily-reports/open/`, {
        headers,
        data: { report_date: "1404/04/26" },
      });
      expect(openRes.ok()).toBeTruthy();
      const unitReport = (await openRes.json()) as { id: string };
      const patchRes = await page.request.patch(
        `${API_BASE}/v1/projects/${projectId}/units/${cfg.unit}/daily-reports/${unitReport.id}/`,
        {
          headers,
          data: {
            weather_condition: "clear",
            activities: [
              {
                row_number: 1,
                shift: "shift_1",
                crew_name: "E2E crew",
                worker_count: 1,
                activity_description: `${cfg.description} Activity Row`,
                activity_ref: activityId,
                unit: "m3",
                quantity: 1,
              },
            ],
            general_activities: [
              {
                activity_description: cfg.description,
                location: "محل آزمون",
                quantity: cfg.quantity,
                unit: "m2",
                notes: "",
              },
            ],
          },
        },
      );
      expect(patchRes.ok()).toBeTruthy();
      const submitRes = await page.request.post(
        `${API_BASE}/v1/projects/${projectId}/units/${cfg.unit}/daily-reports/${unitReport.id}/submit/`,
        { headers },
      );
      expect(submitRes.ok()).toBeTruthy();
      const approveRes = await page.request.post(
        `${API_BASE}/v1/projects/${projectId}/units/${cfg.unit}/daily-reports/${unitReport.id}/approve/`,
        { headers },
      );
      expect(approveRes.ok()).toBeTruthy();
    }

    const ensureRes = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/?date=${encodeURIComponent("1404/04/26")}`,
      { headers },
    );
    expect(ensureRes.ok()).toBeTruthy();
    const ensured = (await ensureRes.json()) as { report_id?: string; id?: string };
    const reportId = ensured.report_id ?? ensured.id!;

    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 20_000 });
    const generalSection = page.getByTestId("summary-section-general");
    await expect(generalSection).toBeVisible();

    // Null quantity → unset badge (row nullability only; no measured flag invented).
    const nullRow = generalSection.locator("tr", { hasText: "General Null Qty" });
    await expect(nullRow.getByTestId("unset-quantity-badge")).toBeVisible();
    await expect(nullRow.getByTestId("unset-quantity-badge")).toHaveText("ثبت‌نشده");
    // Zero → numeric, no badge.
    const zeroRow = generalSection.locator("tr", { hasText: "General Zero Qty" });
    await expect(zeroRow.getByTestId("unset-quantity-badge")).toHaveCount(0);
    await expect(zeroRow.locator("td").nth(2)).toHaveText(/^0(?:\.0+)?$/);

    // English presentation.
    await page.evaluate(() => {
      localStorage.setItem("app-language", "en");
      localStorage.setItem("i18nextLng", "en");
    });
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 20_000 });
    const enNullRow = page.getByTestId("summary-section-general").locator("tr", { hasText: "General Null Qty" });
    await expect(enNullRow.getByTestId("unset-quantity-badge")).toHaveText("Unset");
    await page.screenshot({ path: `${SCREENS_DIR}/general-activities-en.png`, fullPage: true });
    for (const locale of ["fa", "en"]) {
      for (const theme of ["light", "dark"]) {
        for (const width of [1280, 420]) {
          await page.setViewportSize({ width, height: 900 });
          await page.evaluate(({ locale, theme }) => {
            localStorage.setItem("i18nextLng", locale);
            localStorage.setItem("app-language", locale);
            localStorage.setItem("app-theme", theme);
          }, { locale, theme });
          await page.reload();
          const section = page.getByTestId("summary-section-general");
          const badge = section.locator("tr", { hasText: "General Null Qty" }).locator("td").nth(2).getByTestId("unset-quantity-badge");
          await expect(badge).toHaveText(locale === "fa" ? "ثبت‌نشده" : "Unset");
          await assertCautionStyle(badge, theme === "dark");
          const quantity = section.locator("tr", { hasText: "General Zero Qty" }).locator("td").nth(2);
          await expect(quantity).toHaveText(/^0(?:\.0+)?$/);
          await expect(quantity.getByTestId("unset-quantity-badge")).toHaveCount(0);
          await badge.scrollIntoViewIfNeeded();
          await section.screenshot({ path: `${SCREENS_DIR}/general-${locale}-${theme}-${width}.png` });
        }
      }
    }

  });

  test("daily report validation codes: measured-null refusal and zero submit persist (API-backed)", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Val Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-V1",
      name: "Validation Activity",
      wbsId,
      totalQuantity: 30,
    });
    const headers = await authHeaders(page);
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Validation Base Row",
      quantity: 0,
    });

    // Two rows: one measured-but-unset (refuses submit), one explicit zero (valid).
    const patchRes = await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: {
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Validation Unset Row",
            unit: "m3",
            quantity: null,
            quantity_measured: true,
          },
          {
            row_number: 2,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Validation Zero Row",
            unit: "m3",
            quantity: 0,
            quantity_measured: true,
          },
        ],
      },
    });
    expect(patchRes.ok()).toBeTruthy();

    // UI refusal path: server-to-client feedback keeps the report in draft.
    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);

    await page.getByTestId("report-submit-btn").click();
    const refusalToast = page.locator('[role="alert"]').filter({ hasText: /مقدار کارکرد باید مشخص شود|Work quantity must be specified/ });
    await expect(refusalToast).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);

    // API refusal proof: stable code and unchanged persisted lifecycle.
    const apiSubmitRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/submit/`, { headers });
    expect(apiSubmitRes.status()).toBe(400);
    const refusalBody = (await apiSubmitRes.json()) as { error?: { code?: string; message?: string } };
    expect(refusalBody.error?.code).toBe("quantity_unset_invalid");

    // Repair the unset row to an explicit zero, then submit through the UI.
    const reportRes = await page.request.get(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, { headers });
    expect(reportRes.ok()).toBeTruthy();
    const full = (await reportRes.json()) as {
      activities: Array<{ id: string; activity_description: string }>;
    };
    const unsetRow = full.activities.find((a) => a.activity_description === "Validation Unset Row")!;
    const fillRes = await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: {
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Validation Unset Row",
            unit: "m3",
            quantity: 0,
            quantity_measured: true,
            // keep id so this patch updates the existing row instead of duplicating
            ...(unsetRow ? { id: unsetRow.id } : {}),
          },
          {
            row_number: 2,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Validation Zero Row",
            unit: "m3",
            quantity: 0,
            quantity_measured: true,
          },
        ],
      },
    });
    expect(fillRes.ok()).toBeTruthy();

    await page.reload();
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("report-submit-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/ارسال|submitted/i, { timeout: 15_000 });

    // Persistence proof after a hard reload.
    await page.reload();
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/ارسال|submitted/i);
    const reportUrl = `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`;
    const beforeDenied = await (await page.request.get(reportUrl, { headers })).json();
    const visitorLogin = await page.request.post(`${API_BASE}/auth/login/`, {
      data: { phone_number: E2E_USERS.visitor.phone, password: E2E_USERS.visitor.password },
    });
    expect(visitorLogin.ok()).toBeTruthy();
    const visitorToken = (await visitorLogin.json()).access;
    const visitorHeaders = { Authorization: `Bearer ${visitorToken}` };
    for (const action of ["submit", "reject"]) {
      const denied = await page.request.post(`${reportUrl}${action}/`, {
        headers: visitorHeaders, data: { reason: "valid denied reason" },
      });
      expect(denied.status()).toBe(403);
    }
    expect(await (await page.request.get(reportUrl, { headers })).json()).toEqual(beforeDenied);
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await page.getByTestId("report-reject-btn").click();
    await page.getByTestId("report-reject-reason").fill("  exactlyten  ");
    await page.getByTestId("report-reject-confirm-btn").click();
    await expect(page.getByTestId("report-status-badge")).toContainText(/رد|rejected/i);
    await page.reload();
    await expect(page.getByTestId("report-status-badge")).toContainText(/رد|rejected/i);
    const rejected = await (await page.request.get(reportUrl, { headers })).json();
    expect(rejected.status).toBe("rejected");
    expect(rejected.rejection_reason).toBe("exactlyten");
    expect(rejected.activities.every((row: { quantity: string }) => Number(row.quantity) === 0)).toBe(true);

  });

  test("daily report workflow feedback: real API refusal messages on form and view surfaces (exact FA/EN)", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Fdbk Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-F1",
      name: "Feedback Activity",
      wbsId,
      totalQuantity: 15,
    });
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Feedback Base Row",
      quantity: 0,
    });
    const headers = await authHeaders(page);

    // Force the real refusal: measured-but-unset row on a live report.
    const patchRes = await page.request.patch(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/`, {
      headers,
      data: {
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            activity_ref: activityId,
            activity_description: "Feedback Unset Row",
            unit: "m3",
            quantity: null,
            quantity_measured: true,
          },
        ],
      },
    });
    expect(patchRes.ok()).toBeTruthy();

    // Persian (default): exact refusal text through the form callback.
    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("report-submit-btn").click();
    await expect(
      page.locator('[role="alert"]').filter({ hasText: "مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود" }),
    ).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);

    // Same server code, English text after locale switch, still on the form surface.
    await page.evaluate(() => {
      localStorage.setItem("app-language", "en");
      localStorage.setItem("i18nextLng", "en");
    });
    await page.reload();
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("report-submit-btn").click();
    await expect(
      page.locator('[role="alert"]').filter({ hasText: "Work quantity must be specified; enter zero if no work was performed." }),
    ).toBeVisible({ timeout: 15_000 });

    // View surface callback with a real submission attempt (real API again).
    await page.evaluate(() => {
      localStorage.setItem("app-language", "fa");
      localStorage.setItem("i18nextLng", "fa");
    });
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("approval-status-bar")).toBeVisible();
    await page.getByTestId("report-submit-btn").click();
    await expect(
      page.locator('[role="alert"]').filter({ hasText: "مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود" }),
    ).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-status-badge")).toContainText(/پیش‌نویس|draft/i);
  });

  test("daily report workflow feedback: four known codes localized for unknown fallback (UI-only rendering evidence)", async ({ page }) => {
    test.setTimeout(120_000);
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR FbUI Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "DR-FUI1",
      name: "UI Feedback Activity",
      wbsId,
      totalQuantity: 15,
    });
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "UI Feedback Base Row",
      quantity: 0,
    });

    const SERVER_TEXT = "SERVER-ORIGINAL-fallback-proof";
    let currentPayload: { code: string; message: string } | null = null;
    await page.route(`**/api/v1/projects/*/daily-reports/*/submit/`, async (route) => {
      if (currentPayload) {
        await route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({ error: { code: currentPayload.code, message: currentPayload.message, details: { detail: [currentPayload.message] } } }),
        });
        return;
      }
      await route.continue();
    });
    await page.route(`**/api/v1/projects/*/daily-reports/*/reject/`, async (route) => {
      if (currentPayload) {
        await route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({ error: { code: currentPayload.code, message: currentPayload.message, details: { detail: [currentPayload.message] } } }),
        });
        return;
      }
      await route.continue();
    });

    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });

    // Each known code resolves to the exact dailyReports.validationErrors string,
    // NOT the server text: proves the client translation path.
    const faExpectations: Array<[string, string]> = [
      ["report_not_in_submittable_state", "فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند"],
      ["rejection_reason_required", "دلیل رد الزامی است"],
      ["rejection_reason_min_length_10", "دلیل رد باید حداقل ۱۰ کاراکتر باشد"],
      ["quantity_unset_invalid", "مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود"],
    ];
    for (const [code, faText] of faExpectations) {
      currentPayload = { code, message: SERVER_TEXT };
      await page.getByTestId("report-submit-btn").click();
      await expect(
        page.locator('[role="alert"]').filter({ hasText: faText }),
      ).toBeVisible({ timeout: 15_000 });
      await expect(page.locator('[role="alert"]').filter({ hasText: SERVER_TEXT })).toHaveCount(0);
      currentPayload = null;
    }

    // EN texts after a locale change (submit surface again).
    await page.evaluate(() => {
      localStorage.setItem("app-language", "en");
      localStorage.setItem("i18nextLng", "en");
    });
    const enExpectations: Array<[string, string]> = [
      ["report_not_in_submittable_state", "Only draft or rejected reports can be submitted."],
      ["rejection_reason_required", "Rejection reason is required."],
      ["rejection_reason_min_length_10", "Rejection reason must be at least 10 characters."],
      ["quantity_unset_invalid", "Work quantity must be specified; enter zero if no work was performed."],
    ];
    for (const [code, enText] of enExpectations) {
      currentPayload = { code, message: SERVER_TEXT };
      await page.reload();
      await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
      await page.getByTestId("report-submit-btn").click();
      await expect(
        page.locator('[role="alert"]').filter({ hasText: enText }),
      ).toBeVisible({ timeout: 15_000 });
      await expect(page.locator('[role="alert"]').filter({ hasText: SERVER_TEXT })).toHaveCount(0);
      currentPayload = null;
    }

    // Unknown API code keeps the existing fallback (server message, no translation).
    currentPayload = { code: "some_unrelated_unknown_code", message: SERVER_TEXT };
    await page.getByTestId("report-submit-btn").click();
    await expect(
      page.locator('[role="alert"]').filter({ hasText: SERVER_TEXT }),
    ).toBeVisible({ timeout: 15_000 });
    currentPayload = null;

    // Non-API error: broken response body keeps the generic/parse fallback.
    await page.route(`**/api/v1/projects/*/daily-reports/*/submit/`, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: "text/plain",
        body: "not-an-api-envelope-fallback",
      });
    });
    await page.getByTestId("report-submit-btn").click();
    await expect(
      page.locator('[role="alert"]').filter({ hasText: /not-an-api-envelope-fallback|Request failed/ }),
    ).toBeVisible({ timeout: 15_000 });

    // Reject callback of the view surface resolves through the same resolver.
    // The report is submitted via the real API; the reject endpoint is mocked.
    const headers = await authHeaders(page);
    const submitRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/submit/`, { headers });
    expect(submitRes.ok()).toBeTruthy();
    await page.evaluate(() => {
      localStorage.setItem("app-language", "fa");
      localStorage.setItem("i18nextLng", "fa");
    });
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("report-reject-btn")).toBeVisible();

    for (const surface of ["view", "edit"]) {
      for (const locale of ["fa", "en"]) {
        await page.evaluate((locale) => {
          localStorage.setItem("app-language", locale);
          localStorage.setItem("i18nextLng", locale);
        }, locale);
        const expectations = locale === "fa" ? faExpectations : enExpectations;
        for (const [code, message] of [...expectations, ["unknown_workflow_code", SERVER_TEXT]]) {
          currentPayload = { code, message: SERVER_TEXT };
          await page.goto(`${base}/daily-reports/${reportId}/${surface}`);
          await page.getByTestId("report-reject-btn").click();
          await page.getByTestId("report-reject-reason").fill("a valid reason for rendering");
          await page.getByTestId("report-reject-confirm-btn").click();
          await expect(page.locator('[role="alert"]').filter({ hasText: message })).toBeVisible();
          if (code !== "unknown_workflow_code") {
            await expect(page.locator('[role="alert"]').filter({ hasText: SERVER_TEXT })).toHaveCount(0);
          }
        }
      }
    }
    currentPayload = null;
    await page.route(`**/api/v1/projects/*/daily-reports/*/reject/`, (route) =>
      route.fulfill({ status: 400, contentType: "text/plain", body: "not-an-api-envelope-fallback" }),
    );
    await page.goto(`${base}/daily-reports/${reportId}/view`);
    await page.getByTestId("report-reject-btn").click();
    await page.getByTestId("report-reject-reason").fill("a valid reason for rendering");
    await page.getByTestId("report-reject-confirm-btn").click();
    await expect(page.locator('[role="alert"]').filter({ hasText: /not-an-api-envelope-fallback|Request failed/ })).toBeVisible();

  });
});
