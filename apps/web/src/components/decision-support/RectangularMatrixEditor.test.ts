import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  validateCriterionTypes,
  validateRectangularMatrix,
  validateWeightVector,
} from "./ranking-input-rules.ts";

describe("ranking input rules", () => {
  it("rejects empty matrix cells (never coerce to zero)", () => {
    const issues = validateRectangularMatrix([[null, 1]], 1, 2);
    assert.ok(issues.some((i) => i.code === "empty_cell" && i.path === "performance_matrix.0.0"));
  });

  it("rejects weight length mismatch and all-zero", () => {
    assert.ok(validateWeightVector([1], 2).some((i) => i.code === "length_mismatch"));
    assert.ok(validateWeightVector([0, 0], 2).some((i) => i.code === "weights_all_zero"));
  });

  it("rejects invalid types and cost zero", () => {
    assert.ok(validateCriterionTypes(["maybe"], 1).some((i) => i.code === "invalid_type"));
    const costIssues = validateRectangularMatrix([[0]], 1, 1, ["cost"]);
    assert.ok(
      costIssues.some((i) => i.code === "cost_zero" && i.path === "performance_matrix.0.0"),
    );
  });

  it("rejects all-zero benefit column at criteria.j", () => {
    const issues = validateRectangularMatrix(
      [
        [0, 100],
        [0, 200],
      ],
      2,
      2,
      ["benefit", "cost"],
    );
    assert.ok(
      issues.some((i) => i.code === "benefit_column_all_zero" && i.path === "criteria.0"),
    );
  });
});
