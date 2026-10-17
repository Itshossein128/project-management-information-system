---
description: "Dependency-ordered TDD work for contractor stakeholder select"
---

# Tasks: Contractor Stakeholder Select — TDD

**Input**: Design documents in `specs/027-contractor-stakeholder-select/`.  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [API contract](contracts/contractor-select-api.md), [UI contract](contracts/contractor-select-ui.md), [quickstart.md](quickstart.md), project constitution.  
**Created**: 2026-10-17  
**Tests**: Mandatory — user explicitly requested **Use TDD**.  
**Status**: Tasks generated only; no implementation started. Actual Git branch may remain `develop`; logical feature key is `027-contractor-stakeholder-select`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable within the same wave (different files, no unfinished shared-file deps)
- **[Story]**: `[US1]` / `[US2]` / `[US3]` on story-phase tasks only
- Every task includes a repository-relative file path

## TDD rules

For each missing behavioral slice: write failing assertions first, run and record **observed RED**, implement the minimum, then **GREEN** before the next dependent slice. Import/collection failures alone are not behavioral RED. Do not weaken production code or fixtures to force RED. Prefer additive FKs; do not drop `subcontractor_ref` → Contract. No commit/push unless separately requested.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline and shared test helpers without product behavior changes.

- [X] T001 Record branch, dirty tree note, Python/Django versions, Postgres/Redis availability, and focused baseline pytest/typecheck notes in `specs/027-contractor-stakeholder-select/verification.md`
- [X] T002 [P] Add reusable stakeholder/contractor fixtures (active contractor, inactive contractor, non-contractor role, second-project contractor) in `apps/api/core/projects/tests/contractor_select_helpers.py`
- [X] T003 [P] Document intended test module names and quickstart mapping in `specs/027-contractor-stakeholder-select/verification.md` (link to [quickstart.md](quickstart.md))

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Canonical contractor role + list filter + shared validation predicate used by all stories.  
**Independent gate**: `GET .../stakeholders/?role=contractor&status=active` returns only active same-project contractors; writes normalize `پیمانکار` → `contractor`.  
**⚠️ CRITICAL**: No user-story implementation until this phase is GREEN.

### Tests (RED first)

- [X] T004 [P] RED — Assert role write aliases `پیمانکار` / `Contractor` / `contractor` store canonical `contractor`, and list `?role=contractor&status=active` excludes inactive, soft-deleted, and non-contractor roles in `apps/api/core/projects/tests/test_contractor_stakeholder_filter.py`
- [X] T005 [P] RED — Assert project isolation: project B list never returns project A contractors in `apps/api/core/projects/tests/test_contractor_stakeholder_filter.py` (same file OK after T004 RED shapes exist; keep cases independent)

### Implementation

- [X] T006 Add shared contractor constants + normalize helper (canonical code `contractor`; aliases `پیمانکار`, `Contractor`, `contractor` → store `contractor`) and predicate matching data-model: `project_id = current project AND is_deleted = false AND status = active AND role = 'contractor'` in `apps/api/core/projects/contractor_utils.py` (or equivalent module under `apps/api/core/projects/`)
- [X] T007 Wire role normalization on create/update and `role`/`status` query filters on list in `apps/api/core/projects/stakeholder_views.py`
- [X] T008 GREEN — Run `apps/api/core/projects/tests/test_contractor_stakeholder_filter.py` and existing `apps/api/core/projects/tests/test_central_data_stakeholders.py`; record exits in `specs/027-contractor-stakeholder-select/verification.md`

**Checkpoint**: Foundation ready — user stories may start

---

## Phase 3: User Story 1 — Select contractor on department activity (Priority: P1) 🎯 MVP

**Goal**: Non-warehouse department activity create/edit/filter uses Stakeholder contractor selection with durable FK + name snapshot.  
**Independent Test**: Seed active contractor via API → department activity create shows select → save stores `contractor_ref` and displays name → empty contractor list cannot invent free-text names.

### Tests (RED first)

- [X] T009 [P] [US1] RED — Create/update non-warehouse activity requires `contractor_ref` UUID of active same-project contractor; snapshots `contractor` from stakeholder name; rejects missing/other-project/inactive/non-contractor; warehouse path still clears contractor fields — in `apps/api/core/inventory/tests/test_department_activity_contractor_ref.py`
- [X] T010 [P] [US1] RED — List/filter by `contractor_ref` and legacy snapshot substring; inactive contractor still shows historical snapshot name after status change — in `apps/api/core/inventory/tests/test_department_activity_contractor_ref.py`
- [X] T011 [P] [US1] RED — Import resolves پیمانکار cell by exact trimmed name or UUID to one active contractor; unknown name fails row without creating stakeholder — in `apps/api/core/inventory/tests/test_department_activity_contractor_import.py`

