import type { OfflineClaim, OfflineOperation } from "./offlineDB";

export const CLAIM_LEASE_MS = 30_000;

export function decideClaim(
  existing: OfflineClaim | undefined,
  next: Omit<OfflineClaim, "fencing_token">,
  now: number,
): { acquired: boolean; claim: OfflineClaim } {
  const currentToken = existing?.fencing_token ?? 0;
  const stillHeld =
    existing != null &&
    Date.parse(existing.expires_at) > now &&
    existing.owner_tab !== next.owner_tab &&
    existing.actor_id === next.actor_id;
  if (stillHeld && existing) {
    return { acquired: false, claim: existing };
  }
  return {
    acquired: true,
    claim: { ...next, fencing_token: currentToken + 1 },
  };
}

export function ackAllowed(claim: OfflineClaim, fencingToken: number): boolean {
  return claim.fencing_token === fencingToken;
}

export function recoverAbandonedSyncing(operations: OfflineOperation[]): OfflineOperation[] {
  return operations.map((operation) =>
    operation.status === "syncing" ? { ...operation, status: "pending" } : operation,
  );
}

export function visibleToActor(operations: OfflineOperation[], actorId: string): OfflineOperation[] {
  return operations.filter((operation) => operation.actor_id === actorId);
}
