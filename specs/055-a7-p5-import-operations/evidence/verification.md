# Verification: A.7-P5 import operations

## Acceptance rerun — 2026-11-13 (Asia/Tehran)

The isolated image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` was built from this working tree. Its schedule-tree SHA-256 is `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`, the same value now stored in [runtime/source-files.json](runtime/source-files.json) and [runtime/manifest.json](runtime/manifest.json). `real-data/plan.mpp` remains `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Django in the image is 4.2.11.

`ops/a7-p5/run-acceptance.sh` finished with status ready. All 13 matrix groups passed, including request intent, maintenance-budget admission closure, quarantined scratch cleanup, and the healthy follow-up. Native and CLI fallback both stored 6 WBS, 72 activities, and 72 relations. Recovery drained 201 jobs in 2.494s against bound 2553s. Expiry drained 201 originals in 2.793s against bound 6093s. Scratch cleanup removed a 201-workspace cohort in 0.858s and kept an unrelated file. Broker outage restored the same dispatch deadline and reached done. Two real importers confirmed duplicate delivery for both families.

Host command `ops/a7-p5/check-host.sh` passed **110 tests, 0 failures**, in 179.04s. JUnit: [runtime/host-pytest.xml](runtime/host-pytest.xml). That run includes the forwarded maintenance clock. It is not a substitute for the worker evidence above.

The browser suite passed 4/4 in 52.6s on the rebuilt `9f3b7c98...` image during the independent second-operator clean reproduction (`runtime/independent-browser.log`), and `pnpm typecheck` exited 0 (`runtime/independent-final-typecheck.log`). In `reproduction.md` (`## Fifth clean run — independent second-operator reproduction on rebuilt candidate image`), an independent second agent operator in an isolated conversation context tore down the stack (`down -v`, unmounted `/run/a7p5-scratch`, stopped `a7p5-containment.service`) and reproduced the full `quickstart.md` sequence on image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` (13/13 matrix groups `status: "ready"`, broker outage restoration, two-importer concurrent duplicate delivery, 4/4 browser retry suite, maintenance/migration checks, and 110 host pytest regressions in 161.77s) without any code or script changes. `T049` is now closed (`T001`–`T064` complete; independent agent reproduction, not human or employer acceptance).

## Implement continuation — 2026-11-13 (Asia/Tehran)

Read-only analysis had already run before implementation and again after the design corrections. Convergence had already appended T055–T060. This pass routed the remaining code fixes through implementation and did not start P6.

Host command `ops/a7-p5/check-host.sh` passed **109 tests, 0 skips/errors/failures**, 153.61s, on a new phase-specific PostgreSQL database. JUnit: [runtime/host-pytest.xml](runtime/host-pytest.xml). These checks use eager/inline overrides except the separate kernel probes. They are not a real-worker acceptance run. Django stays on the 4.2.11 pin.

- T055: maintenance republish calls the same bounded publication helper. A blocked transport returns before the request budget, leaves the job `pending`, and does not move `dispatch_deadline_at`.
- T057: `maintain_import_jobs` raises `CommandError` for a blocked/failed mandatory result and for `--batch-size` outside 1..100. Quickstart already states the nonzero exit.
- T058: `MigrationExecutor` moves schedule from `0015_periodreportfigure_version` to historical MSP/P6 rows, forward to `0017_import_retry_related_name`, back to 0015, then forward again. Original bytes, results, actor, project, and status remain. Historical terminal rows share one `legacy_backfill` anchor and keep `completed_at` unknown; the pending row stays unanchored. Clearing `file_data` is irreversible: reversing these migrations does not recreate purged bytes. Rollback of a purged original requires a database backup. Do not delete historical jobs or results as a rollback.
- T059: `SET LOCAL lock_timeout` is installed before project and job locks. Two PostgreSQL connections prove a 0.15s budget raises `OperationalError` and leaves the job pending, with no execution token.
- T060: application uses one absolute deadline, the minimum of the remaining execution deadline and 90 seconds from apply start. The remaining SQL budget is applied before statements, and the deadline is checked again before DONE. Cumulative exhaustion rolls back the domain write and records sanitized `processing_timeout`.

T056 now defers an expired unverifiable quarantine, keeps that slot quarantined, reports unfinished token names, and retries those names before later directories. A repeated successful cleanup leaves unrelated files in place and does not reopen admission by itself. The live `a7p5-import` containers were already up on image `a7p5-api:acceptance` and do not mount this working tree. They were not rebuilt or stopped. Real cleanup/catch-up on an image built from this change is still open, so T056 stays unchecked.

Still unchecked, with the gaps recorded in [reproduction.md](reproduction.md): T024, T033, T034, T042, T043, T047, T048, and T049. The latest independent clean attempts did not finish a full passing matrix on the current tree. The fourth attempt passed native, input, duplicate, and background resource probes, then failed because synchronous preview sent `plan.xml` as text/plain and intake returned `invalid_file_type`. That stack was left running. No full P5 acceptance is claimed.

## Previous current verification — 2026-11-13 (Asia/Tehran)

This update supersedes the earlier build/worker/cgroup/browser blockers. The unchanged reference SHA256 is `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Git baseline remains `develop` at `ea38dda2eda939184afd502fa027680b40af7870`; changes are in the working tree, not a published release.