### Implementation

- [X] T012 [US1] Add nullable `contractor_ref` FK → `Stakeholder`, `on_delete=SET_NULL`, same-project validation rule per data-model (“Required for non-warehouse create/update when contractor is required. Must satisfy contractor predicate and `stakeholder.project_id == record.project_id`.”) on `DepartmentActivityRecord` in `apps/api/core/inventory/models.py`
- [X] T013 [US1] Generate additive migration for `contractor_ref` under `apps/api/core/inventory/migrations/`
- [X] T014 [US1] Update serializers to accept `contractor_ref`, ignore client-supplied free-text as authority, set `contractor` snapshot, enforce warehouse clear path in `apps/api/core/inventory/serializers.py`
- [X] T015 [US1] Update queryset filter (`contractor_ref` + legacy `contractor` icontains) in `apps/api/core/inventory/department_activity_services.py` and OpenAPI params in `apps/api/core/inventory/department_activity_data_views.py` as needed
- [X] T016 [US1] Update import mapping/resolve in `apps/api/core/inventory/department_activity_io.py` per rule “resolve to exactly one active contractor by UUID or exact trimmed name; else row error (no silent create)”
- [X] T017 [US1] GREEN — Run `apps/api/core/inventory/tests/test_department_activity_contractor_ref.py`, `apps/api/core/inventory/tests/test_department_activity_contractor_import.py`, and affected cases in `apps/api/core/inventory/tests.py`; record in `specs/027-contractor-stakeholder-select/verification.md`
- [X] T018 [P] [US1] Add `fetchProjectContractors(projectId)` wrapping `GET .../stakeholders/?role=contractor&status=active` in `apps/web/src/app/lib/api/central-data.ts`
- [X] T019 [US1] Create non-creatable `ContractorSelect` (no Add path; empty-state points to ذینفعان) in `apps/web/src/components/form/ContractorSelect.tsx`
- [X] T020 [US1] Replace free-text Input in contractor field with `ContractorSelect` binding `contractor_ref` in `apps/web/src/components/department/department-activity-record-modal.tsx`
- [X] T021 [US1] Update activity list column/filter to use contractor select/options (not free-text-only invent) in `apps/web/src/components/department/department-page.tsx`
- [X] T022 [P] [US1] Add fa/en strings for empty state / validation / filter labels in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [X] T023 [US1] GREEN — `pnpm typecheck` for touched web files; manual or Playwright smoke of department modal empty vs populated per [quickstart.md](quickstart.md) §2; record in `specs/027-contractor-stakeholder-select/verification.md`

**Checkpoint**: US1 MVP independently usable with API-seeded contractors

---

## Phase 4: User Story 2 — Register contractors on ذینفعان (Priority: P1)

**Goal**: Stakeholders UI can create/edit contractor role and status so pickers stay in sync.  
**Independent Test**: On ذینفعان add stakeholder as contractor → options include them; set inactive → options exclude them; non-contractor never appears.

### Tests (RED first)

- [X] T024 [P] [US2] RED — API: PATCH role away from contractor or status `inactive` removes row from `?role=contractor&status=active` while historical department snapshot remains — extend `apps/api/core/projects/tests/test_contractor_stakeholder_filter.py`
- [X] T025 [P] [US2] RED — Browser/component expectation doc or e2e sketch: role control with value `contractor` / label پیمانکار on create — author failing selectors in `e2e/tests/contractor-stakeholder-select.spec.ts` (or project e2e path used by repo) before UI lands

### Implementation

- [X] T026 [US2] Add role select (include `contractor` / پیمانکار) and status control on create (and edit if present) in `apps/web/src/app/routes/project-stakeholders.tsx`; POST/PATCH include `role` and `status`
- [X] T027 [US2] Invalidate stakeholder/contractor query keys after create/update in `apps/web/src/app/routes/project-stakeholders.tsx` (and shared query key helper if introduced under `apps/web/src/app/lib/api/central-data.ts`)
- [X] T028 [P] [US2] Add locales for role option labels in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [X] T029 [US2] GREEN — Run filter tests + e2e/UI check that new contractor appears on department `ContractorSelect` without full page reload workaround beyond normal navigation; record in `specs/027-contractor-stakeholder-select/verification.md`

**Checkpoint**: US1 + US2 product loop complete (register → select)

