# Quickstart: Dashboards, Roles & Reports

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB after FR-RPT migrations (roles seed + `ReportExportVersion`)
- Seeded: ≥2 projects; finance user member of A+B only; second user for SoD approve; approved vs draft domain data for progress/cost

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  permissions/tests/test_sod.py \
  permissions/tests/test_fr_rpt_roles.py \
  projects/tests/test_kpi_drillthrough.py \
  projects/tests/test_role_dashboard_packs.py \
  projects/tests/test_report_export_metadata.py \
  -q
```

Also run focused SoD regression on touched approve paths (IPC / change-request / workflow) if those test modules exist.

## Manual API smoke

1. `GET .../kpis/` → `figures[]` with `figure_key` + `drill.href`; inactive capability → `status=inactive`, `value=null`.
2. `GET .../kpis/drill/?figure_key=...` → rows with `approved` + `last_updated_at`.
3. Finance user `GET /v1/portfolio/dashboard/` → only projects A+B (not C).
4. Creator attempts final IPC (or change-request / workflow) approve → `400 sod_self_approve`; other authorized user succeeds.
5. `POST .../reports/weekly_progress/export/` with two filters → export metadata includes both + `extracted_at`; download envelope includes same (SC-004).
6. Standard report with `approved_only=true` excludes draft figures from totals.

## UI

- Project → Dashboard: role pack figures; click figure opens drill drawer (fa/en).
- Portfolio / Executive: multi-project strip for eligible roles.
- Project → Standard reports: catalog, filters, export download with visible extraction metadata.

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 | Drill from KPI figure to source approval + timestamp in &lt; 2 min |
| SC-002 | 100% tests: non-member project absent from portfolio/pack scope |
| SC-003 | 0% self final-approve success on material transactions |
| SC-004 | 100% exports carry extraction date + filters |
| SC-005 | UAT checklist for PM, site, finance, controls runnable |
| SC-006 | Disabled module figures inactive/null, not fake zero |