- Image building succeeds using the existing local proxy as build-only arguments; no global DNS/proxy change. Private API, PostgreSQL, Redis, independent importer/maintenance workers and Beat ran with eager/inline false.
- Narrow delegated cgroup and a 256 MiB private tmpfs are real and writable/attachable. Whole-helper teardown, OOM, output/disk bounds,75-second timeout and actual worker SIGKILL were exercised. Root's extended matrix passed all ten groups; native JPype and actual Java CLI fallback produced matching stored counts:6 WBS,72 activities,72 relations. P6 XER succeeded too.
- Recovery/expiry each drained ≥201 rows across both families with actual PostgreSQL row locking, a later arrival and competing maintenance. Root's observed elapsed times were1.754s and1.976s respectively; full cutoff/N/bound/outcome identities are in the retained runtime manifest. Clock aging is isolated fixture manipulation, not a seven-day wall-clock trial.
- Actual private Redis loss between durable intake and publication, restoration, reconciliation and later healthy import passed via `python3 ops/a7-p5/check-broker-outage.py`; the fixed dispatch deadline survived. See [broker evidence](runtime/broker-outage.json).
- Root's four real browser trials passed in41.7s (Persian/English ×1280/390px), exercising keyboard retry, fresh upload, actual worker success, interrupted status request and same-job refresh. The later strengthened fresh-intent assertions await final independent rerun.
- Host regression before convergence corrections:91 passed, zero skips/errors/failures,98.59s. Command: `ops/a7-p5/check-host.sh`; [JUnit](runtime/host-pytest.xml). Host tests use inline/eager/locmem overrides; two separate tests exercise actual delegated kernel controls/OOM. They are separate from real Celery acceptance. The former skip-only resource guard is not counted as enforcement proof.
- `pnpm typecheck` exited0. Existing additive migrations are `0016_import_operations_lifecycle` and `0017_import_retry_related_name`. Data backfill checks preserve bytes/history and keep active originals unexpired; final migration schema checks are recorded separately below.

A newly added exact-boundary fixture initially failed4 cases because its `created_at` was newer than its deterministic cohort cutoff. The fixture chronology was corrected; all4 focused cases then passed (both families ×DONE/FAILED), without changing retention policy. The slow-publication regression first reproduced a real request-budget defect and passed after removing blocking executor shutdown. Actual fallback exposed the outdated Java entry-class assumption, which was corrected while preserving both package namespaces and bounded diagnostics.

The required post-implementation `speckit-converge` reviewed14 FRs,6 SCs,18 story acceptance scenarios,10 plan decisions and7 Constitution principles. It appended T055–T057 (bounded maintenance republish, bounded scratch/catch-up, truthful command exit). T055–T059 corrections are implemented. Final host verification passed99 tests with0 skips/errors/failures in202.92s, including the five originally failing maintenance cases, actual migration roundtrip, real PostgreSQL lock-wait limit and actual inherited-pipe/pids resource regression. Independent final runtime/browser verification is still in progress. Source file fingerprints are in runtime/source-files.json. T049 independent clean reproduction is in progress with a separately contextualized agent explicitly chosen by the user; it is not human/employer/production acceptance. Full P5 acceptance remains pending until the final evidence and remaining task details are resolved. No P6 work or deployment is started.

Knowledge retrieval was refreshed sequentially through the authorized local Qwen semantic service; the earlier indexing failure is historical. Code and feature artifacts remain the authority. Valid extension YAML has `hooks: {}`; no executable before/after implement/converge hooks exist. Requirements checklist16/16 is specification quality only.

## Historical record — superseded by current verification above


## Implementation run — 2026-11-12

Checklist `requirements.md`: 16/16 checked. No `before_implement` hooks are registered.

