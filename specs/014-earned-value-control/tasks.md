# Tasks: Earned Value & Project Control (EVM)

**Input**: Design documents from `/specs/014-earned-value-control/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required for every task slice** (plan: prefer failing test before implementation). Pattern: write failing pytest (or UI assertion where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = shared measure/status helpers + baseline validity used by all stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/014-earned-value-control"` and review `specs/014-earned-value-control/plan.md` TDD discipline
- [x] T002 [P] Inventory extension points in `apps/api/core/schedule/{services/evm_service.py,services/progress_service.py,progress_views.py,urls.py,ENDPOINTS.md}` and cost feeds in `apps/api/core/cost_control/models.py`; note gaps vs `specs/014-earned-value-control/research.md`

---

## Phase 2: Foundational — EVM status helpers & baseline validity (Blocking)

**Purpose**: Shared builders for measure/index status enums (`registered` \| `unregistered` \| `incomplete`; `computable` \| `not_computable`) and schedule/budget baseline validity used by every story. Blocks trustworthy US1–US4 work.

**⚠️ CRITICAL**: No story may invent SPI/CPI numeric zeros when status is `not_computable`, or skip baseline warnings.

### Tests (TDD — write first, must FAIL)

- [x] T003 [P] Write failing unit/pytest helpers: measure with `status=unregistered` has `amount=null`; index with `status=not_computable` has `value=null` in `apps/api/core/schedule/tests/test_evm_status_helpers.py`
- [x] T004 [P] Write failing pytest unlocked schedule baseline → `warnings` includes `baseline_not_locked` and `validity != valid` from validity helper in `apps/api/core/schedule/tests/test_evm_baseline_gate.py`

### Implementation

- [x] T005 Implement measure/index DTO helpers (`measure(amount, status)`, `index(value, status, reason?)`) in `apps/api/core/schedule/services/evm_status.py` with enums from `specs/014-earned-value-control/data-model.md` (`registered` \| `unregistered` \| `incomplete`; `computable` \| `not_computable`)
- [x] T006 Implement `resolve_evm_baseline_validity(project_id)` in `apps/api/core/schedule/services/evm_baseline.py`: schedule locked baseline; budget control/approved version (`is_control` + approved, fallback per research); returns `validity` (`valid` \| `partial` \| `invalid`), `warnings`, `schedule_baseline`, `budget_baseline`
- [x] T007 Re-run `test_evm_status_helpers.py` and `test_evm_baseline_gate.py` until green

**Checkpoint**: Status + baseline helpers green; foundation ready for story work

---

## Phase 3: User Story 1 — View EVM indices at cut-off (Priority: P1) 🎯 MVP

**Goal**: At as-of cut-off, report PV/EV/AC (source definitions), SV/CV, SPI/CPI when computable; EV from approved measurement progress; never EV = AC/IPC (FR-002, FR-003 partial, FR-007, SC-001, SC-005)

**Independent Test**: Locked baselines + approved progress + ActualCost → `GET .../progress/kpis/` shows registered PV/EV/AC and computable SPI/CPI; changing only AC does not change EV

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T008 [P] [US1] Write failing pytest locked control budget + locked schedule + approved_progress → `ev.status=registered`, `pv.status=registered`, `ac.status=registered` in `apps/api/core/schedule/tests/test_evm_approved_progress.py` per `specs/014-earned-value-control/contracts/evm-report.md`
- [x] T009 [P] [US1] Write failing pytest EV uses `approved_progress` (not unapproved `actual_progress` only) in `apps/api/core/schedule/tests/test_evm_approved_progress.py`
- [x] T010 [P] [US1] Write failing pytest posting ActualCost without progress change leaves EV unchanged (EV ≠ AC) in `apps/api/core/schedule/tests/test_evm_approved_progress.py`
- [x] T011 [P] [US1] Write failing pytest SPI = EV/PV and CPI = EV/AC when both registered and divisors > 0; SV = EV−PV, CV = EV−AC in `apps/api/core/schedule/tests/test_evm_approved_progress.py`

