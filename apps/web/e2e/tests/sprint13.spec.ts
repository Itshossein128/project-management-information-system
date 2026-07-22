/**
 * Sprint 13: executive KPIs, alerts catalog, overview dashboard.
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Sprint 13 — Executive Dashboard & Alerts Polish", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("overview loads unified KPIs panel", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const kpisPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/kpis/`) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/overview`);
    const resp = await kpisPromise;
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body).toHaveProperty("panel");
    expect(body).toHaveProperty("physical_progress");
    expect(body).toHaveProperty("cash");
    await expect(page.getByTestId("executive-kpi-panel")).toBeVisible();
    await expect(page.getByText(/داشبورد اجرایی/i)).toBeVisible();
  });

  test("alerts page lists sprint13 rule types", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    await page.goto(`${base}/alerts`);
    await expect(page.getByRole("heading", { name: /هشدارها/i })).toBeVisible();

    const rulesPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/alert-rules/`) &&
        r.request().method() === "GET",
    );
    await page.getByRole("button", { name: /قوانین/i }).click();
    const resp = await rulesPromise;
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    const types = new Set((body.results ?? []).map((r: { alert_type: string }) => r.alert_type));
    expect(
      types.has("critical_path_delay") ||
        types.has("ipc_approval_delayed") ||
        types.has("procurement_overdue") ||
        types.size >= 10,
    ).toBeTruthy();

    await page.getByRole("button", { name: /افزودن قانون هشدار/i }).click();
    await page.getByRole("combobox").first().click();
    await expect(page.getByRole("option", { name: /مسیر بحرانی/i })).toBeVisible();
    await expect(page.getByRole("option", { name: /تأیید IPC/i })).toBeVisible();
    await expect(page.getByRole("option", { name: /تأمین و خرید/i })).toBeVisible();
  });

  test("health alias returns same shape as kpis", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
    const headers = { Authorization: `Bearer ${access}` };
    const [kpis, health] = await Promise.all([
      page.request.get(`http://127.0.0.1:8000/api/v1/projects/${projectId}/kpis/`, { headers }),
      page.request.get(`http://127.0.0.1:8000/api/v1/projects/${projectId}/health/`, { headers }),
    ]);
    expect(kpis.ok()).toBeTruthy();
    expect(health.ok()).toBeTruthy();
    const a = await kpis.json();
    const b = await health.json();
    expect(Object.keys(a).sort()).toEqual(Object.keys(b).sort());
  });
});
