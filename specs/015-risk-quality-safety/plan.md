# Implementation Plan: Risk, Quality & Safety

**Branch**: `015-risk-quality-safety` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-risk-quality-safety/spec.md` (FR-RSK gap closure)

## Summary

Close FR-RSK gaps on the existing `risk` app: separate **risk vs issue** lifecycles, complete risk register fields (cause, consequence, response, composite score, FR status set, impact-dimension filters, optional cost/contract/decision links), add first-class **quality/HSE** records (inspection → NCR → corrective action; incident/near miss; work permit; training), and expose a **project + period quality/safety report**—without a parallel risk product, without replacing daily-report incident rows, and without building the general workflow engine (15) or portfolio risk dashboard (16).

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `risk`, `projects`, `wbs`/`projects.Activity`, `cost_control`, `contracts`, `field_reports` (read-only incident feed context); reuse project tenancy + `view_reports` / `edit_reports`  
**Storage**: PostgreSQL (UUID PKs); extend `RiskEvent` + new quality/HSE tables in `risk` app; soft-delete via existing audit base  
**Testing**: pytest + pytest-django per gap (risk/issue separation, composite score rules, inspection validation, period report); UI smoke on risk register + new quality/HSE panels  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Register list/filter O(project events) with indexed project FK; period report aggregates by date range in one query set per entity type; matrix remains open-risk only  
**Constraints**: Project tenancy + server-side membership; bilingual labels for new statuses/types; composite score never fabricated; inspection requires WBS + responsible + date; decision link may be opaque reference until spec 15  
**Scale/Scope**: Extend `risk` models/serializers/views/URLs; risk-register UI + quality/HSE surfaces; period report endpoint; keep barrier/delay/claim paths compatible

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — all routes under `/projects/{uuid}/`; reuse `IsProjectMember` + `HasProjectPermission` (`view_reports` / `edit_reports`); FK targets validated same-project |
| II. Data integrity end-to-end | Pass — migrations for new fields/entities; status vocabulary mapped with data migration from open/in_progress/resolved; composite score derived only when both inputs present |
| III. Bilingual UX | Pass — new status/type/empty-state strings in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — soft-delete retained; close-with-open-action requires acknowledge flag; no silent rewrite of barrier history |
| V. Minimal coherent changes | Pass — extend `risk` app + existing risk-register UI; do not create a second risk/quality Django app |
| VI. Evidence-based verification | Pass — pytest suites named in quickstart; UI smoke after API green |
| VII. Accessible practical UX | Pass — separate risk/issue paths; clear validation on inspection; empty period report sections without fake “perfect safety” zeros |

**Post-Phase 1 re-check**: Pass — design is additive models + register/report endpoints on the existing `risk` bounded context; decision link is an optional opaque reference (no workflow engine); daily-report incidents remain a parallel feed.

## Project Structure

### Documentation (this feature)

```text
specs/015-risk-quality-safety/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── risk-issue-register.md
│   ├── quality-hse-records.md
│   └── quality-safety-period-report.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/risk/
  models.py                         # extend RiskEvent; add Issue kind; quality/HSE models
  serializers.py
  views.py / urls.py                # risk/issue filters; quality CRUD; period report
  services/
    score_service.py                # NEW: composite score rules
    period_report_service.py        # NEW: project+period aggregation
    matrix_service.py               # adapt to FR risk statuses / score scale
  migrations/0005_*.py              # FR fields, statuses, quality/HSE tables
  tests/test_risk_issue_separation.py
  tests/test_risk_score_and_status.py
  tests/test_inspection_validation.py
  tests/test_quality_period_report.py
  ENDPOINTS.md

apps/web/src/
  app/lib/api/risk-events.ts        # extend types; issue filters; score fields
  app/lib/api/quality-hse.ts        # NEW: inspection/NCR/incident/permit/training clients
  app/routes/project-risk-register.tsx   # risk vs issue; FR fields; impact filters
  app/routes/project-quality-hse.tsx     # NEW or tabs: inspection + HSE + period report
  components/risk/...               # forms, close-acknowledge dialog
  components/quality/...            # inspection/NCR/incident panels
  locales en.json / fa.json
  app/routes.ts / routeVars.ts / project-navigation.config.ts
```

**Structure Decision**: Keep FR-RSK in the existing `risk` Django app (Principle V). Risk/issue share the extended `RiskEvent` table with a hard `event_type` discriminator (`risk` vs `issue`); quality/HSE are new sibling models in the same app. UI: deepen risk-register for US1; add a project Quality & HSE route for US2–US4 and the period report. Daily-report `DailyReportIncident` is **not** migrated; period report reads the new HSE register as system of record.

## Complexity Tracking

None — additive fields and sibling models inside the existing `risk` app; no unjustified new bounded context.

## Implementation Phases

1. **P1 Risk & issue register** — FR fields, status vocabulary migration, composite score service, impact filters, optional cost/contract/decision links, issue as distinct `event_type`, close-with-open-action warn+acknowledge, risk-register UI (FR-001–004, 008–010; SC-001–002, SC-005).
2. **P2 Inspection / NCR / corrective action** — models + CRUD + WBS/responsible/date validation; link NCR→inspection; UI capture (FR-005–006; SC-004).
3. **P2 Incident / near miss + period report** — HSE event model; project+period report endpoint and UI (FR-007; SC-003).
4. **P3 Work permit & training** — models + include in period report; light UI.
5. **Polish** — ENDPOINTS.md, matrix compatibility with new statuses/scores, locales, pytest subset + UI smoke.
