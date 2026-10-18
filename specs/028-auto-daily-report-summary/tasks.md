---
description: "Dependency-ordered TDD work for automated project daily report summary"
---

# Tasks: Automated Project Daily Report Summary — TDD

**Input**: Design documents in `specs/028-auto-daily-report-summary/`.  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [API contract](contracts/daily-report-summary-api.md), [UI contract](contracts/daily-report-summary-ui.md), [quickstart.md](quickstart.md), project constitution.  
**Created**: 2026-10-18  
**Tests**: Mandatory — user explicitly requested **Use TDD**.  
**Status**: Tasks generated only; no implementation started. Actual Git branch may remain `develop`; logical feature key is `028-auto-daily-report-summary`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable within the same wave (different files, no unfinished shared-file deps)
- **[Story]**: `[US1]` / `[US2]` / `[US3]` / `[US4]` on story-phase tasks only
- Every task includes a repository-relative file path

## TDD rules

For each missing behavioral slice: write failing assertions first, run and record **observed RED**, implement the minimum, then **GREEN** before the next dependent slice. Import/collection failures alone are not behavioral RED. Do not weaken production code or fixtures to force RED. Prefer additive schema (DailyReport flags + provenance + specialty contribution children); do not invent a parallel summary table. No commit/push unless separately requested.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline and shared test helpers without product behavior changes.

- [ ] T001 Record branch, dirty tree note, Python/Django versions, Postgres/Redis availability, and focused baseline pytest/typecheck notes in `specs/028-auto-daily-report-summary/verification.md`
- [ ] T002 [P] Add reusable fixtures (project, two disciplines civil+electrical, draft/submitted/approved/rejected sub-reports, activity rows, optional overlapping labor titles) in `apps/api/core/field_reports/tests/daily_report_summary_helpers.py`
- [ ] T003 [P] Document intended test module names and quickstart mapping in `specs/028-auto-daily-report-summary/verification.md` (link to [quickstart.md](quickstart.md))

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema + aggregation service skeleton that all stories depend on: ensure-by-date shell (`shift` must be `full`), rebuild input only `status ∈ {submitted, approved}` and `is_deleted=False`, provenance fields, disable blank create.  
**Independent gate**: `ensure_daily_report_summary` creates one current auto-summary per project+date; rebuild ignores drafts; blank `POST /daily-reports/` rejected.  
**⚠️ CRITICAL**: No user-story UI/API product work until this phase is GREEN.

### Tests (RED first)

