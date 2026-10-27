# Feature 036 Verification Evidence Log

This file collects implementation-phase evidence for `036-validation-codes-unset-semantics`. Entries record real executed commands and observed outcomes; pending categories are not claims.

## Baseline (T001)

- Date: 2026-10-27
- Branch: `develop`, HEAD `460afbd` ("feat(daily-reports): complete convergence phase for lifecycle lock and update graph"). No feature branch created; work happens on `develop` per planning note.
- `.specify/feature.json` resolves to `specs/036-validation-codes-unset-semantics` (confirmed via check_prerequisites.py: `FEATURE_DIR=/home/hossein/Desktop/projects/building-management/specs/036-validation-codes-unset-semantics`).
- Preserved pre-existing changes: 6 untracked spec artifacts only (`specs/036-validation-codes-unset-semantics/{contracts/,data-model.md,plan.md,quickstart.md,research.md,tasks.md}`). No tracked source file was modified at baseline; these stay untouched until tasks edit them.
- Checklist gate: `checklists/requirements.md` 16/16 checked → PASS (read-only).
- Acceptance evidence categories (per constitution Principle VI): backend pytest results, `pnpm typecheck` output, real API workflow results, browser E2E (Playwright chromium) results, visual/theme review evidence. Pending until tasks run them.

## Environment (T002)

- PostgreSQL: accepting connections on 5433 (`pg_isready -p 5433` → accepting).
- Redis: `redis-cli ping` → PONG (127.0.0.1:6379).
- Django/venv: `apps/api/.venv/bin/python -c "import django; print(django.get_version())"` → `4.2.11` (pin preserved; `requirements-dev.txt` NOT installed wholesale).
- pnpm 10.17.0; Playwright Chromium `chromium-1243` cached in `~/.cache/ms-playwright`.
- Test-database policy: unique `TEST_DATABASE_NAME` (`test_feature036_...` with timestamp), one pytest process per run; `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true` set only in the test/dev shell (never persisted to `.env`); no secrets logged; no development database dropped or recreated.

## Foundational (T003, T004)

### T003 — E2E fixture inspection

`apps/web/e2e/helpers/project.ts::createDailyReportViaApi` already uses the canonical flow: open a specialty-unit report (`POST /units/{unit}/daily-reports/open/`), patch rows, submit+approve the unit report, then `GET /daily-reports/by-date/` to obtain the auto-created summary report id. It never calls the retired blank `POST /daily-reports/`; production direct-create restrictions are untouched. The existing tests (`daily-report.spec.ts`) prove the fixture reaches both the summary view (`daily-report-summary-view`) and the form/edit grid (`daily-report-form`), so **no helper adaptation was needed**; reusable setup stays in `helpers/project.ts`.

### T004 — Preservation contract (source-traced)

- `apps/api/core/field_reports/models.py` (DailyReportActivity, lines ~301–302): `quantity = DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)`, `quantity_measured = BooleanField(default=True)` — retained unchanged; no migration required.
- `apps/api/core/field_reports/models.py` (DailyReport): status has the four lifecycle values (draft, submitted, under_review, approved, rejected) used by `ReportStatus`; correction/lock metadata untouched by this feature.
- `apps/api/core/field_reports/serializers.py` (lines ~180–239): `DailyReportActivitySerializer.validate_quantity` normalizes blank input (`'' → None`) via `coerce_optional_decimal`, and `validate` writes `None` for not-measured rows. Existing write-path policy (not-measured+numeric inconsistency, non-zero domain rules) is out of change scope.
- `apps/api/core/field_reports/services/lifecycle_errors.py`: `LIFECYCLE_MESSAGES` already contains all four scoped codes with exact FA/EN strings matching `contracts/workflow-api.md`; `lifecycle_error_detail` returns `ErrorDetail(message, code=<stable_code>)`.
- `apps/api/core/field_reports/daily_report_views.py`: `_validate_report_ready_for_submit` filters `is_deleted=False` rows only and raises `quantity_unset_invalid` via `row.quantity_measured and row.quantity is None` (true `is None` check — explicit Decimal zero passes). `_submit` checks `EDITABLE_STATUSES = {draft, rejected}` first → `report_not_in_submittable_state`. `_reject` accepts SUBMITTED/UNDER_REVIEW, trims `request.data['reason']`, then requires non-empty (`rejection_reason_required`) and length ≥ 10 (`rejection_reason_min_length_10`); persistence of trimmed reason happens in `services.reject_report`.
- Gap identified (target of T013): `_reject` raises only `{'reason': [...]}`, so `config/exceptions.py::_extract_message` prefixes `error.message` with `reason: `. Fix must stay local to `_reject` (supply both `detail` and `reason` ErrorDetail leaves); `config/exceptions.py` and the global envelope remain unchanged.
- `apps/api/core/common/mixins.py` + `DailyReportViewSet`: workflow actions dispatch through `self.get_object()` (project-nested, member/permission-scoped); `view/edit/approve` permission fields = `view_reports/edit_reports/approve_reports` — preserved, no authorization changes.
- `apps/web/src/app/lib/api/daily-reports.ts`: type surface exposes quantity (decimal string or null) and quantity_measured; **no quantity/quantity_measured field exists on GeneralActivityRow**, exactly as the data-model states; no mismatch found.

