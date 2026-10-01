---

description: "Task list for warehouse report fields feature"
---

# Tasks: Warehouse Report Fields

**Input**: Design documents from `/specs/001-warehouse-report-fields/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — spec FR-014 / SC-006 require TDD (failing tests first, then implement).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- API: `apps/api/core/inventory/`
- Web: `apps/web/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm branch and design docs; no new packages required

- [X] T001 Confirm branch `001-warehouse-report-fields` and review `specs/001-warehouse-report-fields/{spec,plan,research,data-model,contracts/department-activity-records,quickstart}.md` before coding
- [X] T002 [P] Note existing pytest entrypoint for inventory tests: `apps/api/core/inventory/tests.py` (extend in-place; no new test package)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema + shared helpers that ALL user stories need

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests first (TDD) ⚠️

> Write these tests FIRST and ensure they FAIL before model/migration implementation

- [X] T003 [P] Add failing tests for `is_warehouse_department` and warehouse field presence on `DepartmentActivityRecord` in `apps/api/core/inventory/tests.py`
- [X] T004 [P] Add failing migration/model assertion tests that warehouse columns exist with constraints `material_type` string(255) blank default `''`, `quantity_in` decimal(14,3) default `0`, `quantity_out` decimal(14,3) default `0`, `consumption_location` string(255) blank default `''`, `supplier` string(255) blank default `''`, and generic `location`/`activity_description`/`contractor` allow blank in `apps/api/core/inventory/tests.py`

### Implementation

- [X] T005 Add `is_warehouse_department(department: str) -> bool` beside `department_uses_unit` in `apps/api/core/inventory/models.py`
- [X] T006 Extend `DepartmentActivityRecord` in `apps/api/core/inventory/models.py`: add `material_type` CharField(max_length=255, blank=True, default=''), `quantity_in` DecimalField(max_digits=14, decimal_places=3, default=0), `quantity_out` DecimalField(max_digits=14, decimal_places=3, default=0), `consumption_location` CharField(max_length=255, blank=True, default=''), `supplier` CharField(max_length=255, blank=True, default=''); set `location`, `activity_description`, `contractor` to `blank=True`
- [X] T007 Generate and apply Django migration for T006 under `apps/api/core/inventory/migrations/` (no data remap of legacy warehouse rows)
- [X] T008 Expose new model fields on `DepartmentActivityRecordSerializer` field list in `apps/api/core/inventory/serializers.py` (validation logic comes in US1)
- [X] T009 [P] Extend `DepartmentActivityRecord` TypeScript interface and payload types with `material_type`, `quantity_in`, `quantity_out`, `consumption_location`, `supplier` plus `isWarehouseDepartment` helper in `apps/web/src/app/lib/api-types.ts`
- [X] T010 [P] Add warehouse field/column/filter i18n keys (date, materialType, quantityIn, unit, quantityOut, consumptionLocation, supplier, description + validation messages) in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`

**Checkpoint**: Foundation ready — migration applied; types/i18n stubs present; user stories can begin

---

## Phase 3: User Story 1 - Record warehouse material movement (Priority: P1) 🎯 MVP

**Goal**: Warehouse create form and API accept only warehouse fields and persist them with validation

**Independent Test**: Open warehouse create form, fill eight fields with at least one positive quantity, submit; record saves. Both quantities zero → rejected with message.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Add failing API create tests for warehouse happy path (required: `date`, `material_type`, `unit`, `consumption_location`, `supplier`; optional `description`; at least one of `quantity_in`/`quantity_out` > 0; quantities ≥ 0) in `apps/api/core/inventory/tests.py`
- [X] T012 [P] [US1] Add failing API create tests rejecting both quantities ≤ 0, negative quantities, and missing warehouse required fields in `apps/api/core/inventory/tests.py`
- [X] T013 [P] [US1] Add failing API create test asserting warehouse write clears `location`, `activity_description`, `contractor` to `''` in `apps/api/core/inventory/tests.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement department-aware `validate` on `DepartmentActivityRecordSerializer` in `apps/api/core/inventory/serializers.py`: warehouse requires `date`, `material_type` (max 255), `unit` (max 64), `consumption_location` (max 255), `supplier` (max 255); `quantity_in`/`quantity_out` ≥ 0 with at least one > 0; clear generic fields on warehouse write; reject over-length with field errors
- [X] T015 [US1] Update OpenAPI/request docs for create on `DepartmentActivityRecordViewSet` in `apps/api/core/inventory/views.py` to document warehouse vs generic payloads per `specs/001-warehouse-report-fields/contracts/department-activity-records.md`
- [X] T016 [US1] Add warehouse fields to Django admin list/search for `DepartmentActivityRecord` in `apps/api/core/inventory/admin.py`
- [X] T017 [US1] Branch `DepartmentActivityRecordModal` for `department === "warehouse"` in `apps/web/src/components/department/department-activity-record-modal.tsx`: show only date, material_type, quantity_in, unit, quantity_out, consumption_location, supplier, description; hide location/contractor/activity_description; client canSubmit matches warehouse rules
- [X] T018 [US1] Wire warehouse create payload mapping and sticky-field keys for new fields in `apps/web/src/components/department/department-activity-record-modal.tsx`
- [X] T019 [US1] Run `apps/api/core` pytest for T011–T013 until green; manually verify warehouse modal create once against local API