### Implementation for User Story 1

- [x] T012 [US1] Add `get_approved_progress_on_date(project_id, as_of)` (weighted latest `approved_progress` ≤ as_of) in `apps/api/core/schedule/services/progress_service.py`; keep planned progress helper for PV
- [x] T013 [US1] Refactor `compute_evm` in `apps/api/core/schedule/services/evm_service.py` to: BAC from control/approved budget version; PV = BAC × planned %; EV = BAC × approved %; AC = ActualCost sum; attach structured `pv`/`ev`/`ac`/`sv`/`cv`/`spi`/`cpi` via `evm_status` helpers; preserve legacy numeric keys for compatibility per contract
- [x] T014 [US1] Wire baseline validity into `compute_evm` / `ProjectProgressKpisView` response in `apps/api/core/schedule/progress_views.py`; ensure cache key/invalidation still covers as_of in `apps/api/core/schedule/services/progress_service.py`
- [x] T015 [US1] Re-run `test_evm_approved_progress.py` and existing `apps/api/core/schedule/tests/test_progress.py` until green
- [x] T016 [US1] Frontend: type extended KPI payload in `apps/web/src/app/lib/api/progress.ts`; show PV/EV/AC cards on `apps/web/src/app/routes/project-progress.tsx` using registered amounts; i18n keys in `apps/web/src/app/locales/en.json` and `fa.json`

**Checkpoint**: US1 independently testable — project EVM measures + indices

---

## Phase 4: User Story 2 — Transparent incomplete data (Priority: P1)

**Goal**: Unregistered EV (no approved progress), baseline-not-locked warnings, not-computable SPI/CPI (and dependent forecasts) instead of misleading zeros (FR-001, FR-005–006, FR-008, SC-002, SC-004)

**Independent Test**: No approved progress → `ev.status=unregistered`, CPI not_computable; unlocked baseline → `baseline_not_locked` + `validity != valid`

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T017 [P] [US2] Write failing pytest no `approved_progress` rows → `ev.status=unregistered` and `ev.amount is null` (not silent registered zero) in `apps/api/core/schedule/tests/test_evm_not_computable.py`
- [x] T018 [P] [US2] Write failing pytest AC registered + EV unregistered → `cpi.status=not_computable` and `cv.status=not_computable` in `apps/api/core/schedule/tests/test_evm_not_computable.py`
- [x] T019 [P] [US2] Write failing pytest PV = 0 / unregistered → `spi.status=not_computable` in `apps/api/core/schedule/tests/test_evm_not_computable.py`
- [x] T020 [P] [US2] Write failing pytest unlocked schedule baseline → response `warnings` contains `baseline_not_locked` and `validity` is `partial` or `invalid` in `apps/api/core/schedule/tests/test_evm_baseline_gate.py` (API-level via `progress/kpis/`)
- [x] T021 [P] [US2] Write failing pytest CPI not_computable → `eac`/`etc`/`vac` status `not_computable` (no invented fallback) in `apps/api/core/schedule/tests/test_evm_not_computable.py`

### Implementation for User Story 2

- [x] T022 [US2] Enforce unregistered vs registered-zero rules and index/forecast not_computable chain in `apps/api/core/schedule/services/evm_service.py` per `data-model.md` tables
- [x] T023 [US2] Ensure `GET .../progress/kpis/` returns structured statuses (contract authoritative) in `apps/api/core/schedule/progress_views.py`; document warning codes in `apps/api/core/schedule/ENDPOINTS.md`
- [x] T024 [US2] Re-run `test_evm_not_computable.py` and `test_evm_baseline_gate.py` until green
- [x] T025 [US2] Frontend: validity banner + localized “not computable” / “unregistered” / “baseline is not locked” on `apps/web/src/app/routes/project-progress.tsx` (and shared `apps/web/src/components/progress/` if extracted); never display `0` for unregistered EV; i18n `en.json` / `fa.json`

