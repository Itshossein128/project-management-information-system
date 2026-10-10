export type ValidationIssue = {
  code: string;
  path: string;
  message: string;
};

export const DECISION_SUPPORT_ERROR_CODES = [
  "name_empty",
  "name_duplicate",
  "dimension_invalid",
  "empty_cell",
  "length_mismatch",
  "matrix_shape",
  "non_numeric",
  "non_finite",
  "negative_value",
  "cost_zero",
  "weight_negative",
  "weights_all_zero",
  "invalid_type",
  "invalid_method",
  "decision_input_invalid",
  "run_immutable",
  "method_not_selected",
] as const;

export type DecisionSupportErrorCode = (typeof DECISION_SUPPORT_ERROR_CODES)[number];

export function parseApiValidationIssues(payload: unknown): ValidationIssue[] {
  if (!payload || typeof payload !== "object") return [];
  const root = payload as Record<string, unknown>;
  const error = (root.error ?? root) as Record<string, unknown>;
  const details = (error.details ?? {}) as Record<string, unknown>;
  const issues = details.issues;
  if (!Array.isArray(issues)) return [];
  return issues
    .filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
    .map((item) => ({
      code: String(item.code ?? "validation_error"),
      path: String(item.path ?? ""),
      message: String(item.message ?? ""),
    }));
}

/** Resolve display text from stable code via i18n; fall back to server message. */
export function localizeIssueMessage(
  issue: Pick<ValidationIssue, "code" | "message">,
  t: (key: string, defaultValue?: string) => string,
): string {
  const key = `decisionSupport.errors.${issue.code}`;
  const translated = t(key, "");
  if (translated && translated !== key) return translated;
  return issue.message || t("decisionSupport.invalidName");
}

export function formatIssueLabel(
  issue: ValidationIssue,
  t?: (key: string, defaultValue?: string) => string,
): string {
  const message = t ? localizeIssueMessage(issue, t) : issue.message;
  if (issue.path) return `${issue.path}: ${message}`;
  return message;
}
