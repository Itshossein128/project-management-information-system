# B03 Download and Presentation Contract

Route paths are relative to `/api/v1/projects/{project_id}/`.

## Downloads

| Deliverable | HTTP GET route | Selection and response |
| --- | --- | --- |
| DEL-01 daily Excel and PDF | `daily-reports/{report_id}/excel/` and `daily-reports/{report_id}/pdf/` | Existing routes. Render the exact authorized report version. Return XLSX or PDF. Preserve established attachment filename patterns, including `daily-report-{date}-{shift}.pdf`. |
| DEL-02 discipline Excel | `units/{unit}/daily-reports/{report_id}/excel/` | Existing route. Render the exact authorized non-deleted unit version and its canonical discipline schema. Return XLSX and retain existing filenames. |
| DEL-03 date-range Excel | `daily-reports/excel/?date_from=…&date_to=…` | One XLSX with chronological FILE 4 worksheets for current, approved, non-deleted versions in the inclusive range. Sheet names and the `daily-reports-{from}-{to}.xlsx` filename use slash-free Solar Hijri dates. |
| DEL-04 discipline PDF | `units/{unit}/daily-reports/{report_id}/pdf/` | Exact-version project and canonical unit boundary. Attachment name `unit-daily-report-{unit}-{date}.pdf` uses a slash-free Solar Hijri date. |

Success returns `200` with an attachment header and MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` or `application/pdf`. Exact-version history is available for authorized non-deleted versions.

## Authorization and read behavior

- Resolve the caller and project before resolving report, unit, child, or QC objects. Require `view_reports` and active project membership. A named observation account can access a nonsensitive export when its persisted active organization unit matches the project's owning unit. Staff and human-resources membership alone confer no exception.
- Apply resource-specific permissions to attachments, sensitive details, and sensitive exports. Build any drill-down from the selected version's same-project provenance and resolve its target under the target's own permission checks. Never emit an inaccessible file URL or fetch a child by an unscoped ID.
- Unauthenticated requests receive the established authentication error. Authenticated callers missing permission receive `403`. Out-of-scope or soft-deleted report or unit UUIDs are treated as missing for a caller who may access the requested project route. Carry the system's established error envelope with stable codes and localized messages.
- Requests are read-only. No collection access opens a report, triggers a rebuild or changes a version. The workbook selector ignores general report-list history/status overrides. Current drafts cause their dates to be ineligible until an approved version is current. No silent fallback to older approvals.

## Range input and errors

Both dates are required. Accept Solar Hijri `YYYY/MM/DD` and Gregorian ISO `YYYY-MM-DD`. Use the project report date for inclusion. `DAILY_REPORT_EXCEL_RANGE_MAX_DAYS` defaults to 31 inclusive calendar days. The API resolves the range and eligibility before rendering.

| Case | Status and code |
| --- | --- |
| Missing, invalid or reversed dates | `400`, `invalid_export_date_range` |
| Range exceeds the configured limit | `400`, `export_date_range_too_large` |
| No eligible report dates | `400`, `no_reports_in_export_range` |
| More than one eligible report for a legacy date | `409`, `ambiguous_legacy_report_date` |

Report errors with the existing localized error conventions. Do not deliver a partial or empty workbook.

## Linked attachments and concrete evidence

- List or add version attachments at `units/{unit}/daily-reports/{report_id}/attachments/`. The upload can target an activity row or use `row_kind=report` on the selected version. Successfully uploaded JPEG/PNG images, up to 10 MiB, carry `uploaded_at` and a `download_href`. Download requires active project membership with `view_reports` and returns a short-lived signed URL. Invalid content returns the section contract's `422`. Storage connection failures return `503`. Legacy metadata-only entries have no download URL.
- The concrete row in daily version detail provides `qc_details` to an active report reader. Batch-plant data comes from the row. The lab sample code and sheet count remain separate. Mixer identifier, sheet number, slump and verified 28-day result are unknown when authoritative source evidence is absent. The project-scoped generic inspection link is distinct from a 28-day result.

## Presentation

- Reuse the version-scoped daily detail and existing `daily-reports/{report_id}/contract-summary/` response for the daily screen. Add fields only where necessary, preserving existing keys and canonical codes. Download builders use the same source projection rather than calling the endpoint.
- Use the application's supported request locale and translation catalog. Keep dates, IDs, status codes, permissions, and source codes stable at API boundaries. Preserve Persian fonts, RTL layout, readable LTR text, line breaks, and explicit unknown labels. Use project-local timestamps for attribution.
- All worksheets use A4, one page wide with flexible height, print area, repeating header rows, wrapping, and adequate row heights. User text beginning with spreadsheet formula markers stays literal. Internal formulas remain active and correct.
- FILE 5 writes the Excel numeric equivalent of `0`, `45.5`, and `100` percent as `0`, `0.455`, and `1`, using percent formatting. Null remains blank. FILE 6 retains electrical columns only.
- Daily and discipline reports paginate long tables, repeat eligible headers, and display the signature block at the end. Every non-approved PDF page shows the draft watermark. Approved pages have none. A performed stage shows recorded actor, position and local time when authoritative evidence is present. Unperformed stages show no actor. The metadata fingerprint describes version/approval metadata only.
