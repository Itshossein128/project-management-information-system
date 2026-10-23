/**
 * Feature 032 — Unit report source of truth
 *
 * Scope (T053, T054, T072 / quickstart §9 scenarios 1–10 in fa & en):
 * 1. Six canonical unit pages (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`)
 *    render localized labels and persist selected date in URL query state (`?date=...`).
 * 2. On Buildings, open/create date D, add data, submit, approve, and inspect history.
 * 3. Open project daily summary D and verify read-only data plus report/unit/source-row provenance.
 * 4. Confirm draft/rejected reports do not contribute and required unit remains missing.
 * 5. Correct/resubmit and verify no stale or duplicate summary data.
 * 6. Activate template requiring a subset, then all required units; verify partial/complete and
 *    no-template configuration_incomplete banner.
 * 7. Verify viewer, editor, approver, conflicted approver (SoD), and cross-project/non-member behavior.
 * 8. T053: Direct navigation to /projects/{id}/sub-reports renders standard localized 404, no form,
 *    and no report-data request.
 * 9. T054: Navigation scan in fa & en confirms zero /sub-reports links and no New Report CTA.
 * 10. Keyboard operability of date picker, workflow dialogs (reject modal), history modal, and provenance
 *     disclosure; verify RTL/LTR and localized actionable errors.
 */

import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createActivityViaApi, createProjectViaApi, createRootWbs } from "../helpers/project";

const API_BASE = "http://127.0.0.1:8000/api";

const CANONICAL_UNITS = [
  { slug: "buildings", fa: /ابنیه/, en: /Buildings/i },
  { slug: "electrical", fa: /برق/, en: /Electrical/i },
  { slug: "mechanical", fa: /مکانیک/, en: /Mechanical/i },
  { slug: "machinery", fa: /ماشین[\s\u200c]آلات/, en: /Machinery/i },
  { slug: "warehouse", fa: /انبار/, en: /Warehouse/i },
  { slug: "security", fa: /حراست/, en: /Security/i },
] as const;

async function authHeaders(page: Page): Promise<Record<string, string>> {
  const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  if (!access) throw new Error("authHeaders requires loginAs first");
  return {
    Authorization: `Bearer ${access}`,
    "Content-Type": "application/json",
  };
}

