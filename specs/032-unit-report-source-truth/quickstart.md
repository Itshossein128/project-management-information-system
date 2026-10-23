# Quickstart: Specialty Unit Reporting Source of Truth

Validation guide for the implemented feature. Design references:

- [data-model.md](data-model.md)
- [unit-report-api.md](contracts/unit-report-api.md)
- [report-template-api.md](contracts/report-template-api.md)
- [daily-summary-api.md](contracts/daily-summary-api.md)
- [unit-report-ui.md](contracts/unit-report-ui.md)

## 1. Prerequisites

From the repository root:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

- Use the existing `apps/api/.venv`; do not install `requirements-dev.txt` as a whole because it upgrades the pinned Django 4.2 runtime.
- Ensure root `.env` contains the local values documented in `AGENTS.md`, including synchronous audit and eager Celery settings.
- Run migration and concurrency checks only against a disposable local/test database or sanitized snapshot—not the shared development or production database.
- MinIO and RabbitMQ are not required for this feature’s core workflow.

Backend commands below assume:

```bash
cd apps/api/core
set -a
source ../../../.env
set +a
```

## 2. Establish RED evidence

Before production changes, add and run the behavior tests in this order. Capture the expected failures rather than accepting import/setup failures as RED:

```bash
../.venv/bin/python -m pytest \
  sub_reports/tests/test_unit_report_migrations.py \
  sub_reports/tests/test_unit_report_models.py \
  project_templates/tests/test_required_report_units.py \
  sub_reports/tests/test_unit_report_workflow.py \
  sub_reports/tests/test_unit_report_permissions.py \
  field_reports/tests/test_unit_report_aggregation_eligibility.py \
  field_reports/tests/test_unit_report_provenance.py \
  field_reports/tests/test_unit_report_completeness.py \
  field_reports/tests/test_unit_report_rebuild_idempotency.py -q
```

**Expect before implementation**: failures specifically show missing canonical fields/constraints, template configuration, workflow/version behavior, complete provenance, and canonical completeness.

## 3. Migration and schema proof

After expand/backfill/constraint migrations are implemented:

```bash
../.venv/bin/python manage.py makemigrations --check --dry-run
../.venv/bin/python manage.py migrate --plan
../.venv/bin/python -m pytest sub_reports/tests/test_unit_report_migrations.py -q
../.venv/bin/python manage.py verify_unit_report_migration --json
../.venv/bin/python manage.py verify_blueprint_schema
```

The migration test must execute forward → pre-feature target → forward again through `MigrationExecutor` and restore the leaf migration in `finally`.

**Expect**:

- `makemigrations --check --dry-run` reports no model drift.
- Every source report/activity row is classified as migrated, historical, duplicate alias, or quarantine.
- `civil`/`finishing` map to Buildings; `mechanical`/`plumbing`/`hvac` map to Mechanical; `electrical` maps to Electrical.
- Collision winner is latest business change time, then stable UUID; other records remain historical versions.
- Stable IDs, child counts, states, known actors/times, rejection text, and summary links survive forward/reverse/forward.
- No unknown unit is silently guessed.
- Canonical uniqueness constraints are applied only after backfill validation.

## 4. Model, workflow, permissions, and SoD

```bash
../.venv/bin/python -m pytest \
  sub_reports/tests/test_unit_report_models.py \
  sub_reports/tests/test_unit_report_workflow.py \
  sub_reports/tests/test_unit_report_permissions.py -q
```

Required behavioral cases:

1. Two opens for the same project/date/unit resolve to one current draft.
2. Draft/rejected versions are editable; submitted/approved/historical versions are not.
3. Rejection requires a reason and records rejector/time.
4. Rejected correction resubmits while preserving events.
5. Approved correction creates version n+1 and leaves approved version n read-only.
6. Viewer/editor/approver capabilities match server authorization.
7. Non-member, wrong-project ID, wrong-unit ID, and nested foreign-key injection disclose no report content.
8. A preparer or submitter cannot approve the same report; stable `sod_self_approve` is returned. Verify the existing superuser break-glass separately.
9. Activity CRUD/import cannot bypass parent report status, project permissions, or URL/object unit consistency.

## 5. Aggregation, completeness, and provenance

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_unit_report_aggregation_eligibility.py \
  field_reports/tests/test_unit_report_provenance.py \
  field_reports/tests/test_unit_report_completeness.py \
  field_reports/tests/test_unit_report_rebuild_idempotency.py \
  field_reports/tests/test_daily_report_summary_isolation.py \
  field_reports/tests/test_daily_report_summary_metadata.py \
  field_reports/tests/test_daily_report_summary_permissions.py -q
