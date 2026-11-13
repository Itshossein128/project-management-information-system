# Quickstart: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Feature Directory**: `specs/056-a7-p6-delivery-acceptance`  
**Direct Audit IDs**: `D03`, `D04`  
**Contract Reference**: [`contracts/delivery-acceptance.md`](./contracts/delivery-acceptance.md)  
**Data Model Reference**: [`data-model.md`](./data-model.md)

---

## 1. Record Candidate Version Identity

Before running any acceptance check, record the exact repository commit, working-tree status, and reference file digest from `/home/hossein/Desktop/projects/building-management`:

```bash
git rev-parse HEAD
git status --short
sha256sum real-data/plan.mpp
```

- Expected `real-data/plan.mpp` SHA-256: `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553` (`777216` bytes).
- Never modify `output/a7-requirements-2026-11-10/requirements.json` or `report.md`.
- Keep Django pinned to `4.2.11` (`apps/api/.venv/bin/python -c "import django; assert django.__version__ == '4.2.11'"`).

---

## 2. Verify Predecessor Gates (`051`–`055`)

Verify that all 5 predecessor directories (`specs/051-a7-p1-project-reference` through `specs/055-a7-p5-import-operations`) contain `spec.md`, `handoff.md`, `evidence/verification.md`, and `traceability.md`, and that P5's `T049` second-operator reproduction is recorded in `specs/055-a7-p5-import-operations/evidence/reproduction.md`.

---

## 3. Execute Integrated Backend & Reference Reconciliation Suite (`POS-01`–`POS-10`, `NEG-01`–`NEG-14`)

Ensure native PostgreSQL (`:5433`) and Redis (`:6379`) are running:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Run the integrated P1–P6 backend acceptance and non-regression suite on an isolated PostgreSQL test database:

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  projects/tests/test_project_registration_api.py \
  projects/tests/test_charter_lifecycle.py \
  projects/tests/test_project_lifecycle.py \
  projects/tests/test_wbs_api.py \
  projects/tests/test_wbs_move_api.py \
  projects/tests/test_wbs_DragDrop_integration.py \
  project_templates/tests.py \
  schedule/tests/test_a7_p2_import_safety.py \
  schedule/tests/test_a7_p3_import_fidelity.py \
  schedule/tests/test_a7_p4_import_experience.py \
  schedule/tests/test_a7_p5_import_api.py \
  schedule/tests/test_a7_p5_lifecycle.py \
  schedule/tests/test_a7_p5_migrations.py \
  schedule/tests/test_a7_p5_preparation.py \
  schedule/tests/test_a7_p5_recovery.py \
  schedule/tests/test_a7_p5_retention.py \
  schedule/tests/test_a7_p5_artifact_privacy.py \
  schedule/tests/test_a7_p5_runtime_preflight.py \
  schedule/tests/test_a7_p5_runtime_manifest.py \
  schedule/tests/test_a7_p6_delivery_acceptance.py \
  --junitxml=../../../specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml \
  -q
```

---

## 4. Verify Real Worker & Containment Continuity (`OPS-04`)

Confirm that the schedule runtime source tree matches the P5 acceptance manifest (`specs/055-a7-p5-import-operations/evidence/runtime/manifest.json` and `independent-complete-matrix.json`, schedule-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`, image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`). If any runtime file under `apps/api/core/schedule/` changed, re-run `ops/a7-p5/run-acceptance.sh` against the isolated `a7p5-import` Compose stack.

---

## 5. Execute Real Browser End-to-End Acceptance Suite (`POS`, `NEG`, `OPS-01`–`OPS-03`)

Run the Playwright end-to-end acceptance suite against the live API and web server (covering positive reference journey, P1 carry-over complete/undo-complete and archive/restore browser clicks, P4 carry-over account/project-switch observation, negative/adverse UX, keyboard navigation, and bilingual `fa` RTL / `en` LTR at `1280x800` and `390x844`):

```bash
pnpm exec playwright test e2e/tests/a7-p6-delivery-acceptance.spec.ts
pnpm typecheck
```

---

## 6. Validate the Employer Delivery Package (`D04`)

Run the deterministic package validator to verify that all 56 audit dispositions, 28 scenario records, reference schedule reconciliation totals, 5 role personas, secret-scan rules, and unsigned employer sign-off fields satisfy [`data-model.md`](./data-model.md) and [`contracts/delivery-acceptance.md`](./contracts/delivery-acceptance.md):

```bash
python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py
```

Expected exit code: `0` (`technical_readiness = "ready_for_acceptance"`, `employer_decision = "pending"`, `0` exposed secrets).
