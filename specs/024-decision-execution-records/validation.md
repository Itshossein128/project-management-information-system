# Execution Records Implementation Evidence

Status: feature 024 implemented and verified; all 76 tasks complete.

## Setup

Checklist: 16/16 PASS (read-only). Cwd: building-management; branch: develop; selected feature: 024.
Baseline hashes and source copies: /tmp/records-implement-ntgv_z63. Existing dirty work protected.
Native PostgreSQL 5433 accepting; Redis PONG; API Python 3.12.3, Django 4.2.11. Existing ignores cover runtime/dependency outputs. No install/schema reset.

Evidence categories: meaningful behavioral red/green, PostgreSQL lock observation, API and pure boundary checks, bilingual browser scenarios and traces, final schema/type/scope checks, raw history timing. DEMATEL fixtures prove presentation only.

Foundation: literal independent inputs and browser setup/gates prepared; existing RBAC seed reused. Focused commands follow quickstart. Test-only fixture support has no live acceptance claim. Behavioral red excludes import/selector/setup failures.

## US1 checkpoint

[Backend behavioral red](evidence/backend-red.txt): 18 failures include stale inputs, selection/deletion and equal-time order; six fixture setup errors excluded. [Lock red](evidence/lock-red.txt): four non-ISM lock failures, ISM regression green; narrow per-transaction role seeding repaired test flush lifecycle. [Backend green](evidence/backend-us1.txt): 233 passed, including seven observed PostgreSQL wait cases and prior engines. PATCH/delete wait tests initially passed through incidental write/audit locking; explicit authoritative SELECT FOR UPDATE is additionally source-verified, not claimed as prior behavioral red. `update_case` still refreshes its supplied instance.

[Browser red](evidence/browser-red.txt) → [US1 green](evidence/browser-us1.txt): EN/FA stale SAW result clears on invalid input. US1 AC1–5 / FR001–007 / SC001,002,005 covered by parameterized independent dispatch, exact earlier-record equality, distinct reruns, known rejection zero append and existing input suites. No schema/engine changes; migration dry run clean. Full historical/uncertain/access and final timing proof remain open.

## Shared boundary work

[Rules red](evidence/rules-red.txt), [API boundary red](evidence/api-red.txt), [review red](evidence/review-red.txt) and [lifecycle red](evidence/lifecycle-red.txt) reproduced unsafe envelope acceptance/missing named review/three non-ISM panels continuing after null save. ISM remained regression. Shared guards distinguish partial history from new complete output; current/history separated. [Recovery red](evidence/recovery-red.txt) precedes the extracted bounded QueryClient read. No scientific calculation or historical rewriting. Completed DEMATEL presenter is fixture review only. SC004 final measurement remains outstanding.

## Integrated story evidence

US2 AC1–6: equal-time fixed UUID API pages cover ordering/counts/filter/rejection; actual read-boundary and partial classifiers distinguish corrupt envelope from unavailable sections. Bilingual frozen named ranking, legacy AHP order, ISM predecessor history and signed DEMATEL fixture presenters cover review. Delayed page/filter reads and failed new detail clear old ownership. Exact earlier record equality and immutable route denials cover retention. SC002/003 covered; final SC004 timing remains pending.

US3 AC1–4: literal backend fixture `[[1,3],[1,3],[3,1]]` with equal benefit weights produces SAW Alpha first and TOPSIS Gamma first, while preserving live inputs. Exact equal-input tie tests retain Alpha/Beta ordinal ranks. Browser stored disagreement fixtures and deselected method review perform zero mutations; AHP/DEMATEL legacy browsing does not transfer weights. FR012/019 and SC008 use independent stored outputs, never merged results or policy closure.

US4 AC1–6: real PostgreSQL viewer/no-view/unauthenticated/nonmember/foreign/corrupt run relation tests assert scoped access and unchanged records. Bilingual browser viewer uses a real account and role, keyboard ten-axis selection, language switching and revoked read. Four live-method adapters validate saves before POST, completed responses before callbacks, preserve drafts and disable retries. Lost-response scenarios forward real POSTs and capture committed IDs; held/failing/malformed/ten-second recovery and explicit subsequent attempts test token settlement. Captured A recovery leaves B's filtered history/pending save untouched. Prior AHP/ISM suites remain final regression gates.

Additional [presentation red](evidence/presentation-red.txt) → [green](evidence/presentation-green.txt) proves distinct no-match states and named ranking validation. Duplicate locale keys were removed; JSON key uniqueness checked in both languages. [In-flight recovery red](evidence/inflight-red.txt) reproduced real QueryClient deduplication of a pre-commit GET; recovery now cancels only the captured unfiltered first-page promise before one new forced-fresh read. The final Node suite includes this regression and rejects late timed-out completion.

Limits: separate browser PATCH/POST is not atomic, no revision/idempotency/exactly-once is introduced, explicit retry can append again, page-one absence does not prove no commit. Completed DEMATEL fixtures establish presentation only. Actor name remains current-account presentation, actor identity/time frozen. No production or human sign-off claimed.

## Final verification commands and attribution