- [ ] T004 [P] RED — Assert `DailyReport` gains `is_auto_summary` (default True for ensured rows), `aggregated_at` (nullable), `management_opinion` (TextField blank default), `weather_override` / `site_status_override` (booleans default False), and that ensure uses `shift='full'` per data-model rule “Ensure summary: `shift` must be `full` for auto-summary shells” — in `apps/api/core/field_reports/tests/test_daily_report_summary_models.py`
- [ ] T005 [P] RED — Assert rebuild include set is only sub-reports with `status ∈ {submitted, approved}` and `is_deleted=False` for same `project`+`report_date`; drafts/rejected excluded — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_include.py`
- [ ] T006 [P] RED — Assert blank client `POST /api/v1/projects/{id}/daily-reports/` without ensure-by-date contract is rejected (`400`/`403`) with message that project daily reports are auto-generated — in `apps/api/core/field_reports/tests/test_daily_report_no_blank_create.py`

### Implementation

- [ ] T007 Add `management_opinion`, `weather_override`, `site_status_override`, `is_auto_summary`, `aggregated_at` on `DailyReport` in `apps/api/core/field_reports/models.py` per data-model (TextField blank default; override booleans; `is_auto_summary` boolean; `aggregated_at` nullable DateTime)
- [ ] T008 [P] Add provenance on aggregation-owned children at minimum `DailyReportActivity` and `DailyReportLabor`: `source_sub_report` FK → `DisciplineSubReport` `SET_NULL`, `source_discipline` CharField snapshot, `is_derived` Boolean default False — in `apps/api/core/field_reports/models.py`
- [ ] T009 Generate additive migrations under `apps/api/core/field_reports/migrations/` for T007–T008 fields
- [ ] T010 Implement `ensure_daily_report_summary(project_id, report_date)` and `rebuild_daily_report_summary(project_id, report_date)` stubs that create/get shell with `shift='full'`, `is_auto_summary=True`, set `aggregated_at`, and apply include-set filter from data-model rule 2 — in `apps/api/core/field_reports/services/daily_report_aggregation.py`
- [ ] T011 Wire blank-create rejection (or ensure-only POST) in `apps/api/core/field_reports/daily_report_views.py` per [contracts/daily-report-summary-api.md](contracts/daily-report-summary-api.md) §3
- [ ] T012 GREEN — Run `test_daily_report_summary_models.py`, `test_daily_report_aggregation_include.py`, `test_daily_report_no_blank_create.py`; record exits in `specs/028-auto-daily-report-summary/verification.md`

**Checkpoint**: Foundation ready — user stories may start

---

## Phase 3: User Story 1 — View auto-aggregated daily report for a date (Priority: P1) 🎯 MVP

**Goal**: Submitted specialty reports for date D automatically populate a project daily summary; no «گزارش جدید» required.  
**Independent Test**: Submit civil sub-report with activities for D → open/ensure D → summary activities reflect civil rows with provenance; changing specialty and resubmitting refreshes summary without manual rebuild.

### Tests (RED first)

- [ ] T013 [P] [US1] RED — Contract: `GET` or `POST .../daily-reports/by-date/?date=YYYY-MM-DD` ensures shell, rebuilds, returns detail + `aggregation` block (`is_auto_summary`, `aggregated_at`, `is_partial`, discipline lists) per API contract §1/§6 — in `apps/api/core/field_reports/tests/test_daily_report_by_date.py`
- [ ] T014 [P] [US1] RED — Rebuild unions activity rows from included sub-reports into `DailyReportActivity` with `is_derived=True`, `source_discipline`, `source_sub_report`; preserves description/shift/zone/block/floor/quantity/unit; sets `linked_daily_report` on contributing sub-reports — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_activities.py`
- [ ] T015 [P] [US1] RED — After specialty update+submit for same date, second rebuild replaces prior `is_derived=True` activities (soft-delete/delete then reinsert) without requiring client rebuild action — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_rebuild.py`
- [ ] T016 [P] [US1] RED — `POST/PATCH/DELETE` on derived child collections for `is_auto_summary` reports return `400` with localized “edit via specialty” message — in `apps/api/core/field_reports/tests/test_daily_report_derived_readonly.py`

### Implementation

- [ ] T017 [US1] Complete activity (and weather derive without override) mapping inside `rebuild_daily_report_summary` in `apps/api/core/field_reports/services/daily_report_aggregation.py` (union rows; severity weather order stormy>snowy>rainy>foggy>cloudy>partly_cloudy>sunny; site inactive if any inactive)
- [ ] T018 [US1] Hook rebuild after sub-report submit/approve/reject/delete in `apps/api/core/sub_reports/services.py` (and delete path in views if needed)
- [ ] T019 [US1] Add `by-date` route + view action returning detail + aggregation meta in `apps/api/core/field_reports/urls.py` and `apps/api/core/field_reports/daily_report_views.py`
- [ ] T020 [US1] Extend detail serializers with `aggregation` + child provenance fields in `apps/api/core/field_reports/serializers.py`
- [ ] T021 [US1] Enforce derived child write rejection when `report.is_auto_summary` in child viewsets in `apps/api/core/field_reports/daily_report_views.py`
- [ ] T022 [US1] GREEN — Run US1 pytest modules above; record in `specs/028-auto-daily-report-summary/verification.md`
- [ ] T023 [P] [US1] Add `ensureDailyReportByDate(projectId, date)` client helper in `apps/web/src/app/lib/api/daily-reports.ts`
- [ ] T024 [US1] Remove «گزارش جدید» / Plus create control and `/daily-reports/new` entry from list UX in `apps/web/src/app/routes/daily-reports-list.tsx`; empty state points to specialty/by-date (not create-blank)
- [ ] T025 [US1] Wire list/view open path to ensure-by-date then summary view in `apps/web/src/app/routes/daily-reports-list.tsx` and `apps/web/src/app/routes/daily-report-view.tsx`
- [ ] T026 [P] [US1] Add fa/en strings for no-create empty state, auto-summary hint, derived read-only error in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [ ] T027 [US1] GREEN — `pnpm typecheck`; browser smoke quickstart §1–§3 (no create; specialty submit → summary); record in `specs/028-auto-daily-report-summary/verification.md`

**Checkpoint**: US1 MVP — auto summary from specialty activities + no blank create

---

## Phase 4: User Story 2 — Browse daily reports by date like the Excel workbook (Priority: P1)

**Goal**: Day-organized list/open UX and Excel-sectional summary layout (header, shifts, site, weather, labor, materials, concrete, activities, general, issues, visits, approvals, management).  
**Independent Test**: Open several dates; sections match FR-004 labels; date with zero specialty shows empty/no-data state without create button.

### Tests (RED first)

- [ ] T028 [P] [US2] RED — Empty date ensure returns shell with empty derived children and `aggregation.is_partial` / messaging fields suitable for “no specialty data” — extend `apps/api/core/field_reports/tests/test_daily_report_by_date.py`
- [ ] T029 [P] [US2] RED — Specialty contribution models exist and serialize: labor (`labor_category` indirect/direct, `job_title`, `present_count`, `leave_count`), material, concrete (`volume_m3`), general activity, note (`note_type` issue|visit|other) soft-deletable under sub-report — in `apps/api/core/sub_reports/tests/test_sub_report_contributions.py`
- [ ] T030 [P] [US2] RED — Labor rebuild sums by `(labor_category, normalized job_title)` present/leave across disciplines; materials/concrete/general/notes union with provenance — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_sections.py`

