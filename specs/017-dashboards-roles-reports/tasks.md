# Tasks: Dashboards, Roles & Reports

**Input**: Design documents from `/specs/017-dashboards-roles-reports/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: Not TDD-gated (no user TDD request). Each story includes pytest coverage tasks matching `quickstart.md` / plan so SC evidence is collectible.

**Organization**: Phases by user story (US1–US4). Foundational = provenance helpers + SoD module + FR role constants used by all stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/017-dashboards-roles-reports"` and review `specs/017-dashboards-roles-reports/plan.md`
- [x] T002 [P] Inventory extension points in `apps/api/core/projects/kpi_service.py`, `apps/api/core/schedule/services/period_report_service.py`, `apps/api/core/permissions/constants.py`, approve paths in `apps/api/core/contracts/services/ipc_service.py` / `apps/api/core/projects/` change-request approve / `apps/api/core/workflow/services/instance_service.py` / `apps/api/core/hr/services/exception_service.py`, and UI dashboard routes; note gaps vs `specs/017-dashboards-roles-reports/research.md`

---

## Phase 2: Foundational — Provenance shape, SoD helper, FR roles (Blocking)

**Purpose**: Shared figure provenance helpers, `assert_not_self_final_approve`, and FR role constants/seeds. Blocks trustworthy pack/drill/SoD work.

**⚠️ CRITICAL**: No story may invent KPI zeros for disabled capabilities, or soft-warn-only on material final approve.

- [x] T003 [P] Add `permissions/sod.py` with `assert_not_self_final_approve(created_by_id, actor)` raising `CodedValidationError` `sod_self_approve` when ids equal (non-null); document superuser-only break-glass in module docstring per `specs/017-dashboards-roles-reports/contracts/sod-and-roles.md`
- [x] T004 [P] Cover SoD helper in `apps/api/core/permissions/tests/test_sod.py` (same-user raises; different user passes; null creator passes)
- [x] T005 Add FR system roles to `apps/api/core/permissions/constants.py` / seed path: `executive_approver`, `project_controls`, `site_specialist`, `supervisor_consultant`, and `hr_officer` if missing; map permissions per `specs/017-dashboards-roles-reports/data-model.md` Roles table; keep existing role codes; cover catalog presence in `apps/api/core/permissions/tests/test_fr_rpt_roles.py`
- [x] T006 Add shared figure DTO helpers (fields: `figure_key`, `source_type`, `source_id`, `source_path`, `source_approved`, `last_updated_at`, `value` nullable, `status` ∈ {`ok`,`inactive`,`unavailable`}, `label_unapproved` bool) in `apps/api/core/projects/services/figure_provenance.py` matching progress-report provenance shape
- [x] T007 Ensure role seed/migration runs so new system roles exist in DB (extend existing role seed command or data migration under `apps/api/core/permissions/` or `master_data/` as used today)

**Checkpoint**: SoD helper + FR roles + provenance helpers ready

---

## Phase 3: User Story 1 — Trace dashboard figure to source (Priority: P1) 🎯 MVP

**Goal**: Every KPI/pack figure supports drill to source records with approval status and last-updated; unapproved data excluded from approved-only aggregates unless labeled (FR-001–002, FR-016; SC-001)

**Independent Test**: Open budget/progress KPI → drill → constituent rows show approval + timestamps; approved-only report excludes drafts

