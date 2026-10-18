# Research: Automated Project Daily Report Summary

**Feature**: `028-auto-daily-report-summary`  
**Date**: 2026-10-18

## Decision 1 — Materialized DailyReport as the summary shell

**Decision**: Keep `field_reports.DailyReport` (unique current row per `project` + `report_date` + `shift=full`) as the **persisted project-day summary**. An aggregation service **ensures** the shell exists and **rebuilds derived child rows** from specialty sources. Do not introduce a separate `ProjectDailySummary` table.

**Rationale**: Existing approval, PDF, navigation, progress, and child-row APIs already hang off `DailyReport`. Spec requires one logical report per day and automatic updates; materialization preserves those integrations (constitution V).

**Alternatives considered**:
- Pure compute-on-read DTO with no DailyReport row — rejected; breaks approvals, PDF, unique-per-date constraints, and progress hooks.
- New summary model parallel to DailyReport — rejected; dual stores and migration cost.

## Decision 2 — Specialty source of truth

**Decision**: **Primary authoring surface** remains `sub_reports.DisciplineSubReport` (+ `DisciplineSubReportActivity` and additive specialty contribution structures for labor/materials/concrete as required to feed Excel sections). Aggregation includes sub-reports in statuses **`submitted` and `approved`** (exclude `draft` and `rejected` from the rebuild input set). On reject/delete/soft-delete, rebuild removes their contribution.

**Rationale**: Spec FR-001/FR-006 and existing `linked_daily_report` FK already point at this relationship. Draft exclusion matches MVP assumption (“available for project visibility”).

**Alternatives considered**:
- Continue manual entry on DailyReport as primary — rejected; contradicts FR-001/FR-003.
- Aggregate only `approved` sub-reports — too late for operational day-of visibility; submitted is the minimum include set.
- Include drafts — noisier summaries; optional later.

## Decision 3 — Gap: specialty models vs Excel sections

**Decision**: Today `DisciplineSubReport` mainly carries **activities + weather**. To satisfy FR-004, the feature **extends specialty contribution** so units can supply (as applicable to their discipline): labor present/leave by job title, material receipts, concrete pours, general activities, issues/visits narratives. Implementation may add child tables under `sub_reports` **or** map from existing project-date specialty entry surfaces if already authoritative—prefer extending `sub_reports` for a single rebuild input graph. Until a specialty section exists, the summary section renders **empty** and incompleteness messaging may note the gap—**not** reopened for free-form project-level create.

**Rationale**: Spec requires Excel-like sections and specialty as source of truth; inventing project-level blank forms would reintroduce the removed create path.

**Alternatives considered**:
- Only aggregate activities in MVP and leave other Excel sections forever empty — fails SC-003 (≥90% sections).
- Keep manual DailyReport child editors for non-activity sections — violates FR-006/read-only derived tables assumption.

## Decision 4 — Rebuild trigger and ensure-by-date

**Decision**:
1. **On specialty write path** (create/update/submit/approve/reject/delete of a contributing sub-report or its contribution rows): call `rebuild_daily_report_summary(project_id, report_date)`.
2. **On project daily open by date**: `ensure_daily_report_summary(project_id, report_date)` get-or-creates the shell (shift=`full`) and runs rebuild if stale or never built.
3. No user-facing “Rebuild” required (FR-002).

**Rationale**: Spec wants automatic updates; ensure-on-open covers historical dates and missed hooks.

**Alternatives considered**:
- Nightly batch only — too slow / stale for same-day operations.
- Manual rebuild button — contradicts FR-002.

## Decision 5 — Remove project-level create UX (and constrain API)

**Decision**: Remove «گزارش جدید» / Plus create from `daily-reports-list` and retire `/daily-reports/new` as a blank-form entry. Replace with **open/ensure by date** (picker or row click → view/summary). API: prefer `GET/POST .../daily-reports/by-date/?date=` (or equivalent ensure action) over unrestricted blank `POST /daily-reports/`. Blank `POST` create for project daily reports is **disabled or restricted** to internal ensure (server-owned defaults only)—clients must not create empty authored reports.

