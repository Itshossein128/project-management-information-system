/**
 * FLOW: Progress dashboard KPI cards + S-curve (Sprint 6)
 * MODULE: Physical Progress & S-Curve
 * ROLES: admin, visitor
 *
 * DECISION TREE:
 * 1. Navigate to /projects/{projectId}/progress
 * 2. Assert page RTL layout
 * 3. As admin:
 *   ├─ View KPI grid and S-Curve sections
 *   ├─ Check "فقط تأخیردار" checkbox and assert behavior
 *   └─ View manual progress button
 * 4. As visitor (no edit permissions):
 *   └─ Assert manual progress button is hidden
 *
 * BRANCHES TESTED:
 * - Admin view loads (1/10)
 * - RTL layout (2/10)
 * - Behind-only checkbox toggles successfully (3/10)
 * - Visitor lacks edit access to manual progress (4/10)
 * BRANCHES DEFERRED:
 * - Manual progress submission form flow
 * - History view checks
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

    // RTL layout validation
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");

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

  test("toggles behind-schedule only checkbox", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/progress`);

    await expect(page.getByTestId("progress-kpi-grid")).toBeVisible({ timeout: 20_000 });

    const checkbox = page.getByTestId("progress-behind-checkbox");
    await expect(checkbox).toBeVisible();

    // Default should be unchecked
    await expect(checkbox).not.toBeChecked();

    const requestPromise = page.waitForResponse(
      (r) => r.url().includes("is_behind=true") && r.request().method() === "GET"
    );

    await checkbox.check();
    await expect(checkbox).toBeChecked();

    const response = await requestPromise;
    expect(response.status()).toBe(200);
  });
});

test.describe("Sprint 6 — Physical Progress & S-Curve (Visitor)", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.visitor);
  });

  test("manual progress button is hidden for visitor", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/progress`);

    await expect(page.getByRole("heading", { name: /گزارش پیشرفت پروژه/i })).toBeVisible({
      timeout: 20_000,
    });

    // Visitor should see the dashboard but NOT the manual progress button
    await expect(page.getByTestId("progress-kpi-grid")).toBeVisible();
    await expect(page.getByTestId("progress-manual-btn")).toHaveCount(0);
  });
});
