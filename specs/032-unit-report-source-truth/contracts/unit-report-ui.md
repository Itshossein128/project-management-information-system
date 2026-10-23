# Contract: Specialty Unit Reporting UI

**Feature**: `032-unit-report-source-truth`

## Authoring location

The only user-facing unit-report authoring surfaces are the six existing pages under the top-level Specialty Units menu:

- Buildings (`buildings`)
- Electrical (`electrical`)
- Mechanical (`mechanical`)
- Machinery (`machinery`)
- Warehouse (`warehouse`)
- Security/HSE (`security`)

All six render a shared `UnitDailyReportPanel` inside the existing unit page. No seventh HSE page and no generic standalone report page is introduced.

## Unit report panel

The panel provides:

1. Jalali-aware date picker whose selected date is retained in the URL/query state for deep links and page refresh.
2. Current report open/create behavior for the route unit and selected date.
3. Localized status badge and configuration/permission feedback.
4. Semantic audit summary for preparer, last change, submitter, approver or rejector, and times.
5. Rejection reason with `dir="auto"` and an actionable correction/resubmit path.
6. Controls derived from server capabilities: edit, submit, approve, reject, correct, delete, and history.
7. Accessible version-history table/timeline.
8. Existing report-owned rows for the selected date; row mutation is disabled unless the current report is draft/rejected.

Unit identity comes from the page route and is never selectable inside the form.

## Existing activity log transition

- Existing `DepartmentActivityRecord` history remains visible and exportable.
- Mutable records are attached to the selected unit report and follow its state/permissions.
- Direct independent add/edit/delete/import controls that could bypass the unit report are removed or routed through the current report context.
- The control currently described as a department “daily report” PDF is labeled as an activity-log export so it cannot be confused with the workflow report.
- Detailed specialty fields and layouts are deferred; this feature does not redesign every unit form.

## Workflow behavior

| State | UI behavior |
|---|---|
| `draft` | Assigned editor may edit and submit |
| `submitted` | Read-only; qualified approver may approve or reject |
| `approved` | Read-only; qualified editor may start an explicit correction version |
| `rejected` | Assigned editor sees reason, may edit and resubmit |
| historical version | Always read-only |

Controls being hidden/disabled is not presented as authorization proof. Server error codes are localized and shown inline with `role="alert"` where recovery is possible.

## Retired experience

- Remove `/projects/:projectId/sub-reports` route registration, route constants, navigation item, page component, legacy API helper, hard-coded discipline tabs, obsolete translation entries, and tests that expect it to exist.
- Direct navigation renders the standard localized not-found boundary and does not issue a report-data request.
- Do not redirect to Buildings or another arbitrary unit.
- The project daily-report page contains no “New Report” action and no legacy link. If an authoring hint is useful, show a registry-driven list/popover of the six Specialty Units preserving the selected date.

## Summary completeness and provenance

- Show separate localized states for complete, partial, and configuration incomplete.
- Expected/contributing/missing chips use canonical unit labels from the shared registry.
- Missing required units may link to the corresponding unit page with the same date, subject to normal access.
- Derived rows show unit attribution and an accessible “View sources (N)” disclosure.
- A source is linked only when `can_view_source=true`; otherwise it remains non-clickable attribution.

## Localization and accessibility

- All unit labels, states, actions, audit labels, dialogs, validation feedback, completeness states, and error messages exist in both `fa` and `en`.
- Correct Persian labels include «حراست و HSE», «انبار», and «ماشین‌آلات».
- Use stable codes internally; do not render raw backend English labels.
- Status and completeness are conveyed by text/icon in addition to color.
- Date picker, history, dialogs, disclosures, and workflow controls are keyboard operable.
- Use semantic `<time dateTime>`, `<dl>` for audit data, table captions/headers, and correct RTL/LTR behavior.