**Checkpoint**: US2 independently testable — incomplete-data transparency

---

## Phase 5: User Story 3 — Finish forecasts (Priority: P2)

**Goal**: EAC = BAC/CPI, ETC = EAC−AC, VAC = BAC−EAC when CPI computable; otherwise not_computable (FR-003, FR-008, SC-001)

**Independent Test**: Valid CPI → EAC/ETC/VAC match common method; CPI not_computable → all three not_computable

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T026 [P] [US3] Write failing pytest with valid BAC+CPI → `eac.value == bac/cpi`, `etc.value == eac−ac`, `vac.value == bac−eac` in `apps/api/core/schedule/tests/test_evm_forecast.py`
- [x] T027 [P] [US3] Write failing pytest CPI not_computable → eac/etc/vac not_computable in `apps/api/core/schedule/tests/test_evm_forecast.py` (may overlap US2; keep dedicated forecast assertions)
- [x] T028 [P] [US3] Write failing pytest `meta.eac_method == "bac_over_cpi"` in `apps/api/core/schedule/tests/test_evm_forecast.py` per contract

### Implementation for User Story 3

- [x] T029 [US3] Centralize finish-forecast computation in `apps/api/core/schedule/services/evm_service.py` (or `evm_forecast.py`) using common method only; set `meta.eac_method`
- [x] T030 [US3] Re-run `test_evm_forecast.py` until green; confirm `apps/api/core/economic/services/forecast_service.py` still reads base EVM without breaking inflation overlay
- [x] T031 [US3] Frontend: EAC/ETC/VAC cards respect `status=not_computable` on `apps/web/src/app/routes/project-progress.tsx`; align standard (non-inflation) labels with KPI payload in `apps/web/src/components/economic/EvmForecastPanel.tsx` when CPI computable

**Checkpoint**: US3 independently testable — finish forecasts

---

## Phase 6: User Story 4 — Multi-level EVM (phase & CBS) (Priority: P2)

**Goal**: Phase (WBS) and CBS slice reports with project totals; no silent double count; multi-currency aggregation blocked without conversion; empty slices not SPI/CPI = 1.0 (FR-004, FR-010, SC-003)

**Independent Test**: Seeded phase + CBS budget/progress/cost → `by-phase` and `by-cbs` return registered measures; empty node not_computable; mixed currency blocked

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T032 [P] [US4] Write failing pytest two phase WBS with partitioned BAC + approved progress → each phase EV registered in `apps/api/core/schedule/tests/test_evm_phase_cbs.py` per `specs/014-earned-value-control/contracts/evm-by-phase.md`
- [x] T033 [P] [US4] Write failing pytest CBS node with budget + ActualCost.cbs + approved progress via CBS budget line → CPI computable in `apps/api/core/schedule/tests/test_evm_phase_cbs.py` per `contracts/evm-by-cbs.md`
- [x] T034 [P] [US4] Write failing pytest empty phase/CBS slice → indices `not_computable` (not SPI/CPI = 1.0) in `apps/api/core/schedule/tests/test_evm_phase_cbs.py`
- [x] T035 [P] [US4] Write failing pytest mixed currencies without conversion → aggregation blocked / warning (no silent sum) in `apps/api/core/schedule/tests/test_evm_phase_cbs.py`

### Implementation for User Story 4

- [x] T036 [US4] Implement `build_evm_by_phase(project_id, as_of)` and `build_evm_by_cbs(project_id, as_of, root_id?)` in `apps/api/core/schedule/services/evm_slice_service.py` (BAC from phase/CBS budget lines; EV from approved progress in WBS subtree / CBS-linked activities; AC from ActualCost links; `ac_allocation=direct_only` meta; reuse status helpers)
- [x] T037 [US4] Add `GET .../progress/evm/by-phase/` and `GET .../progress/evm/by-cbs/` in `apps/api/core/schedule/progress_views.py` and `apps/api/core/schedule/urls.py` with `view_dashboard`
- [x] T038 [US4] Re-run `test_evm_phase_cbs.py` until green
- [x] T039 [US4] Frontend: phase + CBS tables in `apps/web/src/components/progress/EvmSliceTable.tsx` (or equivalent) on `apps/web/src/app/routes/project-progress.tsx`; API client in `apps/web/src/app/lib/api/progress.ts`; i18n

