# UI Contract: Site Inactivity, Conflict Guard, and Access Hardening

**Feature**: `specs/031-site-inactivity-security` | **Date**: 2026-10-22

## 1. Covered surfaces

- `ReportHeader` (daily-report form header) — reason selector;
- auto-summary metadata editor in `daily-report-view.tsx` — reason selector;
- `ActivityTab` activities grid + confirmation dialog;
- read-only summary display (`DailyReportSummaryView`).

The editing surfaces share one reason-value source (`INACTIVITY_REASONS` in `apps/web/src/app/lib/api/daily-reports.ts`), the same catalog keys, and the same field-error mapping.

## 2. Dynamic reason selector

- Renders exactly while the selected site status is inactive, offering exactly the five approved values in catalog order.
- Switching the status back to active clears the local reason immediately (`inactivity_reason: null`) and hides the selector.
- Option labels come from `dailyReports.inactivityReasons.{value}` in `fa.json`/`en.json`; visible text is the localized label, never the raw value, in both locales.
- The server error `inactivity_reason_required` maps to the `inactivity_reason` field region with the localized `errors.inactivity_reason_required` text; block save and show inline feedback next to the selector.

## 3. Inactive-day activity confirmation dialog (residual alignment scope)

- Trigger: creating or editing an activity row whose committed quantity is strictly positive while the report's site status is inactive; zero/blank/not-supplied quantities and inactive-immaterial rows never trigger; active site status never triggers.
- Copy (approved, both locales, identical between constants and catalog keys):
  - fa: «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟»
  - en: matching approved English equivalent.
- The dialog copy is looked up via the catalog key `dailyReports.inactiveSiteActivityWarning` (fixing the current `inactiveActivityWarning` miss); components must not depend on the fallback constant being Persian-only.
- Dialog title and footer buttons are localized (fa and en); buttons reuse `dailyReports.confirmActivity` / `dailyReports.cancelActivity`.
- Confirm → resolve save gate success; the row is recorded as entered.
- Cancel (button or overlay/Escape close) → resolve save gate failure; nothing is saved or overwritten and the in-progress entry remains in the editor.
- Behavior parity pointer/table editing (typed or navigated) unaffected when no warning triggers.

## 4. Accessibility

- Dialog: accessible title and description, keyboard-operable confirm/cancel, focus return to the editor row after cancel.
- Reason selector is label-associated (`htmlFor`), the required indication is textual (not color-only).
- Errors reference the field via `aria-describedby`, set `aria-invalid`, and are announced via `role="alert"`/live region consistent with existing error rows.
- Persian renders under RTL and English under LTR; mixed content remains readable.

## 5. Localization keys (all exist; the warning copy wording is the only text change)

| Key (fa/en) | Purpose |
|---|---|
| `dailyReports.inactivityReason` | Field label of the selector |
| `dailyReports.inactivityReasons.{5 values}` | Option labels |
| `errors.inactivity_reason_required` | Validation message |
| `dailyReports.inactiveSiteActivityWarning` | Warning dialog body (reworded to approved text) |
| `dailyReports.confirmActivity` / `dailyReports.cancelActivity` | Dialog buttons |
| new: `dailyReports.inactiveActivityDialogTitle` (fa + en) | Dialog title replacing the inline string |

## 6. Acceptance scenarios

1. In Persian and English, both editing surfaces show exactly the five reasons when the status is inactive and none when active.
2. Confirming the dialog saves the positive-quantity row; canceling keeps the editor state unchanged with no write.
3. Zero-quantity and blank-quantity rows on an inactive day never show the dialog; positive rows on an active day never show it.
4. A Persian and an English editor each complete the closure-reason cycle (set inactive → choose reason → save → reopen → readback label) on the first attempt.
5. Save with inactive + empty reason is blocked inline with the localized `inactivity_reason_required` message and makes no API call.
6. The dialog body text equals the approved copy in both locales (constants and catalogs identical).
