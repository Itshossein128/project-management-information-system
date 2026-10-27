import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ackAllowed, decideClaim, recoverAbandonedSyncing, visibleToActor } from "../offlineClaims.ts";
import type { OfflineClaim, OfflineOperation } from "../offlineDB.ts";

const base = {
  claim_id: "project-1",
  scope: "project-1",
  actor_id: "actor-1",
  project_id: "project-1",
  owner_tab: "tab-a",
  acquired_at: "2026-10-27T00:00:00.000Z",
  expires_at: "2026-10-27T00:00:30.000Z",
};

function operation(status: OfflineOperation["status"], actorId: string): OfflineOperation {
  return {
    operation_id: `${actorId}-${status}`,
    local_report_id: "report",
    actor_id: actorId,
    project_id: "project-1",
    unit: "electrical",
    operation_kind: "create",
    target_type: "header",
    payload: { notes: "keep" },
    predecessor_ids: [],
    created_at: "2026-10-27T00:00:00.000Z",
    status,
  };
}

describe("offline claims (US8 / T063)", () => {
  it("refuses a second tab until the lease expires, then fences the stale owner", () => {
    const held = decideClaim(undefined, base, Date.parse("2026-10-27T00:00:00.000Z"));
    assert.equal(held.acquired, true);
    const blocked = decideClaim(
      held.claim,
      { ...base, owner_tab: "tab-b" },
      Date.parse("2026-10-27T00:00:10.000Z"),
    );
    assert.equal(blocked.acquired, false);
    assert.equal(ackAllowed(blocked.claim, 99), false);
    const expired = decideClaim(
      held.claim,
      { ...base, owner_tab: "tab-b", expires_at: "2026-10-27T00:01:00.000Z" },
      Date.parse("2026-10-27T00:00:31.000Z"),
    );
    assert.equal(expired.acquired, true);
    assert.equal(expired.claim.fencing_token, held.claim.fencing_token + 1);
    assert.equal(ackAllowed(expired.claim, held.claim.fencing_token), false);
    assert.equal(ackAllowed(expired.claim, expired.claim.fencing_token), true);
  });

  it("returns abandoned syncing work to pending and hides another account", () => {
    const recovered = recoverAbandonedSyncing([
      operation("syncing", "actor-1"),
      operation("pending", "actor-1"),
      operation("pending", "actor-2"),
    ]);
    assert.equal(recovered[0].status, "pending");
    assert.deepEqual(visibleToActor(recovered, "actor-1").map((item) => item.actor_id), ["actor-1", "actor-1"]);
    assert.equal(visibleToActor(recovered, "actor-2").some((item) => item.actor_id === "actor-1"), false);
  });
});
