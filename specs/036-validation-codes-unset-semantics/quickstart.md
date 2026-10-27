# Validation Guide: Feature 036

This is an implementation acceptance guide. Commands and scenarios below are not results from this planning run. Data/API/UI rules live in data-model.md and contracts/.

## Prerequisites and safe setup

Use the repository at `/home/hossein/Desktop/projects/building-management`. Retain pinned Django 4.2.11; do not install requirements-dev.txt wholesale. PostgreSQL and Redis must be reachable using root .env. Inspect actual runtime before starting services; cloud AGENTS.md's native-service commands do not establish this desktop host's service state. Do not drop/recreate the development database.

Source .env without printing secrets. For core tests set synchronous audit/eager tasks to avoid optional broker dependencies. File storage, RabbitMQ, PDF/export and deployment are not exercised by this focused acceptance guide.

## Backend regression

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
export TEST_DATABASE_NAME="test_feature036_${USER}_$(date +%s)"
../.venv/bin/python -m pytest field_reports/tests/test_approval_workflow.py -q
```

Run one pytest process for this unique test database. Existing role must have test-database creation permission. Diagnose service/DB errors as infrastructure failures; do not call them test passes. Retain relevant activity serializer/read-only permission regressions from field_reports/tests after the focused suite succeeds; run the broader domain suite if integration changes justify it.

Extend the canonical approval suite before implementation for uncovered cases:

1. **FR-001/002/014**: submitted, under_review and approved submit attempts return 400 with report_not_in_submittable_state in FA/EN, unchanged report lifecycle fields. Draft and rejected valid submits pass.
2. **FR-003–005/013/014**: missing/null/empty/space/tab/newline reasons return rejection_reason_required; 1–9 trimmed chars return rejection_reason_min_length_10; exactly 10 and longer pass in both eligible reject states. Assert trimmed persistence. Check exact localized error.message, reason leaf and client text; the targeted daily-report rejection fix removes the current field prefix without changing the global handler.
3. **FR-006–008**: measured null blocks even when later among valid zero/positive rows; no state/quantity mutation. Explicit Decimal zero forms pass and remain zero after refresh. Deleted invalid rows do not block. Retain existing non-measured inconsistency and non-zero domain behavior.
4. **FR-016**: lack of edit_reports prevents submit; lack of approve_reports prevents reject; foreign-project requests cannot reveal or mutate records. Match current denial semantics and inspect persistence, not only status.

Record which tests fail before the change and pass after; retain already-green scenarios. Do not weaken existing assertions to manufacture success.

## Typecheck

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm typecheck
```

Report actual output on the final tree. AGENTS.md mentions historical type errors, but their current presence must be verified rather than assumed. Typecheck does not prove browser behavior.

## Browser acceptance

Use the apps/web suite rather than the root Playwright config; apps/web/e2e/playwright.config.ts includes API/web servers and global setup. Ensure a disposable seeded test environment and available Chromium first.

```bash
cd /home/hossein/Desktop/projects/building-management/apps/web
pnpm exec playwright test e2e/tests/daily-report.spec.ts --config=e2e/playwright.config.ts --project=chromium-desktop
```

The existing quantity case is named `daily report lifecycle: unset and zero quantity presentation`. Extend it or add focused cases in that canonical suite. Do not assume older create-report helpers work against automatic-summary restrictions: use canonical specialty-unit/by-date setup or isolated fixtures, preserving the production creation guard.

Required browser scenarios:

1. **FR-009–012/015**: read-only activity grid and summary with measured null, not-measured null, not-measured legacy numeric, explicit zero and positive. Locate quantity cells individually and assert exact FA `ثبت‌نشده` / EN `Unset`; zeros and positive quantities have no unset badge.
2. General-activity summary quantity null shows the badge; zero remains numeric. No measured flag is invented.
3. Switch FA → EN and back; assert labels and all four known validation-code feedback messages. Exercise submit/reject callbacks on form and detail views; unknown-code responses retain fallback.
4. Inspect light/dark, RTL/LTR, narrow and desktop widths. Record screenshots showing compact neutral background and visible caution outline; verify readable text and unchanged keyboard operation of editable numeric inputs.
5. In a real API-backed disposable workflow, submit zero and reject with valid trimmed reason; verify persisted report state after reload. Invalid quantity/reason checks must leave state unchanged. If legacy rows require mocked read responses, report those separately as rendering evidence.

## Completion evidence

Acceptance requires focused backend results, typecheck output, real workflow/permission evidence and bilingual browser/visual evidence from the final implementation tree. Record environment/service limitations, isolated test database name, command results and screenshots. No migrations are expected; if implementation introduces a schema change, revisit the plan and migration gate before claiming completion. Passing design checks in speckit-plan are not implementation, E2E or deployment evidence.
