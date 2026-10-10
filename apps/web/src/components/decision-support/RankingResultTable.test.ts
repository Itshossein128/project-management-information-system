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

  it("reads TOPSIS ranking rows with distances and closeness", () => {
    const rows = rankingRowsFromResult({
      ranking: [
        { option: "الف", d_best: 0, d_worst: 0.7071, closeness: 1, score: 1, rank: 1 },
        { option: "ب", d_best: 0.7071, d_worst: 0, closeness: 0, score: 0, rank: 2 },
      ],
    });
    assert.equal(rows.length, 2);
    assert.equal(rows[0]?.option, "الف");
    assert.equal(rows[0]?.d_best, 0);
    assert.equal(rows[0]?.closeness, 1);
    assert.equal(rows[1]?.option, "ب");
    assert.equal(rows[1]?.d_worst, 0);
  });

  it("returns empty for missing ranking", () => {
    assert.deepEqual(rankingRowsFromResult({}), []);
  });
});
