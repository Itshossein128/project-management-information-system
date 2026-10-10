import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { rankingRowsFromResult } from "./ranking-result-rows.ts";

describe("RankingResultTable helpers", () => {
  it("reads SAW ranking rows", () => {
    const rows = rankingRowsFromResult({
      ranking: [
        { option: "الف", score: 1, rank: 1 },
        { option: "ب", score: 0.5, rank: 2 },
      ],
    });
    assert.equal(rows.length, 2);
    assert.equal(rows[0]?.option, "الف");
    assert.equal(rows[0]?.rank, 1);
  });

  it("returns empty for missing ranking", () => {
    assert.deepEqual(rankingRowsFromResult({}), []);
  });
});