```

**Expect**:

- Only current, non-deleted, submitted/approved matching project/date reports contribute.
- Draft, rejected, deleted, superseded, cross-project, and cross-date reports contribute nothing.
- Buildings page data appears in the same-date summary with report/unit/source-row provenance.
- Multi-source totals retain every source in deterministic order.
- Missing units come only from the immutable configuration bound to the report date.
- No configuration yields `configuration_incomplete`, never a hard-coded fallback.
- Correct/resubmit replaces stale contributions exactly once.
- Three unchanged rebuilds have identical canonical payloads after excluding volatile timestamps: content, counts, derivation keys, ordered provenance, completeness, and project-level overrides.

## 6. Real PostgreSQL concurrency

```bash
../.venv/bin/python -m pytest sub_reports/tests/test_unit_report_concurrency.py -q
```

Use independent database connections and synchronization barriers. Prove database state after threads complete for:

- simultaneous open/create;
- simultaneous approved-report corrections;
- edit/delete racing submit;
- approve racing reject;
- two unit submissions rebuilding one project day;
- rebuild racing an override update.

**Expect**: one current unit version per key, one current project summary, no duplicate derivation/provenance keys, complete provenance, and preserved overrides. Passing response codes alone are not sufficient.

## 7. Focused regression suite

```bash
../.venv/bin/python -m pytest \
  sub_reports/tests \
  project_templates/tests \
  field_reports/tests/test_daily_report_aggregation_activities.py \
  field_reports/tests/test_daily_report_aggregation_include.py \
  field_reports/tests/test_daily_report_aggregation_partial.py \
  field_reports/tests/test_daily_report_aggregation_rebuild.py \
  field_reports/tests/test_daily_report_aggregation_sections.py \
  field_reports/tests/test_daily_report_by_date.py \
  field_reports/tests/test_daily_report_derived_readonly.py \
  field_reports/tests/test_daily_report_no_blank_create.py \
  inventory/tests.py \
  inventory/test_department_activity_contractor_import.py \
  inventory/test_department_activity_contractor_ref.py -q
```

Adjust obsolete legacy assertions to canonical behavior; do not delete tests merely because they expose the old architecture.

## 8. Frontend compile and static route checks

Return to repository root:

```bash
cd ../../..
pnpm typecheck
rg -n "sub-reports|PROJECT_SUB_REPORTS|project-sub-reports" apps/web/src apps/web/e2e e2e
```

**Expect**:

- Record the repository’s unrelated baseline type errors separately; no new error may originate from changed unit-report files.
- No product route, navigation, CTA, empty state, client helper, or success-path test exposes `/sub-reports`.
- References may remain only in explicit not-found/retirement assertions or migration documentation.

## 9. Real-stack bilingual browser acceptance

The web package’s Playwright configuration starts API and web and runs its setup. PostgreSQL and Redis must already be running:

```bash
pnpm --filter web exec playwright test \
  --config=e2e/playwright.config.ts \
  e2e/tests/unit-report-source-truth.spec.ts \
  e2e/tests/daily-report.spec.ts
```

Run the complete scenario in both Persian and English:

1. Visit all six unit pages and verify canonical localized labels and date persistence.
2. On Buildings, open/create date D, add data, submit, approve with a different authorized actor, and inspect history.
3. Open project daily summary D and verify read-only data plus report/unit/source-row provenance.
4. Confirm draft/rejected reports do not contribute and the required unit remains missing.
5. Correct/resubmit and verify no stale or duplicate summary data.
6. Activate a template requiring a subset, then all required units; verify partial/complete. Verify no-template configuration-incomplete separately.
7. Verify viewer, editor, approver, conflicted approver, and cross-project/non-member behavior.
8. Directly open `/projects/{id}/sub-reports`; expect localized standard 404, no form, and no report-data request.
9. Scan desktop/mobile navigation and DOM for legacy links; daily reports must have no raw “New Report”.
10. Keyboard-operate date, workflow dialogs, history, and provenance disclosure; verify RTL/LTR and localized actionable errors.

## 10. Sanitized dataset rehearsal and rollback

Before any release or legacy cleanup:

1. Take and verify a restorable database backup of a sanitized staging-equivalent snapshot.
2. Record pre-migration table counts, stable-ID sets, category/status/deletion counts, child counts, and report-summary link graph.
3. Apply migrations and run `verify_unit_report_migration --json`.
4. Compare every pre-migration ID with the permanent trace and quarantine output.
5. Rebuild representative summaries and compare source/provenance accounting.
6. Restore or migrate back to the approved pre-feature boundary and verify original categories, links, states, actors/times, and ID sets.
7. Reapply forward and rerun the verifier.
8. Do not remove legacy fields/tables until this evidence passes and the retirement milestone is approved.

After canonical-only Machinery/Warehouse/Security reports exist, rollback is backup restore plus controlled export/replay; never invent a legacy discipline mapping.

## Evidence Boundaries

- pytest proves enumerated backend behavior on local PostgreSQL, not production load or browser UX.
- Concurrency tests prove local PostgreSQL serialization/invariants, not capacity.
- Typecheck proves compilation only and may include unrelated baseline failures.
- Real-stack Playwright proves seeded local browser/API behavior, not production migration safety.
- Fixture migrations do not prove real dataset accounting; sanitized snapshot rehearsal does.
- SC-010’s 90% first-attempt usability target requires moderated representative-user checks.
- This feature does not prove MinIO/RabbitMQ/file uploads, detailed specialty-section contracts, Excel parity, or PDF/print output.