### Implementation

- [ ] T031 [P] [US2] Add `DisciplineSubReportLabor`, `DisciplineSubReportMaterial`, `DisciplineSubReportConcrete`, `DisciplineSubReportGeneralActivity`, `DisciplineSubReportNote` models in `apps/api/core/sub_reports/models.py` per data-model (soft-deletable; scoped to `sub_report`)
- [ ] T032 [US2] Generate migrations under `apps/api/core/sub_reports/migrations/` for contribution children
- [ ] T033 [US2] Serializers + nested create/update for contribution children in `apps/api/core/sub_reports/serializers.py` and expose via `apps/api/core/sub_reports/views.py` / `urls.py` as needed
- [ ] T034 [US2] Extend rebuild to map labor sums + materials/concrete/general/notes into DailyReport children (add provenance on materials/concrete if not done in T008) in `apps/api/core/field_reports/services/daily_report_aggregation.py` and `apps/api/core/field_reports/models.py`
- [ ] T035 [US2] GREEN — Run `test_sub_report_contributions.py`, `test_daily_report_aggregation_sections.py`, by-date empty cases; record in `specs/028-auto-daily-report-summary/verification.md`
- [ ] T036 [US2] Implement Excel-sectional summary layout components (header, shifts, site, weather, indirect/direct labor, materials, concrete, activities, general, issues, visits, approvals slot, management) under `apps/web/src/components/daily_reports/summary/` (e.g. `DailyReportSummaryView.tsx` + section components)
- [ ] T037 [US2] Render summary sections from detail payload in `apps/web/src/app/routes/daily-report-view.tsx`; hide free-form derived editors for auto-summary
- [ ] T038 [US2] Add date “نمایش گزارش روز” control (Jalali) calling ensure-by-date on list page in `apps/web/src/app/routes/daily-reports-list.tsx`
- [ ] T039 [P] [US2] Add fa/en section titles matching Excel labels in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [ ] T040 [US2] GREEN — `pnpm typecheck`; browser check quickstart §5 + sectional labels vs FR-004; record in `specs/028-auto-daily-report-summary/verification.md`

