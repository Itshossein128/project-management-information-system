# Validation Guide: Ranking Reference Verification

The sibling reference suite and report option are implemented. Final actual results are linked in [validation.md](validation.md); arithmetic, fresh backend and verified reused browser evidence are distinct. Passing document validation alone is not product acceptance.

## Preconditions

Confirm cwd, actual Git branch `develop`, `.specify/feature.json` selecting 025, dirty work and source hashes. Preserve all earlier source/spec/evidence files and the original DOCX/Markdown. Use `apps/api/.venv` for tests and root `.venv` only for Spec Kit. Do not install full requirements-dev, upgrade Django, reset a database or run production actions.

```bash
cd /home/hossein/Desktop/projects/building-management
git branch --show-current
cat .specify/feature.json
apps/api/.venv/bin/python -c 'import sys,django,pytest; print(sys.version.split()[0],django.get_version(),pytest.__version__)'
```

## Test-first verification slices

1. Define literal identities/cases and the report contract. Add discrepancy tests before each helper behavior: altered source/fence/callable, missing/duplicate name, wrong tie order, non-finite/incorrect score, failure/unrun status. Observe meaningful behavioral red and minimally implement the rejection/comparison/report behavior. Import failures are not behavioral red.
2. Add source equality and published-case checks, then bounded parity/rejection/representation checks. Existing correct engines can immediately pass as regressions; do not damage formulas or authoritative documents to manufacture red.
3. If a product mismatch occurs, save exact input/expected/observed red, establish the governing requirement, minimally fix it, and rerun affected tests. Do not rewrite the sample, lower the tolerance or label an unexpected failure intentional to get green.

## Pure reference checks

Load local settings without printing secrets. This suite must not request DB fixtures or connect/unblock the database; a sibling placement avoids product test catalog initialization. Existing settings still require configured environment values.

```bash
cd /home/hossein/Desktop/projects/building-management
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
mkdir -p specs/025-decision-ranking-reference/evidence
cd /home/hossein/Desktop/projects/building-management/apps/api/core
../.venv/bin/python -m pytest decision_support/reference_tests -q --ranking-reference-report=/home/hossein/Desktop/projects/building-management/specs/025-decision-ranking-reference/validation-reference.json
```

Expected: exact authenticated Markdown/DOCX equality; all required bounded families match analytical expectations and each other; exact order/finite/tolerance assertions; rejected inputs show appropriate product paths; conversion differences classified; no DB access/input mutations. See [reference contract](contracts/reference-verification.md) and [data model](data-model.md). Retain actual stdout/stderr/exit separately; report writing is not a replacement for pytest success.

## Product regression evidence

Existing DB-backed tests require native PostgreSQL (normally 5433) and normal local API/browser operation requires Redis (6379). Verify existing services; do not reset data. Use `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true` for normal local tests/server. Use pytest, not manage.py test.

```bash
cd /home/hossein/Desktop/projects/building-management
pg_isready -p 5433
redis-cli ping
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
cd /home/hossein/Desktop/projects/building-management/apps/api/core
../.venv/bin/python -m pytest --reuse-db decision_support/tests/test_saw_service.py decision_support/tests/test_topsis_service.py decision_support/tests/test_validators.py decision_support/tests/test_saw_api.py decision_support/tests/test_topsis_api.py decision_support/tests/test_runs_immutability.py decision_support/tests/test_execution_records.py decision_support/tests/test_execution_records_access.py -q
```

Expected: independent real computations and records, no unrequested method, unchanged manual weights/history, rejected input with located issues, denied unauthorized reads/writes. This run accesses the test DB; distinguish it from pure reference proof.

## Bilingual interaction evidence

If unchanged prior browser observations meet the [reuse contract](contracts/existing-product-boundary.md), record their original artifacts, scope and matching source hashes rather than claiming a fresh run. If not, or if any interaction changed, run applicable existing real EN/FA cases. Start/reuse `pnpm dev:api` and `pnpm dev:web` separately; do not use Docker-dependent `pnpm dev`.

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/decision-execution-records.spec.ts --project chromium-desktop --trace on --grep 'frozen named ranking review|independent disagreement ties|real viewer access keyboard|named ranking feedback'
```

Expected: both language variants run with named inputs and results, exact-tie/independent historical presentation, read-only review, keyboard selection, viewer/revoked access and located feedback. Retain trace attachments and count actual selected/passed/skipped cases. Missing matches do not count as acceptance. Fixture-created historical results prove presentation only; pair them with backend computation checks. This filtered command excludes timing cases that rewrite old feature evidence.

## Final reconciliation and scope checks

Create feature-local `differences.md`, `validation.md`, command/exit evidence and strict JSON report. Reconcile FR-001–FR-014, SC-001–SC-006 and all 16 scenarios, with actual observed outcomes or explicit unrun status. Include relevant dirty source hashes, reference identities, versions and provenance. Inspect the preserved sample's input/output documentation, attribution and limitations separately from numeric proof. Do not put credentials or environment secrets in artifacts.

```bash
cd /home/hossein/Desktop/projects/building-management
apps/api/.venv/bin/python -m json.tool specs/025-decision-ranking-reference/validation-reference.json > /dev/null
git diff --check
```

Verify report strictness and completeness using the report contract, not json.tool alone. Compare all protected baseline files before completion. No model/runtime/UI changes are expected; schema/type/locale checks are triggered by actual affected changes, not claimed from an old run. Any fresh typecheck must report its actual result and preserve unrelated baseline errors. No commit, deployment or full-module human sign-off is included.

## Implemented evidence

Use the commands above. The required-check registry includes falsification tests even when an explicit file selection omits them; omitted tests remain unrun. The report retains expected/raw observed outcomes, all pytest phases and a required-ID manifest. Strict report validation rejects missing IDs, invalid passing phases, incomplete envelopes and non-standard JSON values. Arithmetic reports alone do not claim product/browser acceptance.
