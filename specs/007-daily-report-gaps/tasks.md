---
description: "Task list for Daily Site Report Gap Closure (FR-DR)"
---

# Tasks: Daily Site Report Gap Closure

**Input**: Design documents from `/specs/007-daily-report-gaps/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: existing `field_reports` daily reports (workflow, child rows, sync); soft-delete/audit (002); WBS/activities (004/005); optional `resources` material balance for reconciliation

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002–006). Implemented via `/speckit-implement` (TDD).

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 maps to spec user stories
- Exact file paths required

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm daily-report baseline and scaffold test/i18n stubs

- [X] T001 Verify existing daily-report ViewSets, status workflow, unique `(project, report_date, shift)`, and child write gates in `apps/api/core/field_reports/` (read `ENDPOINTS.md`, `models.py`, `daily_report_views.py`, `services/__init__.py`)
- [X] T002 [P] Create placeholder test modules `apps/api/core/field_reports/tests/test_daily_report_gaps_header.py`, `test_daily_report_gaps_correction.py`, `test_daily_report_gaps_rows.py`, `test_daily_report_gaps_status_unset.py`
- [X] T003 [P] Add i18n stub keys for work front, responsible, absence, material return, site-event owner/due, locked status, correction request, unset-vs-zero, reconciliation statuses under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema for versioning/correction lineage and route mounts all stories need

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing expectations for DailyReport fields `work_front` Char(120) blank, `location_notes` Char(200) blank, `lineage_id` UUID, `version_number` PositiveInt default 1, `supersedes` FK null, `is_current` Bool default True in `apps/api/core/field_reports/tests/test_daily_report_gaps_header.py`
- [X] T005 [P] Write failing expectations for unique constraint: at most one non-deleted `is_current=True` per `(project, report_date, shift)` in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py`
- [X] T006 [P] Write failing expectations for `DailyReportCorrectionRequest` fields per `data-model.md` (source_report, result_report null, reason Text min 10, status in `draft|submitted|approved|cancelled|rejected`, AuditSoftDeleteModel) in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py`

### Implementation

- [X] T007 Add DailyReport versioning + header location fields (`work_front`, `location_notes`, `lineage_id`, `version_number`, `supersedes`, `is_current`) and adjust uniqueness to current-only in `apps/api/core/field_reports/models.py` + migration; backfill `lineage_id=id`, `version_number=1`, `is_current=True` for existing rows
- [X] T008 Add `DailyReportCorrectionRequest` model per `data-model.md` in `apps/api/core/field_reports/models.py` + migration
- [X] T009 [P] Extend child models stubs in `apps/api/core/field_reports/models.py` + migration: Activity `responsible_user` FK null SET_NULL + `responsible_name` Char(120) blank; Labor `absence_count` PositiveIntegerField null; MaterialTransactionType add `return`; Material `consumption_location` Char(120) blank; IncidentType add `site_instruction` + `barrier`; Incident `follow_up_owner_user` FK null, `follow_up_owner_name` Char(120) blank, `due_date` Date null
- [X] T010 Register URL stubs under `apps/api/core/field_reports/` urls for correction-requests, versions, materials/reconciliation per contracts (can 501 until story wires views); update `apps/api/core/field_reports/ENDPOINTS.md` outline
- [X] T011 Re-run T004–T006 until PASS for schema smoke (views may still be incomplete)

**Checkpoint**: Shared schema + route mounts ready

---

## Phase 3: User Story 1 - Complete header and activity responsibility (Priority: P1) 🎯 MVP

**Goal**: Persist header work front; activity responsible; unset-vs-zero for activity quantity

**Independent Test**: Create draft with `work_front`; activity with responsible + measured qty; activity with `quantity_measured=false` and null qty; submit rejects measured+null

### Tests for User Story 1

- [X] T012 [P] [US1] Failing API tests for create/PATCH header `work_front` / `location_notes` and response fields per `contracts/daily-report-header-and-rows.md` in `apps/api/core/field_reports/tests/test_daily_report_gaps_header.py`
- [X] T013 [P] [US1] Failing tests for activity `responsible_user_id` / `responsible_name` and `quantity_measured` rules (`true`⇒qty required incl. 0; `false`⇒qty null; never coerce null→0) in same module or `test_daily_report_gaps_status_unset.py`

### Implementation for User Story 1

- [X] T014 [US1] Wire serializers + views for header/activity new fields and submit validation `quantity_unset_invalid` in `apps/api/core/field_reports/serializers.py`, `daily_report_views.py`, and submit helper in `services/`
- [X] T015 [P] [US1] UI: header work-front field + activity responsible + unset quantity UX in `apps/web/src/components/daily_reports/` (e.g. `DailyReportForm.tsx`, `ActivityTab.tsx`); API types in `apps/web/src/app/lib/api/daily-reports.ts`
- [X] T016 [US1] Re-run T012–T013 until PASS

**Checkpoint**: US1 independently verifiable

---

## Phase 4: User Story 2 - Correction request for locked reports (Priority: P1)

**Goal**: Approved = locked; correction clones new draft version; prior version retained; direct edit denied

**Independent Test**: Approve → PATCH denied → correction with reason → edit/submit/approve result → versions list shows both; second open correction 409

### Tests for User Story 2

- [X] T017 [P] [US2] Failing tests: PATCH/child write on `approved` returns `report_locked`; open correction requires reason ≥10 chars in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py`
- [X] T018 [P] [US2] Failing tests per `contracts/correction-requests.md`: clone children, source `is_current=false` remains `approved`, result `draft` `is_current=true` `version_number=N+1`, versions list, `correction_already_open`, cancel restores single current in same module
- [X] T019 [P] [US2] Failing regression: offline sync-batch returns `conflict` (not merge) for approved current in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` or existing sync test module

### Implementation for User Story 2

- [X] T020 [US2] Implement correction service (clone header+children, lineage/version/`is_current` rules, open/cancel, approve hooks) in `apps/api/core/field_reports/services/correction_service.py`
- [X] T021 [US2] Serializers + views + URLs for `POST .../correction-requests/`, list/detail, `versions/`, cancel per contract; ensure existing approve sets locked semantics; wire into `daily_report_views.py` / urls
- [X] T022 [P] [US2] UI: locked badge, Request correction dialog (reason), version history, navigate to result draft in `apps/web/src/components/daily_reports/` + routes; API client methods in `apps/web/src/app/lib/api/daily-reports.ts`
- [X] T023 [US2] Update sync-batch guard for non-current/historical versions in `apps/api/core/field_reports/services/__init__.py` (or sync module); re-run T017–T019 until PASS

**Checkpoint**: US2 independently verifiable (SC-002)

---

## Phase 5: User Story 3 - Materials return, labor absence, site events (Priority: P2)

**Goal**: Material return + consumption_location; labor absence_count; site event owner/due; advisory reconciliation

**Independent Test**: Save return/absence/event with owner+due; GET detail; GET reconciliation statuses

### Tests for User Story 3

- [X] T024 [P] [US3] Failing API tests for material `transaction_type=return`, `consumption_location`; labor `absence_count` null vs 0; incident types `site_instruction`/`barrier` + owner/due per `contracts/daily-report-header-and-rows.md` in `apps/api/core/field_reports/tests/test_daily_report_gaps_rows.py`
- [X] T025 [P] [US3] Failing tests for `GET .../materials/reconciliation/` statuses `match|mismatch|insufficient_data` per `contracts/material-reconciliation.md` in same module

### Implementation for User Story 3

- [X] T026 [US3] Serializers/views for extended labor/material/incident fields; material type enum includes `return` in `apps/api/core/field_reports/serializers.py` / views
- [X] T027 [US3] Implement reconciliation read service using `resources` balance (read-only, never blocks save) in `apps/api/core/field_reports/services/material_reconciliation.py` + view
- [X] T028 [P] [US3] UI: Materials return + location; Labor absence; Incidents owner/due + new types; optional reconciliation panel in `apps/web/src/components/daily_reports/`; API client updates in `apps/web/src/app/lib/api/daily-reports.ts`
- [X] T029 [US3] Re-run T024–T025 until PASS

**Checkpoint**: US3 independently verifiable (SC-003 / SC-005)

---

## Phase 6: User Story 4 - Status clarity supervisor confirm and manager lock (Priority: P2)

**Goal**: Present approved as locked; keep report_date / created_at / approved_at distinct; fa/en labels

**Independent Test**: Walk draft→submit→approve; response `is_locked`; UI locked copy; timestamps distinct

### Tests for User Story 4

- [X] T030 [P] [US4] Failing API tests that approved responses include `is_locked=true` and distinct `report_date`/`created_at`/`approved_at` per `contracts/status-and-unset-semantics.md` in `apps/api/core/field_reports/tests/test_daily_report_gaps_status_unset.py`
- [X] T031 [P] [US4] Failing tests that submitted/under_review/approved deny child writes; rejected remains editable in same module

### Implementation for User Story 4

- [X] T032 [US4] Add `is_locked` (and optional `status_label_key`) on report serializers in `apps/api/core/field_reports/serializers.py`; ensure write guards match contract table
- [X] T033 [P] [US4] UI: ApprovalStatusBar / list badges show Locked «قفل‌شده» in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` (and list); locale keys in `fa.json`/`en.json`
- [X] T034 [US4] PDF export includes work_front / responsible / absence / return / event owner-due where applicable in `apps/api/core/field_reports/pdf.py`; re-run T030–T031 until PASS