---

## Phase 5: User Story 3 — Same contractor list on all پیمانکار fields (Priority: P2)

**Goal**: Daily report / labor / project party fields and department filter use the same ذینفعان contractor set; history keeps snapshot names.  
**Independent Test**: Same contractor set appears on each in-scope picker; inactive excluded from new picks but visible on old rows.

### Tests (RED first)

- [X] T030 [P] [US3] RED — Daily report activity write accepts `contractor_ref` Stakeholder, sets `subcontractor_name` snapshot, does not require Contract `subcontractor_ref` for picker path — in `apps/api/core/field_reports/tests/test_daily_report_contractor_ref.py`
- [X] T031 [P] [US3] RED — Labor camp entry write accepts `contractor_ref` and snapshots `subcontractor_name` — in `apps/api/core/field_reports/tests/test_labor_camp_contractor_ref.py`
- [X] T032 [P] [US3] RED — Project PATCH optional `contractor_ref` snapshots `Project.contractor` CharField; clears when null — in `apps/api/core/projects/tests/test_project_contractor_ref.py`

### Implementation

- [X] T033 [US3] Add nullable `contractor_ref` → Stakeholder (`SET_NULL`) on `DailyReportActivity` in `apps/api/core/field_reports/models.py` without dropping existing Contract `subcontractor_ref`
- [X] T034 [US3] Add nullable `contractor_ref` → Stakeholder on labor-camp models sharing `subcontractor_name` in `apps/api/core/field_reports/models.py`
- [X] T035 [US3] Add optional `contractor_ref` → Stakeholder on `Project` in `apps/api/core/projects/models.py`
- [X] T036 [US3] Generate additive migrations under `apps/api/core/field_reports/migrations/` and `apps/api/core/projects/migrations/`
- [X] T037 [US3] Update field_reports serializers to validate contractor predicate and snapshot names in `apps/api/core/field_reports/serializers.py`
- [X] T038 [US3] Update project serializer/settings payload for `contractor_ref` in `apps/api/core/projects/serializers.py` (or settings-specific serializer module if that is where `contractor` is exposed)
- [X] T039 [US3] GREEN — Run `test_daily_report_contractor_ref.py`, `test_labor_camp_contractor_ref.py`, `test_project_contractor_ref.py`; record in `specs/027-contractor-stakeholder-select/verification.md`
- [X] T040 [US3] Switch daily-report activity پیمانکار options from contracts list to `fetchProjectContractors` / `contractor_ref` in `apps/web/src/components/daily_reports/DailyReportForm.tsx` and `apps/web/src/components/daily_reports/ActivityTab.tsx`
- [X] T041 [P] [US3] Switch labor-camp پیمانکار entry to contractor select in `apps/web/src/components/daily_reports/LaborCampTab.tsx` and/or `apps/web/src/app/routes/project-labor-camp.tsx` as applicable
- [X] T042 [P] [US3] Replace project settings / create-wizard پیمانکار free text with `ContractorSelect` in `apps/web/src/app/routes/project-settings.tsx` and `apps/web/src/app/routes/project-create-wizard.tsx`
- [X] T043 [US3] GREEN — Typecheck + walkthrough that all in-scope pickers share the same options (SC-001); inactive history display (FR-006); record in `specs/027-contractor-stakeholder-select/verification.md`

**Checkpoint**: All three stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T044 [P] Add/compile backend validation gettext for contractor errors in `apps/api/core/locale/fa/LC_MESSAGES/django.po` (and `.mo` as project practice)
- [X] T045 [P] Confirm out-of-scope surfaces untouched (decision alternatives free text; `subcontractors` app) — note in `specs/027-contractor-stakeholder-select/verification.md`
- [X] T046 Run full [quickstart.md](quickstart.md) scenarios 1–6; map SC-001–SC-005 evidence in `specs/027-contractor-stakeholder-select/verification.md`
- [X] T047 Final regression: focused pytest modules from this feature + `pnpm typecheck`; record exits in `specs/027-contractor-stakeholder-select/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** → no deps
- **Phase 2 Foundational** → after Setup; **blocks** all stories
- **Phase 3 US1 (MVP)** → after Foundational
- **Phase 4 US2** → after Foundational (can parallel with US1 after T008 if staffed; product loop needs both)
- **Phase 5 US3** → after US1 API contractor_ref patterns exist (prefer after T017); UI reuses `ContractorSelect` from T019
- **Phase 6 Polish** → after desired stories complete

### User Story Dependencies

| Story | Depends on | Independently testable by |
|-------|------------|---------------------------|
| US1 | Foundational filters + helpers | API-seeded contractors + department activity |
| US2 | Foundational role normalize | ذینفعان create/inactive → list filter |
| US3 | Foundational + preferably US1 `ContractorSelect` | Daily/labor/project pickers vs same list |

### Within each story

Tests RED → models/migrations → serializers/services → API GREEN → UI → UI GREEN

### Parallel opportunities

- T002 ∥ T003 after T001  
- T004 ∥ T005 (RED wave)  
- T009 ∥ T010 ∥ T011 (US1 RED)  
- T018 ∥ T022 (after API GREEN)  
- T024 ∥ T025 (US2 RED)  
- T030 ∥ T031 ∥ T032 (US3 RED)  
- T041 ∥ T042 after shared select exists  
- T044 ∥ T045  

### Parallel example: User Story 1

```bash
# RED wave (after Foundational GREEN):
# T009, T010, T011 in inventory test modules

