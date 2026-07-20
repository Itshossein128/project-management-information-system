/**
 * FLOW: Progress dashboard KPI cards + S-curve (Sprint 6)
 * MODULE: Physical Progress & S-Curve
 * ROLES: admin
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Sprint 6 — Physical Progress & S-Curve", () => {
  test.setTimeout(90_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("progress page shows KPI grid and S-curve section", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/progress`);

    await expect(page.getByRole("heading", { name: /گزارش پیشرفت پروژه/i })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("progress-kpi-grid")).toBeVisible();
    await expect(page.getByText("پیشرفت فیزیکی")).toBeVisible();
    await expect(page.getByText(/SPI/)).toBeVisible();
    await expect(page.getByTestId("progress-s-curve")).toBeVisible();
    await expect(page.getByRole("heading", { name: /منحنی S/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /روزانه/i })).toBeVisible();
  });
});