- Backend: `set -a; source .env; set +a; cd apps/api/core; ../.venv/bin/python -m pytest --reuse-db decision_support/tests -q` → [backend.txt](evidence/backend.txt), **245 passed**, exit 0. Includes seventeen actual parent `FOR UPDATE` lock-wait cases across all five dispatch paths, targeted PATCH/delete and released selection/deletion rejection. `pg_stat_clear_snapshot()` avoids attributing cached PostgreSQL activity to the wrong statement. No dev database reset.
- Node: `node --experimental-strip-types --test apps/web/src/components/decision-support/*.test.ts apps/web/src/app/lib/api/decision-support.test.ts` → [frontend.txt](evidence/frontend.txt), **84 passed**, exit 0. Unknown-safe sections, zero versus absence, strict completion, actual transport, real QueryClient cancellation/deadline and existing no-client-math checks.
- Typecheck: `pnpm typecheck` → [typecheck.txt](evidence/typecheck.txt), exit 2: five existing errors in `daily-report-view.tsx`, `project-list.tsx` (two), `ManualProgressDrawer.tsx`, `KickoffCharterPanel.tsx`. Those four sources match the implementation baseline byte-for-byte; no Decision Support diagnostics. This is not a repository-wide passing typecheck.
- Schema: `bash apps/api/django.sh makemigrations --check --dry-run` → [migrations.txt](evidence/migrations.txt), exit 0, no changes detected. Models/serializers/migration and dependency files preserved. [versions.txt](evidence/versions.txt) records actual runtime.
- Catalogs: [locale.txt](evidence/locale.txt) compares unchanged PO/MO hashes; no fresh compilation claim. Frontend EN/FA JSON contains no duplicate keys and shared message keys pass Node checks.
- Browser: `pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/decision-execution-records.spec.ts apps/web/e2e/tests/decision-ahp.spec.ts apps/web/e2e/tests/decision-ism.spec.ts --project chromium-desktop --trace on` → [browser.txt](evidence/browser.txt). **130 passed**, exit 0, no skipped/unexpected/flaky tests; [structured report](evidence/browser-report.json). Earlier aborted/instrumentation/selector failures are not acceptance; original AHP keyboard error-button labels are preserved after its regression was detected.

## Final requirement reconciliation

All browser-dependent rows are now backed by the final combined run.

| Requirements | Concrete coverage |
| --- | --- |
| FR001 | Existing independent engine/API suites plus five-path authoritative tests; no prerequisite method |
| FR002 | Known invalid zero-append tests, named ranking feedback, existing AHP/ISM field focus and paths |
| FR003 | Scoped append, initiating identity/time, real committed IDs in loss-response browser cases |
| FR004 | Seventeen observed PostgreSQL lock waits; authoritative inputs/selection/deletion and targeted updates |
| FR005 | Raw plus engine-produced normalized weights and retained context; named ranking/criteria snapshots |
| FR006 | Exact all-field earlier-record equality, immutable routes, locale payload equality |
| FR007 | Identical/changed distinct append and explicit retry after settled uncertainty |
| FR008 | Fixed UUID/time exact pages/filter counts; 100-record complete traversal and history timing |
| FR009 | Labeled stable ID/method/actor/time historical region, no current-result assignments |
| FR010 | Frozen named axes and values after edits; GET-only browsing/counters, no derivation |
| FR011 | SAW/TOPSIS stored rows/distances, AHP CR/weights, ISM matrices/layers/groups, signed DEMATEL fixture review |
| FR012 | Real SAW/TOPSIS order disagreement, stable ties; separate labels/no combined result or transfer |
| FR013 | Null/partial snapshot/output, absent normalized weights, unavailable sections, actor identity fallback |
| FR014 | Global create/PATCH plus four live adapters reject malformed saves; cleared success and zero POST |
| FR015 | Real committed response loss, held/failed/malformed/timeout recovery, pre-commit GET cancellation, explicit retry |
| FR016 | Captured A/B tokens/reselection; detail generation across row/filter/page/case changes and failures |
| FR017 | Real viewer/no-view/nonmember/unauthenticated/foreign/corrupt relation; nested immutable mutations |
| FR018 | EN/FA keyboard history/ten axes/date formatting/messages, language-switched unchanged payload |
| FR019 | Existing AHP/ISM regression suites, legacy sorted AHP, stored ordinal ties/precision and DEMATEL policies |

| Outcome | Coverage |
| --- | --- |
| SC001 | Independent real engines/recorded IDs; no implicit other method |
| SC002 | Complete earlier-row equality after edit/rerun/rejection and immutable mutation denials |
| SC003 | Safe partial/null history, explicit unavailable input/output/normalization, no fabricated zeros |
| SC004 | Fresh final 160 history samples; 100 records, ten rows, complete each-method traversal; per-locale/category threshold |
| SC005 | Zero execution after malformed save, named invalid feedback and stale output clearing |
| SC006 | Held controls through recovery and deadline, visible committed ID, no automatic POST retry |
| SC007 | Real scoped access and bilingual keyboard review/locale payload equality |
| SC008 | Independent disagreement/tie/deselection results and unchanged ranking weights |