**Checkpoint**: US4 independently verifiable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, regression, quickstart validation

- [X] T035 [P] Finalize `apps/api/core/field_reports/ENDPOINTS.md` for all new endpoints and versioning rules
- [X] T036 [P] Ensure material quantity never coerced null→0 across serializers; regression assert in `test_daily_report_gaps_status_unset.py`
- [X] T037 Run focused pytest: `field_reports/tests/test_daily_report_gaps_*.py` (+ existing daily-report CRUD/workflow smoke) from `apps/api/core`
- [X] T038 [P] Manual or Playwright smoke of quickstart Scenarios A–D in `specs/007-daily-report-gaps/quickstart.md` when UI ready
- [X] T039 Verify bilingual locked/correction/unset strings render in fa and en on form + view

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: After Setup — **BLOCKS** all user stories
- **US1 (Phase 3)** / **US2 (Phase 4)**: After Foundational; US1 is MVP; US2 can start in parallel with US1 if staffed (shares models from Phase 2)
- **US3 (Phase 5)** / **US4 (Phase 6)**: After Foundational; can parallelize with each other; US4 lightly depends on serializer shape from US1/US2
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependency on US2–US4
- **US2 (P1)**: After Phase 2 — uses lineage fields from Phase 2; independently testable
- **US3 (P2)**: After Phase 2 — child field extensions; independently testable
- **US4 (P2)**: After Phase 2 — presentation/guards; best after US2 locked path exists for full UX, but API `is_locked` testable on approve alone