Unit and API checks that passed on the normal test database, with `IMPORT_PREPARE_INLINE` forced on except for the subprocess case:

- New `schedule/tests/test_a7_p5_*.py` modules, including a 201-row recovery cohort, a 201-row purge cohort, the 168-hour boundary, slot denial, subprocess XML preparation, and preflight refusal of the shared test database.
- Existing `test_a7_p2_import_safety.py`, `test_msp_import.py`, `test_p6_import.py`, and `test_a7_p4_import_experience.py`: 26 passed before the helper-database correction. The subprocess helper was rechecked after that correction.

`pnpm typecheck` exited 0 after the wizard and locale edits. `makemigrations schedule --check` is clean after `0017_import_retry_related_name`.

Final-tree pytest on 2026-11-12, Django 4.2.11, host test database (not the compose broker):

```bash
cd apps/api/core && ../.venv/bin/python -m pytest schedule/tests/test_a7_p5_*.py schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_a7_p4_import_experience.py schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py schedule/tests/test_mpp_import.py schedule/tests/test_mpp_equivalence.py -q --tb=line
```

Result: 79 passed, 1 skipped, 2 warnings, 89.18s. The skip is `test_kernel_limits_are_not_marked_passed_without_controls` because cgroup delegation and the `a7p5` database are unavailable on the host. These tests use `IMPORT_PREPARE_INLINE` and the locmem cache. They are not worker acceptance.

The isolated image build did not finish. `docker compose -f ops/a7-p5/compose.yml build api` failed while installing Python dependencies: pip could not resolve the package index (`Temporary failure in name resolution` for `files.pythonhosted.org`). No a7p5 container was started. T024, T033, T034, T042, T043, T047, T048, and T049 remain unrun. T049 also has no second operator; see `evidence/reproduction.md`.

These are not broker/worker acceptance. `test_a7_p5_resource_limits.py` skips because `/sys/fs/cgroup` is not writable and the test database is not `a7p5`. The browser spec is skipped on purpose. Compose was not started. Eager execution is not reported as a worker pass.

Knowledge: semantic reindex failed with a local embedding connection error, so retrieval was not used as the basis for the code change. The spec, contracts, and current schedule modules were read directly.

**Date**: 2026-11-12
**Baseline**: `develop`, `ea38dda2eda939184afd502fa027680b40af7870`

## Evidence collected

- Initial `git status --short`: clean as reported by Git.
- Knowledge status: hybrid index fresh by content/configuration hashes; embedding job complete. Ran context for original invocation and full linked prompt; no reindex/downgrade.
- Active template resolved through the project's template stack and copied before authoring. Explicit feature-directory binding returned the intended absolute `FEATURE_DIR`.
- P1/P2/P3 handoffs read; P4 handoff absent. Its verification notes were read separately and are not fresh P5 runtime evidence.
- Existing graph queried with exact vocabulary `mpp import celery convert mpxj timeout cleanup schedule`; owning source paths read. Query was bounded/truncated and used only for navigation.
- User retention choice recorded; specification quality checklist reviewed: 16/16 pass.

## Verification limits

No product-runtime check was run. No evidence here establishes actual conversion, broker/worker readiness, resource enforcement, retry/restart safety, cleanup, migration safety, browser behavior, or delivery acceptance. Environment availability remains unassessed. See [handoff](../handoff.md) for the predecessor gate and [traceability](../traceability.md) for source/design distinctions.

## Final document checks

- Feature paths checked with explicit `SPECIFY_FEATURE_DIRECTORY` and `check_prerequisites.py --paths-only --json`: intended P5 directory/spec returned. The helper's synthetic BRANCH field reflects feature naming, not a Git branch switch; the observed Git checkout remains `develop`.
- Document assertions passed: 14 functional requirements, 6 measurable outcomes, 16 checked quality items, no unresolved clarification markers, valid local links, correct feature binding, and all four existing phase-map entries unchanged.
- Extension YAML parsed again: no executable before/after specify hooks. P4 handoff absence reconfirmed.
- `git diff --check` passed. Generated graph vocabulary was restored to its original tracked content after navigation. No product files were changed.

## Independent planning invocation — 2026-11-12

