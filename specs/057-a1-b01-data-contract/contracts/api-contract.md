# Interface & API Contracts: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Feature**: `057-a1-b01-data-contract` | **Contract Version**: `1.0.0` | **Date**: 2026-11-19

This document defines the HTTP API, Python service, and CLI interfaces owned by **B01**. Machine-readable schema and full mappings live in [daily-report-data-contract.v1.json](./daily-report-data-contract.v1.json).

---

## 1. Read-Only HTTP API Contracts (DRF)

All project-scoped endpoints enforce **Constitution Principle I** (server-side authentication, active project membership or bounded org-admin read-only observation exception, and project read permission).

### 1.1 `GET /api/v1/projects/{project_id}/daily-reports/contract/`
Returns the active versioned Phase A.1 Daily Report Data Contract artifact metadata, decision register (`C01`–`C10` + `GOV-01`), 18-section disposition matrix, bilingual labor metrics, selectable form profiles, and independent field mappings.

- **Auth**: Authenticated + `view_reports` project permission (or bounded org-admin read-only exception).
- **Query Params**:
  - `include_mappings` (`true` | `false`, default `true`)
  - `profile` (optional, e.g., `shiraz-34-32-v1`)
- **Response `200 OK`**:
```json
{
  "contract_version": "1.0.0",
  "reference_form_version": "shiraz-file4-v1",
  "reference_day_fixture": {
    "project_code": "SIM-A1-001",
    "jalali_date": "1406-03-01",
    "gregorian_date": "2027-05-22",
    "project_day": 12,
    "official_report_number": "SIM-A1-001-12-1406-03-01",
    "is_synthetic": true
  },
  "governance": {
    "internal_decision_owner": "AI workflow agent",
    "internal_decision_date": "2026-11-19",
    "internal_verification_owner": "AI workflow agent",
    "employer_acceptance_representative": null,
    "employer_acceptance_date": null,
    "employer_acceptance_owner_package": "B06"
  },
  "scope_decisions": ["..."],
  "broader_sections": ["..."],
  "labor_metrics": ["..."],
  "field_mappings": ["..."]
}
```

### 1.2 `GET /api/v1/projects/{project_id}/daily-reports/{report_id}/contract-summary/`
Returns the B01 contract-evaluated summary envelope for a specific `DailyReport` (including `SIM-A1-001-12-1406-03-01`), without altering legacy serializer fields needed by other modules:

- **Response `200 OK`**:
```json
{
  "contract_version": "1.0.0",
  "is_synthetic_reference": true,
  "official_numbering": {
    "project_code": "SIM-A1-001",
    "actual_start_date": "2027-05-11",
    "report_date_gregorian": "2027-05-22",
    "report_date_jalali": "1406-03-01",
    "project_day": 12,
    "official_report_number": "SIM-A1-001-12-1406-03-01",
    "status": "ok"
  },
  "worked_shifts": [
    { "shift_id": 1, "actual_duration_hours": "8.50", "duration_status": "recorded" },
    { "shift_id": 3, "actual_duration_hours": null, "duration_status": "unknown" }
  ],
  "labor_profile_resolution": {
    "profile_code": "shiraz-34-32-v1",
    "standard_indirect_slots": 34,
    "standard_direct_slots": 32,
    "appendix_indirect_count": 1,
    "appendix_direct_count": 1
  },
  "weather": {
    "observed_source": "weather_logs",
    "wind_speed": "12 km/h NW",
    "soil_condition": "خشک / Dry",
    "forecast_provider": "MET Norway Locationforecast 2.0",
    "forecast_status": "unknown",
    "forecast_days": []
  },
  "signature_scope": {
    "mode": "actor_attribution_and_metadata_fingerprint",
    "pki_digital_signature_claimed": false,
    "whole_body_tamper_seal_claimed": false
  }
}
```

---

For contract-bound reports, the existing `by-date/` endpoint accepts an optional canonical shift ID (`1`, `2`, `3`, or the corresponding `shift_N` bridge). A worked shift resolves to the same logical report, including `canonical_worked_shift_ids`. An unworked shift returns `404` and an invalid identifier returns `400`.

For a legacy date with multiple active legacy reports, `contract-summary/` emits `multiple_current_legacy_reports_for_date` and leaves the official report number unknown. No report rows are merged.

The weather summary reports the observed log date and a source status. Forecasts cover the three project-local days after the report date when the service has all three days available. Forecast times and sampled temperatures are attributed to [MET Norway Locationforecast 2.0](https://api.met.no/weatherapi/locationforecast/2.0/documentation).

## 2. Internal Python Service Contracts (Consumed by B02–B05)

| Module | Function / Class | Contract Guarantee |
| :--- | :--- | :--- |
| `field_reports.services.data_contract` | `load_daily_report_contract(version="1.0.0") -> dict` | Loads and validates the versioned JSON contract (18 sections, `C01`–`C10` + `GOV-01`, field mappings). |
| `field_reports.services.data_contract` | `compute_official_report_number(project_code, actual_start_date, report_date) -> OfficialNumberingResult` | Returns deterministic `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` in Solar Hijri, or `status="unknown"` (`project_day=None`, `official_report_number=None`) if `actual_start_date` is missing or `report_date < actual_start_date`. |
| `field_reports.services.data_contract` | `normalize_canonical_shift_id(raw_shift) -> int` | Accepts canonical `1`, `2`, `3` (or `shift_1`..`shift_3` via explicit legacy bridge); raises `ValidationError` on any invalid code. |
| `field_reports.services.data_contract` | `validate_labor_metric_label(metric_key, *, has_unique_attendance_proof: bool) -> LaborMetricDefinition` | Rejects `person_days` (`نفر-روز`) when `has_unique_attendance_proof=False` (`D07`, `FR-013`). |
| `field_reports.services.man_hours` | `compute_actual_person_hours(headcount, actual_duration_hours) -> Decimal \| None` | Returns `None` (`unknown`) whenever `actual_duration_hours is None` or `headcount is None`; NEVER defaults to `8` hours (`C03`, `FR-012`). |
| `field_reports.services.form_profiles` | `resolve_labor_rows_for_profile(labor_rows, profile_code="shiraz-34-32-v1") -> ProfileResolutionResult` | Partitions labor rows into fixed 34/32 standard slots and isolated `appendix_indirect` / `appendix_direct` lists (`C04`, `FR-014`, `FR-015`). |
| `field_reports.services.weather_forecast` | `get_three_day_forecast(latitude, longitude, *, report_date) -> ForecastResult` | Fetches 3-day forecast from free MET Norway Locationforecast 2.0 with caching; returns `status="unknown"` on missing coordinates, offline, or HTTP/timeout error (`C08`, `FR-017(c)`). |

---

## 3. CLI / Management Command Contract

### `python manage.py seed_a1_reference_fixture [--reset]`
- **Purpose**: Idempotently creates or updates the clearly labeled synthetic Phase A.1 reference project `SIM-A1-001` and its representative reference-day report for Solar Hijri `1406-03-01` (Gregorian `2027-05-22`, project day `12`, official report `SIM-A1-001-12-1406-03-01`) from `apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json`.
- **Safety Invariants (Constitution Principle IV)**:
  - Operates ONLY on `project_code='SIM-A1-001'`; never modifies or deletes any other project.
  - Marks `DailyReport.is_synthetic_reference = True`.
  - Re-running without `--reset` is idempotent (zero duplicate rows).
  - `--reset` restores the published values of fixture-owned rows in place.
  - Never imports unlabeled legacy synthetic audit samples (`GOV-01`, `FR-002`).