**Checkpoint**: US2 — day browse + Excel-like sections populated from specialty contributions

---

## Phase 5: User Story 3 — Specialty units remain the source of truth (Priority: P2)

**Goal**: Specialty create/submit UX stays primary; partial days show incompleteness; drafts do not appear in summary until submit.  
**Independent Test**: Specialty create still works; only some disciplines submitted → partial banner; draft invisible in summary until submit.

### Tests (RED first)

- [ ] T041 [P] [US3] RED — `aggregation.expected_disciplines` / `contributing_disciplines` / `missing_disciplines` / `is_partial` computed per data-model incompleteness projection (default expected civil, electrical, mechanical when no project config) — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_partial.py`
- [ ] T042 [P] [US3] RED — Draft sub-report activities do not appear in rebuild; submit then appears — in `apps/api/core/field_reports/tests/test_daily_report_aggregation_include.py` (extend)
- [ ] T043 [P] [US3] RED — User with view-reports but without specialty edit can GET by-date summary; cannot POST sub-reports — in `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py`

### Implementation

- [ ] T044 [US3] Implement incompleteness projection in aggregation service + serializer `aggregation` block in `apps/api/core/field_reports/services/daily_report_aggregation.py` and `apps/api/core/field_reports/serializers.py`
- [ ] T045 [US3] GREEN — Run partial/include/permission tests; record in `specs/028-auto-daily-report-summary/verification.md`
- [ ] T046 [US3] Show partial/missing-discipline banner on summary view in `apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx` and wire in `apps/web/src/app/routes/daily-report-view.tsx`
- [ ] T047 [US3] Keep specialty create/submit flows working; optional success note that project summary updates — in `apps/web/src/app/routes/project-sub-reports.tsx` (and contribution UI if added under same route or child components)
- [ ] T048 [P] [US3] Localize incompleteness banner + discipline labels in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [ ] T049 [US3] GREEN — Browser quickstart §2, §4, §8; record in `specs/028-auto-daily-report-summary/verification.md`

**Checkpoint**: US3 — specialty authoring intact + partial visibility

---

## Phase 6: User Story 4 — Approvals and management notes on the summary (Priority: P3)

**Goal**: Authorized users record confirmations / management opinion on summary without editing derived rows; metadata survives rebuild.  
**Independent Test**: Set management opinion + approve flow; trigger specialty rebuild; opinion and approval fields remain; derived tables still read-only.

### Tests (RED first)

- [ ] T050 [P] [US4] RED — PATCH `management_opinion` and weather/site when overrides set; rebuild does not clobber when `weather_override`/`site_status_override` true (data-model rule 7) — in `apps/api/core/field_reports/tests/test_daily_report_summary_metadata.py`
- [ ] T051 [P] [US4] RED — Existing submit/review/approve/reject on auto-summary shell still works and is not reset by rebuild — in `apps/api/core/field_reports/tests/test_daily_report_summary_approvals.py`

### Implementation

- [ ] T052 [US4] Allow PATCH of summary-owned fields (`management_opinion`, override flags + weather/site when override) in `apps/api/core/field_reports/serializers.py` / `daily_report_views.py`; rebuild preserves them in `apps/api/core/field_reports/services/daily_report_aggregation.py`
- [ ] T053 [US4] GREEN — Run metadata + approval tests; record in `specs/028-auto-daily-report-summary/verification.md`
- [ ] T054 [US4] UI: editable management opinion + reuse `ApprovalStatusBar` on summary view; derived tables remain read-only — in `apps/web/src/app/routes/daily-report-view.tsx` and `apps/web/src/components/daily_reports/summary/`
- [ ] T055 [P] [US4] fa/en for management opinion label / save errors in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [ ] T056 [US4] GREEN — Browser quickstart §6–§7; record in `specs/028-auto-daily-report-summary/verification.md`

**Checkpoint**: All four user stories independently demonstrable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Hardening across stories.

- [ ] T057 [P] Redirect or remove blank create route `apps/web/src/app/routes/daily-report-form.tsx` / router registration so `/daily-reports/new` cannot author blank summaries; update `apps/web/src/app/routes.ts` (or equivalent route table)
- [ ] T058 Audit offline sync path so blank project daily creates are not enqueued from removed button — in `apps/web/src/app/lib/syncService.ts` and `apps/web/src/app/lib/offlineWrite.ts`
- [ ] T059 [P] Cross-project isolation regression: by-date and rebuild never read other project sub-reports — in `apps/api/core/field_reports/tests/test_daily_report_summary_isolation.py`
- [ ] T060 Run full quickstart.md validation checklist; append results to `specs/028-auto-daily-report-summary/verification.md`
- [ ] T061 [P] Update decision-tree notes if create-report node retired — under `docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/` (and `docs/decision-tree/inventory.json` if required by project convention)
- [ ] T062 Final GREEN sweep: focused pytest modules for this feature + `pnpm typecheck`; record in `specs/028-auto-daily-report-summary/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational; practically after US1 API ensure/rebuild for richer UI (can parallelize contribution models with US1 after T012)
- **US3 (Phase 5)**: After US1 aggregation meta exists; builds on partial banner
- **US4 (Phase 6)**: After shell ensure + rebuild preserve semantics (US1 foundation)
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|------------|-------------------------|
| US1 | Phase 2 | Yes — specialty activities → summary |
| US2 | Phase 2 (+ US1 by-date for UX) | Yes — sections + empty date |
| US3 | US1 aggregation block | Yes — partial + specialty create |
| US4 | US1 rebuild preserve hooks | Yes — opinion/approvals |

