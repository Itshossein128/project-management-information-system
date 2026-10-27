# Phase 0 Research: Validation Codes and Unset Semantics

**Date**: 2026-10-27. Evidence: local source inspection and two read-only research agents using `gpt-6-luna`. No runtime tests executed. Questions below are resolved design inputs, not claims that the feature is delivered.

## 1. Existing workflow validation and envelope

**Decision**: Reuse `field_reports/services/lifecycle_errors.py`, `_submit`, `_reject`, and `_validate_report_ready_for_submit` in `field_reports/daily_report_views.py`. Preserve the global exception envelope and expose stable codes without parsing translated strings.

**Rationale**: All four codes and exact Persian leaf messages already exist (lifecycle_errors.py:8–24). Submit checks draft/rejected before readiness (:302–319); measured null detection uses `is None` (:71–81), which accepts decimal zero. Reject checks submitted/under_review, trims `reason`, then tests missing and <10 (:342–356). `common/mixins.py` dispatches through get_object; permission selection and project-scoped queryset remain in the view. `config/exceptions.py:38–55,98–138` emits `{error:{code,message,details}}` and preserves ErrorDetail leaf codes.

Current behavior flattens reason errors as `reason: <message>`, which conflicts with the spec's exact rejection messages. Resolve this in the daily-report `_reject` path only: include the same localized ErrorDetail in top-level `detail` and field-level `reason` entries. The existing handler already prioritizes `detail` when selecting error.message, while preserving the reason leaf in error.details. Thus error.message and details.reason[0] both contain the exact text, stable code extraction survives, and the global envelope/handler remain unchanged. Existing field-level reason details are preserved; details gains a detail entry. Client known-code translations produce the same exact feedback. Regression tests must assert exact error.message for all four codes.

**Alternatives considered**: Replacing the error envelope or moving guards into a new workflow engine would change unrelated contracts. Duplicating already implemented backend guards would create inconsistent validation. Neither is required.

## 2. Persisted quantity and legacy data

**Decision**: Keep nullable decimal quantity plus measured flag and the existing write/submit validation rules. Display treats null or explicit not-measured as unset without modifying stored data.

**Rationale**: `field_reports/models.py:301–302` already stores decimal(18,4), nullable quantity and boolean quantity_measured. Activity serializer normalizes blank input and not-measured writes (`serializers.py:206–225`); legacy database reads may still contain numeric quantity with false. Submit currently rejects this inconsistent combination under its existing generic validation. The feature requires display precedence, not changing that submission rule. No calculation, migration, or data cleanup is necessary.

**Alternatives considered**: Defaulting null to zero destroys information; cleaning legacy rows on read would mutate history; adding a third stored state duplicates information.

## 3. Exact read-only display scope

**Decision**: Reuse `UnsetQuantityBadge` for read-only EditableGrid activity quantity cells and DailyReportSummaryView's activity and general-activity quantity columns. For general activities, pass no measured flag and decide only from nullable quantity.

**Rationale**: Badge predicate already correctly uses `quantity == null || quantityMeasured === false`. EditableGrid's quantity-specific branch and the main summary activity table already reuse it. The summary general-activity column still uses `row.quantity ?? '—'` (DailyReportSummaryView.tsx:722–738); its GeneralActivityRow type has nullable quantity and no measured flag. Including this quantity column follows FR-009's summary scope without inventing schema or expanding to materials, equipment, labor, concrete, security or totals.

**Alternatives considered**: Excluding a visible summary activity quantity column leaves null ambiguous. A new measured flag for general activities broadens the data contract. Replacing every numeric placeholder in the product exceeds scope.

## 4. Label, border and accessibility

**Decision**: Change `dailyReports.unsetQuantity` English value from `Not recorded` to exact `Unset`, retain Persian `ثبت‌نشده`, and add caution ring/border styling locally to UnsetQuantityBadge with existing warning theme tokens and a muted neutral background.

**Rationale**: `ui/badge.tsx:6–16` supplies compact typography, neutral background and a generic ring but no explicit caution-colored outline. The current English locale value differs from FR-012. A component-local class preserves other neutral badges and the existing numeric/editor branches. Verify visible outline and readable text in both themes; meaning must remain explicit in text.

**Alternatives considered**: Globally changing the neutral Badge variant affects unrelated statuses. Using danger styling overstates severity. Color alone is inaccessible.

## 5. Client validation-code localization

**Decision**: Add all four translations under `dailyReports.validationErrors.<code>` and use ApiRequestError.code to select them in daily-report submit/reject feedback. Share the small mapping/helper between form and view where needed, while retaining existing fallback for unknown codes and non-API errors. Preserve other domains' existing `errors.rejection_reason_required` entry unchanged.

**Rationale**: `api-client.ts` already sends Accept-Language and preserves `ApiRequestError.code`. DailyReportForm and daily-report-view currently toast Error.message. Locale catalogs contain only an existing shared rejection_reason_required key among the four codes, with a different Persian sentence. Use the daily-report-specific namespace to avoid changing shared unit-report feedback.

**Alternatives considered**: Depending exclusively on server text cannot guarantee exact daily-report client feedback and locale switching. A global API-client translation rewrite is larger than necessary. Matching Persian/English text is unstable.

## 6. Verification strategy and fixture compatibility

**Decision**: Extend existing pytest approval-workflow tests and apps/web/e2e/tests/daily-report.spec.ts. Use the apps/web Playwright configuration and its server setup; avoid assuming the root config starts services. Cover actual API errors and real browser display separately.

**Rationale**: Existing backend tests cover main codes, zero and locales, but need reason boundaries/whitespace, rejected-state submit, multi-row validation, persistence and no-mutation/permission assertions. Existing E2E around :293–373 accepts either language and only false/null versus zero. It needs exact bilingual strings, measured/null, legacy false/numeric, positive quantity, general-activity null and visual checks. Older daily-report fixture creation may predate automatic summaries; adapt fixtures through canonical specialty-unit/by-date flows or isolated controlled test setup, never relax production auto-summary restrictions.

**Alternatives considered**: New framework or duplicate broad suites add maintenance without coverage. Mocked browser responses prove rendering only, so they must be reported separately from real workflow/permission tests. Shared reused test databases risk overlapping schema creation; use a unique TEST_DATABASE_NAME and one pytest process.

## Resolved unknowns

Backend ownership, API shape, localization, scope of general activities, legacy precedence, border treatment, test runner, no-migration strategy and authorization boundaries are resolved above. No blocking product clarification remains. Installed service availability and acceptance results belong to implementation validation, not research assumptions.