- [x] T008 [US1] Enrich `build_project_kpis` in `apps/api/core/projects/kpi_service.py` to emit additive `figures[]` with `figure_key`, provenance fields, `drill.href`, and `status=inactive`/`value=null` when dependent `ProjectCapabilitySetting` is disabled (never fabricate success zero) per `contracts/kpi-drillthrough.md`
- [x] T009 [US1] Implement `apps/api/core/projects/services/kpi_drill_service.py` listing drill rows (`id`, `display`, `amount`/`qty`, `approval_status`, `approved`, `last_updated_at`, `source_path`) for known `figure_key`s (at least EVM/progress + one finance/commitment or budget figure); unknown key → 404 `unknown_figure_key`
- [x] T010 [US1] Wire `GET .../kpis/drill/` in `apps/api/core/projects/` views/urls with `view_dashboard` + membership; default `approved_only=true`
- [x] T011 [US1] Add pytest in `apps/api/core/projects/tests/test_kpi_drillthrough.py`: figures present; drill returns approved+timestamp; inactive capability figure null/inactive; unknown figure_key 404; approved_only excludes unapproved constituents
- [x] T012 [US1] Frontend: `apps/web/src/app/lib/api/dashboards.ts` KPI+drill clients; `apps/web/src/components/dashboard/FigureDrillDrawer.tsx`; wire click-to-drill on project dashboard surface (`apps/web/src/app/routes/project-dashboard.tsx` or equivalent existing route); i18n in `apps/web/src/app/locales/en.json` and `fa.json`

**Checkpoint**: US1 independently testable — drill-through MVP

---

## Phase 4: User Story 2 — Role-based dashboard & segregation of duties (Priority: P1)

**Goal**: Packs filtered by role + allowed projects; hard SoD on material final approve; viewer read-only for workflow (FR-003, FR-013–014; SC-002–003)

**Independent Test**: Finance member of A+B only does not see C on portfolio dashboard; creator self-approve → `sod_self_approve`

- [x] T013 [US2] Implement `apps/api/core/projects/services/dashboard_pack_service.py` building packs (`executive`, `project_manager`, `finance`, `project_controls`) from member roles; indicator groups per `data-model.md` catalog; project scope = membership only
- [x] T014 [US2] Wire `GET /api/v1/projects/{id}/dashboard/pack/` and `GET /api/v1/portfolio/dashboard/` in `apps/api/core/projects/` views/urls (portfolio under `portfolio_urls` if that is the existing pattern) per `contracts/role-dashboard-packs.md`
- [x] T015 [US2] Call `assert_not_self_final_approve` from final approve in `apps/api/core/contracts/services/ipc_service.py` (`approve_ipc`), project change-request approve service/views, `apps/api/core/workflow/services/instance_service.py` (final approve to `approved`), cost/payment final approve path(s) under `apps/api/core/cost_control/`, and harden `apps/api/core/hr/services/exception_service.py` approve from soft-warn to hard-block
- [x] T016 [US2] Pytest in `apps/api/core/projects/tests/test_role_dashboard_packs.py`: finance user portfolio omits non-member project; pack role filtering; viewer pack GET allowed without approve perms
- [x] T017 [US2] Pytest SoD integration: creator cannot final-approve own IPC (or change-request) in existing or new test module under `apps/api/core/contracts/tests/` / `apps/api/core/projects/tests/`; expect `400` `sod_self_approve`
- [x] T018 [US2] Frontend: portfolio/executive strip route `apps/web/src/app/routes/executive-dashboard.tsx` (or extend portfolio home); show role pack on project dashboard; register `routeVars.ts` / `routes` / `project-navigation.config.ts`; localize SoD error toast

**Checkpoint**: US2 independently testable — scoped packs + hard SoD

---

## Phase 5: User Story 3 — Standard reports & export metadata (Priority: P2)

**Goal**: Report catalog, shared filters, approved-only default, confidential redaction, immutable export versions with extraction date + filters (FR-010–012, FR-015–016; SC-004)

**Independent Test**: Export with two filters → metadata and download envelope include both + `extracted_at`

