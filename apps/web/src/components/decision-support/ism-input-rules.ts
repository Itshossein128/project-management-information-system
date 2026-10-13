import type { ValidationIssue } from "./validation-issues";

export function createIsmMatrix(n: number): (number | null)[][] {
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 0 : null)),
  );
}
export function selectIsmValue(token: string): number | null {
  if (token === "") return null;
  if (token === "0") return 0;
  if (token === "1") return 1;
  throw new Error("Invalid binary option");
}
export function editIsmCell(
  matrix: unknown,
  i: number,
  j: number,
  value: number | null,
): unknown {
  if (!Array.isArray(matrix) || !Array.isArray(matrix[i])) return matrix;
  const next = structuredClone(matrix);
  next[i][j] = value;
  return next;
}
export function hydrateIsmMatrix(value: unknown, n: number): unknown {
  return Array.isArray(value) && value.length === 0
    ? createIsmMatrix(n)
    : structuredClone(value);
}
export function validateIsmDraft(
  criteria: string[],
  value: unknown,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const issue = (code: string, path: string) =>
    issues.push({ code, path, message: "" });
  if (criteria.length < 1 || criteria.length > 10)
    issue("dimension_invalid", "criteria");
  const seen = new Set<string>();
  criteria.forEach((name, i) => {
    const text = typeof name === "string" ? name.trim() : "";
    if (typeof name !== "string") issue("invalid_type", "criteria." + i);
    else if (!text) issue("name_empty", "criteria." + i);
    else if (seen.has(text)) issue("name_duplicate", "criteria." + i);
    seen.add(text);
  });
  const n = criteria.length;
  if (!Array.isArray(value)) {
    issue("dimension_invalid", "ism_matrix");
    return issues;
  }
  if (value.length !== n) issue("dimension_invalid", "ism_matrix");
  value.forEach((row, i) => {
    if (!Array.isArray(row)) {
      issue("dimension_invalid", "ism_matrix." + i);
      return;
    }
    if (row.length !== n) issue("dimension_invalid", "ism_matrix." + i);
    row.forEach((cell, j) => {
      const path = `ism_matrix.${i}.${j}`;
      if (
        cell === null ||
        cell === undefined ||
        (typeof cell === "string" && !cell.trim())
      )
        issue("cell_empty", path);
      else if (typeof cell !== "number") issue("non_numeric", path);
      else if (!Number.isFinite(cell)) issue("non_finite", path);
      else if (cell !== 0 && cell !== 1) issue("ism_relation_invalid", path);
    });
  });
  return issues;
}

export function remapIsmMatrix(
  matrix: unknown,
  n: number,
  operation: { kind: string; index?: number; from?: number; to?: number },
): unknown {
  if (operation.kind === "rename") return structuredClone(matrix);
  if (
    !Array.isArray(matrix) ||
    matrix.some((row) => !Array.isArray(row) || row.length !== matrix.length)
  )
    return structuredClone(matrix);
  const indices: (number | null)[] = Array.from(
    { length: matrix.length },
    (_, i) => i,
  );
  if (operation.kind === "add" && operation.index !== undefined)
    indices.splice(operation.index, 0, null);
  else if (operation.kind === "remove" && operation.index !== undefined)
    indices.splice(operation.index, 1);
  else if (
    operation.kind === "move" &&
    operation.from !== undefined &&
    operation.to !== undefined
  ) {
    const [index] = indices.splice(operation.from, 1);
    indices.splice(operation.to, 0, index!);
  }
  if (indices.length !== n) return structuredClone(matrix);
  return indices.map((oldI, i) =>
    indices.map((oldJ, j) =>
      oldI === null || oldJ === null
        ? i === j
          ? 0
          : null
        : matrix[oldI][oldJ],
    ),
  );
}
