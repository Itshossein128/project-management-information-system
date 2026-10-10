import type { SawRankingRow } from "@/app/lib/api/decision-support";

/** Pure helper for unit tests — extracts display rows. */
export function rankingRowsFromResult(result: {
  ranking?: SawRankingRow[];
}): SawRankingRow[] {
  return Array.isArray(result.ranking) ? result.ranking : [];
}
