import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { reconcileServerWithLocalSnapshot } from "../offlineHydration.ts";
import type { LocalReportSnapshot } from "../offlineDB.ts";

describe("offlineHydration — local overlay and tombstone reconciliation (US2 / T026)", () => {
  it("preserves local header modifications over server header refetch", () => {
    const serverHeader = {
      form_code: "SRV-01",
      notes: "original notes from server",
      weather_condition: "sunny",
    };

    const snapshot: Partial<LocalReportSnapshot> = {
      local_report_id: "local-rep-1",
      overlay_header: {
        notes: "offline edited notes",
      },
      base_header: serverHeader,
      overlay_rows: {},
      tombstones: {},
    };

    const reconciled = reconcileServerWithLocalSnapshot(
      serverHeader,
      [],
      snapshot as LocalReportSnapshot,
    );

    assert.equal(reconciled.header.notes, "offline edited notes");
    assert.equal(reconciled.header.form_code, "SRV-01");
    assert.equal(reconciled.header.weather_condition, "sunny");
  });

  it("merges unchanged server rows, applies local updates, appends new local rows, and excludes tombstones", () => {
    const serverRows = [
      { id: "row-1", description: "foundation pouring", quantity: 50 },
      { id: "row-2", description: "rebar placement", quantity: 20 },
      { id: "row-3", description: "formwork erection", quantity: 15 },
    ];

    const snapshot: Partial<LocalReportSnapshot> = {
      local_report_id: "local-rep-1",
      overlay_header: {},
      overlay_rows: {
        activities: [
          // Update row-2
          { id: "row-2", client_id: "client-row-2", description: "rebar placement updated", quantity: 35 },
          // New row
          { client_id: "client-row-new", description: "curing compound", quantity: 10 },
        ],
      },
      tombstones: {
        activities: ["row-3"], // row-3 deleted locally
      },
    };

    const reconciled = reconcileServerWithLocalSnapshot(
      {},
      serverRows,
      snapshot as LocalReportSnapshot,
      "activities",
    );

    // Expected:
    // row-1: unchanged, status: synced
    // row-2: updated description/quantity, status: pending
    // row-3: omitted because of tombstone
    // client-row-new: appended, status: pending
    const rows = reconciled.rows;
    assert.equal(rows.length, 3);

    const row1 = rows.find((r: any) => r.id === "row-1");
    assert.ok(row1);
    assert.equal(row1.quantity, 50);
    assert.equal(row1.sync_status, "synced");

    const row2 = rows.find((r: any) => r.id === "row-2");
    assert.ok(row2);
    assert.equal(row2.description, "rebar placement updated");
    assert.equal(row2.quantity, 35);
    assert.equal(row2.sync_status, "pending");

    const row3 = rows.find((r: any) => r.id === "row-3");
    assert.equal(row3, undefined, "deleted row with tombstone must be excluded");

    const newRow = rows.find((r: any) => r.client_id === "client-row-new");
    assert.ok(newRow);
    assert.equal(newRow.description, "curing compound");
    assert.equal(newRow.sync_status, "pending");
  });

  it("handles missing snapshot gracefully returning server state with synced status", () => {
    const serverRows = [{ id: "srv-row", description: "unaltered", quantity: 100 }];
    const reconciled = reconcileServerWithLocalSnapshot(
      { form_code: "X" },
      serverRows,
      null,
      "activities",
    );

    assert.equal(reconciled.header.form_code, "X");
    assert.equal(reconciled.rows.length, 1);
    assert.equal(reconciled.rows[0].sync_status, "synced");
  });
});