## User Story 1 — Submit Only Complete Measured Quantities (T005–T010)

- T005/T006 (tests first): added `TestMeasuredNullRefusal` (5 API contract cases: measured null among zero/positive rows; rejected-state resubmit refusal; multiple null rows with EN Accept-Language; deleted invalid-row exclusion; explicit zero forms 0/0.0/0.00 passing and persisting `0.0000`) and `TestWorkflowPermissionBoundaries` (T009: viewer-role submit → 403 with unchanged lifecycle; site_supervisor reject without approve_reports → 403 with unchanged submitted report; foreign-project submit → 403 + report untouched). Added e2e `daily report validation codes: measured-null refusal and zero submit persist (API-backed)` (T006): browser submit of a measured-null row shows the server quantity message and leaves the report in draft; explicit API refusal proof (`400, error.code=quantity_unset_invalid`); after repairing the row to explicit zero the UI submit succeeds and the submitted status persists across a hard reload.
- T007 baseline evaluation: the first run reported 2 failures — both were test-infrastructure defects (an unconditional `submitted_by is None` assertion contradicted a legitimate earlier submit; child rows have no `soft_delete()` method). After correcting the tests to snapshot-compare lifecycle fields and set `is_deleted` directly, **all US1 cases pass against the unchanged implementation**: the backend measured-null refusal (`is None`), rejected-state resubmit refusal, deleted-row exclusion and explicit-zero acceptance were already correct, so T008 required **no production change** (already-correct code left unchanged, per contract) and the green results are retained regression evidence, not manufactured red.
- T010 execution:
  - Backend: test DB `test_feature036_hossein_1793090434` (single pytest process), commands outside: `cd apps/api/core; set -a; source .env; set +a; export AUDIT_LOG_ASYNC=false CELERY_TASK_ALWAYS_EAGER=true TEST_DATABASE_NAME=...; ../.venv/bin/python -m pytest field_reports/tests/test_approval_workflow.py -q` → **18 passed** (includes T005/T009 additions and retained cases).
  - Browser: `cd apps/web && pnpm exec playwright test e2e/tests/daily-report.spec.ts --config=e2e/playwright.config.ts --project=chromium-desktop` → **8 passed** (49.4s) covering real workflow and presentation tests. (Reproducibility note: run Playwright directly with a file filter; the `pnpm --filter web test:e2e -- <file>` form still triggers pre-existing ENOENT import errors in unrelated decision-support specs that read locale files by repo-root-relative path.)
  - State-persistence evidence: zero/null/flags asserted via `refresh_from_db()` before/after failed submits (status draft/rejected unchanged, `rejection_reason` retained, quantities unmodified); successful zero submit persists `submitted` across a browser reload.
- US1 Checkpoint: satisfied — measured-null blocks, explicit zero passes and persists, invalid/unauthorized actions leave records untouched, all without the US2 client error mapper.

## User Story 2 — Receive Stable Workflow Validation Feedback (T011–T019)

