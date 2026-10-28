# Research & Architectural Decisions: Automated Periodic Reports Rollup, Figure Provenance, and Controlled Override Audit

**Feature**: `041-periodic-reports-rollup`  
**Status**: Completed  
**Authors**: Antigravity Full-Stack AI Engineer  

---

## 1. Architectural Context & Problem Statement

In construction project management under Iranian and international contract standards, weekly site reports (گزارش‌های هفتگی کارگاه) and monthly executive progress reports (گزارش‌های ماهانه پروژه) are formal contractual documents. Currently, the periodic report engine in `apps/api/core/schedule/services/period_report_service.py` provides high-level schedule stubs and financial snapshots, but:
1. **No Daily Report Rollup**: Weekly reports do not pull labor man-hours, machinery operating hours, material quantities, or completed activities from daily reports. Site teams must compile numbers manually.
2. **Missing Approval Boundary**: Unapproved or draft daily records are not checked, and missing days in reporting cycles produce no explicit warnings.
3. **Absence of Provenance & Referential Protection**: Aggregated figures cannot be broken down to their constituent daily entries. Furthermore, underlying daily logs can be deleted, corrupting historical figures without referential protection (`PROTECT`).
4. **Unregulated Figure Overrides**: Overrides currently accept single-character or blank reasons, overwrite the primary value without preserving `calculated_value`, allow users with only `edit_activities` to override reports, and do not present footnotes in the UI.
5. **Incomplete Monthly Status Report**: Monthly reports lack HSE incident rollups, QC inspection summaries, Cost Performance Index (CPI), and official release serialization.
6. **Locale & Presentation Mismatch**: The UI uses Gregorian Monday–Sunday defaults and dumps raw JSON strings in table cells.

---

## 2. Decision Log & Alternatives Considered

### Decision 1: Aggregation Architecture for Daily Reports in Weekly Progress Reports
- **Decision**: The rollup engine in `period_report_service.py` will query approved `DailyReport` records for the project within `[period_start, period_end]`. It will compute:
  1. `completed_activities`: Work activities completed in the period (filtered by actual finish date or verified 100% completion).
  2. `critical_activities`: Scheduled activities on the critical path with negative schedule variance or delay.
  3. `labor_machinery`: Sum of regular hours and overtime hours grouped by contractor and labor trade/category; and machinery operating, idle, and repair hours grouped by equipment type.
  4. `materials`: Total delivered and consumed quantities grouped by material description/specification and unit.
  5. `next_week_plan`: Upcoming activities in the lookahead window `[period_end + 1 day, period_end + 7 days]`.
- **Alternative Considered**: Performing aggregation in database views or Celery background jobs.
  - *Rejected*: Report generation is an intentional synchronous user action executed on demand. In-memory aggregation over the 7 daily records of a workweek takes < 50ms and allows atomic creation of `PeriodReportFigure` and `PeriodReportFigureSourceItem` records in a single database transaction.

### Decision 2: Approval Gate & Header Warning Mechanism
- **Decision**: Daily reports with status other than `ReportStatus.APPROVED` (or days where no daily report was submitted) are strictly excluded from numerical sums. Each missing or unapproved calendar day in the workweek triggers an explicit Persian warning entry in the `warnings` array of `ProjectPeriodReport`:
  `«گزارش روز [تاریخ شمسی] تأیید نشده است و احجام آن در این گزارش لحاظ نگردید»`.
  If no daily reports exist for the entire period:
  `«هیچ گزارش روزانه‌ای برای بازه انتخابی ثبت نشده است»`.
- **Alternative Considered**: Silently treating draft reports as zero or including draft reports with a caveat.
  - *Rejected*: In contractual disputes, incorporating unapproved daily draft numbers creates liability. Explicit header warnings ensure complete transparency and legal defensibility.

### Decision 3: Granular Figure Provenance & Referential Protection (`models.PROTECT`)
- **Decision**: Create a dedicated model `PeriodReportFigureSourceItem` linking each `PeriodReportFigure` to its exact constituent records.
  To strictly enforce referential integrity protection (preventing deletion of source daily reports or their items):
  - Model has explicit foreign keys with `on_delete=models.PROTECT` to `DailyReport`, `DailyReportLabor`, `DailyReportEquipment`, `DailyReportMaterial`, `DailyReportActivity`, `DailyReportIncident`.
  - When an authorized user views a figure, a provenance endpoint `GET /api/v1/projects/{project_pk}/progress-reports/figures/{figure_id}/sources/` returns the itemized list: Jalali date, daily report code, contributing volume, creator user, and approving supervisor.
  - Any attempt to directly modify figure values using HTTP PUT/PATCH is rejected with HTTP 400 and code `figure_immutable`.
