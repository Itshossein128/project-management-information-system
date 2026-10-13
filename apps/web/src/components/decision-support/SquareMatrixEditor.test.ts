import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createDefaultPairwiseMatrix, updatePairwiseCell, reconcilePairwiseMatrix } from "./square-matrix-rules.ts";

describe("SquareMatrixEditor pairwise reciprocal rules", () => {
  it("initializes an n x n identity pairwise matrix with 1.0 on diagonal", () => {
    const mat = createDefaultPairwiseMatrix(3);
    assert.equal(mat.length, 3);
    assert.deepEqual(mat[0], [1, null, null]);
    assert.deepEqual(mat[1], [null, 1, null]);
    assert.deepEqual(mat[2], [null, null, 1]);
  });

  it("updates reciprocal cell automatically when an off-diagonal cell changes", () => {
    const mat = createDefaultPairwiseMatrix(3);
    const updated = updatePairwiseCell(mat, 0, 1, 2); // C1 vs C2 = 2
    assert.equal(updated[0][1], 2);
    assert.equal(updated[1][0], 0.5); // C2 vs C1 = 1/2
    assert.equal(updated[0][0], 1); // Diagonal preserved
  });

  it("handles decimal or fraction reciprocal accurately", () => {
    const mat = createDefaultPairwiseMatrix(3);
    const updated = updatePairwiseCell(mat, 0, 2, 3);
    assert.equal(updated[0][2], 3);
    assert.equal(Math.abs(updated[2][0] - 1 / 3) < 1e-6, true);
  });

  it("does not alter other cells in the matrix", () => {
    const mat = createDefaultPairwiseMatrix(3);
    const updated = updatePairwiseCell(mat, 1, 2, 5);
    assert.equal(updated[1][2], 5);
    assert.equal(updated[2][1], 0.2);
    assert.equal(updated[0][1], null);
    assert.equal(updated[1][0], null);
  });
});

it("owns n=1 and clears both directions without mutating input", () => {
  assert.deepEqual(createDefaultPairwiseMatrix(1), [[1]]);
  const m = [[1, 7], [1/7, 1]];
  assert.deepEqual(updatePairwiseCell(m, 0, 1, null), [[1, null], [null, 1]]);
  assert.equal(m[0][1], 7);
});
it("reconciles by trimmed names, preserves pairs and blanks renamed/new pairs", () => {
  const m = [[1, 3], [1/3, 1]];
  assert.deepEqual(reconcilePairwiseMatrix([" A ", "B"], ["B", "A", "C"], m),
    [[1, 1/3, null], [3, 1, null], [null, null, 1]]);
  assert.deepEqual(reconcilePairwiseMatrix(["A", "B"], ["A", "Renamed"], m),
    [[1, null], [null, 1]]);
  assert.deepEqual(reconcilePairwiseMatrix(["A", "B"], ["B"], m), [[1]]);
});
it("does not repair malformed retained diagonal judgments during reconciliation", () => {
  assert.deepEqual(reconcilePairwiseMatrix(["A"], ["A", "B"], [[null]]),
    [[null, null], [null, 1]]);
});
