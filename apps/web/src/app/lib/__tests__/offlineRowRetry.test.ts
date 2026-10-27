import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { buildSupersedingRetry, operationsForRetry, recordFieldError } from "../offlineRowRetry.ts";
import type { LocalReportSnapshot, OfflineOperation } from "../offlineDB.ts";

const failed: OfflineOperation = {
  operation_id: "op-failed",
  local_report_id: "report-1",
  client_id: "row-1",
  actor_id: "actor-1",
  project_id: "project-1",
  unit: "electrical",
  operation_kind: "create",
  target_type: "activities",
  payload: { quantity: -1, activity_description: "bad" },
  predecessor_ids: [],
  created_at: "2026-10-27T00:00:00.000Z",
  status: "failed",
  error_code: "quantity_must_be_positive",
  error_message: "مقدار باید مثبت باشد",
};

describe("offline row retry (US5 / T045)", () => {
  it("keeps a stable field error linked to the row identity and survives a reload", () => {
    const snapshot: LocalReportSnapshot = {
      local_report_id: "report-1",
      actor_id: "actor-1",
      project_id: "project-1",
      unit: "electrical",
      report_date: "2026-10-27",
      status: "draft",
      base_header: {},
      base_rows: {},
      overlay_header: {},
      overlay_rows: {},
      tombstones: {},
      field_errors: {},
      created_at: failed.created_at,
      updated_at: failed.created_at,
    };
    const stored = recordFieldError(snapshot, {
      actor_id: failed.actor_id,
      project_id: failed.project_id,
      unit: failed.unit,
      local_report_id: failed.local_report_id,
      section: failed.target_type,
      client_id: failed.client_id ?? "",
      operation_id: failed.operation_id,
      field: "quantity",
      code: "quantity_must_be_positive",
      message: failed.error_message ?? "",
    });
    const reloaded = JSON.parse(JSON.stringify(stored)) as LocalReportSnapshot;
    assert.equal(reloaded.field_errors["row-1"].quantity, "quantity_must_be_positive");
    assert.equal(reloaded.actor_id, "actor-1");
    assert.equal(reloaded.project_id, "project-1");
    assert.equal(reloaded.unit, "electrical");
  });

  it("retries only the corrected target under a new operation id and leaves the old payload unchanged", () => {
    const originalPayload = structuredClone(failed.payload);
    const retry = buildSupersedingRetry(failed, { quantity: 2, activity_description: "fixed" }, "op-retry", "2026-10-27T01:00:00.000Z");
    assert.deepEqual(failed.payload, originalPayload);
    assert.equal(retry.operation_id, "op-retry");
    assert.notEqual(retry.operation_id, failed.operation_id);
    assert.equal(retry.supersedes_operation_id, "op-failed");
    assert.deepEqual(retry.predecessor_ids, ["op-failed"]);
    assert.equal(retry.client_id, "row-1");
    const synced: OfflineOperation = { ...failed, operation_id: "op-ok", status: "synced", client_id: "row-ok" };
    assert.deepEqual(operationsForRetry([failed, synced, retry], retry), ["op-retry"]);
  });
});
