/** Client-side structural helpers for ranking editors. No SAW scoring. */

export type RankingIssue = { code: string; path: string; message: string };

export type CriterionTypeInput = "benefit" | "cost" | string;

export function validateWeightVector(weights: (number | null | "")[], n: number): RankingIssue[] {
  const issues: RankingIssue[] = [];
  if (weights.length !== n) {
    issues.push({ code: "length_mismatch", path: "weights", message: "weights length mismatch" });
    return issues;
  }
  let sum = 0;
  let allNumeric = true;
  for (let j = 0; j < weights.length; j++) {
    const w = weights[j];
    if (w === null || w === "" || Number.isNaN(Number(w))) {
      issues.push({ code: "non_numeric", path: `weights.${j}`, message: "weight empty" });
      allNumeric = false;
      continue;
    }
    const wf = Number(w);
    if (!Number.isFinite(wf)) {
      issues.push({ code: "non_finite", path: `weights.${j}`, message: "weight non-finite" });
      allNumeric = false;
      continue;
    }
    if (wf < 0) {
      issues.push({ code: "weight_negative", path: `weights.${j}`, message: "weight negative" });
    }
    sum += wf;
  }
  if (allNumeric && weights.length === n && sum <= 0) {
    issues.push({ code: "weights_all_zero", path: "weights", message: "weights all zero" });
  }
  return issues;
}

export function validateCriterionTypes(
  types: CriterionTypeInput[],
  n: number,
): RankingIssue[] {
  const issues: RankingIssue[] = [];
  if (types.length !== n) {
    issues.push({ code: "length_mismatch", path: "types", message: "types length mismatch" });
    return issues;
  }
  for (let j = 0; j < types.length; j++) {
    const t = types[j];
    if (t !== "benefit" && t !== "cost") {
      issues.push({
        code: "invalid_type",
        path: `types.${j}`,
        message: "Type must be benefit or cost.",
      });
    }
  }
  return issues;
}

export function validateRectangularMatrix(
  matrix: (number | null | "")[][],
  m: number,
  n: number,
  types?: CriterionTypeInput[],
): RankingIssue[] {
  const issues: RankingIssue[] = [];
  if (matrix.length !== m) {
    issues.push({
      code: "matrix_shape",
      path: "performance_matrix",
      message: "row count mismatch",
    });
  }

  const numericGrid: (number | null)[][] = [];

  for (let i = 0; i < matrix.length; i++) {
    const row = matrix[i] ?? [];
    if (row.length !== n) {
      issues.push({
        code: "length_mismatch",
        path: `performance_matrix.${i}`,
        message: "row length mismatch",
      });
    }
    const numericRow: (number | null)[] = [];
    for (let j = 0; j < row.length; j++) {
      const cell = row[j];
      const path = `performance_matrix.${i}.${j}`;
      if (cell === null || cell === "" || cell === undefined) {
        issues.push({ code: "empty_cell", path, message: "empty cell" });
        numericRow.push(null);
        continue;
      }
      const cf = Number(cell);
      if (Number.isNaN(cf)) {
        issues.push({ code: "non_numeric", path, message: "non-numeric" });
        numericRow.push(null);
        continue;
      }
      if (!Number.isFinite(cf)) {
        issues.push({ code: "non_finite", path, message: "non-finite" });
        numericRow.push(null);
        continue;
      }
      if (cf < 0) {
        issues.push({ code: "negative_value", path, message: "negative" });
      }
      if (types && types[j] === "cost" && cf === 0) {
        issues.push({
          code: "cost_zero",
          path,
          message: "Cost criterion cell cannot be zero.",
        });
      }
      numericRow.push(cf);
    }
    numericGrid.push(numericRow);
  }

  // AC13: all-zero benefit column (even if weight is zero) — structural guard only
  if (types && types.length === n && numericGrid.length === m && m > 0) {
    for (let j = 0; j < n; j++) {
      if (types[j] !== "benefit") continue;
      const col: number[] = [];
      let complete = true;
      for (let i = 0; i < m; i++) {
        const v = numericGrid[i]?.[j];
        if (v === null || v === undefined) {
          complete = false;
          break;
        }
        col.push(v);
      }
      if (complete && col.length === m && col.every((v) => v === 0)) {
        issues.push({
          code: "benefit_column_all_zero",
          path: `criteria.${j}`,
          message: "Benefit criterion column cannot be all zeros.",
        });
      }
    }
  }

  return issues;
}

/** Display-only normalize; not used for scoring. */
export function previewNormalizedWeights(weights: number[]): number[] | null {
  const sum = weights.reduce((a, b) => a + b, 0);
  if (sum <= 0) return null;
  return weights.map((w) => w / sum);
}