- [x] T019 [US3] Add `ReportExportVersion` model in `apps/api/core/projects/models.py` with fields: `report_type` string, `project` FK null for portfolio, `filters` JSON, `extracted_at` required, `extracted_by` FK User required, `approved_only` bool default true, `file_url` string, optional `payload_sha256`; immutable (no update API); migration `apps/api/core/projects/migrations/00xx_fr_rpt_report_export.py`
- [x] T020 [US3] Implement `apps/api/core/projects/services/report_export_service.py` + catalog registry wrapping at least: `weekly_progress`, `monthly_project`, `portfolio_summary` (or portfolio cash), `risk_issue`, `budget_variance` (stub OK if domain aggregate exists); shared filters `project`/`unit`/`date_from`/`date_to`/`contract`/`wbs`/`cbs`/`owner`/`status`; default `approved_only=true`; redact wage/contacts without permission
- [x] T021 [US3] Wire catalog/run/export/download endpoints per `contracts/standard-reports-export.md` in `apps/api/core/projects/` views/urls (+ portfolio catalog/export paths)
- [x] T022 [US3] Pytest in `apps/api/core/projects/tests/test_report_export_metadata.py`: export persists `extracted_at` + filters; download envelope includes them; `approved_only=true` excludes unapproved; confidential field redacted without `view_wage` where applicable
- [x] T023 [US3] Frontend: `apps/web/src/app/lib/api/standard-reports.ts`; route `apps/web/src/app/routes/project-standard-reports.tsx`; filters + export download; nav + i18n

**Checkpoint**: US3 independently testable — exports always carry metadata

---

## Phase 6: User Story 4 — Role dashboard packs expansion (Priority: P2)

**Goal**: Deliver executive, PM, finance (+ controls) packs with required indicator groups; inactive for disabled modules; HR/site and unit-manager stubs OK (FR-004–009; SC-006)

**Independent Test**: Each delivered pack shows its groups for eligible role; disabled module → inactive not zero

- [x] T024 [US4] Expand pack catalogs in `apps/api/core/projects/services/dashboard_pack_service.py` for executive / PM / finance / controls indicator groups listed in `spec.md` FR-004–007; wire available domain aggregates; missing modules → `status=inactive`
- [x] T025 [US4] Add stub pack entries for `hr_site` and `unit_manager` that return inactive/unavailable groups rather than fake zeros in `apps/api/core/projects/services/dashboard_pack_service.py`
- [x] T026 [US4] Extend `apps/api/core/projects/tests/test_role_dashboard_packs.py` for pack contents + SC-006 inactive behavior
- [x] T027 [US4] Frontend: render pack groups on `apps/web/src/app/routes/project-dashboard.tsx` and `apps/web/src/app/routes/executive-dashboard.tsx`; inactive badge/label via `en.json`/`fa.json`; no fabricated zero charts

**Checkpoint**: US4 independently testable — phase-1 pack set

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, UAT checklist, full quickstart verification

- [x] T028 [P] Update `apps/api/core/projects/ENDPOINTS.md` (and portfolio docs if separate) for kpis figures/drill, packs, reports catalog/export
- [x] T029 [P] Add UAT checklist markdown under `specs/017-dashboards-roles-reports/checklists/uat-sc005.md` covering PM, site, finance, controls primary scenarios (SC-005)
- [x] T030 Run full pytest set from `specs/017-dashboards-roles-reports/quickstart.md` and fix regressions
- [x] T031 [P] UI smoke on seeded data: `FigureDrillDrawer.tsx`, executive/portfolio pack scope, SoD error toast, `project-standard-reports.tsx` export metadata (fa/en)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: After Setup — **BLOCKS** all stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational — uses SoD + roles from Phase 2; packs may consume US1 figures when present
- **US3 (Phase 5)**: After Foundational — independent of packs; benefits from approved-only conventions in US1
- **US4 (Phase 6)**: After US1 figure keys exist (prefer after US1); expands US2 pack service
- **Polish (Phase 7)**: After desired stories

### User Story Dependencies

| Story | Depends on | Notes |
|-------|------------|-------|
| US1 Drill-through | Phase 2 | MVP |
| US2 Roles + SoD | Phase 2 | Parallel with US1 if staffed (different files) |
| US3 Reports/export | Phase 2 | Parallel-safe |
| US4 Pack expansion | US1 figures + US2 pack endpoint | Extends pack service |

