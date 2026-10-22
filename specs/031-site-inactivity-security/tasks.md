---
description: "Task list for Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening implementation"
---

# Tasks: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Input**: Design documents from `/specs/031-site-inactivity-security/`
- Spec: [spec.md](./spec.md)
- Plan: [plan.md](./plan.md)
- Research: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- API Contract: [contracts/daily-report-inactivity-api.md](./contracts/daily-report-inactivity-api.md)
- UI Contract: [contracts/daily-report-inactivity-ui.md](./contracts/daily-report-inactivity-ui.md)
- Quickstart & Verification: [quickstart.md](./quickstart.md)

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Backend invariants and the by-date permission rule are already implemented with passing tests (research R1). This is brownfield convergence: the residual scope's new coverage (guard-predicate unit tests, bilingual guard E2E, incremental edge-case backend tests) must be written and observed to FAIL against the current copy/keys before the alignment tasks land.

**Character of work**: NO new migrations, NO permission changes, NO model/serializer/aggregation behavior changes — research R1 verified those chains exist and pass. Remaining work is automated verification of existing invariants plus copy/key/label alignment and browser evidence.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- Include exact file paths in descriptions; quote verbatim constraints from data-model.md where applicable

## Path Conventions

- Backend (Django 4.2 + DRF): `apps/api/core/`
- Frontend (React Router 7 + Vite): `apps/web/src/`
- End-to-End Tests (Playwright): `e2e/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test environment readiness and baseline verification

- [X] T001 Verify backend test database connectivity and pytest configuration in `apps/api/core/pytest.ini` against PostgreSQL port 5433 and Redis port 6379 (start `sudo pg_ctlcluster 16 main start` and `sudo redis-server /etc/redis/redis.conf --daemonize yes` if stopped)
- [X] T002 [P] Verify frontend typecheck (`pnpm typecheck`) and node test harness (`node --test --experimental-strip-types`) run cleanly on the current tree

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the existing invariance chain before any residual alignment work depends on it

**⚠️ CRITICAL**: This feature changes no schema, permissions, or validation behavior. The existing chains documented in research R1 must be confirmed passing before residual work begins, so failures found here are reported and fixed before story work proceeds.

- [X] T003 [P] Run the existing inactivity-reason test modules `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` (inactivity validation, PDF weather/inactivity tests) and record evidence for FR-001/FR-002/FR-003/FR-010: five approved reason values accepted, unknown strings rejected, code `inactivity_reason_required` attached to `inactivity_reason`, active clears reason, submit/review/approve rechecks, reconciliation preserves/clears reason
- [X] T004 [P] Run `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py` and record evidence for FR-011/FR-012: viewer POST `daily-reports/by-date/` → 403 with no record created, viewer GET existing → 200, GET missing date → 404, editor POST succeeds; confirm `apps/api/core/field_reports/ENDPOINTS.md` lines documenting `daily-reports/by-date/` POST → `edit_reports` and GET → `view_reports` match the implementation

**Checkpoint**: Existing invariants confirmed green. Residual copy/label/e2e work can now proceed per story.

---

## Phase 3: User Story 1 - Record a standard inactivity reason when the site is closed (Priority: P1) 🎯 MVP

**Goal**: Closure-reason cycle is fully verified: dynamic selector showing exactly the five localized reasons in both editable surfaces (header + summary metadata editor), conditional validation failures with localized guidance, active-state clearing, and PDF parity — with label sourcing moved to the locale catalogs (FR-004/FR-005).

**Independent Test**: Mark a report inactive without a reason (observe inline `errors.inactivity_reason_required` rejection and no API write), cycle through each of the five reasons in Persian and English and observe catalog-driven option labels and readback, switch back to active (selector hides, reason cleared, save succeeds), and confirm the active-state PDF contains no reason text.

**Character**: US1 has one code task only (label source); its tests are evidence-first against existing behavior, with one incremental edge-case addition.

### Tests for User Story 1 ⚠️

> **NOTE: Write these FIRST. The extend-test cases below target documented edge cases not yet covered by the existing suite; they must FAIL (or be absent) before T006 lands where they exercise label sourcing, and behave independently otherwise.**

- [X] T005 [P] [US1] Extend `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` with partial-update edge-case tests: (a) stored inactive-reasoned report receives a PATCH changing only `site_status` to `inactive` without sending `inactivity_reason` → passes using the stored reason, (b) stored inactive-reasoned report receives a PATCH changing only `inactivity_reason` → invalid new value rejected with `inactivity_reason_required`, valid new value accepted (data-model §2 effective-state rules 1–2), (c) active-state clearing of a stale reason on partial update (SC-003)
- [X] T006 [US1] Move the shared option-label source to the locale catalogs: keep `INACTIVITY_REASONS` value list in `apps/web/src/app/lib/api/daily-reports.ts` as the single ordered value source, and render the option labels in `apps/web/src/components/daily_reports/ReportHeader.tsx` and `apps/web/src/app/routes/daily-report-view.tsx` (summary metadata editor) through `dailyReports.inactivityReasons.{value}` from `apps/web/src/app/locales/fa.json` and `en.json` — values stay language-independent ("Labels come from both `fa` and `en` locale catalogs", FR-004/FR-005; "Reuse a single ordered metadata source", UI contract §2). Extend the existing E2E in `e2e/tests/daily-report-header-weather.spec.ts` ("inactive site status requires inactivity reason in metadata editor") to assert exactly five options rendered with catalog-driven visible labels per locale project

**Checkpoint**: At this point User Story 1 is independently verifiable: validation chain (existing) + catalog-driven labels (new) + edge-case tests (new) pass.

---

## Phase 4: User Story 2 - Guard positive execution volumes on a closed day (Priority: P2)

**Goal**: The inactive-day confirmation dialog emits the approved copy from both locale catalogs, with a fixed locale-key lookup and localized title/buttons; confirm proceeds and cancel aborts; the predicate triggers only for strictly positive quantities on active=false reports (FR-008/FR-009 + UI contract §3).

**Independent Test**: With an inactive report: create a positive-quantity row (dialog appears with approved fa text; confirm saves; edit another positive row; cancel keeps entry and saves nothing); with zero/blank quantity and with an active report (no dialog). Repeat the dialog flow in English.

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL before T009/T010) ⚠️

- [X] T007 [P] [US2] Write failing unit tests in `apps/web/src/app/lib/__tests__/activityGuard.test.ts` asserting: (a) `shouldWarnInactiveSiteActivity` triggers only when site status is `inactive` and quantity is a numeric value strictly `> 0` (zero, blank, null, undefined, NaN never trigger — data-model §3), (b) `INACTIVE_ACTIVITY_WARNING_FA` equals the approved text «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟» verbatim, (c) `INACTIVE_ACTIVITY_WARNING_EN` equals the approved English equivalent, (d) the fa/en constants equal the `dailyReports.inactiveSiteActivityWarning` values imported from `apps/web/src/app/locales/fa.json` and `en.json` (catalog consistency, UI contract §3)
- [X] T008 [P] [US2] Write failing E2E tests in `e2e/tests/daily-report-inactivity-guard.spec.ts` (mocked API per existing E2E conventions; run `chromium-desktop` and `mobile-chrome` only, keep the standard `testInfo.project.name === "pwa-offline"` skip guard): inactive + positive-quantity row → `inactive-activity-confirm-dialog` visible with approved copy; `inactive-activity-confirm-btn` → row saved; `inactive-activity-cancel-btn` → no write and in-progress entry retained; zero/blank quantity and active-site positive-quantity rows → dialog absent; Persian and English projects assert localized dialog body, title, and button labels (UI contract §3, §4)

### Implementation for User Story 2

- [X] T009 [US2] Align the guard copy constants in `apps/web/src/components/daily_reports/activity-guard.ts`: `INACTIVE_ACTIVITY_WARNING_FA` → «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟» and the approved English equivalent for `INACTIVE_ACTIVITY_WARNING_EN` (approved text per PROMPT-03 FR-008; keeps exporting `shouldWarnInactiveSiteActivity` unchanged)
- [X] T010 [US2] Fix the locale-key lookup and localize dialog chrome in `apps/web/src/components/daily_reports/ActivityTab.tsx`: request the catalog key `dailyReports.inactiveSiteActivityWarning` (currently the component requests the non-existent `dailyReports.inactiveActivityWarning`, so the hardcoded fallback always wins — research R2), add the missing key `dailyReports.inactiveActivityDialogTitle` to `apps/web/src/app/locales/fa.json` and `en.json` with an approved bilingual title (replacing the inline `تأیید ثبت کارکرد در روز تعطیل`), localize the footer buttons through existing `dailyReports.confirmActivity` / `dailyReports.cancelActivity` keys, and keep `TESTID`s `inactive-activity-confirm-dialog`, `inactive-activity-confirm-btn`, `inactive-activity-cancel-btn` stable (UI contract §3, §5). Confirm dialog accessibility per UI contract §4 (title/description association, keyboard-operable buttons, focus return after cancel)

**Checkpoint**: User Story 2 independently verifiable: unit tests green, bilingual E2E green, copy equals approved text in both catalogs and constants.

---

## Phase 5: User Story 3 - Restrict daily-report creation to editors who can edit reports (Priority: P1)

**Goal**: The by-date permission matrix is verified on the current tree and its documentation matches; no code changes expected (FR-011/FR-012 already implemented with dedicated tests — research R1/R4).

**Independent Test**: Run the permission test module and confirm viewer-denied POST, viewer-allowed GET, and editor-allowed POST; grep ENDPOINTS.md.

### Verification for User Story 3

- [X] T011 [P] [US3] Verify and document the permission evidence: run `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py -v` capturing the 403-for-viewer and 200/404-read outcomes for `POST`/`GET /daily-reports/by-date/`, confirm no viewer-triggered record exists after denial (FR-011 acceptance scenario 1), and confirm `apps/api/core/field_reports/ENDPOINTS.md` permission-table wording (POST → `edit_reports`, GET → `view_reports`) — record evidence in the verification report; make no permission code change

**Checkpoint**: US3 evidence recorded with zero code delta.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Seeds hygiene, full regression, documentation parity, and final verification evidence

- [X] T012 [P] Verify dev seeds use only approved reason values in `apps/api/core/projects/seeds/full_project.py` (any inactive sample daily report names one of `weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, `safety_incident`; active samples carry `""`); fix violations if found; verify `apps/api/core/field_reports/ENDPOINTS.md` documentation wording matches the final copy state
- [X] T013 Run full backend regression: `cd apps/api/core && set -a && source ../../../.env && set +a && ../.venv/bin/python -m pytest field_reports/tests sub_reports/tests -q` and `../.venv/bin/python manage.py verify_blueprint_schema` (40/40 blueprint tables, no schema change expected)
- [X] T014 [P] Run frontend typecheck `pnpm typecheck` and node unit tests `node --test --experimental-strip-types apps/web/src/app/lib/__tests__/offlineDB.test.ts apps/web/src/app/lib/__tests__/temperatureValidation.test.ts apps/web/src/app/lib/__tests__/activityGuard.test.ts`
- [X] T015 Run the full new E2E spec `pnpm exec playwright test e2e/tests/daily-report-inactivity-guard.spec.ts` plus the inactive-sites E2E in `e2e/tests/daily-report-header-weather.spec.ts` across `chromium-desktop` and `mobile-chrome` projects, confirming all suites exit 0 and the `pwa-offline` project is skipped with the standard guard ("Requires the dev server")
- [X] T016 Execute the quickstart verification workflow per `specs/031-site-inactivity-security/quickstart.md` and compile the final verification evidence report naming each evidence category used (backend pytest / migration-schema checks / frontend typecheck / node unit / browser E2E / PDF extraction / localization grep), per Constitution Principle VI

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (invariants must be proven green)
- **User Stories (Phase 3 + 4 + 5)**: All depend on Phase 2; US1, US2, US3 are independent of each other
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent — existing validation chain + one label-source task + edge-case tests
- **User Story 2 (P2)**: Independent — copy/key alignment preceded by its own failing tests (T007, T008) then T009, T010
- **User Story 3 (P1)**: Independent — evidence-only; can be recorded at any time after Phase 2