- Read the installed planning skill, original specification/checklist, Constitution, current conversion/tasks/views/model/settings and deployment sources. Both before/after plan hooks checked from valid YAML: none registered.
- Refreshed the stale hybrid index with the existing authorized local Qwen service after confirming the prior embedding job complete. A second sequential refresh included the newly copied plan template; no concurrent index jobs. The subsequent original-request context reported fresh supported context with no clarification questions.
- Ran `.venv/bin/python .specify/scripts/python/setup_plan.py --json` with the absolute P5 feature binding. It returned the correct FEATURE_SPEC/IMPL_PLAN/FEATURE_DIR; its synthetic BRANCH label does not change actual Git branch `develop`.
- Two read-only research agents inspected lifecycle/retention and conversion/containment. Official Django, Celery 5.6-line, Python 3.12, JPype, Docker and Linux cgroup documentation informed design; links are in research.md. Local package/executable inventory is source/environment inventory only. Daemon access and containment delegation were not tested.
- Generated plan/research/data-model/two contracts/quickstart; reviewed Constitution before and after design. No exceptions. The current explicit planning request permits independent design; predecessor handoff remains a hard gate for dependent implementation.
- No tasks, application code, migration, service startup, database mutation, product tests, actual conversion, worker execution, fault injection, cleanup or deployment performed. Quickstart labels proposed implementation outputs and unrun scenarios explicitly.

Final design-document checks passed: six expected artifacts exist with completed template sections; local links resolve; no unresolved design placeholders; seven-day rule preserved; tasks.md not generated; normalized feature binding correct; Git branch remains develop. The setup helper normalizes feature.json to a repository-relative path resolving to the same explicit absolute target. New document whitespace was checked explicitly because untracked files are not covered by git diff --check. Extension YAML parsed after design with no before/after plan hooks. P4 handoff absence reconfirmed. These are document checks only.

## Task generation — 2026-11-12

Read the installed tasks skill, active template returned by `setup_tasks.py --json`, spec, plan, model, both contracts, research, quickstart and Constitution. Explicit absolute feature binding returned the intended FEATURE_DIR and four optional design-document groups. Extension hooks before generation: valid YAML, none registered.

The hybrid index was stale from prior design artifacts; status reported the previous embedding job complete. Refreshed sequentially using the authorized local Qwen semantic service, then original-request context reported fresh supported context with no clarification questions. Source paths and task scope derive from original feature artifacts, not retrieval rank.

Generated 54 initially unchecked tasks across setup/foundation/four stories/polish. US1=8, US2=10, US3=9, US4=7; shared=20. Five same-phase disjoint test-file pairs are potential authoring opportunities. No agents, parallel implementation, runtime tests, migrations, services, database mutations or deployment were dispatched. P4 handoff absence remains an implementation gate; T001 records the required verification rather than fabricating readiness. Next step is read-only speckit-analyze.

Final task-document validation passed: 54 sequential unique IDs T001–T054, all unchecked; labels match story phases; each task names a concrete repository path; counts match 20 shared/8 US1/10 US2/9 US3/7 US4. All ten P markers form five verified disjoint-file pairs. All 14 FRs, six SCs and four audit IDs have task mappings. Four independent acceptance criteria and story-specific parallel examples are present; local Markdown links and whitespace checks passed. Extension YAML was parsed after generation: no executable before/after tasks hooks. P4 handoff remains absent. No product-runtime verification occurred.

## User-authorized analysis remediation — 2026-11-12

The user explicitly authorized edits after the read-only analysis. The four findings were corrected in the existing design documents and task descriptions, separately from the analysis pass:

- I1: explicit intent=new/retry, required FAILED predecessor for business retry, fresh-upload/new-identity rules, API-client/wizard propagation and status-refresh separation.
- I2: authorization/cheap bounded upload identity followed by scoped in-flight match before capacity, plus a project-locked post-preparation race recheck; sole-slot saturation coverage added.
- U1: stable oldest-first finite cohorts, N including queued work ahead, fair deferred-row revisit, B=100 consecutive batches, C=10-second per-item budget, G≤1-second inter-batch delay, single leader, catch-up admission gate and explicit failed/blocked maintenance budgets. Conservative formulas include the 480-second prior-lifecycle allowance; ≥201-item deterministic and actual-runtime evidence obligations added. Values are engineering acceptance settings under stated health assumptions, not a new customer SLA.
- I3: jobless input/capacity/dependency rejection is distinguished from existing stored safety refusals and failures after durable admission. Accepted-job identity/FAILED assertions and pre-admission rejection observations are separate in scenarios, success criteria and runtime tasks.

Status before editing: prior embedding job complete; the stale hybrid index was refreshed sequentially with the authorized local Qwen service. Original-request context then reported fresh retrieval; its generic semantic-only clarification was resolved from the explicit preceding four-finding report and the user's edit authorization. No speculative retrieved source defined the fixes.

