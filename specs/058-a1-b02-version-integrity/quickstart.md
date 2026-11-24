# Quickstart Validation Guide: Phase A.1 / B02 Version Integrity, Derived-Row Lock & Lineage Preservation

**Feature**: `058-a1-b02-version-integrity`  
**References**: [spec.md](./spec.md) | [data-model.md](./data-model.md) | [contracts/version-integrity-api.md](./contracts/version-integrity-api.md)

## 1. Prerequisites

1. Native PostgreSQL (port `5433`) and Redis (port `6379`) running:
   ```bash
   sudo pg_ctlcluster 16 main start
   sudo redis-server /etc/redis/redis.conf --daemonize yes
   ```
2. B01 migrations and blueprint schema intact (0 new migrations in B02):
   ```bash
   cd apps/api/core && set -a && source ../../../.env && set +a
   ../.venv/bin/python manage.py verify_blueprint_schema
   ```
   Expected: `40/40` blueprint tables and `25` extension tables verified.

## 2. Automated Pytest Verification (B02 + Regression Suite)

Run the dedicated B02 version-integrity test suite and existing daily-report lifecycle/aggregation regression suites:
```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  field_reports/tests/test_a1_b02_version_integrity.py \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_daily_report_derived_readonly.py \
  field_reports/tests/test_unit_report_provenance.py \
  field_reports/tests/test_unit_report_rebuild_idempotency.py \
  field_reports/tests/test_unit_report_aggregation_eligibility.py \
  field_reports/tests/test_unit_report_completeness.py \
  field_reports/tests/test_activity_log_sync.py \
  field_reports/tests/test_offline_legacy_protection.py \
  field_reports/tests/test_summary_snapshot_comparison.py \
  field_reports/tests/test_approval_workflow.py \
  field_reports/tests/test_daily_report_summary_permissions.py
```
Expected: **100% pass, 0 failures, 0 `XFAIL` markers** for all B02 defects (`DEF-B02-01` through `DEF-B02-06`).

## 3. End-to-End Validation Scenarios

### Scenario A — Full Revision Lifecycle & Multi-Source Lineage (`SC-001`, `SC-003`, `DEF-B02-01`..`04`)
1. Build an approved derived daily summary (`v1`) aggregated from at least two units (`buildings` + `electrical`) contributing to a shared derived row with `2` `DailyReportDerivedSource` records, plus a saved `management_opinion` and `weather_override=True`.
2. Open a correction (`POST .../correction-requests/` with reason ≥ 10 chars) → verify `v2` has `is_auto_summary=True`, `management_opinion` preserved, `weather_override=True`, `reporting_configuration` preserved, and `2` remapped `DailyReportDerivedSource` rows pointing to `v2`'s child row UUID.
3. Attempt direct `POST`, `PATCH`, and `DELETE` on `v2` derived child rows (single-row, labor batch upsert, legacy nested `activities` PATCH, and `sync-batch`) → direct, batch, and legacy writes return `400`. Offline sync returns `200` with an item error carrying `derived_readonly`. Stored rows stay unchanged.
4. Edit authorized project metadata (`management_opinion`) on `v2` → succeeds (`200`).
5. Update a source unit sub-report and trigger authorized rebuild (`POST .../rebuild/` or unit submit) → `v2` derived rows refresh while `management_opinion` and `weather_override` remain preserved.
6. Submit and approve `v2` (with valid approver respecting separation of duties) → verify `v2` is `approved` + `is_current=True`, `v1` is `approved` + `is_current=False`, and both versions retain independent, complete provenance.

### Scenario B — Official Activity Master Log Current-Version Policy (`SC-004`, `DEF-B02-05`)
1. With `v1` (approved, superseded, quantity `5`, headcount `4`) and `v2` (approved, current, quantity `5`, headcount `4`):
   - Query `GET .../activity-log/` → verify exactly `1` row returned with quantity `5` and headcount `4` (never `2` rows / `10` / `8`).
   - Open `GET .../activity-log/excel/` and check that the ACTIVITY sheet has one data row with quantity `5` and headcount `4`.
   - Query `GET .../daily-reports/{v2_id}/versions/` → verify both `v1` and `v2` appear in version history.

### Scenario C — Cancellation & Exact Restoration (`SC-001`, `SC-003`)
1. Open a correction `v3` from approved `v2`, then cancel it (`POST .../correction-requests/{id}/cancel/`).
2. Verify `v3` is soft-deleted (`is_current=False`), `v2` is restored as `is_current=True` with `is_auto_summary=True`, `management_opinion`, `weather_override`, and all `2` provenance records intact, and `activity-log` reflects `v2` cleanly.

### Scenario D — Historical / Approved / Deleted Rebuild Rejection (`SC-006`, `DEF-B02-06`)
1. Invoke explicit rebuild against: (a) superseded historical `v1` (`is_current=False`), (b) current approved `v2` (`status=approved`), and (c) cancelled soft-deleted `v3` (`is_deleted=True`).
2. Verify all three are rejected with localized bilingual errors (`historical_rebuild_rejected`, `report_locked`, `rebuild_target_deleted`) and 0 rows/provenance/snapshots are modified.
3. Modify a source unit sub-report after `v2` is approved → verify `v2`'s approved snapshot remains unchanged and drift comparison detects the difference.

### Scenario E — Concurrency, Six-Unit Templates, Source Eligibility & RBAC (`SC-007`)
1. Submit two concurrent correction requests on the same approved report → one succeeds (`201`), second rejected (`400`, `correction_already_open`).
2. Verify two `ProjectReportingConfiguration` versions with different effective dates enforce date-effective required units across the 6 valid units.
3. Verify `draft`, `rejected`, `soft-deleted`, superseded, other-date, and other-project unit sub-reports contribute 0 rows and 0 completeness credit.
4. Verify read-only viewer can open `by-date` without `edit_reports`, unauthorized/cross-project/admin-observer users are denied mutations (`403`), rejection reason `< 10` chars is rejected (`400`), and bilingual FA/EN error messages match `Accept-Language`.

## 4. Live bilingual walkthrough

Run the web and API servers against a dedicated local database with synthetic project members and two eligible source units. Use an independent correction for each language.

1. In Persian and English, sign in through the web UI and open the dated project activity log. Check that the current approved activity appears once.
2. Open a correction with the API and visit the draft's daily-report view. Check reading direction, the two-source disclosure, preserved opinion and weather override, and the localized metadata editor. Save a new opinion and reload to check persistence.
3. Return to the same dated activity log and confirm the official list is empty while the correction is open. Cancel the correction and reload to check that the approved activity returns.
4. Call explicit rebuild on the approved report with each language header and verify the same `report_locked` code with the localized message.

## 5. Governance Note
Passing all automated and live checks above establishes **technical readiness** for Package B02 (`A.1.03`) and unblocks `B03`/`B04`. **Employer final acceptance** remains gated on independent review in Package `B06`.
