import { ApiRequestError } from "@/app/lib/api-client";

/**
 * Stable daily-report workflow validation codes (spec 036, contracts/workflow-api.md).
 * Text lives under dailyReports.validationErrors.<code> in both locales.
 */
const DAILY_REPORT_VALIDATION_CODES = [
  "report_not_in_submittable_state",
  "rejection_reason_required",
  "rejection_reason_min_length_10",
  "quantity_unset_invalid",
] as const;

type DailyReportValidationCode = (typeof DAILY_REPORT_VALIDATION_CODES)[number];

function isDailyReportValidationCode(code: string | undefined): code is DailyReportValidationCode {
  return (
    typeof code === "string" &&
    (DAILY_REPORT_VALIDATION_CODES as readonly string[]).includes(code)
  );
}

/**
 * Resolve a submit/reject mutation error daily-report feedback text.
 *
 * Only the four known workflow codes are translated by the client; unknown API
 * codes and non-API errors keep the existing fallback (server message/generic).
 */
export function dailyReportWorkflowErrorMessage(
  error: unknown,
  t: (key: string) => string,
): string {
  if (
    error instanceof ApiRequestError &&
    isDailyReportValidationCode(error.code)
  ) {
    return t(`dailyReports.validationErrors.${error.code}`);
  }
  return error instanceof Error ? error.message : String(error);
}