Post-edit checks: prerequisites resolved the intended absolute FEATURE_DIR; all 14 FRs and six SCs remain; T001–T054 remain sequential and unchecked with original story counts (shared 20, US1 8, US2 10, US3 9, US4 7). Reviewed intent/linkage, duplicate-before-capacity ordering, fixed-expiry claim refusal, finite-cohort formulas and admitted/rejected failure semantics across spec/plan/model/research/contracts/quickstart/tasks. Existing local links, concrete frontend path references, document whitespace and git diff --check passed. Before/after analyze hooks parsed from YAML: none registered. The four original findings are addressed at document/task level; this is not product-runtime evidence.

Only P5 documentation was edited in this remediation. No application code, migration, database, service, runtime test, worker or deployment was changed/run. Actual P4 handoff remains absent, T001 remains open, and independent runtime/profile/reproduction evidence is still required.

## User-requested predecessor preparation — 2026-11-12

Prepared the actual P4 handoff in its owning feature, added its missing audit traceability and fresh recheck/JUnit evidence, and refreshed P1/P2/P3 downstream-readiness notes. The selected integrated suite passed 93 tests with zero skips/failures/errors in 101.72 seconds on a newly created phase-specific test database; fresh pnpm typecheck exited 0 and Django remains 4.2.11. No source/schema/service or original fixture was changed. Browser matrix/screenshot presence and committed source correspondence were checked; browser trials were not rerun. See [actual recheck](../../054-a7-p4-import-experience/evidence/handoff-recheck.md).

Only T001 was marked complete after examining actual handoffs, phase-map entries, fresh test evidence and prior browser limits. T002–T054 remain unchecked; none of the P5 product or real-worker/containment/retention/recovery scenarios has been executed. Active spec/plan/handoff/checklist prerequisite wording was updated; historical absence notes remain as chronology rather than current blockers. This is local downstream readiness only; predecessor employer acceptance and the explicitly missing browser/guide observations were not invented.

## Final correction evidence — 2026-11-13

The independent pre-correction run found a real pids failure: inherited child pipes hid kernel exhaustion until75s and returned processing_timeout. Its failed manifest/logs remain under runtime/independent-precorrection-*. The launcher now checks kernel events during pipe draining and stops waiting after helper exit, then kills/reaps the owned whole group. This was verified by the new actual kernel regression; final independent runtime is pending. A separate real two-connection PostgreSQL red test also proved lock_timeout was applied too late; it now applies before lock acquisition and the pending job remains unchanged on budget exhaustion.

Final regression command: `ops/a7-p5/check-host.sh`;99 passed,0skips/errors/failures,202.92s. [JUnit](runtime/host-pytest.xml) includes actual schema reverse/forward preservation and both-family exact retention boundaries. Controlled blocked-transport/clock tests are labeled regression evidence; actual worker/broker/browser evidence remains separate. `pnpm typecheck` passed; later changes were backend/operations/test-only.

## Cumulative application correction and frozen-tree regression

T060's proper red test proved that a multi-query/CPU-delay application could outlive the per-statement profile and still commit DONE. The implementation now uses an absolute application deadline, min(remaining execution deadline,application start+90s), reapplies the remaining SQL budget before every statement, and checks again before final DONE. PostgreSQL timeout SQLSTATE mapping handles both psycopg2/3 and permits rollback/savepoint cleanup after exhaustion. Controlled tests prove a prior domain update rolls back on pre-DONE exhaustion and actual pg_sleep is canceled inside a nested transaction with sanitized processing_timeout.

Focused lifecycle5 passed10.61s. The final full frozen-tree command `ops/a7-p5/check-host.sh` passed**106 tests,0 skips/errors/failures**,213.94s. JUnit is runtime/host-pytest.xml. Earlier104/99/91 counts are historical runs before the last corrections; the106 run supersedes their current-tree claim. Typecheck remains passed; subsequent application-source changes were backend-only. The temporary reused apply-budget test database was removed after confirming no active connections.

Independent focused public input checks passed on the prior candidate: invalid XML=msp_invalid_xml; password=mpp_password_protected; truncated OLE=mpp_unsupported with tested MPXJ; renamed wrong content=invalid_file_type. A helper called directly after bypassing public intake classifies wrong native bytes as mpp_corrupt; test expectations distinguish these layers. The first two newly added native transport expectations were corrected to those observed categories; no production classification was changed merely to match a test.