**Rationale**: FR-003/FR-011 explicitly forbid invite-to-create empty project daily reports.

**Alternatives considered**:
- Hide button only, keep POST — rejected; API clients could still bypass.
- Soft-deprecate create for one release — acceptable only if UI already blocked and POST returns clear 403/410; prefer hard disable for project blank create.

## Decision 6 — Derived rows read-only; summary metadata editable

**Decision**: After a report is managed as an auto-summary, **PATCH/POST/DELETE on derived child collections** (activities, labor, materials, concrete, etc. that aggregation owns) returns a clear validation error. Allowed project-level mutations: weather/site **override** fields (optional), `general_notes` / issues narratives if designated summary-owned, **management opinion**, and existing **submit/review/approve/reject** workflow on the DailyReport shell. Rebuild **must not wipe** summary-owned metadata or approval timestamps.

**Rationale**: FR-009 + assumptions; constitution IV safe mutations.

**Alternatives considered**:
- Fully editable summary after aggregate — reintroduces dual authorship and drift.
- No approvals on summary — fails Excel confirmation section and existing product workflow.

## Decision 7 — Weather and site status reconciliation

**Decision**:
1. If project summary has an **explicit override** for weather or site status, keep it across rebuilds.
2. Else derive weather as the **most severe** among contributing sub-reports (severity order: stormy > snowy > rainy > foggy > cloudy > partly_cloudy > sunny; empty ignored).
3. Site status: **`inactive` if any** contributing report marks inactive / non-working day signal; else `active`.
4. Shift hours: use project defaults or first non-empty specialty value; document in service constants.

**Rationale**: Spec assumptions; deterministic and explainable.

**Alternatives considered**:
- Last-writer-wins — nondeterministic across disciplines.
- Require manual weather always — friction; override covers exceptions.

## Decision 8 — Labor and line-item aggregation rules

**Decision**:
- **Labor**: sum `present` / `leave` (or shift counts / absence) **by** `(labor_category, job_title)` across contributing specialty labor rows.
- **Activities / materials / concrete / general**: **union** of contribution rows into DailyReport child tables, copying description, shift, contractor, headcount, zone/block/floor, quantity, unit, notes; set provenance (`source_sub_report`, `source_discipline`).
- Narratives (issues, visits): concatenate with discipline attribution unless a summary-owned field supersedes.

**Rationale**: FR-007/FR-008.

## Decision 9 — Incompleteness banner

**Decision**: Summary payload includes `contributing_disciplines`, `missing_disciplines` (configured expected set minus submitted/approved for that date), and `is_partial`. UI shows a banner when `is_partial`. Expected discipline set = project-configured list or all `Discipline` enum values enabled for the project (default: civil, electrical, mechanical if project has no config).

**Rationale**: FR-012.

## Decision 10 — Excel-like UI (not pixel-perfect xlsx export)

**Decision**: Redesign project daily **view** into sectional layout matching the reference workbook sections (header, shifts, site status, weather, indirect/direct labor, materials, concrete, executed activities, general activities, issues, visits, approvals, management opinion). MVP **does not** require binary `.xlsx` export parity; PDF may remain existing path or follow later.

**Rationale**: Spec assumptions; SC-003 sectional parity.

## Decision 11 — Offline / sync create queue

**Decision**: Project-level offline **create** of blank daily reports is out of line with FR-003. Offline queue may still sync **child edits on specialty** or summary metadata if already supported; do **not** enqueue new blank project daily creates from the removed button. Document any residual offline create paths as bugs to remove or redirect to specialty entry.

**Rationale**: Avoid reintroducing create via syncService.

## Decision 12 — Verification approach

**Decision**: pytest for rebuild sums/unions, status include/exclude, no blank create, permission isolation, metadata survival across rebuild; frontend typecheck; browser: list without create, ensure-by-date, specialty submit updates summary, incomplete banner, fa/en section labels.

**Rationale**: Constitution VI.