# After model/serializer GREEN (T017):
# T018 fetch helper ∥ T022 locales
# then T019 → T020 → T021 sequential UI
```

---

## Implementation Strategy

### MVP (US1 only)

1. Phase 1 + Phase 2  
2. Phase 3 US1 through T023  
3. **STOP** — demo department activity select with API-seeded contractors  

### Incremental

1. Add US2 (ذینفعان UI) → full register→select loop  
2. Add US3 → remaining پیمانکار surfaces  
3. Polish + quickstart evidence  

### Suggested MVP scope

**Phases 1–3 (T001–T023)** — department activity contractor select backed by stakeholder contractors.

---

## Notes

- Quote constraints from data-model when implementing FK/import validation  
- Do not use `CreatableSelect` for پیمانکار  
- Do not merge `subcontractors` / Contract registers  
- Preserve legacy free-text snapshot readability until edit  

## Task count summary

| Phase | Tasks | Story |
|-------|-------|-------|
| Setup | T001–T003 (3) | — |
| Foundational | T004–T008 (5) | — |
| US1 MVP | T009–T023 (15) | US1 |
| US2 | T024–T029 (6) | US2 |
| US3 | T030–T043 (14) | US3 |
| Polish | T044–T047 (4) | — |
| **Total** | **47** | |

Format validation: all tasks use `- [ ]`, sequential `Tnnn`, optional `[P]`, story labels only on US phases, and include file paths.


## Phase 7: Convergence

> Appended by `/speckit-converge` after assessing current code against spec/plan/tasks (checkbox claims are not evidence). Complete via `/speckit-implement`.

- [X] T048 CRITICAL — Add ذینفعان edit UI to update stakeholder `role` and `status` (so contractors can be inactivated / reclassified) in `apps/web/src/app/routes/project-stakeholders.tsx` per FR-003 and US2/AC2 (`partial`)
- [X] T049 CRITICAL — Stop inventable free-text پیمانکار on project create: replace or constrain the field in `apps/web/src/app/routes/project-create-wizard.tsx` per FR-001, FR-007, SC-001, and T042 (`contradicts`)
- [X] T050 [P] Replace free-text پیمانکار inputs with `ContractorSelect`/`contractor_ref` in `apps/web/src/app/routes/project-labor-camp.tsx` per FR-009 and T041 (`partial`)
- [X] T051 Require durable contractor identity on daily-report activity save: reject unbound free-text `subcontractor_name` without valid `contractor_ref` (and tighten combobox UX) in `apps/api/core/field_reports/serializers.py` and `apps/web/src/components/daily_reports/EditableGrid.tsx` / `ActivityTab.tsx` per FR-001, FR-005, FR-007 (`partial`)
- [X] T052 [P] Same unbound-name guard for labor-camp writes in `apps/api/core/field_reports/serializers.py` and `apps/web/src/components/daily_reports/LaborCampTab.tsx` per FR-005, FR-007 (`partial`)
- [X] T053 [P] Author/run e2e for contractor role on ذینفعان + department `ContractorSelect` empty/populated in `e2e/tests/contractor-stakeholder-select.spec.ts` per T025 and US2 (`missing`)
- [X] T054 [P] Add and compile FA gettext for contractor validation messages in `apps/api/core/locale/fa/LC_MESSAGES/django.po` (and `.mo`) per Constitution III and T044 (`missing`)
- [X] T055 Record `pnpm typecheck`, quickstart scenarios 1–6, and SC-001–SC-005 evidence in `specs/027-contractor-stakeholder-select/verification.md` per T023, T046, T047 (`missing`)
