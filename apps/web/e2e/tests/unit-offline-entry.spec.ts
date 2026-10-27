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
    const unitPage = `${projectBase}/electrical?date=2026-10-27`;

    await page.goto(unitPage);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });

    // Go offline
    await context.setOffline(true);

    // Verify offline indicator appears
    const offlineIndicator = page.getByTestId("offline-indicator");
    await expect(offlineIndicator).toBeVisible({ timeout: 10_000 });

    await page.locator("#button-createUnitReportDraft").click();
    await expect(page.getByTestId("unit-section-tab-activities")).toBeVisible();
    await expect(page.getByTestId("unit-section-tab-labor")).toBeVisible();
    await expect(page.getByTestId("unit-section-tab-materials")).toHaveCount(0);
    await page.getByTestId("unit-section-tab-labor").click();
    await expect(page.getByTestId("unit-section-labor").first()).toBeVisible();
    await page.getByTestId("unit-section-tab-activities").click();
    await expect(page.getByTestId("unit-section-activities").first()).toBeVisible();

    // Enter notes or activity record
    const notesInput = page.getByTestId("unit-report-general-notes");
    await expect(notesInput).toBeVisible();
    await notesInput.fill("Offline electrical draft notes");
    await page.getByTestId("unit-report-save-btn").click();

    await expect.poll(() => page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return (await db.getAll("offline_operations")).some((op) => op.payload?.notes === "Offline electrical draft notes");
    })).toBe(true);

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
    expect(idbData.snapshot.overlay_header.notes).toBe("Offline electrical draft notes");
    expect(idbData.snapshot.actor_id).toBe(await page.evaluate(() => String(JSON.parse(localStorage.getItem("auth_user")!).id)));

    expect(idbData.op).not.toBeNull();
    {
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
    const unitPage = `${projectBase}/electrical?date=2026-10-27`;

    await page.goto(unitPage);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });
    await context.setOffline(true);
    await page.locator("#button-createUnitReportDraft").click();

    const notesInput = page.getByTestId("unit-report-general-notes");
    await expect(notesInput).toBeVisible();
    {
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
      await expect(page.locator("#alert-unitReportActionError")).toBeVisible();
      const persisted = await page.evaluate(async () => {
        const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
        return (await db.getAll("offline_operations")).some((op) => op.payload?.notes === "Must not be cleared on storage error");
      });
      expect(persisted).toBe(false);
    }
  });

  test("general section saves a new row while offline", async ({ page, context }) => {
    const projectBase = await createProjectViaApi(page);
    await page.goto(`${projectBase}/electrical?date=2026-10-27`);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });
    await context.setOffline(true);
    await page.locator("#button-createUnitReportDraft").click();
    await page.locator("#tab-unitReportSection-general").click();
    const section = page.getByTestId("unit-section-general-activities");
    await section.locator("form input").first().fill("offline general activity");
    await section.locator('button[type="submit"]').click();
    await expect(section).toContainText("offline general activity");
    const operations = await page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return db.getAll("offline_operations");
    });
    expect(operations.some((operation) => operation.target_type === "general-activities" &&
      (operation.payload as { activity_description?: string }).activity_description === "offline general activity")).toBe(true);
    await context.setOffline(false);
    await expect.poll(() => page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      const rows = await db.getAll("offline_operations");
      return rows.find((operation) => operation.target_type === "general-activities")?.status;
    }), { timeout: 20_000 }).toBe("synced");
  });

  test("machinery section queues a new row while offline", async ({ page, context }) => {
    const projectBase = await createProjectViaApi(page);
    await page.goto(`${projectBase}/machinery?date=2026-10-27`);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });
    await context.setOffline(true);
    await page.locator("#button-createUnitReportDraft").click();
    await page.getByTestId("add-unit-machinery-row").click();
    await page.locator("#input-unitMachineryEquipmentType").fill("offline excavator");
    await page.locator("#input-unitMachineryStatusTotal").fill("1");
    await page.locator("#input-unitMachineryStatusActive").fill("1");
    await page.getByTestId("save-unit-machinery-row").click();
    await expect.poll(() => page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return (await db.getAll("offline_operations")).some((op) => op.target_type === "machinery" &&
        (op.payload as { equipment_type?: string }).equipment_type === "offline excavator");
    })).toBe(true);
    await context.setOffline(false);
    await expect.poll(() => page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return (await db.getAll("offline_operations")).find((op) => op.target_type === "machinery")?.status;
    }), { timeout: 20_000 }).toBe("synced");
  });

  test("interrupted draft request retains a durable local operation", async ({ page }) => {
    const projectBase = await createProjectViaApi(page);
    await page.goto(`${projectBase}/electrical?date=2026-10-27`);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });
    await page.route("**/units/electrical/daily-reports/**", async (route) => {
      if (route.request().method() === "POST") await route.abort("connectionreset");
      else await route.continue();
    });
    await page.locator("#button-createUnitReportDraft").click();
    await expect.poll(() => page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return (await db.getAll("offline_operations")).some((op) => op.operation_kind === "create_report" && op.unit === "electrical");
    })).toBe(true);
  });
});