### Parallel Opportunities

- T001–T002 setup parallel
- T003–T004 SoD helper + tests parallel with T005–T007 roles/provenance
- After Phase 2: US1 and US3 can proceed in parallel; US2 SoD wiring parallel to US1 UI
- US4 after US1/US2 pack skeleton

---

## Parallel Example: User Story 1

```bash
Task: "T008 enrich kpi_service figures in projects/kpi_service.py"
Task: "T009 kpi_drill_service.py"
# then T010 wire + T011 pytest + T012 UI
```

## Parallel Example: User Story 2

```bash
Task: "T015 wire SoD into ipc/workflow/change-request/hr approve services"
Task: "T013 dashboard_pack_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1–2  
2. Phase 3 US1 (figures + drill + UI drawer)  
3. **STOP and VALIDATE** SC-001  
4. Demo trustable KPI drill

### Incremental Delivery

1. Foundation  
2. US1 drill → US2 SoD + scoped packs → US3 exports → US4 pack expansion  
3. Polish + UAT checklist

### Parallel Team Strategy

1. Team completes Phase 1–2  
2. Dev A: US1; Dev B: US2 SoD + roles; Dev C: US3 exports  
3. US4 integrates pack catalogs once figure_keys stable

---

## Notes

- Dashboards remain read-only over domain SoR — do not create parallel fact tables
- Quote constraints from `data-model.md` (immutable export; inactive ≠ zero; hard SoD)
- Phase-1 packs: executive + PM + finance (+ controls); HR/site & unit-manager stubs OK
- Suggested MVP: **US1 only** after Phase 2

---

## Phase 8: Convergence

> Gaps found by `/speckit-converge` against current code vs `spec.md` / `plan.md` / prior tasks. Complete via `/speckit-implement`.

- [ ] T032 Expand executive pack indicator groups in `apps/api/core/projects/services/dashboard_pack_service.py` (and supporting `figure_key`s in `apps/api/core/projects/kpi_service.py` when upstream exists) to cover budget/forecast final cost, profitability, liquidity need, high risks, milestone delays, and overdue decisions per FR-004 / US4/AC1 (partial)
- [ ] T033 Expand project_manager pack figures for scope, milestones, unapproved daily reports, risks, open changes, contract status, and overdue actions per FR-005 / US4/AC2 (partial)
- [ ] T034 Expand project_controls pack figures for WBS, baseline, variances, finish forecast, and schedule data quality per FR-006 (partial)
- [ ] T035 Expand finance pack figures for commitment, payment, IPC, receivables, collections, and projected cash flow per FR-007 (partial)
- [ ] T036 Add missing standard report catalog types and builders in `apps/api/core/projects/services/report_export_service.py`: site daily, lookahead plan, stakeholder status, changes, procurement/contract status, and cash flow per FR-010 (missing)
- [ ] T037 Wire hard SoD (`assert_not_self_final_approve`) on commitment final approve and/or payment final-post path in `apps/api/core/cost_control/` (today `approve_commitment` and `create_payment` omit SoD) per FR-014 / T015 / US2/AC2 (partial)
- [ ] T038 Apply shared report filters (unit, contract, WBS/CBS, owner, status, period) inside each report builder rather than only declaring them in catalog metadata per FR-011 (partial)
- [ ] T039 Deepen confidential-field redaction for wage/contacts on report payloads (recursive where needed) and cover with pytest for `view_wage` gate per FR-015 / US3 (partial)
- [ ] T040 Set KPI figure `source_approved` / `label_unapproved` from constituent approval state (stop hard-coding `source_approved=True` in `kpi_service._build_kpi_figures`) and honor unapproved labeling on standard reports per FR-016 / US1/AC2 (partial)
- [ ] T041 Review or document `apps/api/core/projects/services/` package layout vs prior `projects/services.py` module as intentional FR-RPT structure (justify keep) per plan touch-points (unrequested)
