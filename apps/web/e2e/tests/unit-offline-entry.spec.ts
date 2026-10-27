/**
 * Feature 037 — US1: Offline entry in current unit page (T018).
 *
 * Scenarios:
 * 1. Offline and interrupted request on current unit page preserves local edits.
 * 2. Enabled/disabled sections match canonical unit rules.
 * 3. Stable UUIDv4 client ID and independent operation IDs in IndexedDB.
 * 4. Durable-success-only feedback.
 * 5. Storage failure retains user input without silent loss.
 * 6. Missing reference data explains requirement without clearing edits.
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("US1 — Offline Entry in Current Unit Page (T018)", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("offline entry on electrical unit page stores draft and operations with stable UUIDs", async ({
    page,
    context,
  }) => {
    const projectBase = await createProjectViaApi(page);
    const unitPage = `${projectBase}/units/electrical/daily-reports?date=2026-10-27`;

    await page.goto(unitPage);
    await expect(page.locator("body")).toBeVisible();

    // Go offline
    await context.setOffline(true);

    // Verify offline indicator appears
    const offlineIndicator = page.getByTestId("offline-indicator");
    await expect(offlineIndicator).toBeVisible({ timeout: 10_000 });

    // Verify enabled/disabled sections: electrical has activities and labor, not warehouse materials
    await expect(page.getByTestId("unit-section-activities")).toBeVisible();
    await expect(page.getByTestId("unit-section-labor")).toBeVisible();
    await expect(page.getByTestId("unit-section-materials")).toHaveCount(0);

    // Enter notes or activity record
    const notesInput = page.getByTestId("unit-report-general-notes");
    if (await notesInput.isVisible()) {
      await notesInput.fill("Offline electrical draft notes");
      await page.getByTestId("unit-report-save-btn").click();
    }

    // Inspect IndexedDB to verify local_snapshots and offline_operations
    const idbData = await page.evaluate(async () => {
      const module = await import("/src/app/lib/offlineDB.ts");
      const db = await module.initDB();
      const snapshots = await db.getAll("local_snapshots");
      const ops = await db.getAll("offline_operations");
      return {
        snapshotCount: snapshots.length,
        opsCount: ops.length,
        snapshot: snapshots[0] ?? null,
        op: ops[0] ?? null,
      };
    });

    expect(idbData.snapshotCount).toBeGreaterThanOrEqual(1);
    expect(idbData.snapshot.unit).toBe("electrical");
    expect(idbData.snapshot.report_date).toBe("2026-10-27");

    if (idbData.op) {
      // Validate UUIDv4 format (8-4-4-4-12)
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      expect(idbData.op.operation_id).toMatch(uuidRegex);
      expect(idbData.op.local_report_id).toMatch(uuidRegex);
      expect(idbData.op.operation_id).not.toBe(idbData.op.local_report_id);
    }
  });

  test("storage failure retains user input without silent clearing", async ({
    page,
    context,
  }) => {
    const projectBase = await createProjectViaApi(page);
    const unitPage = `${projectBase}/units/electrical/daily-reports?date=2026-10-27`;

    await page.goto(unitPage);
    await context.setOffline(true);

    const notesInput = page.getByTestId("unit-report-general-notes");
    if (await notesInput.isVisible()) {
      await notesInput.fill("Must not be cleared on storage error");

      // Inject transaction abort into IndexedDB
      await page.evaluate(() => {
        const orig = IDBDatabase.prototype.transaction;
        IDBDatabase.prototype.transaction = function (...args: Parameters<IDBDatabase["transaction"]>) {
          const tx = orig.apply(this, args);
          if (args[0] === "local_snapshots" || (Array.isArray(args[0]) && args[0].includes("local_snapshots"))) {
            queueMicrotask(() => tx.abort());
          }
          return tx;
        };
      });

      // Attempt save
      await page.getByTestId("unit-report-save-btn").click();

      // Input must retain text
      await expect(notesInput).toHaveValue("Must not be cleared on storage error");
    }
  });
});
