# Contract: Unit-Report Sections & Summary UI (feature 033)

Frontend targets the existing Specialty Units pages (`apps/web/src/components/department/unit-daily-report-panel.tsx` family). No new route; `/sub-reports` stays retired (032).

## 1. Unit-page section editors

Per canonical unit, the panel shows section tabs matching that unit's responsibility set:

| Unit | Sections |
|---|---|
| Buildings | Executed activities (+ attachments), Direct/indirect labor, Concrete, General activities, Issues/barriers, Visits |
| Electrical | Executed activities (+ attachments), Labor (direct + applicable indirect), General activities, Issues/barriers |
| Mechanical | Executed activities (+ attachments), Labor, Concrete, General activities, Issues/barriers |
| Machinery | Machinery status (five statuses) + hours/stoppage (reason from controlled choices), General activities |
| Warehouse | Materials receipts/consumption (transaction-typed rows), General activities |
| Security/HSE | Issues/barriers, Visits, HSE incidents (severity, immediate action), General activities |

Editor expectations (Constitution VII):

- Required fields are marked and validated inline with localized error chips; server error codes (section API) map to localized messages; never show raw codes only.
- Searchable creatable selects (contractor, WBS activity, material, job title, batching plant) place their **Add action inside the opened menu**, not outside it.
- Lists render in the row order that aggregation will preserve (`row_number`); reorder is an explicit edit action, applied by renumbering.
- Submit/correction flows reuse the 032 panel controls; on submit, section-level violations shown field-by-field with `submission_blocked_by_section_contract` as the banner reason.
- Attachment upload shows the size/type limit up front, uses inline feedback for rejection, and previews only validated images.

## 2. Project daily summary display

`DailyReportSummaryView` extensions (read-only presentation of the summary-API shape):

- **Machinery table**: columns total/active/ready/inactive/under-repair (+ hours and reason where present), localized headers, text-plus-color status, one row per item identity or type, no duplicate items. A dedicated provenance affordance navigates to the Machinery unit row.
- **Materials**: main table lists **only resolved receipts**; a visible "details" toggle/drill-down reveals consumption rows, unresolved-reference rows, and per-row reconciliation status (match/mismatch/insufficient data, with the referenced document label). Consumption is never hidden from the details view (FR-022).
- **Labor**: indirect/direct/overall totals per title (localized, `fa` numerals safe, Jalali-aware dates only where shown); each combined total with >1 source exposes a drill-down listing **every** contributing row/unit (badge style, keyboard accessible).
- **Executed activities**: full column set, crew and contractor as separate columns; every row's provenance affordance navigates in one step to the source unit context (Constitution I: navigation modifier doesn't bypass permissions — unauthorized sources render a permission notice, never the data).
- **Structured narrative sections**: general activities, issues/barriers (owner + due date, overdue visually and textually marked), visits, HSE incidents (severity pill + immediate action + notification confirmed state) rendered as tables/lists in preserved display order; no inline editing; correction affordance deep-links the source unit row (read-only derived rows remain read-only — FR-043).
- **Concrete**: full column set; declared sampling rows show the QC link; missing/incomplete test information surfaces as a visible warning state sourced from validation, not fabricated zeros.
- **Attachments**: per-section accessible image count with links; no gallery in the summary; printable/PDF layout remains the next feature's scope (no gallery markup shipped here).
- **Empty / zero / unknown**: sections render a distinct "no data submitted" state vs literal `0` vs "unknown/not provided" (`—` for unknown), everywhere data is displayed; missing data never displays as a fabricated zero (FR-040).
- Totals footer parity: indirect/direct/overall labor totals always computable and shown when at least one contributing labor row exists.

## 3. Localization & accessibility

- All new strings in `fa.json`/`en.json` (labels, section names, statuses, validation codes, drill-down text, empty/zero/unknown states); stable identifiers never localized.
- Jalali/`en` date inputs (capture date, due date) follow the 032 date-picker standards (bilingual persistence check on reopen).
- Keyboard accessibility: all section editors operable via keyboard; drill-down links focusable with visible focus state; tables have proper header semantics.
- Screen-reader labels for status pills (severity, reconciliation status, partial-complete states), not color-only signals.

## 4. Boundary

The summary this feature renders is the bounded data surface (tables, totals, counts, links); final printable/PDF-Excel composition, report header/number/page numbering visuals, and signature areas are intentionally out of scope here (third feature of the series).