- T011 (tests first): added `TestRejectionFeedbackContract` (non-submittable submit attempts from under_review and approved with exact FA/EN `report_not_in_submittable_state` messages; reject valid flows from submitted and under_review with trimmed persistence; reason missing `reason` key/null/empty/spaces/tab+newline → `rejection_reason_required` with exact messages and `details.reason` leaf; 1–9 trimmed lengths → `rejection_reason_min_length_10`; exactly-10 trimmed EN (`exactlyten`) and FA (`دلیل کوتاه`) passing; long FA reason passing; invalid reasons leaving a snapshot-computed lifecycle untouched). Tightened the existing bilingual test's two approval-check `in` assertions to exact `error.message` equality.
- T011 baseline (RED): 5 failed / 18 passed — demonstrable failure was `'reason: دلیل رد الزامی است'` vs exact expected message (the field-prefixed `error.message` gap), reproduced exactly as contracts/workflow-api.md describes.
- T013 (fix): `_reject` in `apps/api/core/field_reports/daily_report_views.py` now raises both `detail` and `reason` ErrorDetail leaves with the same localized message/code for both rejection branches; `config/exceptions.py` and the envelope remain unchanged. Two initial test-flow defects in new tests (rejected-state ordering, stale in-memory status) were corrected in the tests themselves; no production code beyond the two branches changed. Result: **23 passed** (1p04m) on `test_feature036_hossein_1793090434` with `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true` — GREEN retained across US1 + US2 suites.
- T014: `dailyReports.validationErrors` added to `apps/web/src/app/locales/{en,fa}.json` with the four exact contract strings; shared `errors.rejection_reason_required` entries left untouched.
- T015/T016/T017: new `apps/web/src/components/daily_reports/workflow-error-message.ts` resolver (four known codes → `dailyReports.validationErrors.<code>` via `ApiRequestError.code`; unknown/non-API errors keep server-message/generic fallback). Wired the workflow `onError` of `DailyReportForm.tsx` and `daily-report-view.tsx` to it (current translator). `ApprovalStatusBar` reason guard (`reason.trim().length < 10` disabled) matches the trimmed backend boundary — inspected, no change required.
- T012 (browser feedback): added two e2e tests. (a) Real-API test `daily report workflow feedback: real API refusal messages on form and view surfaces (exact FA/EN)`: live measured-null submit refusal through the form shows exact FA text, exact EN text after setting `i18nextLng=en` and reloading, and the same refusal on the `/view` route — status badge stays draft each time. (b) `daily report workflow feedback: four known codes localized for unknown fallback (UI-only rendering evidence)`: route-intercepted 400s with distinctive server text prove all four codes render the client translation (not the server text) in FA and EN, unknown code keeps server fallback, non-API JSON keeps parse fallback, and the view reject callback resolves `rejection_reason_required` through the shared resolver. Labeled UI-only for the mocked parts; the real-API tests are separate.
- T018/T019: reruns after integration — backend `test_approval_workflow.py` → 23 passed including combined US1/US2 cases; browser suite (10 tests) → **10 passed (1.1m)** on the final integrated tree. Locale switching changes text only; the four identifiers stay stable; unknown-code fallback retained. (A mid-session test run failed with 9 × 30s timeouts when dev servers wedged; retry on the same tree passed cleanly — infrastructure event, not behavior.)
- US2 Checkpoint: satisfied. Exact rejection `error.message` is unprefixed; all four codes have bilingual feedback on form and view; US1 quantity/permission guarantees remained green throughout.


## Continuation audit — 2026-10-27 (T020 onward)

The continuation started on `develop` at `0975a61`, with nine tracked source/test files already modified, the workflow-error resolver untracked, and the feature artifacts/screenshots present. The earlier Baseline section describes the prior run, not this continuation's clean/dirty state. All pre-existing changes were preserved. The current requirements checklist remained 16/16; `.specify/extensions.yml` parses as `hooks: {}` with no pre/post implementation hooks. Root ignore files already cover Python/Node dependencies, environment files, generated builds, logs and test artifacts; package.json is private, with no publishing ignore requirement. No applicable Terraform, Helm, ESLint or Prettier setup was found.

### US3 tests and retained implementation (T020–T025)

