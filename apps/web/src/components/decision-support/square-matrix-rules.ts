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
      row.push(1.0);
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
  } else if (value > 0) {
    next[col][row] = 1.0 / value;
  }

  return next;
}
