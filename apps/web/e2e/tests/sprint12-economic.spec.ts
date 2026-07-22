/**
 * Sprint 12: economic dashboard — overview, forecast, financing, Monte Carlo, sensitivity.
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createActualCostViaApi, createProjectViaApi, createRootWbs } from "../helpers/project";

test.describe("Sprint 12 — Economic Engine", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("economic overview loads snapshot API", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const wbsId = await createRootWbs(page, base);
    await createActualCostViaApi(page, base, {
      amount: 2_500_000,
      costCategory: "labor",
      wbsId,
    });

    const snapPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/economic/snapshot/`) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/economic`);
    await expect(page.getByRole("heading", { name: /تحلیل اقتصادی/i })).toBeVisible();
    await expect(page.getByTestId("economic-overview")).toBeVisible();
    await expect(page.getByText("سود حسابداری")).toBeVisible();
    const snap = await snapPromise;
    expect(snap.ok()).toBeTruthy();
  });

  test("forecast tab loads EVM + WC + real cash-flow APIs", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;

    const forecastPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/economic/forecast/`) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/economic`);
    await page.getByRole("button", { name: /پیش‌بینی EVM/i }).click();
    await expect(page.getByTestId("economic-forecast")).toBeVisible();
    const forecast = await forecastPromise;
    expect(forecast.ok()).toBeTruthy();
    const body = await forecast.json();
    expect(body).toHaveProperty("eac_inflation_adjusted");
  });

  test("financing tab loads payment-delay data", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;
    const finPromise = page.waitForResponse(
      (r) =>
        (r.url().includes(`/projects/${projectId}/economic/financing-cost/`) ||
          r.url().includes(`/projects/${projectId}/economic/payment-delay/`)) &&
        r.request().method() === "GET",
    );
    await page.goto(`${base}/economic`);
    await page.getByRole("button", { name: /تأمین مالی/i }).click();
    const fin = await finPromise;
    expect(fin.ok()).toBeTruthy();
    const body = await fin.json();
    expect(body).toHaveProperty("total_financing_cost");
  });

  test("monte carlo run returns task and sensitivity tab can load", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const projectId = base.split("/").pop()!;

    await page.goto(`${base}/economic`);
    await page.getByRole("button", { name: /مونت‌کارلو/i }).click();
    await expect(page.getByTestId("monte-carlo-panel")).toBeVisible();

    const simulatePromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/economic/simulate/`) &&
        r.request().method() === "POST",
    );
    await page.getByTestId("run-simulation").click();
    const simulate = await simulatePromise;
    expect(simulate.status()).toBe(202);
    const simBody = await simulate.json();
    expect(simBody).toHaveProperty("task_id");

    await page.getByRole("button", { name: /حساسیت/i }).click();
    const sensPromise = page.waitForResponse(
      (r) =>
        r.url().includes(`/projects/${projectId}/economic/sensitivity/`) &&
        r.request().method() === "GET",
    );
    // Retap if already loaded once
    await page.getByRole("button", { name: /حساسیت/i }).click();
    const sens = await sensPromise;
    expect(sens.ok()).toBeTruthy();
  });
});
