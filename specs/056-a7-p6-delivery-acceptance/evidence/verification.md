# Verification Evidence: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Phase**: `A.7-P6` (`specs/056-a7-p6-delivery-acceptance`)  
**Direct Audit IDs**: `D03`, `D04` (plus integrated closure of all 56 A.7 audit items `P01`–`P11`, `W01`–`W07`, `M01`–`M04`, `S01`–`S08`, `I01`–`I22`, `D01`–`D04`)  
**Stage**: Implementation & Acceptance Verification Complete (`/speckit-implement` / `/speckit-converge`)  
**Date**: 2026-11-13

## 1. Knowledge & Graph Context Verification

1. **Knowledge CLI Context Lookup**:
   - Checked `python3 scripts/knowledge/cli.py status` and refreshed `.knowledge/index.sqlite3` via `python3 scripts/knowledge/cli.py index` (`"mode": "lexical"`).
   - Ran `python3 scripts/knowledge/cli.py context "/speckit-specify @[output/a7-requirements-2026-11-10/speckit-prompts/06-delivery-acceptance.md]" --lexical` and `python3 scripts/knowledge/cli.py context "$(cat output/a7-requirements-2026-11-10/speckit-prompts/06-delivery-acceptance.md)" --lexical --format markdown`.
   - Result: `fresh: true`, `abstained: false`, `requires_clarification: false`.
2. **Graphify Query**:
   - Executed MCP `graphify:query_graph` with question: `"project lifecycle charter change request wbs template schedule baseline msp p6 import acceptance"` (2,382 connected nodes traversed).

## 2. Predecessor Gate Audit (`051`–`055`)

| Phase | Directory | Inspected Files | Gate Status |
| --- | --- | --- | --- |
| `A.7-P1` | `specs/051-a7-p1-project-reference` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md` | **Ready & Verified**: All P1 lifecycle, charter, change-request, reference catalog, and WBS tests pass; carry-over browser clicks (`complete` → `undo-complete` and `archive` → `restore`) verified in P6 Playwright E2E. |
| `A.7-P2` | `specs/052-a7-p2-import-safety` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md` | **Ready & Verified**: Standalone `traceability.md` backfilled (`T003`); all 49 P2 import safety, idempotency, replacement guard, and rollback tests pass. |
| `A.7-P3` | `specs/053-a7-p3-import-fidelity` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md` | **Ready & Verified**: Standalone `traceability.md` backfilled (`T004`); `T034` stakeholder policy verified against `real-data/plan.mpp` (`6` WBS, `72` activities, `72` relationships). |
| `A.7-P4` | `specs/054-a7-p4-import-experience` | `spec.md`, `handoff.md`, `traceability.md`, `evidence/verification.md` | **Ready & Verified**: All P4 wizard, error-code, and bilingual UX tests pass; carry-over live account-switch and project-switch browser isolation verified in P6 Playwright E2E. |
| `A.7-P5` | `specs/055-a7-p5-import-operations` | `spec.md`, `handoff.md`, `tasks.md`, `traceability.md`, `evidence/verification.md`, `evidence/reproduction.md` | **Ready & Verified (`T049` Closed)**: Independent second-operator subagent (`conversationId: de389ce3-d1d2-4991-b379-f9c719ecfb7d`) completed clean reproduction of `quickstart.md` on candidate image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` (13/13 runtime matrix groups, `check-broker-outage.py`, `check-concurrent-delivery.py`, 4/4 Playwright retry tests, `maintain_import_jobs`, `makemigrations --check`, 110/110 `check-host.sh`, `pnpm typecheck`). All 64/64 P5 tasks (`T001`–`T064`) are `[x]`. |

## 3. Executed Verification Suites & Evidence Artifacts

### 3.1 Combined P1–P5 Non-Regression Backend Suite (`T008`)

- **Command**:
  ```bash
  export TEST_DATABASE_NAME="test_a7p5_p6_regression_$(date +%s)_$$"
  export AUDIT_LOG_ASYNC=false CELERY_TASK_ALWAYS_EAGER=true
  export IMPORT_CGROUP_ROOT=/sys/fs/cgroup/system.slice/a7p5-containment.service
  export A7P5_CGROUP_HOST_ROOT="$IMPORT_CGROUP_ROOT"
  export IMPORT_SCRATCH_ROOT=/run/a7p5-host-regression
  sudo -n --preserve-env=DATABASE_URL,REDIS_URL,TEST_DATABASE_NAME,AUDIT_LOG_ASYNC,CELERY_TASK_ALWAYS_EAGER,IMPORT_CGROUP_ROOT,A7P5_CGROUP_HOST_ROOT,IMPORT_SCRATCH_ROOT env PYTHONDONTWRITEBYTECODE=1 \
    apps/api/.venv/bin/python -m pytest -c apps/api/core/pytest.ini \
    apps/api/core/projects/tests/test_a7_p1_reference_project.py \
    apps/api/core/projects/tests/test_project_status_undo.py \
    apps/api/core/projects/tests/test_project_archive_restore.py \
    apps/api/core/projects/tests/test_project_registration_lifecycle.py \
    apps/api/core/projects/tests/test_project_contractor_ref.py \
    apps/api/core/schedule/tests/test_a7_p2_import_safety.py \
    apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py \
    apps/api/core/schedule/tests/test_a7_p4_import_experience.py \
    apps/api/core/schedule/tests/test_a7_p5_*.py \
    apps/api/core/schedule/tests/test_msp_import.py \
    apps/api/core/schedule/tests/test_p6_import.py \
    apps/api/core/schedule/tests/test_mpp_import.py \
    apps/api/core/schedule/tests/test_mpp_equivalence.py \
    -q --tb=short -p no:cacheprovider \
    --junitxml=specs/056-a7-p6-delivery-acceptance/evidence/p1-p5-regression-junit.xml
  ```
