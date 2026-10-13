/**
 * Pure display helpers for AHP criteria weights table.
 */

export function formatWeightPercent(weight: number): string {
  if (typeof weight !== "number" || isNaN(weight)) return "0.0%";
  return `${(weight * 100).toFixed(1)}%`;
}

export function formatWeightDecimal(weight: number, decimals = 4): string {
  if (typeof weight !== "number" || isNaN(weight)) return "0.0000";
  return weight.toFixed(decimals);
}
