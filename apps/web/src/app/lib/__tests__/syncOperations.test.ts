import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { reconcileOperationAcks, SYNC_OPERATIONS_V2_PATH } from "../syncOperations.ts";

describe("sync operation acknowledgements (US3 / T031)", () => {
  it("posts the versioned collection with a trailing slash", () => {
    assert.equal(SYNC_OPERATIONS_V2_PATH.endsWith("/"), true);
    assert.match(SYNC_OPERATIONS_V2_PATH, /sync-operations\/v2\/$/);
  });

  it("matches acknowledgements by operation id, not response order", () => {
    const decision = reconcileOperationAcks(["op-a", "op-b"], {
      contract_version: 2,
      synced_ids: ["op-b", "op-a"],
      results: [
        { operation_id: "op-b", outcome: "success", target: { client_id: "c-b", server_id: "s-b" } },
        { operation_id: "op-a", outcome: "success", target: { client_id: "c-a", server_id: "s-a" } },
      ],
    });
    assert.deepEqual(decision.acknowledged, ["op-a", "op-b"]);
    assert.deepEqual(decision.mappings, [
      { operationId: "op-a", clientId: "c-a", serverId: "s-a" },
      { operationId: "op-b", clientId: "c-b", serverId: "s-b" },
    ]);
  });

  it("retains operations when results are missing, duplicated, unknown, or inconsistent", () => {
    const decision = reconcileOperationAcks(["keep", "missing", "dup", "extra-synced"], {
      contract_version: 2,
      synced_ids: ["keep", "not-success", "unknown-id"],
      results: [
        { operation_id: "keep", outcome: "success", target: { client_id: "c", server_id: "s" } },
        { operation_id: "dup", outcome: "success", target: { client_id: "c1", server_id: "s1" } },
        { operation_id: "dup", outcome: "success", target: { client_id: "c2", server_id: "s2" } },
        { operation_id: "not-success", outcome: "validation_error", error: { code: "invalid" } },
        { operation_id: "unknown-id", outcome: "success" },
        { operation_id: "", outcome: "success" },
      ],
    });
    assert.deepEqual(decision.acknowledged, ["keep"]);
    assert.deepEqual(decision.retained, ["missing", "dup", "extra-synced"]);
  });
});
