import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { reconcileServerChoice, retainUntilReceipts } from "../offlineConflictResolution.ts";

describe("offline conflict reconciliation (US7 / T057)", () => {
  it("drops only the selected scope and keeps unrelated operations after reload", () => {
    const snapshot = {
      local_report_id: "local-1",
      overlay_rows: { activities: [{ client_id: "a" }, { client_id: "b" }] },
    };
    const operations = [
      { operation_id: "op-a", local_report_id: "local-1", client_id: "a", status: "conflict" },
      { operation_id: "op-b", local_report_id: "local-1", client_id: "b", status: "pending" },
      { operation_id: "op-c", local_report_id: "local-2", client_id: "c", status: "pending" },
    ];
    const resolved = reconcileServerChoice(snapshot, operations, ["op-a"]);
    const reloaded = JSON.parse(JSON.stringify(resolved));
    assert.deepEqual(reloaded.operations.map((item: { operation_id: string }) => item.operation_id), ["op-b", "op-c"]);
    assert.deepEqual(reloaded.snapshot.overlay_rows.activities, [{ client_id: "b" }]);
    assert.equal(retainUntilReceipts(["op-a", "op-b"], ["op-a"]), true);
    assert.equal(retainUntilReceipts(["op-a"], ["op-a"]), false);
  });
});
