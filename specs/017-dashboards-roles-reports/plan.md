# Implementation Plan: Dashboards, Roles & Reports

**Branch**: `017-dashboards-roles-reports` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-dashboards-roles-reports/spec.md` (FR-RPT gap closure)

## Summary

Close FR-RPT gaps without inventing a second system of record: add **systematic KPI drill-through** (source records + approval status + last-updated) on unified project KPIs and role dashboard packs; enforce **role×project** visibility for packs and portfolio strips; implement **hard segregation of duties** on material final-approve paths; align the **minimum role set**; deliver a **standard report catalog** with shared filters, **approved-data defaults**, confidential-field masking, and **export versions** that always carry extraction date + filter metadata; treat disabled project capabilities as **inactive/hidden**, never fabricated zeros.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `projects` (KPI + packs), `permissions` (roles + SoD), `schedule` (period reports / provenance pattern), `cost_control`, `contracts`, `cash_flow`, `risk`, `hr`, `field_reports`, `workflow` (read aggregates); `view_dashboard` / existing domain view permissions  
**Storage**: PostgreSQL (UUID PKs); new `ReportExportVersion` (+ optional pack preference) under `projects` or thin `reporting` tables; no duplication of domain fact tables  
**Testing**: pytest for drill provenance, SoD rejection, role pack project scoping, export metadata, inactive capability; UI smoke on role dashboard + report export  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Dashboard pack compose from cached domain KPIs where present (reuse KPI TTL); drill endpoints page/filter source lists; export generation synchronous for v1 (eager Celery OK)  
**Constraints**: Server-side project membership; bilingual labels; dashboards read-only for facts; SoD hard-block final approve by creator; reports default to approved data; confidential wage/contacts already gated — apply same on report serializers  
**Scale/Scope**: Extend `projects.kpi_service` + new pack/drill/export services; patch material approve services for SoD; extend role constants; role-dashboard + reports UI routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — pack/drill/report routes check membership + `view_dashboard` (and domain perms for confidential fields); portfolio strips only include member projects |
| II. Data integrity end-to-end | Pass — aggregates read domain SoR; export versions store metadata; no parallel fact tables |
| III. Bilingual UX | Pass — pack names, inactive labels, SoD errors, export UI in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — SoD hard-reject with clear code; exports append-only versions; dashboards do not mutate domain facts |
| V. Minimal coherent changes | Pass — extend `projects` + `permissions` + existing approve/report surfaces; avoid a second analytics product |
| VI. Evidence-based verification | Pass — pytest suites in quickstart; UI smoke after API green |
| VII. Accessible practical UX | Pass — drill affordance on figures; inactive vs zero distinction; viewer read-only |

**Post-Phase 1 re-check**: Pass — design reuses progress-report provenance shape for KPI drill; SoD central helper applied at approve boundaries; report catalog wraps existing domain reports plus export metadata entity; phase-1 packs are a documented subset.

## Project Structure

### Documentation (this feature)

```text
specs/017-dashboards-roles-reports/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── kpi-drillthrough.md
│   ├── role-dashboard-packs.md
│   ├── sod-and-roles.md
│   └── standard-reports-export.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/permissions/
  constants.py                      # FR role map + new system roles
  sod.py                            # NEW: assert_not_self_approve(creator, actor)
  tests/test_sod.py
  tests/test_fr_rpt_roles.py

apps/api/core/projects/
  kpi_service.py                    # attach figure keys + provenance hooks
  services/dashboard_pack_service.py  # NEW: role packs, capability inactive
  services/kpi_drill_service.py       # NEW: drill lists by figure_key
  services/report_export_service.py   # NEW: export version + metadata
  models.py                         # ReportExportVersion (+ optional UserDashboardPref)
  views / urls                      # packs, drill, report catalog/export
  migrations/00xx_fr_rpt_*.py
  tests/test_kpi_drillthrough.py
  tests/test_role_dashboard_packs.py
  tests/test_report_export_metadata.py
  ENDPOINTS.md

apps/api/core/{cost_control,contracts,projects,workflow,hr}/
  *approve* services                # call sod.assert_not_self_approve on final approve

apps/api/core/schedule/
  period_report_*                   # ensure approved-default + export metadata hook if used as catalog item

apps/web/src/
  app/lib/api/dashboards.ts         # NEW
  app/lib/api/standard-reports.ts   # NEW
  app/routes/project-dashboard.tsx  # deepen / role pack
  app/routes/executive-dashboard.tsx # or portfolio strip
  app/routes/project-standard-reports.tsx
  components/dashboard/FigureDrillDrawer.tsx
  locales en.json / fa.json
  routeVars / routes / project-navigation.config.ts
```

**Structure Decision**: Keep FR-RPT in **`projects` + `permissions`** (Principle V). Dashboards and exports are read/aggregate layers over domain SoR. Reuse the progress-report provenance fields (`source_type`, `source_id`, `source_path`, `source_approved`, `last_updated_at`) as the canonical drill contract for KPI figures. Phase-1 packs: **executive strip + PM + finance (or controls)**; HR/site and unit-manager packs follow once aggregates are wired. SoD is a shared helper invoked from existing final-approve services (hard 403/400), not soft-warn-only.

## Complexity Tracking

None — no new analytics product; optional `ReportExportVersion` table is justified for SC-004 audit of exports.

## Implementation Phases

1. **P1 Drill-through + approved-data labeling** — figure_key on KPI payload; drill endpoint; progress/budget sample figures; unapproved excluded or labeled (FR-001–002, 016; SC-001).
2. **P1 Roles + SoD + project scoping** — FR role mapping; pack endpoint scoped to membership; SoD on material approves (FR-003, 013–014; SC-002–003).
3. **P2 Standard reports + export metadata** — catalog, shared filters, export version with extraction date + filters; confidential masking (FR-010–012, 015; SC-004).
4. **P2 Role packs expansion** — executive/PM/finance(+controls) packs; inactive capability handling; remaining packs as follow-on (FR-004–009; SC-006).
5. **Polish** — ENDPOINTS.md, UAT checklist for SC-005, locales, pytest + UI smoke.
