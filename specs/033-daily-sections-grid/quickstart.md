# Quickstart: Validating Specialty Unit Daily Sections and Structured Aggregation

**Feature**: 033-daily-sections-grid | **Date**: 2026-10-23
Purpose: running validation pass for the section contracts, aggregation guarantees, and the unit→summary path. It references [data-model.md](./data-model.md) and [contracts/](./contracts/) rather than duplicating them, and contains no implementation bodies.

## Prerequisites

1. Start PostgreSQL and Redis before the API (AGENTS.md cloud-VM table):
   ```bash
   sudo pg_ctlcluster 16 main start
   sudo redis-server /etc/redis/redis.conf --daemonize yes
   ```
2. API venv exists (`apps/api/.venv`, Django pinned 4.2.11); root `.env` present (update-script defaults).
3. jq/pytest tooling installed; seed data available (`pnpm db:migrate && pnpm db:seed` on a fresh DB).
4. Playwright browsers installed once: `pnpm exec playwright install --with-deps chromium`.
5. Known environment boundaries: RabbitMQ/MinIO are Docker-only locally — file-upload (attachment) E2E steps are full-environment features; local runs must state this explicitly in reports.

## 1. RED-then-GREEN section contracts (backend)

```bash
cd apps/api/core && set -a && source /workspace/.env && set +a && ../.venv/bin/python -m pytest \
  sub_reports/tests/test_section_contracts.py \
  sub_reports/tests/test_labor_catalog.py \
  sub_reports/tests/test_machinery_contract.py \
  sub_reports/tests/test_materials_receipt_contract.py \
  sub_reports/tests/test_concrete_qc_link.py \
  sub_reports/tests/test_structured_narrative.py
```

Expected outcomes, mapped to spec scenarios:
- Positive-only completed quantity; non-negative counts; concrete >0; sampling completeness (US1/US2/US5/US9 subset).
- Cross-project WBS/contractor/plant/document/image references → permission/validation errors, no partial rows stored (scenario 2 override).
- Stoppage reason required when stoppage > 0; `Σ hours ≤ 24`; vocabulary check (US3).
- Receipts resolved only with warehouse-document references; generic rows never receipts (US4).
- Barriers need owner+due; HSE incidents need severity+immediate action; `other` notes never auto-promoted (US6).
- Attachments: type/size/mis-declared content/cross-project target (US7).
- Job title resolution against the effective catalog snapshot, legacy-alias first; unknown titles rejected (US2).

## 2. Aggregation redesign evidence

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_unit_report_aggregation_eligibility.py \
  field_reports/tests/test_unit_report_provenance.py \
  field_reports/tests/test_unit_report_completeness.py \
  field_reports/tests/test_unit_report_rebuild_idempotency.py \
  field_reports/tests/test_machinery_derivation.py \
  field_reports/tests/test_receipts_only_summary.py \
  field_reports/tests/test_structured_transfer.py
```

Expected outcomes:
- Activity appears with all columns + source link; provenance per row and complete multi-source sets for totals (scenarios 1, 3).
- Machinery five-status table derived from the Machinery unit report; duplicate identity counted exactly once (scenario 4).
- Main table receipts only; consumption traceable via the details endpoint (scenario 5).
- Structured narrative rows stay structured/ordered after ≥2 rebuilds; general notes never become issues (scenario 6).
- Three consecutive rebuilds → identical payload; mid-failure leaves prior summary intact; rejecting/replacing one unit removes/replaces only that unit's rows (scenarios 7–8); overrides and management opinion preserved.
- Man-hours computed per effective rule; category + overall totals present; DRILL-DOWN lists every source.

## 3. Reconciliation (document-anchored)

```bash
../.venv/bin/python -m pytest field_reports/tests/ -k reconciliation
```

Expected: comparison against the specific referenced document; equal → `match`; differing → `mismatch` with both quantities; missing/unresolvable reference → `insufficient_data` (never fabricated match); global balance appears only as labeled cross-check.

## 4. Migration/safety checks

```bash
../.venv/bin/python manage.py makemigrations --check --dry-run  # no surprise drift
../.venv/bin/python manage.py migrate apps/api --plan           # additive migrations visible after tasks
../.venv/bin/python manage.py migrate apps/api --fake …  # instead of fakes run forward+reverse in the task phase
../.venv/bin/python manage.py verify_blueprint_schema
```

(The exact per-app forward/reverse/forward commands belong to the tasks phase; documented here at plan granularity.)

## 5. Frontend typecheck + browser path

```bash
pnpm typecheck   # expect: pre-existing unrelated DailyReportForm baseline only; no new errors
pnpm dev:api &   # 8000 (start after Postgres/Redis)
pnpm dev:web &   # 5173
pnpm e2e -- --grep "daily-sections"
```

Browser E2E (`apps/web/e2e/tests/daily-sections-aggregation.spec.ts`) walkthrough per unit page:
1. Buildings: create/edit/submit an executed-activity row with full contract → approve → open summary → verify row + source link; invalid quantity/shift/cross-project attempt shows localized errors (scenarios 1–2).
2. Machinery + Warehouse: enter machinery statuses (with a 0-reason and >24h rejection attempt) and one receipt + one consumption → summary shows machinery table, receipt-only main table, drill-down consumption (scenarios 3–5).
3. Structured narrative: enter a general activity, barrier (owner + due date), visit, HSE incident → summary keeps structure/order; incident notification confirmed; untyped note never an issue (scenario 6).
4. Correction loop: reject a unit report → summary loses only that unit's rows; resubmit → rows reappear exactly once; rebuild twice more → unchanged (scenarios 7–8).
5. Bilingual pass: toggle fa/en on editors and summary; verify labels, errors, date-picker persistence both locales.

## 6. What each category proves (and does not)

| Evidence | Proves | Does not prove |
|---|---|---|
| pytest suites above | model/serializer/service/API contracts on PostgreSQL | browser rendering; production scale |
| Concurrency tests | atomic rebuild under contention | throughput targets |
| Migration checks | additive schema apply/reverse safety | real dataset volume |
| Typecheck | compile-level soundness | runtime behavior |
| Playwright | seeded local unit→summary UX in both locales | production authorization config; MinIO-backed upload flows |
| Reconciliation tests | document-anchored semantics | full warehouse document variety across integrations |

File-upload E2E requires the full-environment storage service; local reports must name this boundary explicitly (Constitution VI), alongside any other runtime-only service.