### Parallel Opportunities

- T002/T003; T004–T006; T009 with T008 after T007 starts
- After Phase 2: US1 and US2 in parallel (different test modules / service files)
- US3 UI tabs (materials/labor/incidents) parallelizable within story
- T035/T036/T038/T039 in polish

---

## Parallel Example: User Story 2

```bash
# Tests in parallel:
Task: T017 failing locked-write + reason tests in test_daily_report_gaps_correction.py
Task: T018 failing correction clone/versions tests in test_daily_report_gaps_correction.py
Task: T019 failing sync-batch conflict regression

# Then implementation:
Task: T020 correction_service.py
Task: T021 views/URLs
Task: T022 UI correction + history (parallel with T021 if API contract stable)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + Phase 2  
2. Phase 3 (US1) — header work front, responsible, unset qty  
3. **STOP and VALIDATE** quickstart Scenario A  
4. Then US2 (correction) — required for SC-DR-003 compliance

### Incremental Delivery

1. Setup + Foundational → schema ready  
2. US1 → demo complete draft fields  
3. US2 → demo lock + correction (compliance MVP)  
4. US3 → materials/labor/events + reconciliation  
5. US4 → status copy polish + PDF  
6. Polish → ENDPOINTS + pytest + quickstart

### Suggested MVP scope

**US1 + US2** (Phases 1–4): delivers header completeness and the correction/lock acceptance bar (SC-001, SC-002, SC-004). US3/US4 follow for full FR-DR gap closure.

---

## Notes

- Do not implement until `/speckit-implement` (or explicit user request)
- Reuse `view_reports` / `edit_reports` / `approve_reports` — no new permission codes unless product later splits correction
- Approved = locked (D1); uniqueness is current-only (D3)
- Avoid rebuilding weekly/monthly progress (08) or HR capacity (006)

---

## Phase 8: Convergence

**Purpose**: Close remaining gaps found by `/speckit-converge` against spec.md, plan.md, tasks.md, and constitution (present-state assessment; prior `[X]` claims re-verified).

- [X] T040 Surface material reconciliation hints (match / mismatch / insufficient_data) in the daily-report Materials UI via `fetchMaterialReconciliation` without blocking save, in `apps/web/src/components/daily_reports/MaterialsTab.tsx` (and related form if needed) per SC-005 / US3/AC4 (partial)
- [X] T041 Add version-history UI that lists lineage versions from `GET .../versions/` and lets users open prior locked reports for read-only review in `apps/web/src/components/daily_reports/` (e.g. `ApprovalStatusBar.tsx` or a versions panel) per US2/AC2 / T022 (partial)
- [X] T042 CRITICAL complete end-to-end PDF coverage for new daily-report fields: labor `absence_count`, material return/location, incident follow-up owner and due date in `apps/api/core/field_reports/pdf.py` per Constitution II / T034 (partial)
- [X] T043 Add or run Playwright (or documented manual) smoke for quickstart Scenarios A–D (create with work front + responsible, lock + correction, return/absence/site event, locked status timestamps) under `e2e/` or record evidence per Constitution VI / T038 (partial)
- [X] T044 Soft-warn on submit when header `work_front` is empty (do not hard-block) in `apps/api/core/field_reports/daily_report_views.py` submit validation and surface in UI per FR-001 / data-model submit rules (partial)
