# Form 5 decision (Sprint 5)

**Decision:** Reuse `DailyReportLabor` for standalone manpower entry — do **not** create a separate `DailyManpower` model.

**Rationale:**
- Form 5 UI is a pivot grid (job title × three shifts), matching `shift_1/2/3_count` on `DailyReportLabor`.
- Keeps personnel summary (Form 10) on one unified table.
- Avoids duplicate headcount records.

**Schema changes:**
- `report` FK is now nullable.
- Added `project` + `report_date` for standalone rows (`report IS NULL`).
- Unique constraints split between report-scoped and standalone-scoped rows.
