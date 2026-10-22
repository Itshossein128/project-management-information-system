# Research: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Feature**: `specs/031-site-inactivity-security` | **Date**: 2026-10-22

## R1 — Current implementation state of the inactivity cycle

**Decision**: Treat the feature as brownfield convergence; implement only the documented residual deltas.
**Rationale**: Verified against the current tree, all PROMPT-03 obligations already have implementations and tests:

| Prompt item | Status | Evidence (current tree) |
|---|---|---|
| Five standard reasons | Implemented | `apps/api/core/field_reports/models.py` — `InactivityReason` TextChoices: `weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, `safety_incident`, with the approved Persian labels |
| Conditional mandatory reason, code `inactivity_reason_required` | Implemented | `DailyReport.clean()`/`save()` (active clears reason); `serializers.py` `validate` raises ValidationError with `code='inactivity_reason_required'` attached to `inactivity_reason`; `daily_report_views.py` repeats the guard on submit/review/approve paths |
| Dynamic header dropdown | Implemented | `ReportHeader.tsx` renders the reason select only while `site_status === "inactive"` and resets it to null on switching back to active; summary metadata editor (`daily-report-view.tsx`) has the equivalent select (covered by an existing E2E) |
| PDF parity | Implemented | `pdf.py` renders `get_inactivity_reason_display()` in the header table only when `site_status == 'inactive' and inactivity_reason` — active reports show no fabricated reason |
| Inactive-day activity guard | Implemented | `activity-guard.ts` predicate (inactive + strictly positive numeric quantity) + `ActivityTab.tsx` confirm dialog wired through `beforeSaveRow`; confirm proceeds, cancel aborts the save |
| by-date POST permission | Implemented | `daily_report_views.py` `get_permissions` pattern; `ENDPOINTS.md` documents POST → `edit_reports`, GET → `view_reports`; dedicated tests in `tests/test_daily_report_summary_permissions.py` (viewer POST → 403, GET of existing/tests missing date) |
| Bilingual catalogs | Implemented | `fa.json` / `en.json` contain `dailyReports.inactivityReason` (field label), `dailyReports.inactivityReasons` (five value labels), `errors.inactivity_reason_required`, and the warning keys |
| Readback labels | Implemented | Serializers expose `inactivity_reason_label`; `DailyReportSummaryView.tsx` appends the localized reason to the status readout |

**Alternatives considered**: Rebuilding the reason machinery as new entities/tables (rejected — violates Minimal Coherent Changes and duplicates the existing tested chain).

## R2 — Warning copy and locale-key mismatch (the real US2 gap)

**Decision**: Align the guard copy to the approved PROMPT-03 text and unify the locale key.
**Rationale**: `ActivityTab.tsx` calls `t("dailyReports.inactiveActivityWarning", INACTIVE_ACTIVITY_WARNING_FA)`, but the catalogs define `dailyReports.inactiveSiteActivityWarning` — the lookup key does not exist, so the dialog always falls back to the hardcoded constant and is not translatable. Additionally, the fallback text («…آیا از ثبت کارکرد اجرایی اطمینان دارید؟») deviates from the approved prompt wording («…آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟»). The dialog title (`تأیید ثبت کارکرد در روز تعطیل`) and footer buttons (`انصراف` / `تأیید و ذخیره`) are inline Persian strings although matching keys (`confirmActivity`, `cancelActivity`) already exist in both catalogs.
**Alternatives considered**: Keep the current copy and reinterpret the spec (rejected — FR-008 pins the exact message text); rename the widget to match the constant (rejected — catalog keys are the stable surface and the button keys already exist).

## R3 — Shared reason-option labels and bilingual catalogs

**Decision**: Keep `INACTIVITY_REASONS` in `apps/web/src/app/lib/api/daily-reports.ts` as the single ordered value source, but have both editing surfaces render option labels through the existing `dailyReports.inactivityReasons` catalog keys rather than the hardcoded Persian labels.
**Rationale**: FR-004/FR-005 require exactly the five values in both Persian and English from both catalogs; the list-of-values metadata already exists in `fa.json`/`en.json`, so no new keys are needed. The stable values remain language-independent.
**Alternatives considered**: Duplicating a second localized list inside each surface (rejected — contract forbids duplicated abbreviated labels); server-driven labels (rejected — labels are presentation state, values are the contract).

## R4 — Validation across all write paths and the offline queue

**Decision**: Keep server-side enforcement as the write-path boundary; the offline queue replays into the same serializer validation, which is sufficient for FR-010.
**Rationale**: The serializer and lifecycle views guard every create/full-update/partial-update/submit/review/approve path; queued offline header mutations (`offlineWrite.ts` carries `site_status: report?.site_status` metadata and sync payloads flow through `syncBatch`) are rejected by the same server rules with `inactivity_reason_required` on replay. Client-side pre-gating for the reason on offline queueing is not required by the approved prompt (the guard is specified for the positive-quantity warning only).
**Alternatives considered**: Adding a client-side reason pre-check to offline queue insertion (out of specified scope; defer unless implement observes a concrete failure).

## R5 — Aggregation and override behavior

**Decision**: Leave `daily_report_aggregation.py` behavior unchanged; its existing rules already satisfy the spec.
**Rationale**: Rebuild preserves a validly chosen reason and clears it only when the reconciled status is active (`InactivityReason.values` membership guard), and an approved `site_status_override` keeps the editor's authority — matching spec assumptions.

## R6 — Verification strategy for the residual scope

**Decision**: Separate evidence categories: (a) backend pytest re-run of the inactivity and permission test modules; (b) `pnpm typecheck`; (c) new unit tests for the guard predicate constants/keys; (d) new bilingual Playwright E2E covering inactive-day confirm, cancel, and zero-quantity paths; (e) PDF text extraction spot-check for the reason row.
**Rationale**: Constitution Principle VI demands distinct backend/browser/verification categories; the residual work is UX-copy-level, so browser evidence is the decisive category.
**Alternatives considered**: Relying on existing backend tests alone (rejected — the deltas are user-facing bilingual copy).