### Within Each User Story

1. Tests written FIRST (US1 edge cases, US2 TDD pair) and observed to FAIL where the residual change is the enabling delta
2. Implementation before integration verification
3. E2E evidence after implementation tasks complete

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel
- **Phase 2**: T003 and T004 can run in parallel
- **Phase 3 (US1)**: T005 can run in parallel with T006's file work only if T006 hasn't already localized labels; otherwise T005 then T006
- **Phase 4 (US2)**: T007 and T008 can run in parallel; T009 and T010 touch different files after tests exist
- **Phase 6**: T012 and T014 can run in parallel; T013 after code tasks; T015 after T010; T016 last

---

## Parallel Example: User Story 2

```bash
# Launch failing tests for User Story 2 in parallel:
Task T007: "Write failing unit tests in apps/web/src/app/lib/__tests__/activityGuard.test.ts"
Task T008: "Write failing E2E tests in e2e/tests/daily-report-inactivity-guard.spec.ts"

# Then implement in order:
Task T009: "Align guard copy constants in apps/web/src/components/daily_reports/activity-guard.ts"
Task T010: "Fix locale-key lookup and localize dialog chrome in apps/web/src/components/daily_reports/ActivityTab.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — proves existing invariants)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the closure-reason cycle end-to-end in both locales
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → evidence baseline
2. US1 → closure cycle verified → Deploy/Demo (MVP!)
3. US2 → guard copy/key alignment + bilingual browser evidence → Deploy/Demo
4. US3 → permission evidence recorded (no code delta)
5. Polish → full regression + verification report

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify failing tests fail before implementing (TDD for US2; evidence-first for US1/US3)
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
- Avoid: schema changes, permission changes, serializer/aggregation behavior changes, duplicate label sources in components (reuse `INACTIVITY_REASONS` + catalogs)
