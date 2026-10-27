import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { chromium } from "@playwright/test";

const origin = process.env.OFFLINE_TEST_ORIGIN ?? "http://127.0.0.1:5198";
let browser: Awaited<ReturnType<typeof chromium.launch>>;

before(async () => {
  browser = await chromium.launch({ headless: true });
});

after(async () => {
  await browser?.close();
});

describe("offlineWrite unit report operations and snapshots", () => {
  it("never selects another account's legacy queue for replay", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });
      const pending = await page.evaluate(async () => {
        const db = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
        localStorage.setItem("auth_user", JSON.stringify({ id: "actor-b" }));
        await db.addToQueue({ queue_id: "other", entity_type: "daily_report", project_id: "project",
          actor_id: "actor-a", unit: "electrical", method: "POST", endpoint: "/test/", payload: {},
          created_at: new Date().toISOString(), status: "pending", retry_count: 0, error_message: null });
        await db.addToQueue({ queue_id: "own", entity_type: "daily_report", project_id: "project",
          actor_id: "actor-b", unit: "electrical", method: "POST", endpoint: "/test/", payload: {},
          created_at: new Date().toISOString(), status: "pending", retry_count: 0, error_message: null });
        return (await db.getPendingQueue()).map((item) => item.queue_id);
      });
      assert.deepEqual(pending, ["own"]);
    } finally { await context.close(); }
  });
  it("uses the signed-in user for local scope and refuses missing identity", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });
      const result = await page.evaluate(async () => {
        const auth = await import(/* @vite-ignore */ "/src/app/lib/auth-storage.ts");
        localStorage.setItem("auth_user_id", "stale-account");
        localStorage.setItem("auth_user", JSON.stringify({ id: "current-account" }));
        const current = auth.getStoredActorId();
        localStorage.removeItem("auth_user");
        let refused = false;
        try { auth.requireStoredActorId(); } catch { refused = true; }
        return { current, refused };
      });
      assert.equal(result.current, "current-account");
      assert.equal(result.refused, true);
    } finally { await context.close(); }
  });
  it("does not reveal snapshots without a proven actor or across accounts", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });
      const result = await page.evaluate(async () => {
        const db = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
        const writer = await import(/* @vite-ignore */ "/src/app/lib/offlineWrite.ts");
        const { snapshot } = await writer.queueUnitReportOperation({
          actorId: "actor-a", projectId: "shared-project", unit: "electrical",
          reportDate: "2026-10-27", operationKind: "create_report", targetType: "header",
          payload: { notes: "private" },
        });
        let crossAccountWriteRejected = false;
        try {
          await writer.queueUnitReportOperation({
            actorId: "actor-b", projectId: "shared-project", unit: "electrical",
            reportDate: "2026-10-27", localReportId: snapshot.local_report_id,
            operationKind: "header_update", targetType: "header", payload: { notes: "wrong actor" },
          });
        } catch { crossAccountWriteRejected = true; }
        let ownWriteAccepted = true;
        try {
          await writer.queueUnitReportOperation({
            actorId: "actor-a", projectId: "shared-project", unit: "electrical",
            reportDate: "", localReportId: snapshot.local_report_id,
            operationKind: "create", targetType: "activities", payload: { activity_description: "own" },
          });
        } catch { ownWriteAccepted = false; }
        return {
          unscoped: await db.findLocalSnapshot("shared-project", "electrical", "2026-10-27"),
          other: await db.findLocalSnapshot("shared-project", "electrical", "2026-10-27", "actor-b"),
          list: await db.getLocalSnapshotsByProject("shared-project"),
          own: await db.findLocalSnapshot("shared-project", "electrical", "2026-10-27", "actor-a"),
          id: snapshot.local_report_id,
          crossAccountWriteRejected,
          ownWriteAccepted,
        };
      });
      assert.equal(result.unscoped, undefined);
      assert.equal(result.other, undefined);
      assert.deepEqual(result.list, []);
      assert.equal(result.own?.local_report_id, result.id);
      assert.equal(result.crossAccountWriteRejected, true);
      assert.equal(result.ownWriteAccepted, true);
    } finally {
      await context.close();
    }
  });
  it("atomically commits snapshot and operation with independent UUIDs and scope", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });

      const result = await page.evaluate(async () => {
        const dbModule = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
        const writeModule = await import(/* @vite-ignore */ "/src/app/lib/offlineWrite.ts");

        const { operation, snapshot } = await writeModule.queueUnitReportOperation({
          actorId: "actor-123",
          projectId: "proj-abc",
          unit: "electrical",
          reportDate: "2026-10-27",
          operationKind: "create",
          targetType: "activities",
          payload: { description: "install conduit", quantity: 15 },
        });

        const storedSnapshot = await dbModule.getLocalSnapshot(snapshot.local_report_id);
        const storedOperation = await dbModule.getOperation(operation.operation_id);

        return {
          opId: operation.operation_id,
          reportId: snapshot.local_report_id,
          clientId: operation.client_id,
          actorId: operation.actor_id,
          unit: operation.unit,
          status: operation.status,
          hasStoredSnapshot: Boolean(storedSnapshot),
          hasStoredOp: Boolean(storedOperation),
          overlayCount: snapshot.overlay_rows.activities?.length ?? 0,
        };
      });

      assert.ok(result.opId, "operation must have UUID");
      assert.ok(result.reportId, "snapshot must have UUID");
      assert.ok(result.clientId, "row must have client UUID");
      assert.notEqual(result.opId, result.reportId);
      assert.notEqual(result.opId, result.clientId);
      assert.equal(result.actorId, "actor-123");
      assert.equal(result.unit, "electrical");
      assert.equal(result.status, "pending");
      assert.equal(result.hasStoredSnapshot, true);
      assert.equal(result.hasStoredOp, true);
      assert.equal(result.overlayCount, 1);
    } finally {
      await context.close();
    }
  });

  it("links successive operations via predecessor_ids and updates overlay without mutating base", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });

      const result = await page.evaluate(async () => {
        const writeModule = await import(/* @vite-ignore */ "/src/app/lib/offlineWrite.ts");
        const dbModule = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");

        // 1. Create row
        const first = await writeModule.queueUnitReportOperation({
          actorId: "actor-456",
          projectId: "proj-xyz",
          unit: "mechanical",
          reportDate: "2026-10-28",
          operationKind: "create",
          targetType: "materials",
          payload: { item_name: "pipe 2 inch", amount: 10 },
          baseRows: { materials: [{ id: "base-mat-1", item_name: "existing", amount: 5 }] },
        });

        // 2. Update same row
        const second = await writeModule.queueUnitReportOperation({
          actorId: "actor-456",
          projectId: "proj-xyz",
          unit: "mechanical",
          reportDate: "2026-10-28",
          localReportId: first.snapshot.local_report_id,
          clientId: first.operation.client_id,
          operationKind: "update",
          targetType: "materials",
          payload: { item_name: "pipe 2 inch", amount: 25 },
        });

        const snapshot = await dbModule.getLocalSnapshot(first.snapshot.local_report_id);

        return {
          firstOpId: first.operation.operation_id,
          secondOpId: second.operation.operation_id,
          secondPredecessors: second.operation.predecessor_ids,
          baseRowCount: snapshot?.base_rows.materials?.length ?? 0,
          overlayRowCount: snapshot?.overlay_rows.materials?.length ?? 0,
          finalAmount: (snapshot?.overlay_rows.materials?.[0] as any)?.amount,
        };
      });

      assert.notEqual(result.firstOpId, result.secondOpId);
      assert.ok(
        result.secondPredecessors.includes(result.firstOpId),
        "second operation must record first operation in predecessor_ids",
      );
      assert.equal(result.baseRowCount, 1, "base rows must remain unmutated");
      assert.equal(result.overlayRowCount, 1, "overlay row updated in place");
      assert.equal(result.finalAmount, 25, "overlay has updated payload");
    } finally {
      await context.close();
    }
  });

  it("records tombstone on row deletion and removes row from overlay", async () => {
    const context = await browser.newContext();
    try {
      const page = await context.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });

      const result = await page.evaluate(async () => {
        const writeModule = await import(/* @vite-ignore */ "/src/app/lib/offlineWrite.ts");
        const dbModule = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");

        // 1. Create row
        const created = await writeModule.queueUnitReportOperation({
          actorId: "actor-789",
          projectId: "proj-tomb",
          unit: "civil",
          reportDate: "2026-10-29",
          operationKind: "create",
          targetType: "labor",
          payload: { job_title: "welder", count: 3 },
        });

        // 2. Delete row
        const deleted = await writeModule.queueUnitReportOperation({
          actorId: "actor-789",
          projectId: "proj-tomb",
          unit: "civil",
          reportDate: "2026-10-29",
          localReportId: created.snapshot.local_report_id,
          clientId: created.operation.client_id,
          operationKind: "delete",
          targetType: "labor",
          payload: {},
        });

        const snapshot = await dbModule.getLocalSnapshot(created.snapshot.local_report_id);

        return {
          clientId: created.operation.client_id,
          overlayCount: snapshot?.overlay_rows.labor?.length ?? 0,
          tombstones: snapshot?.tombstones.labor ?? [],
          deleteOpKind: deleted.operation.operation_kind,
        };
      });

      assert.equal(result.overlayCount, 0, "deleted row removed from overlay");
      assert.ok(
        result.tombstones.includes(result.clientId!),
        "client id must be recorded in tombstones",
      );
      assert.equal(result.deleteOpKind, "delete");
    } finally {
      await context.close();
    }
  });
});