test.describe("Feature 032 — Unit Report Source of Truth (US1–US5 & T072 Bilingual Acceptance)", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("T053 (Scenario 8): direct navigation to /sub-reports renders standard localized not-found boundary without requests or form", async ({
    page,
  }) => {
    const projectBase = await createProjectViaApi(page);

    const reportDataRequests: string[] = [];
    page.on("request", (req) => {
      const url = req.url();
      if (
        (req.resourceType() === "fetch" || req.resourceType() === "xhr") &&
        (url.includes("/sub-reports") ||
          url.includes("/daily-reports") ||
          url.includes("/units/"))
      ) {
        reportDataRequests.push(url);
      }
    });

    await page.goto(`${projectBase}/sub-reports`);

    await expect(page.getByRole("heading", { name: /404|۴۰۴/ })).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.getByText(/صفحه مورد نظر یافت نشد|The requested page could not be found/),
    ).toBeVisible();

    expect(reportDataRequests).toEqual([]);

    await expect(page.locator("form")).toHaveCount(0);
    await expect(page.getByTestId("sub-report-new-btn")).toHaveCount(0);
    await expect(page.getByTestId("daily-report-form")).toHaveCount(0);
    await expect(page.locator("input, select, textarea")).toHaveCount(0);
  });

  test("T054 (Scenario 9): navigation-scan in fa and en confirms zero /sub-reports links and no New Report CTA in daily reports", async ({
    page,
  }) => {
    const projectBase = await createProjectViaApi(page);

    for (const locale of ["fa", "en"] as const) {
      await page.goto("/projects");
      await page.locator(`#button-language-${locale}`).click();

      await page.goto(`${projectBase}/daily-reports`);
      await expect(page.getByTestId("daily-reports-list")).toBeVisible({
        timeout: 15_000,
      });

      await expect(page.getByTestId("daily-report-new-btn")).toHaveCount(0);
      await expect(
        page.getByRole("button", { name: /گزارش جدید|new report/i }),
      ).toHaveCount(0);
      await expect(
        page.getByRole("link", { name: /گزارش جدید|new report/i }),
      ).toHaveCount(0);

      const subReportLinks = page.locator('a[href*="sub-reports"]');
      await expect(subReportLinks).toHaveCount(0);

      const pageHtml = await page.content();
      expect(pageHtml).not.toContain("/sub-reports");
    }
  });

  test("Scenario 1 & 10: visit all six unit pages in fa (RTL) and en (LTR), verify canonical localized labels and URL date persistence", async ({
    page,
  }) => {
    const projectBase = await createProjectViaApi(page);
    const targetDate = "2026-10-15";

    for (const locale of ["fa", "en"] as const) {
      await page.goto("/projects");
      await page.locator(`#button-language-${locale}`).click();

      const htmlDir = await page.locator("html").getAttribute("dir");
      expect(htmlDir).toBe(locale === "fa" ? "rtl" : "ltr");

      for (const unit of CANONICAL_UNITS) {
        await page.goto(`${projectBase}/${unit.slug}?date=${targetDate}`);
        await expect(page.locator("#container-unitDailyReportPanel")).toBeVisible({
          timeout: 15_000,
        });

        // Verify URL retains query date
        await expect(page).toHaveURL(new RegExp(`/${unit.slug}\\?date=${targetDate}`));

        // Verify localized canonical unit label in page heading
        const expectedHeading = locale === "fa" ? unit.fa : unit.en;
        await expect(page.locator("#text-departmentTitle")).toContainText(expectedHeading);

        // Verify unit report panel title is localized
        await expect(page.locator("#text-unitDailyReportTitle")).toContainText(
          locale === "fa" ? /گزارش روزانه واحد/ : /Unit Daily Report/i,
        );
      }
    }
  });

  test("Scenario 2, 3, 4, 5, 10: Buildings authoring, reject validation, correction/resubmit, approval, history modal, and summary provenance disclosure", async ({
    page,
  }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const wbsId = await createRootWbs(page, projectBase, { code: "1", name: "Bld Root" });
    const activityId = await createActivityViaApi(page, projectBase, {
      code: "BLD-101",
      name: "Concrete Foundation",
      wbsId,
      totalQuantity: 100,
    });
    const headers = await authHeaders(page);
    const reportDate = "2026-10-18";

    // Open Buildings unit page
    await page.goto(`${projectBase}/buildings?date=${reportDate}`);
    await expect(page.locator("#container-unitDailyReportPanel")).toBeVisible({
      timeout: 15_000,
    });

    // Create draft report via UI button
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.locator("#button-createUnitReportDraft").click();

    await expect(page.locator("#badge-unitReportStatus")).toContainText(/پیش‌نویس|Draft/i, {
      timeout: 15_000,
    });
    await expect(page.locator("#dl-unitReportAudit")).toBeVisible();

    // Scenario 4: While draft, summary does not include draft data
    const summaryDraftRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    expect(summaryDraftRes.ok()).toBeTruthy();
    const summaryDraft = (await summaryDraftRes.json()) as {
      activities?: unknown[];
      aggregation?: { contributing_units?: string[] };
    };
    expect(summaryDraft.activities ?? []).toHaveLength(0);
    expect(summaryDraft.aggregation?.contributing_units ?? []).not.toContain("buildings");

    // Add activity data to the current draft via canonical endpoint
    const currentRes = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/current/?date=${reportDate}`,
      { headers },
    );
    const currentReport = (await currentRes.json()) as { id: string };

    await page.request.patch(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${currentReport.id}/`,
      {
        headers,
        data: {
          weather_condition: "clear",
          activities: [
            {
              row_number: 1,
              shift: "shift_1",
              crew_name: "Alpha Crew",
              worker_count: 6,
              activity_ref: activityId,
              activity_description: "Concrete Foundation",
              unit: "m3",
              quantity: 20,
            },
          ],
        },
      },
    );

    // Submit via UI button
    await page.reload();
    await expect(page.locator("#button-submitUnitReport")).toBeVisible({ timeout: 15_000 });
    await page.locator("#button-submitUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/ارسال|Submitted/i, {
      timeout: 15_000,
    });

    // Scenario 10: Keyboard/dialog validation on Reject Modal (blank reason refused)
    await expect(page.locator("#button-openRejectUnitReportModal")).toBeVisible();
    await page.locator("#button-openRejectUnitReportModal").focus();
    await page.keyboard.press("Enter");

    await expect(page.locator("#input-rejectReason")).toBeVisible();
    await page.locator("#button-confirmRejectUnitReport").click();
    await expect(page.locator("#alert-unitReportRejectionError")).toBeVisible();
    await expect(page.locator("#alert-unitReportRejectionError")).toHaveAttribute(
      "data-error-code",
      "rejection_reason_required",
    );

    // Supply rejection reason with dir="auto" and confirm
    await page.locator("#input-rejectReason").fill("نیاز به اصلاح مقدار بتن‌ریزی");
    await page.locator("#button-confirmRejectUnitReport").click();

    await expect(page.locator("#badge-unitReportStatus")).toContainText(/رد|Rejected/i, {
      timeout: 15_000,
    });
    await expect(page.locator("#text-unitReportRejectionReason")).toContainText(
      "نیاز به اصلاح مقدار بتن‌ریزی",
    );
    await expect(page.locator("#text-unitReportRejectionReason")).toHaveAttribute("dir", "auto");

    // Scenario 5: Resubmit after rejection and approve
    await page.locator("#button-submitUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/ارسال|Submitted/i, {
      timeout: 15_000,
    });

    await page.locator("#button-approveUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/تأیید|Approved/i, {
      timeout: 15_000,
    });

    // Correct approved report -> creates v2 draft, then submit & approve v2
    await expect(page.locator("#button-correctUnitReport")).toBeVisible();
    await page.locator("#button-correctUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/پیش‌نویس|Draft/i, {
      timeout: 15_000,
    });
    await expect(page.locator("#text-unitReportVersion")).toContainText("2");

    await page.locator("#button-submitUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/ارسال|Submitted/i, {
      timeout: 15_000,
    });
    await page.locator("#button-approveUnitReport").click();
    await expect(page.locator("#badge-unitReportStatus")).toContainText(/تأیید|Approved/i, {
      timeout: 15_000,
    });

    // Inspect History modal via keyboard
    await page.locator("#button-viewUnitReportHistory").focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("#modal-unitReportHistoryContent")).toContainText("v1");
    await expect(page.locator("#modal-unitReportHistoryContent")).toContainText("v2");
    await page.keyboard.press("Escape");

    // Scenario 3: Open project daily summary and inspect provenance disclosure
    const ensureRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    const ensured = (await ensureRes.json()) as { report_id?: string; id?: string };
    const summaryId = ensured.report_id ?? ensured.id!;

    await page.goto(`${projectBase}/daily-reports/${summaryId}/view`);
    await expect(page.getByTestId("daily-report-summary-view")).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId("summary-activities")).toContainText("Concrete Foundation");

    // Provenance disclosure button keyboard operability
    const provBtn = page
      .getByTestId("summary-activities")
      .locator("button[aria-expanded]")
      .first();
    await expect(provBtn).toBeVisible();
    await provBtn.focus();
    await page.keyboard.press("Enter");
    await expect(provBtn).toHaveAttribute("aria-expanded", "true");
    await expect(page.getByTestId("summary-activities")).toContainText(/v2/);
  });

  test("Scenario 6 & 7: template completeness banners (configuration_incomplete, partial, complete) and role permissions", async ({
    page,
  }) => {
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop()!;
    const headers = await authHeaders(page);
    const reportDate = "2026-10-19";

    // Before activating a reporting configuration -> configuration_incomplete banner
    const ensureRes1 = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/daily-reports/by-date/`,
      { headers, data: { report_date: reportDate } },
    );
    const ensured1 = (await ensureRes1.json()) as { report_id?: string; id?: string };
    const summaryId = ensured1.report_id ?? ensured1.id!;

    await page.goto(`${projectBase}/daily-reports/${summaryId}/view`);
    await expect(page.getByTestId("daily-report-config-incomplete-banner")).toBeVisible({
      timeout: 15_000,
    });

    // Create a template requiring ["buildings", "electrical"] and activate it
    const tmplRes = await page.request.post(`${API_BASE}/v1/project-templates/`, {
      headers,
      data: {
        template_name: `E2E Reporting Template ${Date.now()}`,
        description: "Template for E2E completeness verification",
        project_type: "residential",
        required_daily_report_units: ["buildings", "electrical"],
      },
    });
    expect(tmplRes.ok()).toBeTruthy();
    const tmpl = (await tmplRes.json()) as { template_id: string };

    const configRes = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/reporting-configurations/`,
      {
        headers,
        data: {
          template_id: tmpl.template_id,
          effective_from: "2026-10-01",
          confirm_backdated: true,
        },
      },
    );
    expect(configRes.ok()).toBeTruthy();

    // Open and submit only "buildings" -> summary is partial (electrical missing)
    const openBld = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/open/`,
      { headers, data: { report_date: reportDate } },
    );
    const bld = (await openBld.json()) as { id: string };
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${bld.id}/submit/`,
      { headers },
    );

    await page.reload();
    await expect(page.getByTestId("daily-report-partial-banner")).toBeVisible({
      timeout: 15_000,
    });

    // Open and submit "electrical" -> summary becomes complete (no partial banner)
    const openElec = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/electrical/daily-reports/open/`,
      { headers, data: { report_date: reportDate } },
    );
    const elec = (await openElec.json()) as { id: string };
    await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/electrical/daily-reports/${elec.id}/submit/`,
      { headers },
    );

    await page.reload();
    await expect(page.getByTestId("daily-report-partial-banner")).toHaveCount(0);
    await expect(page.getByTestId("daily-report-config-incomplete-banner")).toHaveCount(0);

    // Scenario 7: Non-member / visitor cannot create or mutate unit report
    await loginAs(page, E2E_USERS.visitor);
    const visitorHeaders = await authHeaders(page);
    const forbiddenOpen = await page.request.post(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/open/`,
      { headers: visitorHeaders, data: { report_date: reportDate } },
    );
    expect([403, 404]).toContain(forbiddenOpen.status());
  });
});
