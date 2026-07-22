/**
 * Sprint 9 smoke: cash flow, procurement, alerts, gantt, subcontractors.
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi, createRootWbs } from "../helpers/project";

test.describe("Sprint 9 — Cash Flow, Procurement, Alerts, Gantt, Subcontractors", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("cash flow page loads three tabs", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/cash-flow`);
    await expect(page.getByRole("heading", { name: /جریان نقدی/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "تراکنش‌ها" })).toBeVisible();
    await expect(page.getByRole("button", { name: /پیش‌بینی/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /تحلیل کمبود/i })).toBeVisible();
  });

  test("procurement page lists requests table", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/procurement`);
    await expect(page.getByTestId("procurement-page")).toBeVisible();
    await expect(page.getByRole("heading", { name: /تأمین و خرید/i })).toBeVisible();
  });

  test("alerts page loads active tab", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/alerts`);
    await expect(page.getByRole("heading", { name: /هشدارها/i })).toBeVisible();
  });

  test("gantt page loads with baseline compare toggle", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await createRootWbs(page, base, { code: "1", name: "Gantt Root" });
    await page.goto(`${base}/schedule/gantt`);
    await expect(page.getByRole("heading", { name: "گانت" })).toBeVisible();
    await expect(page.getByText("جدول مقایسه مبنا")).toBeVisible();
  });

  test("subcontractors registry page loads", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/subcontractors`);
    await expect(page.getByRole("heading", { name: /پیمانکاران فرعی/i })).toBeVisible();
  });
});
