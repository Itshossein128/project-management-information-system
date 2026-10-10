import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createDefaultPairwiseMatrix, updatePairwiseCell } from "./square-matrix-rules.ts";

describe("SquareMatrixEditor pairwise reciprocal rules", () => {
  it("initializes an n x n identity pairwise matrix with 1.0 on diagonal", () => {
    const mat = createDefaultPairwiseMatrix(3);
    assert.equal(mat.length, 3);
    assert.deepEqual(mat[0], [1, 1, 1]);
    assert.deepEqual(mat[1], [1, 1, 1]);
    assert.deepEqual(mat[2], [1, 1, 1]);
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
    assert.equal(updated[0][1], 1);
    assert.equal(updated[1][0], 1);
  });
});