**Checkpoint**: Warehouse create works end-to-end via API + UI (MVP)

---

## Phase 4: User Story 2 - Browse and find warehouse records (Priority: P1)

**Goal**: Warehouse list/table/search/filter/sort use warehouse columns

**Independent Test**: With warehouse records present, department page shows warehouse columns; filter/search by material_type, consumption_location, or supplier returns matches.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T020 [P] [US2] Add failing queryset filter/search/ordering tests for `material_type`, `consumption_location`, `supplier`, `quantity_in`, `quantity_out` in `apps/api/core/inventory/tests.py` (via `get_department_activity_queryset` / list API)
- [X] T021 [P] [US2] Add failing list API contract test that warehouse responses include warehouse fields with values in `apps/api/core/inventory/tests.py`

### Implementation for User Story 2

- [X] T022 [US2] Extend `_ALLOWED_ORDERING_FIELDS`, text filters, and `search` Q-objects for warehouse fields in `apps/api/core/inventory/department_activity_services.py`
- [X] T023 [US2] Document new list query params (`material_type`, `consumption_location`, `supplier`) on list views in `apps/api/core/inventory/views.py` and `apps/api/core/inventory/department_activity_data_views.py`
- [X] T024 [US2] Extend list params type with warehouse filters in `apps/web/src/app/lib/api-types.ts`
- [X] T025 [US2] Branch warehouse table columns in `apps/web/src/components/department/department-page.tsx` to date, material_type, quantity_in, unit, quantity_out, consumption_location, supplier, description (no location/contractor/activity_description)
- [X] T026 [US2] Branch warehouse filters/search UX in `apps/web/src/components/department/department-page.tsx` to use warehouse field keys and i18n labels
- [X] T027 [US2] Run pytest for T020–T021 until green against `apps/api/core/inventory/tests.py`; verify warehouse table/filters in browser via `apps/web/src/components/department/department-page.tsx` (fa/en)

**Checkpoint**: Warehouse browse/search works independently

---

## Phase 5: User Story 3 - Non-warehouse departments unchanged (Priority: P2)

**Goal**: Buildings/mechanical/security/machinery/electrical keep generic schema and UI

**Independent Test**: Open a non-warehouse department create form and list — legacy fields only; warehouse-only fields absent; existing creates still succeed.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T028 [P] [US3] Add failing/regression API tests that non-warehouse create still requires `location`, `activity_description`, `contractor` (+ `unit` when applicable) and clears warehouse fields to `''`/`0` in `apps/api/core/inventory/tests.py`
- [X] T029 [P] [US3] Add failing/regression security-without-unit create test still passes after warehouse changes in `apps/api/core/inventory/tests.py`

### Implementation for User Story 3