| Acceptance scenarios | Evidence category |
| --- | --- |
| US1 AC1 | Parameterized dispatch/provenance/one append; real browser success |
| US1 AC2 | Existing method-only APIs and no unrelated-input prerequisites |
| US1 AC3 | Invalid zero append, stale output clearing, named/focused fields |
| US1 AC4 | Complete frozen-row equality and distinct explicit reruns |
| US1 AC5 | Actual lock waits plus released input/selection/deletion state |
| US2 AC1 | Equal-time deterministic API pages and 100-record complete filters |
| US2 AC2 | Bilingual ranking frozen inputs/raw/normalized weights/results/distances |
| US2 AC3 | Legacy AHP, existing ISM matrices/groups and completed DEMATEL stored fixture |
| US2 AC4 | Exact prior-record equality after edits/reruns and own frozen labels |
| US2 AC5 | Partial/null/stub review; unavailable sections and no normalization synthesis |
| US2 AC6 | Scoped PUT/PATCH/DELETE denials and full row equality |
| US3 AC1 | Real backend order disagreement; independently labeled stored browser fixture |
| US3 AC2 | Equal-score original order and stored ordinal ranks |
| US3 AC3 | Live inputs unchanged by engines; zero browser review writes/weight transfer |
| US3 AC4 | Deselection retains GET-only filtered historical review |
| US4 AC1 | EN/FA keyboard ten-axis history and locale payload identity |
| US4 AC2 | Real viewer read success, disabled controls and direct mutation rejection |
| US4 AC3 | Real foreign/no-view/nonmember and double-scoped corrupt relation rejection |
| US4 AC4 | Malformed saves/completed responses, actual committed response loss, bounded read/retry behavior |
| US4 AC5 | Filtered recovery switches to matching authoritative all-method page one/committed row |
| US4 AC6 | A/B captured pending state and late detail generation guards |

All thirteen specified edge cases are covered by the rows above: distinct empty/filter/error recovery; equal-time complete traversal; unrelated raw drafts; renamed frozen axes; zero/null/absence; missing legacy normalization; AHP advisory inconsistency; ISM groups; DEMATEL stub distinction; unknown responses; explicit duplicate-capable retry; deleted/revoked/actor fallback/failed detail; locale/precision unchanged storage. The final combined browser run closes the presentation gate.

Constitution I–VII: server membership/permission/scoping retained; parent integrity/immutable rows and schema preserved; bilingual/browser gate; explicit disposable mutations/no retry/deploy; shared existing lifecycle/presenters; genuine red/green and final separate categories; native keyboard/named axes/locatable errors. No exception, new dependency or production-like action.

Final fixture-only augmentation adds literal ISM cycle/group classification coverage; existing browser fixture values and application source remain unchanged. Timeout-test instrumentation waits for the actual forwarded commit response before checking the bounded recovery interval; POST latency is not recovery time.

Primitive identifier hardening: [method ID red](evidence/method-id-red.txt) and [named-row/role red](evidence/row-ids-red.txt) reproduced coercible array values passing unknown-safe guards. Stable method IDs, stored names and role IDs now require strings before membership checks. Final Node suite is 84 passing tests.


## Final closure

Final Chromium run: **130 passed**, exit 0, one worker, zero skips/failures/retries. Actual final command additionally used `--reporter=list,json` and `PLAYWRIGHT_JSON_OUTPUT_FILE=/tmp/records-final-report.json`; the clean stdout and structured report are retained. Fifty-two new record cases plus 32 AHP and 46 ISM regressions passed. Traces are in the report attachment paths under `apps/web/test-results/`. Earlier interrupted/harness failures are excluded from acceptance.

SC004: [raw samples and environment](validation-performance.json): 160/160 trials within 2000 ms, zero failed trials. Forty page plus forty detail selections per locale; each prepared set has 100 records, 20 per method, with full all-method/each-method traversal. Page trials include nine network-backed and 31 cached selections per locale; detail trials are all network-backed. Nearest-rank p95: EN page 118.4 ms/detail 102.5 ms; FA page 115.2 ms/detail 104.8 ms. These are local selection-to-readable-history timings, not old calculation timings or a production/network guarantee.

Preservation: [audit](evidence/preservation.json) checks all 2766 baseline files, including unrelated dirty work, source docs, 018–023, protected 024 requirements/design/checklist, pure engines, model/serializers, migrations/dependencies and unrelated type-error sources. The older ISM timing JSON regenerated by its suite was archived as compatibility evidence here, then restored byte-for-byte from the baseline; it is not SC004 evidence. Shared route/API edits retain existing formatting conventions; new components/helpers pass Prettier, all changes pass whitespace checks.

The requirements checklist remains 16/16 and byte-preserved. No extension file exists, so before/after-implement hooks are skipped as instructed. No commit, push, deploy, database reset, dependency install, reviewer checkbox rewrite or human sign-off occurred. Prior feature human gates remain unchanged. DEMATEL engine and source O01/O02 remain outside this completion.
