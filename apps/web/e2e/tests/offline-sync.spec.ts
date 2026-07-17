/**
 * FLOW: Offline write → reconnect → sync (Sprint 5)
 * MODULE: Offline Sync
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("Offline sync — Sprint 5", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("connectivity banner hides when online and appears when offline", async ({
    page,
    context,
  }) => {
    await page.goto("/projects");
    await expect(page.locator("body")).toBeVisible();
    // Healthy online: no permanent banner
    await expect(page.getByTestId("offline-indicator")).toHaveCount(0, {
      timeout: 15_000,
    });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });
    await context.setOffline(false);
  });

  test("offline header save queues and syncs after reconnect", async ({ page, context }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/daily-reports/new`);
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });

    await context.setOffline(true);
    await expect(page.getByTestId("offline-indicator")).toContainText(/آفلاین/i, {
      timeout: 10_000,
    });

    await page.getByTestId("daily-report-save-header").click();
    await expect(page.getByText(/به صورت آفلاین ذخیره شد|آفلاین ذخیره/i).first()).toBeVisible({
      timeout: 15_000,
    });

    await context.setOffline(false);
    await page.goto(`${base}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });

    const syncBtn = page.getByTestId("daily-reports-sync-now");
    if (await syncBtn.isVisible().catch(() => false)) {
      await syncBtn.click();
      await expect(page.getByText(/همگام‌سازی شد|همگام/i).first()).toBeVisible({
        timeout: 20_000,
      });
    } else {
      // Auto-sync may have already drained the queue — banner hides when healthy.
      await expect(page.getByTestId("offline-indicator")).toHaveCount(0, {
        timeout: 20_000,
      });
    }

    await expect(page.getByTestId("daily-reports-list")).toBeVisible();
    await expect(page.locator("table tbody tr").first()).toBeVisible({ timeout: 20_000 });
  });
});
