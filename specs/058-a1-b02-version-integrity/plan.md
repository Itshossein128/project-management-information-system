# Implementation Plan: Phase A.1 Daily Report Version Integrity, Derived-Row Lock & Lineage Preservation (B02)

**Branch**: `058-a1-b02-version-integrity` | **Date**: 2026-11-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/058-a1-b02-version-integrity/spec.md`

## Summary

Package B02 (`A.1.03`) closes all six verified Stage 1.2 QA defects (`DEF-B02-01`–`DEF-B02-06`) and proves preserved core behaviors (`H06`, `D02`, `D03`, `W01`, `W06`) across Velora's daily-report revision lifecycle without rewriting working subsystems or adding database migrations:
1. Preserve `is_auto_summary`, `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, `aggregated_at`, B01 contract metadata, and `worked_shifts` in `correction_service.open_correction()` while keeping approval/workflow fields version-bound (`DEF-B02-01`, `DEF-B02-04`).
2. Clone and remap the complete multi-source `DailyReportDerivedSource` set to the new child row UUIDs in `_clone_children()` (`DEF-B02-03`).
3. Enforce ownership-based derived-row read-only locks and current-version guards across child single-row, batch upsert, legacy nested `partial_update`, and offline `sync_batch` (`X01` coordination) paths (`DEF-B02-02`).
4. Enforce explicit bilingual rejection semantics in `rebuild_daily_report_summary()` and a dedicated `POST .../rebuild/` endpoint for approved, historical/non-current, archived, and deleted targets (`FR-011`, `SC-006`, `DEF-B02-06`), while preserving editable-draft rebuild (`FR-009`) and non-mutating snapshot drift detection on unit submit (`FR-012`).
5. Restrict `activity_log_queryset()` to `report__status=APPROVED` AND `report__is_current=True` (`DEF-B02-05`, `E15`) so operational totals never double-count superseded versions and downstream Package `B04` inherits the exact policy.

## Technical Context

**Language/Version**: Python 3.12 (Django `4.2.11` pinned runtime boundary + Django REST Framework); TypeScript / React Router 7 + Vite (verification of existing UI consumers).  
**Primary Dependencies**: Django 4.2.11, DRF, `drf-spectacular`, existing `field_reports`, `sub_reports`, `project_templates`, and `permissions` apps.  
**Storage**: PostgreSQL 16 (port 5433) + Redis 7 (port 6379) for cache & rate-limiting; **0 new DB migrations** (reuses verified 40/40 blueprint + 25 extension tables).  
**Testing**: `pytest` + `pytest-django` via `apps/api/.venv/bin/python -m pytest`; live API/UI verification against native Postgres/Redis (`:8000` / `:5173`).  
**Target Platform**: Linux server (Velora pnpm monorepo).  
**Project Type**: Web application (`apps/api` backend + `apps/web` frontend).  
**Performance Goals**: Atomic single-transaction correction clone/remap (`select_for_update`), zero N+1 explosion on provenance bulk cloning (`bulk_create`), immediate Redis activity-log cache invalidation on approval/cancellation.  
**Constraints**: Preserve Django 4.2.11 pin; preserve B01 ratified decisions (`C01`–`C10`, `GOV-01`); retain `B01`/`A.8` ownership of `X01` offline sync; distinguish B02 technical readiness from employer final acceptance in `B06`.  
**Scale/Scope**: Surgical backend service/view hardening across 6 existing files in `apps/api/core/field_reports/` + comprehensive automated test suite (`test_a1_b02_version_integrity.py`) + API docs (`ENDPOINTS.md`) + bilingual verification.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design Status | Post-Design Status | Evidence / Alignment |
| :--- | :--- | :--- | :--- |
| **I. Server-Enforced Authorization & Tenant/Project Isolation** | PASS | PASS | All correction, cancel, rebuild, child-row, and metadata endpoints enforce active project membership + `edit_reports`/`approve_reports`/`view_reports` server-side; read-only admin observers cannot mutate; cross-project access and self-approval SoD are enforced and tested. |
| **II. Data Integrity & End-to-End Domain Consistency** | PASS | PASS | Complete `DailyReportDerivedSource` UUID remapping, `worked_shifts` preservation, current-approved `activity_log_queryset` (shared with `FILE1` and B04), and zero schema regressions (0 migrations needed). |
| **III. Bilingual & Locale-Correct Experience** | PASS | PASS | All new/updated lifecycle, lock, and rebuild rejection errors use `lifecycle_error_detail()` with both `fa` and `en` translations and language-independent error codes (`report_not_current`, `historical_rebuild_rejected`, `rebuild_target_deleted`, `report_not_editable`, `report_locked`, `derived_collection_read_only`). |
| **IV. Explicit, Safe Business Mutations** | PASS | PASS | Correction open/cancel use `@transaction.atomic` + `select_for_update()` row locking; cancellation is strictly guarded and restores `v_n` losslessly; historical/approved/deleted rebuilds are explicitly rejected with zero mutation. |
| **V. Minimal Coherent Changes** | PASS | PASS | Extends existing `correction_service.py`, `daily_report_aggregation.py`, `daily_report_views.py`, `activity_log.py`, `lifecycle_errors.py`, and `services/__init__.py` with zero parallel subsystems and zero migrations. |
| **VI. Evidence-Based Verification** | PASS | PASS | Plan requires full B02 pytest suite (0 `XFAIL`), existing regression suites, blueprint schema verification, and live API/UI bilingual verification; explicitly separates B02 technical readiness from `B06` employer acceptance. |
| **VII. Accessible, Practical Construction-Management UX** | PASS | PASS | Preserving `is_auto_summary=True` on revisions automatically keeps `daily-report-view.tsx` and `DailyReportForm.tsx` in derived read-only mode while allowing authorized management metadata edits with clear localized feedback. |