- [X] T030 [US3] Ensure serializer non-warehouse branch in `apps/api/core/inventory/serializers.py` preserves prior required rules and zeroes/clears `material_type`, `quantity_in`, `quantity_out`, `consumption_location`, `supplier` on write
- [X] T031 [US3] Confirm `DepartmentActivityRecordModal` non-warehouse branch in `apps/web/src/components/department/department-activity-record-modal.tsx` still shows only generic fields (no warehouse inputs)
- [X] T032 [US3] Confirm `department-page.tsx` non-warehouse columns/filters remain the legacy set in `apps/web/src/components/department/department-page.tsx`
- [X] T033 [US3] Run full department-activity pytest subset in `apps/api/core/inventory/tests.py` until green including T028–T029

**Checkpoint**: Non-warehouse flows unchanged; no warehouse UI leakage

---

## Phase 6: User Story 4 - Import, export, and reports (Priority: P2)

**Goal**: Warehouse Excel import/export and daily/weekly PDF use warehouse columns

**Independent Test**: Export warehouse Excel matches warehouse headers; import valid file creates rows; invalid rows error; daily/weekly PDF shows warehouse columns.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T034 [P] [US4] Add failing export header/row tests for `department=warehouse` expecting `date, material_type, quantity_in, unit, quantity_out, consumption_location, supplier, description` in `apps/api/core/inventory/tests.py`
- [X] T035 [P] [US4] Add failing import tests for warehouse happy path + missing columns + both quantities zero row errors in `apps/api/core/inventory/tests.py`
- [X] T036 [P] [US4] Add failing PDF report smoke tests asserting warehouse column labels/values (not contractor/activity_description) for warehouse department in `apps/api/core/inventory/tests.py`

### Implementation for User Story 4

- [X] T037 [US4] Make `export_headers_for_department`, `HEADER_ALIASES`, `export_activities_to_xlsx`, `_required_import_fields`, and `import_activities_from_xlsx` warehouse-aware in `apps/api/core/inventory/department_activity_io.py` (Persian/English aliases per contract)
- [X] T038 [US4] Update `generate_activity_report_pdf` warehouse table columns in `apps/api/core/inventory/department_activity_io.py` to Date | Material type | In | Unit | Out | Consumption location | Supplier | Description
- [X] T039 [US4] Align export/import/report OpenAPI params/descriptions in `apps/api/core/inventory/department_activity_data_views.py` with warehouse contract
- [X] T040 [US4] Ensure web export/import buttons on warehouse department page in `apps/web/src/components/department/department-page.tsx` still call existing endpoints with `department=warehouse` (no broken assumptions on generic headers)
- [X] T041 [US4] Run pytest for T034–T036 until green; smoke Excel round-trip and one daily/weekly PDF download per `specs/001-warehouse-report-fields/quickstart.md`

**Checkpoint**: Warehouse IO and reports aligned with form/list schema

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and cleanup across stories

- [X] T042 [P] Update `__str__` on `DepartmentActivityRecord` in `apps/api/core/inventory/models.py` to prefer `material_type` for warehouse rows (avoid empty `activity_description`)
- [X] T043 [P] Run frontend typecheck for touched web files (`pnpm typecheck`) covering `apps/web/src/app/lib/api-types.ts` and `apps/web/src/components/department/*`
- [X] T044 Execute full quickstart validation checklist in `specs/001-warehouse-report-fields/quickstart.md` (migrate, pytest warehouse+DepartmentActivity, API create/list/export/import, UI fa/en, non-warehouse smoke)
- [X] T045 Confirm no silent legacy remap: existing warehouse rows remain readable with empty new fields after migration (spot-check via `apps/api/core/inventory/admin.py` or list API)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; practically after US1 serializer fields exist for list values
- **US3 (Phase 5)**: Depends on Foundational + US1 serializer branching (regression after warehouse validate)
- **US4 (Phase 6)**: Depends on Foundational + model fields; can proceed after US1 persistence works
- **Polish (Phase 7)**: Depends on desired user stories complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependency on other stories — **MVP**
- **US2 (P1)**: After Phase 2; best after US1 so create can seed list data
- **US3 (P2)**: After US1 serializer department branching exists
- **US4 (P2)**: After Phase 2 model fields; independent of UI list/form polish but shares IO with warehouse schema

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Serializer/services before UI
- Story complete before moving to next priority when sequential

