# AHP implementation evidence
Date: 2026-10-11. Feature: 021-decision-ahp. Worktree: develop at c5328c4.
Existing dirty planning artifacts preserved. Requirements gate: 16/16 checked; no extension hooks configured.
Runtime verified: Python 3.12.3, Django 4.2.11, Node v25.2.1; native PostgreSQL 5433 and Redis 6379 listening. API/web initially stopped. No dependency upgrades or database reset.
Existing git/Docker ignores cover dependency, build, Python cache, virtualenv and local environment artifacts. Private packages do not require publishing ignores.
Models preserved: title String max 200; method String max 32; case FK DecisionCase CASCADE; project FK Project CASCADE; actor User FK PROTECT; id UUID; selected_methods must contain ahp for execution. Existing view_decision_support/edit_decision_support permissions; no migrations or new permissions.
Human four-criterion timing is not yet observed. Scripted typing is not timing evidence.

US1 TDD: original extended backend run failed 3 / passed 16: two input-order regressions and representable row-product overflow (ZeroDivisionError). After log-domain normalization and independent ranks, 19 backend tests passed (54.26s). New helper import failed before reconciliation existed; all six helper tests then passed.
Browser harness: initial JSON import and API hot-reload connection problems corrected. Locale now selected through the actual language control; two Persian happy-path browser tests passed before the expanded suite.

US1 browser: six bilingual entry/reorder/reload scenarios passed, followed by two 2/3/6 result-display scenarios. Actual result order/rank/decimal/percent and html direction checked.
US2: 30 backend tests passed; client-inference source regression failed then passed after removing client CR threshold helper/default consistency. Two bilingual circular-warning/revision scenarios passed (16.1s), each asserting one persisted inconsistent run followed by a second consistent run.
US3 TDD: 9 failed /55 passed backend; string coercion, exact diagonal, non-string names, huge integer conversion and unrepresentable output regressions. Both browser cell-association checks failed at aria-invalid before fix. After fixes: 64 backend passed, 2 bilingual keyboard/blank/nonpositive browser scenarios passed (17.4s). JSON NaN rejected at parser with parse_error; service nonfinite values yield decision_input_invalid/non_finite. Backend Persian messages added through existing gettext catalog and compiled.

US3 supplemental: 14 localized API tests passed, checking English/Persian messages differ; four bilingual malformed diagonal/reciprocal browser cases passed (18.7s). Diagonal remains visible, read-only and focusable when invalid.
US4 TDD: four backend regressions failed (raw normalization, incomplete ranking rejection, stale overwrite, missing filter), then 23 API/immutability tests passed (10.71s). Four browser history/lifecycle scenarios initially failed on missing independent history controls, then passed (26.4s): 12 AHP runs plus a SAW run, method filter before paging, frozen result/matrix separate from edited draft, and deliberately held old case/run responses. Tenant double-scope, foreign immutable endpoints and legacy sorted row preservation covered by API tests. Models unchanged.
Interim typecheck: no decision-support errors after repairing translation callback typing. Five errors remain in unchanged daily-report-view.tsx, project-list.tsx (2), ManualProgressDrawer.tsx and KickoffCharterPanel.tsx; final verification will report them separately.

Final hardening: new retained-null-diagonal helper regression failed then passed without silently repairing malformed state. JSON exponent 1e400 initially caused PostgreSQL DataError; a red API regression reproduced it. Draft-number validation now returns non_finite at ahp_matrix.0.0 before storage while allowing incomplete/nonpositive drafts for execution validation. Finite cyclic 1e308 inputs yield coded non_finite at ahp_matrix with no run. Full backend rerun: 115 passed (19.56s), exit 0. Node rerun: 40 passed, exit 0.
Ten-criterion browser regression failed in both languages because the workspace grid expanded instead of scrolling. min-width correction confines the table to its editor; both keyboard preset/horizontal-navigation cases passed (16.5s).
Browser authentication uses one real worker login and isolated per-test browser contexts/projects; production rate limiting stays enabled. The earlier 22-scenario full run passed (1.2m); final expanded suite is running.

