/**
 * Pure rules for square matrices (AHP pairwise, DEMATEL, ISM).
 * No UI or DOM dependencies.
 */

export function createDefaultPairwiseMatrix(n: number): (number | null)[][] {
  if (n <= 0) return [];
  const matrix: (number | null)[][] = [];
  for (let i = 0; i < n; i++) {
    const row: (number | null)[] = [];
    for (let j = 0; j < n; j++) {
      row.push(i === j ? 1 : null);
    }
    matrix.push(row);
  }
  return matrix;
}

export function updatePairwiseCell(
  matrix: (number | null)[][],
  row: number,
  col: number,
  value: number | null,
): (number | null)[][] {
  const next = matrix.map((r) => [...r]);
  if (row < 0 || row >= next.length || col < 0 || col >= next.length) {
    return next;
  }

  next[row][col] = value;

  // Diagonal cell is always 1.0 in pairwise comparison
  if (row === col) {
    next[row][col] = 1.0;
    return next;
  }

  // Reciprocal update for opposite cell
  if (value === null || value === undefined) {
    next[col][row] = null;
  } else if (Number.isFinite(value) && value > 0) {
    next[col][row] = 1.0 / value;
  }

  return next;
}

/** Retain comparisons only for the same trimmed criterion identities. */
export function reconcilePairwiseMatrix(
  previous: string[], next: string[], matrix: (number | null)[][],
): (number | null)[][] {
  const indices = previous.map(name => name.trim());
  return next.map((name, i) => next.map((other, j) => {
    const oldI = indices.indexOf(name.trim());
    const oldJ = indices.indexOf(other.trim());
    if (oldI >= 0 && oldJ >= 0) return matrix[oldI]?.[oldJ] ?? null;
    return i === j ? 1 : null;
  }));
}