**Gate Result**: **PASS** (0 violations; Complexity Tracking not required).

## Project Structure

### Documentation (this feature)

```text
specs/058-a1-b02-version-integrity/
├── plan.md                              # This file (/speckit-plan output)
├── research.md                          # Phase 0 design decisions & rationale
├── data-model.md                        # Phase 1 entities, invariants & rebuild matrix
├── quickstart.md                        # Phase 1 runnable validation guide
├── contracts/
│   └── version-integrity-api.md         # Phase 1 API, service & error-code contracts
├── checklists/
│   └── requirements.md                  # Specify quality checklist (16/16 PASS)
└── tasks.md                             # Phase 2 output (/speckit-tasks - NOT created yet)
```

### Source Code (repository root)

```text
apps/api/core/field_reports/
├── services/
│   ├── correction_service.py            # Preserve summary identity/metadata/worked_shifts; remap DailyReportDerivedSource; invalidate activity-log cache on cancel
│   ├── daily_report_aggregation.py      # Explicit FR-011/SC-006 rebuild rejection for approved/historical/non-current/archived/deleted targets; preserve FR-009 editable-draft rebuild & FR-012 non-mutating unit-trigger
│   ├── activity_log.py                  # Add report__is_current=True to official approved queryset (E15, B04 handoff)
│   ├── lifecycle_errors.py              # Add bilingual FA/EN error messages for new B02 lock/rebuild codes
│   └── __init__.py                      # Defense-in-depth derived-row check in sync_batch (X01 coordination); SoD check in approve_report if needed
├── daily_report_views.py                # Ownership-based _assert_editable across child/batch/legacy partial_update; non-current guards; explicit POST .../rebuild/ action
├── ENDPOINTS.md                         # Document POST .../rebuild/ and updated lock/activity-log semantics
└── tests/
    └── test_a1_b02_version_integrity.py # Dedicated B02 test suite covering DEF-B02-01..06, US1..US5, concurrency, SoD, RBAC, bilingual errors (0 XFAIL)

apps/web/src/
├── app/routes/daily-report-view.tsx     # Existing consumer of is_auto_summary (verify read-only revision UX; edit only if needed)
└── app/routes/project-activity-log.tsx  # Existing consumer of /activity-log/ (verify current-approved totals; edit only if needed)
```

**Structure Decision**: Existing Velora pnpm monorepo (`apps/api` Django/DRF + `apps/web` React Router 7). All B02 logic changes reside in `apps/api/core/field_reports/` with zero new apps, zero new tables/migrations, and non-invasive verification of existing `apps/web` consumers.

## Complexity Tracking

> No Constitution Check violations; no complexity exemptions required.