## Final verification

| Gate | Command (repo root unless stated) | Result |
|---|---|---|
| PostgreSQL API/service regression | API core cwd; source root .env, then ../.venv/bin/python -m pytest decision_support/tests -q --reuse-db | 115 passed, exit 0, 19.56s |
| Frontend helpers/source/locale | node --experimental-strip-types --test apps/web/src/components/decision-support/*.test.ts | 40 passed, exit 0 |
| Bilingual real browser | pnpm exec playwright test --config apps/web/e2e/playwright.config.ts decision-ahp.spec.ts --trace on | 26 passed, exit 0, 1.4m |
| Typecheck | pnpm typecheck | exit 2; five existing errors outside decision support |
| Migration dry-run | bash apps/api/django.sh makemigrations decision_support --check --dry-run | No changes detected, exit 0 |
| Diff hygiene/model preservation | git diff --check; git diff --exit-code -- apps/api/core/decision_support/models.py apps/api/core/decision_support/migrations | exit 0 |

Final browser run used the existing native services and an owned local API started with bash apps/api/django.sh runserver 127.0.0.1:8000 --noreload --nothreading. The prior threaded development server accumulated 97 idle PostgreSQL connections and caused three infrastructure failures after 20 passing scenarios. Restarting only that owned process reduced the development DB count to one; the complete 26-scenario rerun passed. No DB reset, global settings change or rate-limit disablement.

Typecheck errors remain at daily-report-view.tsx:198, project-list.tsx:30 and :37, ManualProgressDrawer.tsx:171, and KickoffCharterPanel.tsx:78. All four files match HEAD and no dependencies were changed. No decision-support error is reported.

Screenshots of English and Persian result tables were visually inspected: localized labels/status, coherent named row/column identity, decimal/percent/rank display and LTR/RTL layout. Traces retained for every browser scenario. Stub/legacy browser responses use explicitly substituted historical fixtures; real API frozen-history and legacy-row preservation are separately asserted in pytest.

Retained local logs, screenshots and traces: /tmp/ahp-validation-20261011-w11qg8_6. Browser tests remain reproducible in apps/web/e2e/tests/decision-ahp.spec.ts.

| Requirements | Evidence |
|---|---|
| FR-001–FR-004, SC-002 | Geometric mean/input-order/ties/n=1..10, full RI, CI/CR threshold/circular and finite-output pytest fixtures |
| FR-005, SC-003 | Strict types/shape/exact diagonal/product residual/JSON range, coded paths/no records; keyboard-linked bilingual errors |
| FR-006–FR-008, SC-004 | AHP-only API/browser, raw/incomplete ranking drafts and stale-field preservation, whole snapshot/result/actor/time immutability |
| FR-009–FR-013, SC-005 | Persisted inconsistent run, fraction/custom/out-of-scale/clear/reorder/rename/remove/reload, server-derived display/advisory |
| FR-014–FR-015, SC-006–SC-007 | Source audits fail on missing targets, complete static AHP key/interpolation checks, 13 browser scenarios per language including keyboard/ten-column scroll |
| FR-016 and tenant/permission scope | Mixed paginated history, filter validation before pagination, double-scoped IDs, read-only history and delayed response guards |
| SC-001 / T041 | Pending: no observed human four-criterion workflow time supplied |

41/42 tasks complete. T041 stays unchecked. Existing requirements checklist is read-only and remains 16/16. No extension hooks registered (before/after checks); original spec and refreshed plan were preserved during implementation. O05 advisory and O06 reciprocal entry remain interim decisions. No commits, pushes, deployment or production verification. No claim of ORM/database append-only enforcement.

## Convergence implementation (2026-10-11)

Evidence directory: /tmp/ahp-convergence-20261011-124lk_fl. T043: 13 new API/service localization regressions failed before the template/catalog fix, then all 13 passed (4.29s); stable codes/paths and zero invalid runs asserted. Existing ranking coercion remains unchanged.

T044: missing request-failure helper regression was red; both English/Persian browser scenarios failed because no alert appeared on a rejected save. After general-error fallback/localization: 12 helper checks and two browser scenarios passed (20.7s), covering save/run 403/404/429/non-JSON 500, global case-save feedback, zero failed runs and successful recovery. Field issues and late-response guards retained.

T045: both browser tests failed with browser/app locale mismatches, then both passed (21.5s) after using the application language for history dates. English with fa-IR browser and Persian with en-US browser, live language switches, list/viewer agreement and unchanged extracted_at are asserted.

T046: English/Persian real typing regressions both failed at Ax instead of Axyz. Stable row keys fixed the remount. The first rerun exposed an LTR-arrow assumption in the Persian test, corrected to RTL logical movement. Four new/existing rename/reorder tests then passed (22.4s), asserting focus/caret, insertion/backspace, blank renamed pairs and preserved surviving comparisons after removal.

T047: three representable-range regressions failed (service cyclic sum, overflowing individual ratio with representable mean, HTTP persisted run), while three valid guard/baseline checks passed. Scaled mean contributions with fsum fixed arithmetic. The API freeze check was corrected to compare persisted JSONB before/after rather than in-memory floats against PostgreSQL numeric canonicalization. Seven checks then passed, including genuinely unrepresentable weights/mean coded rejection, successful inconsistent HTTP 201 and unchanged frozen record after case edit.

T048: six root-path regressions failed /six existing shape cases passed, then all 12 service/API cases passed after a generalized localized square-matrix root issue. Wrong counts, ragged lengths and non-list rows retain row detail, localized root messages and zero runs.


### Final convergence verification

| Gate | Result | Evidence |
|---|---|---|
| Full PostgreSQL decision_support pytest | 145 passed; exit 0; 32.36s | final-api.log |
| Decision-support Node helper/source/locale checks | 50 passed; exit 0 | final-node.log |
| Full real-browser AHP suite | 32 passed; exit 0; 2.2m; 16 scenarios per language | final-browser.log and 32 retained traces |
| pnpm typecheck | exit 2; five errors outside decision support; no AHP error | final-typecheck.log |
| Decision-support migration dry-run | No changes detected; exit 0 | final-migrations.log |
| Diff hygiene and model/migration preservation | git diff --check and scoped git diff checks exit 0 | current working tree checks |

Raw command logs, before/after regression logs, final screenshots and all 32 traces are retained at /tmp/ahp-convergence-20261011-124lk_fl. Commands preserve the test process exit before displaying log tails. Final browser checks ran against the refreshed owned API with --noreload --nothreading and existing native PostgreSQL/Redis; no DB reset, dependency upgrade, rate-limit disablement or new schema/permissions.

Typecheck errors remain at daily-report-view.tsx:198, project-list.tsx:30/:37, components/progress/ManualProgressDrawer.tsx:171 and components/projects/KickoffCharterPanel.tsx:78. Scoped git diff verifies these four files are unchanged. They are outside this feature's fixes.

T043–T048 are completed with failing regressions followed by green targeted and full-suite verification. 47/49 task markers are complete. T041 and T049 remain unchecked: the user replied "I can't" to the requested human timing exercise, so SC-001 is unavailable, not passed. No scripted typing/engine metric substitutes for that acceptance evidence.

Hashes verify spec.md, plan.md, constitution, models.py and the requirements checklist are byte-identical to the start of this implementation turn. Existing unrelated/planning work is preserved. Before/after extension-hook checks found no .specify/extensions.yml, so hooks are skipped. No commit, push, deployment, production verification or claim of DB-level append-only enforcement.