**Checkpoint**: US4 independently testable — multi-level EVM

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, cache invalidation, measurement-version regression, bilingual polish, quickstart suite

### Tests (TDD / regression)

- [x] T040 [P] Write failing pytest unapproved measurement definition edit does not change EV derived from prior `approved_progress` / `measurement_version` rows in `apps/api/core/schedule/tests/test_evm_approved_progress.py` (FR-009, SC-006)
- [x] T041 [P] Write or extend pytest that KPI cache invalidates on progress approval / baseline lock / actual cost write via existing `invalidate_progress_caches` paths in `apps/api/core/schedule/tests/test_progress.py` or dedicated cache test

### Implementation

- [x] T042 Implement / verify measurement-version stability and cache invalidation hooks in `apps/api/core/schedule/services/progress_service.py` and callers; re-run T040–T041 until green
- [x] T043 [P] Update `apps/api/core/schedule/ENDPOINTS.md` for extended kpis + by-phase + by-cbs contracts
- [x] T044 [P] Bilingual pass: all new EVM strings present in `apps/web/src/app/locales/en.json` and `fa.json`
- [x] T045 Run full quickstart suite from `specs/014-earned-value-control/quickstart.md` (`test_evm_baseline_gate`, `test_evm_not_computable`, `test_evm_approved_progress`, `test_evm_phase_cbs`, `test_progress`, plus `test_evm_forecast` / `test_evm_status_helpers`)

**Checkpoint**: Feature ready for `/speckit-implement` verification

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational; strongly recommended immediately after US1 (shares `compute_evm` / KPI response; both P1)
- **US3 (Phase 5)**: After US1 (needs structured CPI/BAC); after US2 for forecast not_computable UX consistency
- **US4 (Phase 6)**: After Foundational + US1 status/EV rules (slice service reuses helpers); can start in parallel with US3 once US1 green
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|------------|-------------------------|
| US1 | Phase 2 | Yes — project KPIs |
| US2 | Phase 2 (+ US1 response shape ideal) | Yes — incomplete-data cases alone |
| US3 | US1 formulas | Yes — forecast pytest file |
| US4 | Phase 2 + US1 EV/status rules | Yes — phase/CBS endpoints |

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Helpers/services before endpoints
- Endpoints before frontend
- Story green before next priority (US2 may ship with US1 as combined P1 MVP)

### Parallel Opportunities

- T003 ∥ T004 (foundational tests)
- T008–T011 (US1 tests)
- T017–T021 (US2 tests)
- T026–T028 (US3 tests)
- T032–T035 (US4 tests)
- After US1 green: US3 backend and US4 backend can proceed in parallel if staffed
- T043 ∥ T044 (docs / i18n)

---

## Parallel Example: User Story 1

```bash
# Launch US1 failing tests together:
Task: "T008 approved EV registered in test_evm_approved_progress.py"
Task: "T009 EV uses approved_progress in test_evm_approved_progress.py"
Task: "T010 EV ≠ AC in test_evm_approved_progress.py"
Task: "T011 SPI/CPI/SV/CV formulas in test_evm_approved_progress.py"

# Then implement T012 → T013 → T014 → T015 → T016 sequentially
```

---

## Parallel Example: User Story 4

```bash
# Launch US4 failing tests together:
Task: "T032 by-phase EV in test_evm_phase_cbs.py"
Task: "T033 by-cbs CPI in test_evm_phase_cbs.py"
Task: "T034 empty slice not_computable in test_evm_phase_cbs.py"
Task: "T035 mixed currency blocked in test_evm_phase_cbs.py"

# Then T036 → T037 → T038 → T039
```