- **Result**: `168 passed, 0 failed, 0 skipped in 170.91s (0:02:50)`
- **Evidence**: `specs/056-a7-p6-delivery-acceptance/evidence/p1-p5-regression-junit.xml`

### 3.2 Integrated P6 Positive & Negative Acceptance Suite (`T011`, `T013`, `T014`)

- **Command**:
  ```bash
  apps/api/.venv/bin/python -m pytest -c apps/api/core/pytest.ini \
    apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py \
    --junitxml=specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml
  ```
- **Result**: `2 passed in 87.19s (0:01:27)`
  - `test_a7_p6_positive_reference_journey_pos01_to_pos10`: `PASSED` (covers `POS-01` through `POS-10`, including `real-data/plan.mpp` 6 WBS / 72 activities / 72 relations / 1 initial baseline reconciliation, repeat append idempotency, safe replacement guard, 4-way dates/Gantt/CPM validity gate, and full `suspend` ↔ `resume`, `complete` → `undo-completion`, `archive` → `restore` lifecycle transitions with 100% data preservation).
  - `test_a7_p6_negative_adverse_concurrency_and_access_boundaries_neg01_to_neg14`: `PASSED` (covers `NEG-01` through `NEG-14` across 5 separated role personas with zero unintended data mutations).
- **Evidence**: `specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml`

### 3.3 Real-Stack Playwright Browser E2E Acceptance Suite (`T015`, `T016`)

- **Command**:
  ```bash
  A7P6_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-p6-auth.json" \
    pnpm exec playwright test --config=e2e/playwright.a7-p6.config.ts
  ```
- **Result**: `6 passed (41.2s)`
  1. `lifecycle complete -> undo_completion and archive -> restore in browser (POS-10)`: `PASSED` (`3.5s`)
  2. `schedule import wizard, invalid upload recovery, and responsive layout (fa 1280px) (POS-05, POS-06, NEG-06, NEG-07, OPS-01..03)`: `PASSED` (`9.1s`)
  3. `schedule import wizard, invalid upload recovery, and responsive layout (en 1280px) (POS-05, POS-06, NEG-06, NEG-07, OPS-01..03)`: `PASSED` (`9.1s`)
  4. `schedule import wizard, invalid upload recovery, and responsive layout (fa 390px) (POS-05, POS-06, NEG-06, NEG-07, OPS-01..03)`: `PASSED` (`8.5s`)
  5. `schedule import wizard, invalid upload recovery, and responsive layout (en 390px) (POS-05, POS-06, NEG-06, NEG-07, OPS-01..03)`: `PASSED` (`8.3s`)
  6. `project-switch and viewer account-switch isolation in browser (I10, NEG-11, NEG-12)`: `PASSED` (`1.9s`)
- **Screenshots Captured**:
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/lifecycle-completed-undo-fa-1280.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/lifecycle-archived-restore-fa-1280.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-fa-1280.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-en-1280.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-fa-390.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/import-en-390.png`
  - `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/viewer-readonly-fa-1280.png`

### 3.4 Frontend Typecheck (`T015`)

- **Command**: `pnpm typecheck` (`react-router typegen && tsc`)
- **Result**: Exited with code `0` (`0` errors).

### 3.5 Deterministic Delivery Package Validator (`T019`)

- **Command**: `python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py`
- **Output**:
  ```json
  {
    "status": "passed",
    "audit_items_verified": 56,
    "scenarios_verified": 28,
    "reconciliation_fixtures_verified": 4,
    "secret_scan": "clean",
    "technical_readiness": "ready_for_acceptance",
    "employer_decision": "pending"
  }
  ```

## 4. Separation of Technical Readiness vs. Human Employer Sign-Off (`FR-009`)

- **Technical Readiness (`technical_readiness`)**: `ready_for_acceptance` — All 56 audit items (`P01`–`D04`) are `تأیید فنی` on the integrated candidate version, all 28 acceptance scenarios (`POS-01`–`POS-10`, `NEG-01`–`NEG-14`, `OPS-01`–`OPS-04`) have `technical_result = "pass"`, and `0` blocking defects remain open.
- **Human Employer Decision (`employer_decision`)**: `pending` — `employer_signer_role` and `employer_signed_at` in `evidence/package.json` and `evidence/minutes.md` are intentionally left blank for the employer representative's independent execution of `guide.md`.
