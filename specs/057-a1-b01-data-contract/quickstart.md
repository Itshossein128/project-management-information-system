# Quickstart & Validation Guide: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Feature**: `057-a1-b01-data-contract` | **Date**: 2026-11-19 | **Spec**: [spec.md](./spec.md)

This guide defines the runnable verification steps proving **B01** end-to-end once implemented. For entity schemas see [data-model.md](./data-model.md); for API, service, and CLI interfaces see [contracts/api-contract.md](./contracts/api-contract.md) and [contracts/daily-report-data-contract.v1.json](./contracts/daily-report-data-contract.v1.json).

---

## 1. Prerequisites

Ensure native PostgreSQL (port `5433`) and Redis (port `6379`) are running, and root `.env` is configured (`AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`):

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Apply Django migrations (using the pinned Django 4.2 venv at `apps/api/.venv`):

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python manage.py migrate
```

---

## 2. Validation Scenario 1 — Migration Apply, Data Preservation, Uniqueness & Rollback Awareness (Constitution Principle II)

On an isolated PostgreSQL verification database, verify forward apply, reverse rollback, and re-apply of both additive B01 migrations (`projects/0022_project_coordinates` and `field_reports/0026_daily_report_b01_contract`) against PostgreSQL:

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python manage.py migrate projects 0022
../.venv/bin/python manage.py migrate projects 0021
../.venv/bin/python manage.py migrate projects 0022
../.venv/bin/python manage.py migrate field_reports 0026
../.venv/bin/python manage.py migrate field_reports 0025
../.venv/bin/python manage.py migrate field_reports 0026
```

**Expected Outcome**:
- Forward migration `projects/0022_project_coordinates` (depending on `0021_project_measurement_unit`) adds nullable `latitude` and `longitude` on `projects`; reverse to `0021` and re-apply to `0022` succeed cleanly without affecting pre-existing project rows.
- Forward migration `field_reports/0026_daily_report_b01_contract` (depending on `0025_material_unknown_type`) creates `daily_report_worked_shifts`, adds defaulted/nullable columns on `daily_reports`, and creates `unique_current_contract_daily_report_per_date` alongside legacy `unique_current_daily_report_per_date_shift`.
- Reverse migration to `0025` and re-apply to `0026` succeed cleanly without altering or deleting pre-existing legacy `daily_reports` rows.
- Pytest verifies that pre-existing legacy same-date `day` + `night` rows (`contract_version=''`) remain preserved, while inserting two current contract-bound reports (`contract_version='1.0.0'`) for the same `(project, report_date)` raises `IntegrityError` even if their legacy `shift` values differ.

---

## 3. Validation Scenario 2 — Seed & Verify `SIM-A1-001` Reference-Day Fixture (`US1`, `FR-001`, `FR-002`)

Run the idempotent synthetic reference fixture command twice to verify creation and idempotency:

```bash
../.venv/bin/python manage.py seed_a1_reference_fixture
../.venv/bin/python manage.py seed_a1_reference_fixture
```

**Expected Outcome**:
- Project `SIM-A1-001` exists with `start_date = 2027-05-11` (Solar Hijri `1406-02-21`).
- Exactly one current `DailyReport` exists for `2027-05-22` (Solar Hijri `1406-03-01`) with `is_synthetic_reference = True`, `project_day = 12`, and `official_report_number = "SIM-A1-001-12-1406-03-01"`.
- Worked shifts list ONLY Shifts `1` (`8.50` h) and `3` (`None` / unknown); Shift `2` is absent.
- Activity rows include measured `0`, `0.00`, `12.50`, unset (`null`), and `not-measured`.
- Labor rows include standard Shiraz 34/32 titles plus custom/historical titles for Appendix verification.
- `WeatherLog` for `2027-05-22` includes `wind_speed` and `soil_condition`.
- Second invocation produces zero duplicate rows and leaves all non-`SIM-A1-001` projects untouched. Use `--reset` to restore the fixture-owned rows in place.

---

## 4. Validation Scenario 3 — Run B01 Contract & Regression Pytest Suite (`US1`–`US6`, `SC-001`–`SC-006`)

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python -m pytest field_reports/tests/test_a1_b01_data_contract.py -v
```

**Expected Outcome** (all tests pass):
1. **Migration, Legacy Preservation & Final Uniqueness (`C03`, `FR-011`, Principle II)**: Pre-existing legacy same-date `day` + `night` rows (`contract_version=''`) remain preserved, while inserting two current contract-bound reports (`contract_version='1.0.0'`) on the same `(project, report_date)` raises `IntegrityError` under `unique_current_contract_daily_report_per_date` even with differing legacy `shift` values; superseded (`is_current=False`) and soft-deleted (`is_deleted=True`) revisions remain allowed; a recorded duration outside `(0, 24]` fails its database constraint; reverse migration `0026 -> 0025 -> 0026` is clean.
2. **Contract Completeness (`SC-001`, `SC-002`, `SC-003`)**: `daily_report_contract_v1.json` validates with version `1.0.0`, all 18 broader sections mapped, `C01`–`C10` + `GOV-01` recorded with provenance, employer acceptance fields `null` (deferred to `B06`), and 100% of required reference-form fields mapped.
3. **Zero vs. Unset vs. Not-Measured (`C02`, `FR-009`, `FR-010`)**: `0`/`0.00` stays numeric zero; `null`/`not-measured` remains unknown and excluded from sums (fixture total `12.50` with `unrecorded_count = 2`); positive-only domain validators still reject `<= 0`.
4. **Shifts, Actual Durations & Bilingual Labor Metrics (`C03`, `FR-011`–`FR-013`)**: Only worked shifts `1`/`3` appear; invalid shift IDs raise validation error; missing Shift `3` duration produces `person_hours = None` (`unknown`, NEVER `8` h default); `person_days` (`نفر-روز`) is rejected without unique attendance proof.
5. **Catalog vs. Shiraz 34/32 Profile & Appendix (`C04`, `FR-014`, `FR-015`)**: `resolve_labor_rows_for_profile(..., "shiraz-34-32-v1")` maps standard roles into 34/32 slots and isolates extra/custom/historical titles into `appendix_indirect` / `appendix_direct` without altering historical records.
6. **Official Numbering, Weather Logs & MET Norway Fallback (`C08`, `FR-017`)**: `SIM-A1-001` on `1406-03-01` produces `SIM-A1-001-12-1406-03-01`; missing `start_date` or `report_date < start_date` returns `status="unknown"`; MET Norway responses are tested with controlled provider data, and offline or missing-coordinate forecasts degrade to `status="unknown"` without fabricated values.
7. **Authorization & Scope Boundaries (`C06`, `FR-018`, `FR-019`, Constitution Principle I)**: Unauthenticated or unauthorized users receive `401`/`403` on the contract endpoints; authorized project members receive `200 OK`; `signature_scope` asserts `pki_digital_signature_claimed: false`.

---

## 5. Verification Boundary Statement (Constitution Principle VI)

- Running Scenarios 1, 2, and 3 establishes **B01 internal verification** against `SC-001`–`SC-006` using PostgreSQL, Redis, Django migrations, and pytest.
- Live browser UAT of downstream exporter/filter UIs (`B03`/`B04`), independent numeric reconciliation (`B05`), and final employer acceptance sign-off (`B06`, recording named employer representative and acceptance date under `GOV-01`) remain explicitly outside B01 and are handed off to their recorded owner packages.