---

## Implementation Strategy

### MVP First (US1 + US2 recommended)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational (CRITICAL)  
3. Complete Phase 3: US1 — project EVM measures/indices  
4. Complete Phase 4: US2 — transparency (same P1; avoids shipping misleading zeros)  
5. **STOP and VALIDATE** against quickstart SC-001, SC-002, SC-004, SC-005  

### Incremental Delivery

1. Setup + Foundational → helpers ready  
2. US1 → demo project KPIs  
3. US2 → demo incomplete-data safety  
4. US3 → finish forecasts polish  
5. US4 → phase/CBS tables  
6. Polish → docs + SC-006 + full quickstart  

### Parallel Team Strategy

1. Team completes Setup + Foundational together  
2. Dev A: US1 → US2 (P1 path)  
3. Dev B (after US1 green): US4 slices  
4. Dev C (after US1 green): US3 forecasts + economic panel alignment  
5. Integrate in Polish  

---

## Notes

- [P] = different files, no incomplete dependencies  
- No new EVM fact table in v1 — computed-on-read per research  
- Preserve legacy KPI numeric fields while structured statuses are authoritative  
- Economic inflation EAC remains out of scope; do not break `economic` forecast consumers  
- Commit after each task or logical TDD group  
- Avoid: silent EV=0 for missing progress; SPI/CPI=1.0 on empty slices; summing mixed currencies  

---

## Phase 8: Convergence

**Purpose**: Close gaps found by `/speckit-converge` against current code vs spec/plan/tasks (2026-10-09). Prior phases T001–T045 remain unchanged.

- [x] T046 CRITICAL/HIGH: Call `invalidate_progress_caches(project_id)` from ActualCost create/update/approve/void paths in `apps/api/core/cost_control/views.py` and/or `apps/api/core/cost_control/services/actual_cost_service.py` so EVM KPI/phase/CBS caches do not serve stale AC after cost mutations per plan:T041/T042 and FR-002 (`missing`)
- [x] T047 [P] Write failing pytest that ActualCost create/approve triggers progress/EVM cache invalidation (or clears cached `progress/kpis` payload) in `apps/api/core/schedule/tests/test_progress.py` or `apps/api/core/cost_control/tests/` per plan:T041 (`missing`)
- [x] T048 HIGH: In `apps/api/core/schedule/services/evm_slice_service.py`, when sum of phase BAC does not partition control BAC, set `roll_up=partial` (not always `included`) and keep project_totals from global `compute_evm` per FR-004, SC-003, and data-model roll-up rules (`partial`)
- [x] T049 [P] Add pytest for incomplete phase BAC partition → `roll_up=partial` on affected slices in `apps/api/core/schedule/tests/test_evm_phase_cbs.py` per FR-004 (`partial`)
- [x] T050 MEDIUM: Align `apps/web/src/components/economic/EvmForecastPanel.tsx` with progress EVM semantics — show localized `progress.evm.notComputable` when SPI/CPI/EAC/ETC/VAC are null/not computable, and prefer values consistent with `fetchProgressKpis` when CPI is computable per T031 / US3 / Constitution III (`partial`)
- [x] T051 MEDIUM: In `apps/web/src/app/routes/project-progress.tsx` (+ i18n), treat `budget_baseline_not_approved` (and related budget warnings) with an explicit localized baseline/budget validity message, not only `baseline_not_locked` → generic partial copy, per FR-001 / US2/AC2 (`partial`)
- [x] T052 [P] MEDIUM: Extend `test_invalidate_clears_kpi_cache_keys` in `apps/api/core/schedule/tests/test_progress.py` to assert Redis scan patterns for `evm_phase` and `evm_cbs` keys are deleted alongside `kpis` per plan:T041 (`partial`)
