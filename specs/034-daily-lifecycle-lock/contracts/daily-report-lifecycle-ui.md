# Contract: Daily Report Lifecycle UI

## Correction cancellation

The existing approval status bar remains the sole correction/cancellation entry point.

| State | Required behavior |
|---|---|
| Current correction draft: `draft`, version > 1, matching open request | Show `انصراف از اصلاح / لغو درخواست`; explicit confirmation is required. |
| Successful cancellation | Refresh report/history state and navigate to returned `source_report_id`; give localized feedback. |
| Other state, no matching open request, or not server-correctable | Do not render cancellation. |

The client renders affordances from current state; the server remains authoritative for every transition.

## Version history

Keep version number/current/status/lock markers. For every version also show modifier name, correction reason, and `approved_at` via the established Jalali date-time formatter. Render unavailable values honestly, keep the panel keyboard reachable, and never copy a successor’s correction reason to the root version.

## Quantity-state presentation

| Stored state | Editable activity view | Read-only activity view | Summary |
|---|---|---|---|
| Numeric quantity, including `0` | Numeric editor/value; `0` visible | Numeric `0` | Numeric `0` |
| `quantity` is null | Blank editor until input; labelled state in display context | Muted `ثبت‌نشده` warning label | Muted `ثبت‌نشده` warning label |
| `quantity_measured` is false | Existing not-measured editing semantics | Muted `ثبت‌نشده` warning label | Muted `ثبت‌نشده` warning label |

The label has text plus muted warning styling; colour is supplemental. Restrict this reusable rule to activity quantity surfaces in this feature.

## Browser-test affordances

Preserve existing correction/version test ids. Add stable semantic ids for cancellation trigger, confirmation dialog/action, and unset quantity label; these complement accessible labels and visible Persian text.
