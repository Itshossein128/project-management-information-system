/**
 * Sprint 11: subcontractors, risk register, documents/correspondence.
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Sprint 11 — Risks & Documents", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("risk register page loads matrix API", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const matrixPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/risk-events/matrix/`) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/risk-register`);
    await expect(page.getByRole("heading", { name: /ریسک و تأخیر/i })).toBeVisible();
    const resp = await matrixPromise;
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body).toHaveProperty("matrix");
    expect(body).toHaveProperty("total_open");
  });

  test("documents page loads archive and correspondence tabs", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const docsPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/documents/`) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/documents`);
    await expect(page.getByRole("heading", { name: /مدارک و مکاتبات/i })).toBeVisible();
    const docsResp = await docsPromise;
    expect(docsResp.ok()).toBeTruthy();
    await page.getByRole("tab", { name: /مکاتبات/i }).click();
    await expect(page.getByText(/باز/i).first()).toBeVisible();
  });

  test("subcontractors registry still loads", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/subcontractors`);
    await expect(page.getByRole("heading", { name: /پیمانکار/i })).toBeVisible();
  });
});