- **Alternative Considered**: Storing provenance as a raw JSON blob on `PeriodReportFigure`.
  - *Rejected*: JSON blobs cannot enforce relational database constraints (`on_delete=models.PROTECT`). Deleting a daily report would leave broken orphan pointers. Foreign keys with `PROTECT` guarantee true database-level immutability.

### Decision 4: Controlled Figure Override Audit Workflow
- **Decision**: 
  - Authorization: Only users with `edit_reports` or `approve_reports` permissions on the project can submit figure overrides. Users with `edit_activities` or general viewer permissions receive HTTP 403.
  - Rationale constraint: The `reason` field must contain at least 10 non-whitespace characters. Submissions with shorter reasons fail validation with error code `override_reason_required` and message `«دلیل بازنویسی باید حداقل ۱۰ کاراکتر باشد»`.
  - Value preservation: `PeriodReportFigure.calculated_value` retains the initial computed value permanently. `PeriodReportFigure.value` holds the new active overridden value, and `is_overridden` is set to `True`.
  - Audit trail: `PeriodReportFigureOverride` logs `old_value`, `new_value`, `reason`, `created_by`, and `created_at`.
  - Presentation: Overridden figures display an asterisk (`*`) and an explanatory footnote in both web UI and export views.
- **Alternative Considered**: Allowing the overriding user to modify the figure silently and overwriting `calculated_value`.
  - *Rejected*: Violates Constitution Principle IV (Safe Business Mutations) and Contract Auditability (US-PR-07). Original calculated figures must never be erased.

### Decision 5: Monthly Comprehensive Chapters, SPI/CPI, and Serialized Release
- **Decision**: Monthly reports will compile 7 comprehensive chapters:
  1. `progress_summary`: Cumulative planned vs actual physical progress with S-curve data points.
  2. `financial_ipc`: Financial status, commitments, and Interim Payment Certificates (IPC).
  3. `hse_summary`: Rollup of daily HSE incidents (safety, environmental, near-misses, lost time).
  4. `qc_summary`: Quality inspections and Non-Conformance Reports (NCR) summary.
  5. `variance_analysis`: Schedule variance, SPI (`EV / PV`), and CPI (`EV / AC`). If cost or planned data is not recorded, explicitly return `value_status = "not_recorded"` rather than misleading 0.0 values.
  6. `risks_decisions`: Critical risks, technical obstacles, and required decisions.
  7. `next_month_forecast`: Lookahead forecast for the upcoming month.
  - Approval workflow: An official approval endpoint `POST /api/v1/projects/{project_pk}/progress-reports/{report_id}/approve/` requires `approve_reports` permission, transitions report status to `approved`, sets `approved_by` and `approved_at`, and assigns an immutable unique official serial number formatted as:
    `REP-{PROJECT_CODE}-{JALALI_YEAR_MONTH}-{SEQ}` (e.g., `REP-PRJ01-140508-M01`).
  - Once approved, report figures and metadata are locked and immutable.
- **Alternative Considered**: Dynamic serial numbers generated on the fly during rendering.
  - *Rejected*: Legal documentation requires an immutable, registered serial number assigned once at formal sign-off.

### Decision 6: Solar Hijri (Jalali) Calendar Workweeks and Structured Presentation
- **Decision**:
  - The construction workweek in Iran runs from Saturday (شنبه) to Friday (جمعه).
  - In `apps/web/src/app/lib/jalali-utils.ts`, implement helpers `getSolarHijriWorkweekBounds()` and `getSolarHijriMonthBounds()` using `react-date-object` (persian calendar).
  - Replace raw JSON string dumps in `PeriodReportsPanel.tsx` with dedicated responsive cards and tables for:
    - Labor man-hours breakdown (trades, shifts, regular and overtime hours)
    - Machinery operational status (active, idle, repair hours)
    - Material delivery and consumption table
    - Completed activities and critical delays
    - Footnote audit drawer for overridden figures
    - Provenance modal showing the itemized daily sources.

---

## 3. Technology Stack & Dependencies

- **Backend**: Python 3.12, Django 4.2.11, Django REST Framework, `jdatetime`, PostgreSQL 16 (port 5433), Redis (port 6379).
- **Frontend**: React Router 7, Vite, Tailwind CSS, TanStack Query, `react-date-object`, Lucide icons.
- **Testing**: `pytest`, `pytest-django`, `@pytest.mark.django_db`, React component unit/type checking via `pnpm --filter web build`.
