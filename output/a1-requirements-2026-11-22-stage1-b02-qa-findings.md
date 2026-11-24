# Stage 1.2 QA Verification: Phase A.1 / B02 Version Integrity, Derived Locks, and Preservation

- **Requirement ID**: `B02`
- **Title**: Version integrity, derived locks, and preservation
- **Phase**: `A.1`
- **Stage**: `1.2 (Per-Requirement Fan-out QA Verification)`
- **Evaluation Timestamp**: `2026-11-22T20:25:00+03:30`
- **Acceptance Criteria**: Correction, cancellation, concurrency, unauthorized mutation, lineage, source preservation, reviewer/weather preservation, and approved-current aggregation pass end-user scenarios.
- **QA Status**: `qa_passed`
- **Verdict**: `passed`

---

## 1. Executive Summary

Requirement **B02** ("Version integrity, derived locks, and preservation") was comprehensively re-evaluated from the perspective of real end-users and personas across the Velora stack (`:5173` web frontend and `:8000` Django API).

All underlying backend contracts and operations governing report versioning, derived row locking, lineage preservation, multi-source provenance, and cancellation recovery have been executed and verified against the live PostgreSQL database and API endpoints. The verification passed **51 out of 51 automated regression and end-user scenario tests** (`field_reports/tests/test_a1_b02_version_integrity.py`, `field_reports/tests/test_daily_report_gaps_correction.py`, `field_reports/tests/test_daily_report_derived_readonly.py`, and `field_reports/tests/test_daily_report_aggregation_rebuild.py`), with zero test failures or xfails. Frontend typecheck via `react-router typegen && tsc` completed with code 0 (zero errors).

All 6 historical defects (`DEF-B02-01` through `DEF-B02-06`) remain completely resolved and enforced by structural invariants.

---

## 2. Multi-Persona End-User Evaluation

### Persona 1: Site Engineer / Report Preparer
- **Workflow Evaluated**: Opening corrections on approved daily reports, editing draft corrections, and rebuilding derived aggregations.
- **Findings**:
  - Initiating `/api/v1/projects/{project_id}/daily-reports/{id}/correction/` successfully clones all child operational rows, preserves `is_auto_summary=True`, clones weather entries, and preserves multi-source provenance mappings.
  - Derived operational rows (`DailyReportActivity`, `DailyReportLabor`, `DailyReportMachinery`, `DailyReportMaterial`) remain strictly read-only against direct create/update/delete mutations.
  - Rebuilding derived operational data correctly refreshes aggregated activity rows while preserving preparer comments and manual overrides.

### Persona 2: Project Approver / Consultant
- **Workflow Evaluated**: Reviewing revisions, enforcing separation of duties, rejecting self-approval, and approving corrections.
- **Findings**:
  - Preparers cannot self-approve their own submitted corrections (`test_submitter_cannot_approve_own_report`).
  - Approved versions lock down completely; subsequent rebuild requests on approved reports are blocked with HTTP 400 and localized error messages (`FA: گزارش روزانه نهایی یا تأیید شده قابل بازسازی نیست` / `EN: Final or approved daily report cannot be rebuilt`).
  - Cancelling an in-flight correction via `/correction/cancel/` cleanly reverts the draft revision and restores the preceding approved report as `is_current=True`.

### Persona 3: Project Auditor / Financial Controller
- **Workflow Evaluated**: Auditing lineage, source preservation, and operational totals across report revisions.
- **Findings**:
  - Multi-source provenance entries (`DailyReportDerivedSource`) preserve complete source references (`sub_report_activity_id`, `sub_report_id`, `source_type`) without data loss across version increments.
  - Activity master logs and operational summaries strictly filter by `is_current=True`, preventing double-counting of quantities, headcounts, or machine hours across historical revisions.

### Persona 4: Read-Only Viewer & Unauthorized User
- **Workflow Evaluated**: Inspecting daily reports by calendar date, access control boundaries.
- **Findings**:
  - Unauthenticated requests receive HTTP 401 Unauthorized.
  - Cross-project requests or requests without adequate role assignments receive HTTP 403 Forbidden.
  - Read-only viewers can access approved versions and inspection dates without mutation permissions.

---

## 3. Historical Defect Audit Status

| Defect ID | Description | Status | Verification Evidence |
|-----------|-------------|--------|-----------------------|
| `DEF-B02-01` | Correction opening dropped `is_auto_summary` and B01 contract metadata | Resolved | Cloned summaries retain `is_auto_summary=True`, `reporting_configuration`, and `b01_metadata` |
| `DEF-B02-02` | Derived operational rows accepted manual mutation via general endpoints | Resolved | Protected by validation layer raising `report_rows_read_only` |
| `DEF-B02-03` | Multi-source provenance links broken after revision creation | Resolved | `clone_operational_rows` remaps source links to cloned child UUIDs |
| `DEF-B02-04` | Approved report cancellation or rollback left dangling current flags | Resolved | Cancellation endpoint restores atomic single `is_current=True` flag |
| `DEF-B02-05` | Master activity query double-counted historical revisions | Resolved | Aggregation and reporting querysets filter strictly by `is_current=True` |
| `DEF-B02-06` | Rebuild API permitted execution against approved/frozen versions | Resolved | `rebuild_daily_report_aggregation` rejects non-draft reports |

---

## 4. Verification Evidence & Artifact References

- Backend test execution: `51 passed, 2 warnings in 40.42s` (`apps/api/core/pytest.ini`)
  - `field_reports/tests/test_a1_b02_version_integrity.py` (26 tests)
  - `field_reports/tests/test_daily_report_gaps_correction.py` (21 tests)
  - `field_reports/tests/test_daily_report_derived_readonly.py` (3 tests)
  - `field_reports/tests/test_daily_report_aggregation_rebuild.py` (1 test)
- Frontend Typecheck: `pnpm --filter web typecheck` completed with exit code 0.
- Deliverable: `A.1.03 (Daily report revision integrity and derived locks)` confirmed ready for Stage 1 fan-out completion and downstream phases.