- The English `Unset` label, local warning-token ring and general-activity shared badge were already present at this continuation's start. They were inspected and retained; no rollback was used to manufacture RED evidence. The read-only branch of EditableGrid already calls the shared predicate/badge, and ActivityTab reaches it. No grid production fix was required.
- Tightened exact badge labels with `toHaveText`, replacing unsupported `toContainText(..., {exact:true})` calls. Numeric assertions now target the activity quantity column (index 7) or general quantity column (index 2); zero elsewhere in a row cannot satisfy them.
- Expanded read-response rendering coverage to measured/null, false/null, legacy false/string-zero, legacy false/positive, measured numeric zero, measured string zero and positive. Both summary and approved read-only grid are checked in FA/EN × light/dark × 1280/420 px viewports. The legacy/approved-null matrix is a GET-response fixture only; APIRequestContext reads bypass that interception and compare the actual persisted report before/after rendering. No legacy values are written or normalized by these tests.
- General activities are created through two real specialty-unit reports with null/zero quantities, approved and aggregated by-date. Their summary is checked in both locales/themes/widths without inventing a measured flag.
- Browser computed-style assertions compare the visible 2px inset ring against existing palette warning-500 (light) / warning-400 (dark), background against the neutral --muted token, and compact font size <=12px. Keyboard regression enters 7 then restores 0 in the existing numeric input.
- Initial continuation failures were test defects: wrong quantity column index, reference to an unavailable runtime --color-warning variable, substring row matches (Positive also matched Legacy False Positive), and setting only i18nextLng while app-language still selected the other locale. These were corrected in the tests; none is claimed as RED product behavior or fixed by weakening assertions.
- Focused quantity run: from apps/web, `pnpm exec playwright test e2e/tests/daily-report.spec.ts --config=e2e/playwright.config.ts --project=chromium-desktop --grep 'quantity presentation|general activity quantity'` → **2 passed (53.4s)**. Subsequent screenshot framing and feedback-test additions are covered by the final combined run below.

### Final backend/typecheck checks (T027)

- Verified Django runtime 4.2.11, PostgreSQL :5433 accepting connections, Redis PONG. No dependency installation, root .env edit or development-database reset.
- From apps/api/core, sourced `/home/hossein/Desktop/projects/building-management/.env`, exported `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`, `TEST_DATABASE_NAME=test_feature036_final_1793095883`, then ran:
  `../.venv/bin/python -m pytest field_reports/tests/test_approval_workflow.py field_reports/tests/test_daily_report_gaps_status_unset.py field_reports/tests/test_daily_report_derived_readonly.py field_reports/tests/test_daily_report_summary_permissions.py -q`
  → **39 passed, 2 warnings in 72.38s**. One isolated test database and one pytest process; no concurrent schema setup. Backend production source did not change afterward.
- From repository root, `pnpm typecheck` → **exit 0**. Historical AGENTS.md type errors were absent on this tree. Frontend production source did not change afterward; E2E files are excluded from this project's typecheck and are executed separately by Playwright.

### Integrity/data-path review (T029)

Final source diff changes only daily-report rejection error construction, client feedback localization and quantity presentation, plus tests/docs. No model/migration, serializer, API type, permission, calculation or aggregation code changed.

- DecimalField precision/nullability and quantity_measured default remain in field_reports/models.py:301–302. DailyReportActivitySerializer retains explicit nullable decimal and existing blank/not-measured normalization; general activity serialization remains nullable decimal with no measured field.
- Sync uses services/__init__.py child serializer mapping, validation and save paths; it does not import the UI predicate or workflow feedback helper. Those files are unchanged.
- daily_report_aggregation.py carries source quantity into activity/general rows and source provenance, including its existing quantity_measured derivation; unchanged. No claim is made that this feature fixes unrelated aggregation policies.
- The import/transfer boundary is the existing specialty-unit/by-date flow and serializers; no quantity contract was altered. API activity-log export in services/activity_log.py retains its null-safe numeric conversion. field_reports/pdf.py retains its current quantity rendering. No imports/exports/PDF formatting change or runtime verification of those outputs is claimed.
- UnsetQuantityBadge and the feedback helper are presentation consumers only. Backend authorization/project resolution, global exception handler, shared Badge variants and numeric calculations remain unchanged. **No migration is required.**


### Visual review (T026, SC-005)

Observer: the implementing agent inspected actual Playwright PNGs with the image viewer, without opening an editor or deriving the displayed classifications from raw quantities. On first image inspection, the outlined `ثبت‌نشده` / `Unset` pills were distinguishable from plain `0`, `0.00` and `12.5000`. The ring is amber over a neutral background in both themes; labels are compact and readable. This is an **agent visual acceptance review**, not a human usability study or a measured human first-inspection success rate. No human review result is inferred.

Reviewed evidence:

