/** Normalize display digits as a decimal string, preserving money precision. */
export function normalizeLiquidityAmount(input: string): string | null {
  const digits = input
    .trim()
    .replace(/[۰-۹]/g, (digit) => String(digit.charCodeAt(0) - 0x06f0))
    .replace(/[٠-٩]/g, (digit) => String(digit.charCodeAt(0) - 0x0660))
    .replace(/٫/g, ".");
  if (
    /[,٬]/.test(digits) &&
    !/^\d{1,3}(?:[,٬]\d{3})+(?:\.\d{1,2})?$/.test(digits)
  )
    return null;
  const normalized = digits.replace(/[,٬]/g, "");
  return /^\d+(?:\.\d{1,2})?$/.test(normalized) ? normalized : null;
}

export function allocationDecisionBlocker(state: {
  cycleId: string;
  proposalCycleId: string;
  lineCount: number;
  ownerId: string;
  rationale: string;
  overlapRequired: boolean;
  acknowledged: boolean;
}):
  | "cycleRequired"
  | "proposalRequired"
  | "ownerRequired"
  | "rationaleRequired"
  | "acknowledgementRequired"
  | null {
  if (!state.cycleId) return "cycleRequired";
  if (state.proposalCycleId !== state.cycleId || !state.lineCount)
    return "proposalRequired";
  if (!state.ownerId.trim()) return "ownerRequired";
  if (!state.rationale.trim()) return "rationaleRequired";
  if (state.overlapRequired && !state.acknowledged)
    return "acknowledgementRequired";
  return null;
}
