import type { RankingRow, SawRankingRow, TopsisRankingRow } from "@/app/lib/api/decision-support";

export type { RankingRow, SawRankingRow, TopsisRankingRow };

/** Pure helper for unit tests — extracts display rows. */
export function rankingRowsFromResult<T extends RankingRow = RankingRow>(result: {
  ranking?: T[];
}): T[] {
  return Array.isArray(result.ranking) ? result.ranking : [];
}
