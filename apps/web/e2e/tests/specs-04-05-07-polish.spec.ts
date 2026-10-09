/**
 * FLOW: Specs 04/05/07 polish — WBS description/meta, near-critical legend, responsible_user
 * MODULE: WBS / Schedule / Daily reports
 * ROLES: admin
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createActivityViaApi,
  createDailyReportViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

test.describe("Specs 04/05/07 polish", () => {
  test.setTimeout(120_000);
  // Serial + 429 retry: auth login is 10/m IP-limited.
  test.describe.configure({ mode: "serial" });

  test.beforeEach(async ({ page }) => {
    let lastError: unknown;
    for (let attempt = 0; attempt < 8; attempt++) {
      try {
        await loginAs(page, E2E_USERS.admin);
        return;
      } catch (err) {
        lastError = err;
        if (!String(err).includes("429") || attempt === 7) throw err;
        await page.waitForTimeout(8_000);
      }
    }
    throw lastError;
  });

  test("WBS description editable and package-meta warning shown", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await createRootWbs(page, base, { code: "1", name: "Polish Root" });

    await page.goto(`${base}/wbs`);
    await expect(page.getByTestId("wbs-package-meta-warning")).toBeVisible({
      timeout: 15_000,
    });

    const row = page.getByTestId("wbs-row-1");
    await row.hover();
    await row.getByRole("button", { name: /ویرایش|Edit/i }).click();
    await expect(page.getByTestId("wbs-description-1")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("wbs-description-1").fill("E2E WBS description");
    const editor = page.getByTestId("wbs-node-1");
    await editor.getByRole("button", { name: /^ذخیره$|^Save$/i }).click();
    await expect(page.getByTestId("wbs-description-view-1")).toContainText(
      "E2E WBS description",
      { timeout: 10_000 },
    );
  });

  test("schedule status shows near-critical legend", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/schedule/status`);
    await expect(page.getByTestId("near-critical-legend")).toBeVisible({
      timeout: 20_000,
    });
  });

  test("activity tab can set responsible_user and persist", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const wbsId = await createRootWbs(page, base, { code: "1", name: "DR Root" });
    const activityId = await createActivityViaApi(page, base, {
      code: "A-RU",
      name: "Responsible User Activity",
      wbsId,
      totalQuantity: 10,
    });
    const reportId = await createDailyReportViaApi(page, base, {
      activityId,
      activityDescription: "Responsible User Activity",
      quantity: 1,
    });

    await page.goto(`${base}/daily-reports/${reportId}/edit`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("report-tab-activities").click();

    const responsibleSelect = page.getByTestId("activity-responsible-user").first();
    await expect(responsibleSelect).toBeVisible({ timeout: 15_000 });
    const options = responsibleSelect.locator("option:not([value=''])");
    await expect(options.first()).toBeAttached({ timeout: 10_000 });
    const value = await options.first().getAttribute("value");
    expect(value).toBeTruthy();

    const saveRespPromise = page.waitForResponse(
      (r) =>
        r.url().includes("/daily-reports/") &&
        r.url().includes("/activities/") &&
        ["POST", "PATCH", "PUT"].includes(r.request().method()),
      { timeout: 25_000 },
    );
    await responsibleSelect.selectOption(value!);
    await expect(responsibleSelect).toHaveValue(value!);
    // EditableGrid autosaves dirty rows (~900ms debounce)
    const saveResp = await saveRespPromise;
    expect(saveResp.ok()).toBeTruthy();

    const projectId = base.split("/").pop();
    const listRes = await page.request.get(
      `http://127.0.0.1:8000/api/v1/projects/${projectId}/daily-reports/${reportId}/`,
      {
        headers: {
          Authorization: `Bearer ${await page.evaluate(() =>
            localStorage.getItem("auth_access_token"),
          )}`,
        },
      },
    );
    expect(listRes.ok()).toBeTruthy();
    const detail = (await listRes.json()) as {
      activities?: Array<{ responsible_user?: string | null }>;
    };
    const users = (detail.activities ?? []).map((a) => a.responsible_user).filter(Boolean);
    expect(users).toContain(value);
  });
});
