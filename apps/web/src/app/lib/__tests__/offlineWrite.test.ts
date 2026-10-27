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