### Within Each User Story

1. RED tests first (observed fail)  
2. Models/migrations → services → API → GREEN pytest  
3. Web client/UI → typecheck/browser GREEN  

### Parallel Opportunities

- T002∥T003; T004∥T005∥T006; T013∥T014∥T015∥T016  
- T028∥T029∥T030; T031 parallel to late US1 after foundation  
- T041∥T042∥T043; T050∥T051  
- Locale tasks marked [P] alongside UI when files do not conflict  

### Parallel Example: User Story 1

```bash
# RED wave (parallel):
# T013 by-date contract — apps/api/core/field_reports/tests/test_daily_report_by_date.py
# T014 activity union — apps/api/core/field_reports/tests/test_daily_report_aggregation_activities.py
# T015 rebuild refresh — apps/api/core/field_reports/tests/test_daily_report_aggregation_rebuild.py
# T016 derived readonly — apps/api/core/field_reports/tests/test_daily_report_derived_readonly.py

# Then implement aggregation + API (T017–T021), GREEN (T022), then web (T023–T027)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational (CRITICAL)  
3. Phase 3 US1 — auto aggregate activities + remove create + by-date  
4. **STOP and VALIDATE** via quickstart §1–§3  

### Incremental Delivery

1. US1 → demo auto summary from رشته activities  
2. US2 → Excel sections + contribution types  
3. US3 → incompleteness + permission clarity  
4. US4 → management opinion + approval survival  
5. Polish → offline/routes/decision-tree  

### Suggested MVP scope

**US1 only** (T001–T027): foundation + ensure/rebuild activities + no blank create + basic view open by date.

---

## Notes

- [P] = different files / no unfinished shared-file deps  
- Quote constraints from data-model in implementation tasks; do not invent a second summary store  
- xlsx binary export is out of MVP (research Decision 10)  
- Commit only when user requests  