### Parallel Opportunities

- T003–T004 in parallel; T009–T010 in parallel after model direction known
- Within US1: T011–T013 in parallel; then T014 sequential; T016–T017 can parallelize after T014 (admin vs modal)
- Within US2: T020–T021 in parallel; T024–T026 after T022
- Within US3: T028–T029 in parallel
- Within US4: T034–T036 in parallel; T037–T038 sequential in same file (do not parallelize same-file edits)
- US2 UI (T025–T026) and US4 IO (T037–T039) can proceed in parallel by different people after Phase 2

---

## Parallel Example: User Story 1

```bash
# Launch all US1 failing tests together:
Task: "T011 warehouse create happy-path tests in apps/api/core/inventory/tests.py"
Task: "T012 warehouse validation rejection tests in apps/api/core/inventory/tests.py"
Task: "T013 warehouse clears generic fields test in apps/api/core/inventory/tests.py"

# After tests fail, implement serializer then parallelize admin + modal:
Task: "T014 serializer validate in apps/api/core/inventory/serializers.py"
Task: "T016 admin fields in apps/api/core/inventory/admin.py"
Task: "T017 warehouse modal branch in apps/web/src/components/department/department-activity-record-modal.tsx"
```

---

## Parallel Example: User Story 4

```bash
# Failing IO tests in parallel:
Task: "T034 warehouse export tests in apps/api/core/inventory/tests.py"
Task: "T035 warehouse import tests in apps/api/core/inventory/tests.py"
Task: "T036 warehouse PDF smoke tests in apps/api/core/inventory/tests.py"

# Then implement IO (same file — sequential):
Task: "T037 Excel import/export warehouse-aware in department_activity_io.py"
Task: "T038 PDF warehouse columns in department_activity_io.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (migration + types + i18n)
3. Complete Phase 3: US1 (TDD create API + modal)
4. **STOP and VALIDATE**: Warehouse create independently
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational → schema ready
2. US1 → warehouse create MVP
3. US2 → list/search/columns
4. US3 → non-warehouse regression lock
5. US4 → Excel/PDF parity
6. Polish → quickstart sign-off

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. After Phase 2:
   - Dev A: US1 then US3 regression
   - Dev B: US2 list/filters UI + services
   - Dev C: US4 IO/PDF (after model migration)
3. Integrate and run full `inventory/tests.py` + quickstart

---

## Notes

- [P] = different files, no incomplete-task dependencies
- Spec mandates TDD — do not skip failing-test tasks
- Quote constraints from data-model in implementation (max lengths, decimal 14,3, blank defaults, at least one quantity > 0)
- No automatic remap of legacy warehouse `location`/`contractor`/`activity_description` into new fields
- Commit after each task or logical group
- Stop at checkpoints to validate stories independently

---

## Phase 8: Convergence

**Purpose**: Close remaining gaps between current code and spec/plan/constitution after `/speckit-implement`

**Gap summary**: 4 findings (partial×3, unrequested×1) — HIGH×1, MEDIUM×1, LOW×2

- [X] T046 Perform browser verification of warehouse create form and list/filters in fa and en (including Jalali date reopen/persist) per Constitution III / Constitution VI / US1/AC1 / US2/AC1; update `specs/001-warehouse-report-fields/quickstart.md` UI done-when checkbox with evidence (partial)
- [X] T047 Localize warehouse create/import validation error messages (required fields, negative quantities, both quantities ≤ 0) for Persian and English in `apps/api/core/inventory/serializers.py` and `apps/api/core/inventory/department_activity_io.py` per FR-012 / Constitution III (partial)
- [X] T048 [P] Add failing-then-passing pytest cases that warehouse create rejects over-length `material_type`, `consumption_location`, `supplier`, and `unit` with field errors in `apps/api/core/inventory/tests.py` per edge-case / FR-014 (partial)
- [X] T049 [P] Review unrequested PDF `setPageCompression(0)` in `generate_activity_report_pdf` in `apps/api/core/inventory/department_activity_io.py`: keep with an explicit comment justifying smoke-test readability, or restore compression and assert warehouse PDF columns via a testable header helper (unrequested)