- [FA light activity summary, desktop](screenshots/quantity-view-fa-light-1280.png)
- [FA dark activity summary, desktop](screenshots/quantity-view-fa-dark-1280.png)
- [EN light approved read-only grid, desktop](screenshots/quantity-edit-en-light-1280.png)
- [FA light activity summary, narrow with quantity column scrolled into view](screenshots/quantity-view-fa-light-420.png)
- [EN dark general activities, narrow](screenshots/general-en-dark-420.png)

The full screenshot matrix also includes view/edit × FA/EN × light/dark × 1280/420 plus the general-activity variants. Initial full-page screenshots showed the app header rather than the target tables because the application scrolls internally. Final evidence captures the target section/grid, scrolling its quantity column into view. Narrow tables retain the existing horizontal scrolling; a single narrow frame does not show every description and quantity simultaneously. No responsive-layout redesign was introduced.

### Final combined browser acceptance (T028)

From `/home/hossein/Desktop/projects/building-management/apps/web`:

`pnpm exec playwright test e2e/tests/daily-report.spec.ts --config=e2e/playwright.config.ts --project=chromium-desktop`

→ **11 passed (1.8m)**, one worker, after the final test/screenshot updates. This run supersedes the earlier continuation runs that exposed test-only defects. Playwright's dev servers used synchronous audit/eager tasks; global setup reported no migrations to apply and seeded the existing E2E users. The corrected direct command is now in quickstart.md.

Live evidence: canonical specialty-unit/by-date summary creation, approval and correction controls; measured-null refusal; explicit-zero submission and submitted status after reload; valid rejection using `  exactlyten  ` through the browser, rejected status after reload, API-persisted trimmed `exactlyten` and unchanged zero quantities. Visitor-token submit/reject attempts returned 403 and an authenticated API reread matched the pre-denial report exactly.

Rendering-only evidence: controlled GET responses supply unsupported legacy combinations for the activity display matrix; intercepted 400 responses exercise four known feedback codes and unknown-code fallback in both FA/EN on form/view rejection callbacks, alongside the form submit feedback matrix. Malformed-response fallback is checked on form submit and view reject. These fixtures do not prove server authorization; authorization is covered separately by real API denial/persistence assertions and pytest.

Warnings/limits: optional RabbitMQ schedule-event publication logged AMQPConnectionError during project setup; those API requests still succeeded and all scoped tests passed. RabbitMQ delivery, MinIO uploads, PDF/export rendering, broader repository suites, CI and deployment were not exercised. Existing cache-backend, JWT-key-length and dependency deprecation warnings were observed; no infrastructure or dependency changes were made for them.

### Requirement coverage and acceptance (T030)

- FR-001/002: backend non-submittable-state and source-state tests, exact bilingual code/message assertions; live submit workflow.
- FR-003/004/005: missing/null/blank/whitespace and trimmed-length boundary backend cases, both reject source states, exact error envelope; live exactly-10 trimmed browser rejection with persistence.
- FR-006/007/008: multi-row measured-null refusal and Decimal zero regressions, live refusal → zero repair → successful submit, no-mutation checks.
- FR-009/010/011/012: seven-case activity matrix on summary/read-only grid, real general null/zero summary, exact cell values/labels and computed style checks in both locales/themes/viewport widths, keyboard input preservation.
- FR-013/014: exact locale catalogs, server Accept-Language tests, browser locale switching and known-code resolution on both surfaces, retained unknown/malformed fallback.
- FR-015: canonical pytest and Playwright regressions above; no assertions removed or disabled.
- FR-016: existing project/role boundaries retained; pytest no-edit/no-approve/foreign-project no-mutation tests and live visitor-token denial with persisted-state comparison.
- SC-001/002/003/004: all enumerated scoped automated acceptance cases passed on the final production tree. This is bounded suite coverage, not a claim about unenumerated inputs.
- SC-005: agent first-inspection screenshot review passed as described above; independent human usability validation remains unmeasured.

Acceptance decision: **scoped implementation and technical acceptance complete**, with the explicit human-usability and unexercised-service/output boundaries above. All 30 task work items are complete; checklist files remained read-only. Final whitespace validation: `git diff --check` passed. No schema migration, commit, push or deployment was performed by this continuation.

Post-execution hooks: parsed `.specify/extensions.yml` with PyYAML after validation; `hooks.after_implement` is absent (`hooks: {}`), so there are no hooks to dispatch.
