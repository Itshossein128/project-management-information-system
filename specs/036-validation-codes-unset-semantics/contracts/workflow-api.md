# Contract: Daily-Report Workflow Validation

Existing REST routes, request/response shapes, successful side effects and permissions remain authoritative. Base: `/api/v1/projects/{project_id}/daily-reports/{report_id}`.

## Authorization and lookup

Authenticated project-scoped resource resolution and existing project membership/permission logic run before workflow validation. Submit requires edit_reports; reject requires approve_reports. Read-only UI requires existing view_reports access. Preserve current 401/403/404 behavior; do not promise one uniform denial status across all authentication/foreign-resource cases. Every denied action leaves records unchanged.

## POST /submit/

Existing request body; no quantity payload is inferred from the action. Validate persisted non-deleted rows.

1. Only draft and rejected are submittable. Other existing states → HTTP 400, report_not_in_submittable_state.
2. Retain existing inactive-day and other readiness rules. Any measured=true / quantity=null activity → HTTP 400, quantity_unset_invalid.
3. Decimal zero, including 0.00, passes the quantity completeness rule. Another invalid row still blocks the report. Deleted rows do not participate.
4. Success remains HTTP 200 with existing report-detail payload and optional submit_warnings. Preserve the standard submit mutations and all existing validation ordering beyond these rules.

## POST /reject/

Request key: `reason` (string or null in scoped cases). Do not rename it to rejection_reason.

1. Only submitted and under_review follow the existing reject path; other-state errors retain existing behavior.
2. Missing key/null/empty/whitespace after trimming → HTTP 400, rejection_reason_required.
3. Nonempty trimmed length <10 → HTTP 400, rejection_reason_min_length_10.
4. Trimmed length >=10 → HTTP 200 when all existing rules/permissions pass. Persist the trimmed reason and existing reviewer metadata.

## Stable codes and exact feedback

- report_not_in_submittable_state: FA `فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند`; EN `Only draft or rejected reports can be submitted.`
- rejection_reason_required: FA `دلیل رد الزامی است`; EN `Rejection reason is required.`
- rejection_reason_min_length_10: FA `دلیل رد باید حداقل ۱۰ کاراکتر باشد`; EN `Rejection reason must be at least 10 characters.`
- quantity_unset_invalid: FA `مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود`; EN `Work quantity must be specified; enter zero if no work was performed.`

HTTP 400 retains the envelope:

```json
{
  "error": {
    "code": "rejection_reason_required",
    "message": "دلیل رد الزامی است",
    "details": {
      "detail": ["دلیل رد الزامی است"],
      "reason": ["دلیل رد الزامی است"]
    }
  }
}
```

This is the target rejection error contract. Current code prefixes error.message with `reason: `; close that spec gap locally in `_reject` by supplying both `detail` and `reason` ErrorDetail entries containing the same localized message/code. The existing exception handler prioritizes detail and retains field errors, so no global handler change is needed. Assert exact error.message, reason leaf and client feedback. Submit errors already use details.detail and an unprefixed message. The envelope is unchanged; rejection details gains detail while retaining reason.

## Locale and client feedback

Server selects lifecycle text from the first Accept-Language entry (`fa*` or `en*`), defaulting to Persian for normal requests without a matching language. Stable codes remain identical. Existing api-client propagates UI locale through Accept-Language and retains ApiRequestError.code.

Daily-report form/view submit/reject callbacks resolve the four known codes to localized feedback above; unknown codes preserve existing server-message/generic fallback. Supply both locales under `dailyReports.validationErrors.<code>` for all four identifiers. Leave shared `errors` keys used by specialty-unit reports unchanged. A locale change affects the next rendered feedback, never the identifier.

## Regression invariants

Invalid/denied actions must not change status, submitted_at, reviewed_at, reason, quantity values or measured flags. Test both valid reject source states, both submit source states, multi-row invalidity, deleted-row exclusion, exact 10-character trimmed boundary, tab/newline whitespace and persisted zero. Corrections, locking, approve rules, aggregation, imports/exports and arithmetic are outside this contract's change scope.
