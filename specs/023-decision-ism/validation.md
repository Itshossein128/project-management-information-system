# ISM implementation validation

Started 2026-10-12 on `develop`. Existing AHP work retained; baseline hashes and source copies: `/tmp/ism-implement-ybpjr292` (local evidence, not committed). Active feature `023-decision-ism`. Requirements checklist 16/16 checked; never changed by implementation.

Environment: PostgreSQL 5433 accepts connections; Redis PONG. API Python 3.12.3 / Django 4.2.11; existing Playwright chromium-desktop config. No dependencies installed, no DB reset, no DEMATEL dependency.

Reference contract: single diagonal0/1, zero, chain C/B/A, diamond D/(B,C)/A, disconnected, two/three/multiple cycles, ten-chain/ten-cycle; literal expectations plus test-only traversal oracle independent of Warshall.

## TDD and verification evidence

- T001,T002,T003: Setup completed; source/hash baseline retained; PostgreSQL/Redis ready; reference fixtures fixed before implementation.

- T004,T005: Validator behavioral red: 3 binary-range assertions failed, 21 passed (/tmp/ism-validator-behavior-red.txt); added exact binary guard; final 24 passed.

- T006,T007: Draft behavioral red: Infinity reached PostgreSQL invalid JSON and matrix-only correction revalidated unrelated cost-zero ranking (/tmp/ism-draft-red.txt); finite guards/isolation fixed; strict/draft/AHP API combined 61 passed (/tmp/ism-draft-green.txt).

- T008,T009,T010: Browser red: global save enabled during AHP PATCH, view-only title writable; /tmp/ism-coordinator-red.txt and /tmp/ism-permission-red.txt. Added route token gate, frozen mutation variables, narrow adapters, read-only fieldsets. Foundation browser 2 passed (/tmp/ism-foundation-green.txt); permission presentation mock is supplemental, real API denial remains later. Typecheck has five unrelated pre-existing errors, no Decision Support errors (/tmp/ism-typecheck-foundation.txt).

- T011: Existing AHP browser regression 30 passed, 2 scroll failures after fieldset wrapper; added min-w-0, targeted EN/FA ten-criterion 2 passed (/tmp/ism-ahp-scroll-green.txt). Shared foundation completed. Full final-tree browser suite remains final check.

- T012,T013,T017,T018,T019: Engine behavioral red: 10 reference/oracle cases failed (/tmp/ism-service-red.txt); API stub/stale/deselected/deleted 4 failures (/tmp/ism-api-red.txt). Added pure Boolean Warshall, active-set layers, maximal groups and ISM-only scoped atomic lock/reload. Focused domain/AHP/immutability 83 passed (/tmp/ism-engine-green.txt); actual PostgreSQL wait_event_type=Lock and defensive no-progress versus valid cycle checks 2 passed (/tmp/ism-lock-green.txt). Reference oracle exhausts 512 three-node inputs. API dispatch other methods unchanged.

- T014,T015,T016,T020,T021,T022,T023,T024,T025,T026,T027,T028: Frontend rules behavioral red 5 failures (/tmp/ism-frontend-rules-red.txt), minimal defaults/edit/validation/guard now 5 passed (/tmp/ism-frontend-rules-green.txt). New pure ism-result-rules.ts re-exported by API keeps Node tests independent of browser-only alias transport; no client derivation. Browser missing panel red (/tmp/ism-entry-browser-red.txt); EN/FA chain/diamond/zero/both single diagonals now 2 scenario groups (10 networks) passed (/tmp/ism-entry-browser-green.txt). Restarted prior no-reload local API so live browser uses current engine. Fixed JSX syntax and typed unknown state updater. US1 MVP checkpoint completed; full feature acceptance outstanding.

- T029,T030,T031,T032,T033,T034,T035,T036,T037,T038,T039,T040,T041,T042,T043: Draft recovery red: scalar ism_matrix crashed list() (/tmp/ism-recovery-red.txt); preserved raw value via deepcopy. Test-only migration RBAC catalog fixture prevents reused transaction DB losing role fixtures; no dev DB reset. API/recovery/AHP 49 passed (/tmp/ism-recovery-green.txt). Remap/operation metadata behavioral red 2 failed (/tmp/ism-remap-behavior-red.txt); helper/named-list/issue regression 20 passed (/tmp/ism-remap-green.txt). Browser red: ISM issue not clickable (/tmp/ism-draft-browser-red.txt); EN/FA blank correction/rename/move/add/remove now 2 passed (/tmp/ism-draft-browser-green.txt), including real saved directed matrices. Existing Ism panel failure handling is regression checked rather than manufactured red. Persian new messages compiled with msgfmt --check.

- T044,T045,T046,T047,T048,T049,T050,T051,T052,T053,T054: Named-pair feedback browser red (/tmp/ism-named-error-red.txt) now EN/FA 2 passed (/tmp/ism-named-error-green.txt). Invalid/network/save/run recovery EN/FA 2 passed (/tmp/ism-failure-browser.txt). Expanded cycle/invariant and immutable-run regression 44 passed (/tmp/ism-history-backend-green.txt); structural group guard 2 tests passed (/tmp/ism-groups-guard-green.txt), already correct after US1. Missing group display browser red (/tmp/ism-history-browser-red.txt); server group presentation, accurate interpretation and frozen viewer now EN/FA 2 passed (/tmp/ism-history-browser-green.txt). Frozen old snapshot/result/actor/time unchanged after edit/rerun/lang; legacy stub unavailable, generic history reused.

- T055,T056,T057,T059,T060,T063,T064: US4 access API plus no-view-math: 18 passed in /tmp/ism-access-green.txt. Locale/frontend analysis audits: 11 passed in /tmp/ism-locale-source-green.txt. Real EN/FA keyboard ten-axis, native ArrowDown/Tab/error focus, localized layer 10/date and unchanged frozen payload: 2 passed; viewer API/browser 2 passed (/tmp/ism-us4-browser.txt). Existing correct enforcement/focus/locale behaviors recorded as regression; delay assertion correction is test-only, not behavioral red.

- T058,T061,T062,T065,T066,T067: Delayed AHP/SAW/TOPSIS/global/ISM PATCH conflict scenarios and old ISM POST response vs newer case gate: 2 EN/FA passed in /tmp/ism-delays-green.txt. Duplicate native disabled clicks generated one PATCH, every cross-method action/editor was disabled, real returned snapshots remained frozen and newer case/result/gate stayed isolated. SAW/TOPSIS real mixed-method runs returned ok. Actual viewer/browser denial and keyboard/date/RTL proof from /tmp/ism-us4-browser.txt plus API18 green; previous draft/failure flows provide all criterion-operation and request-error coverage. No new authorization permission or fake regression red.

- T068: Updated endpoint and schema guidance for implemented ISM and DEMATEL-only stub, binary draft vs execute validation, immutable structural output and scoped existing permissions. Quickstart now uses all helper tests, reuse-db catalog fixture and a self-contained browser timing metadata collector.

- T069,T070,T071,T073: Final backend 200 passed (38.08s), final Node helper/guard/key/analysis audits 66 passed, msgfmt --check exit0 (existing missing-header warnings), makemigrations --check --dry-run exit0 No changes detected, Python3.12.3/Django4.2.11. Typecheck exit2 with five confirmed unchanged errors outside Decision Support: daily-report-view.tsx198, project-list.tsx30/37, ManualProgressDrawer.tsx171, KickoffCharterPanel.tsx78. Logs /tmp/ism-final-{backend,frontend,typecheck,locale,migrations,versions}.txt. New expanded case-switch test then found duplicate method keys; final browser/Node/type evidence will follow that route-only fix.

- T061: Expanded all-five late-case test exposed real duplicate SAW/TOPSIS panels because method siblings shared project:case React keys (/tmp/ism-method-key-red.txt). Added method suffixes to all panel keys; all AHP/SAW/TOPSIS/global/ISM old-response vs newer pending-case scenarios now EN/FA 2 passed (/tmp/ism-method-key-green.txt). New disconnected/three-cycle/two separate groups browser references EN/FA 2 passed (/tmp/ism-extra-us4-green.txt). Final combined 54-case browser run started after key fix.

## Initial implementation verification (T001–T076)

All production changes, including distinct method/case React keys, preceded this final combined browser run. Retained logs are under [evidence/](evidence/). No automatic commit, push, deployment or human sign-off occurred.

| Category | Final outcome | Evidence |
| --- | --- | --- |
| PostgreSQL Decision Support | 200 passed; exit 0; 38.08 seconds | [backend.txt](evidence/backend.txt) |
| Frontend helpers, structural guards, keys and analysis boundaries | 66 passed; exit 0; after method-key fix | [frontend.txt](evidence/frontend.txt) |
| Typecheck | Exit 2; five existing errors outside Decision Support, zero Decision Support diagnostics | [typecheck.txt](evidence/typecheck.txt) |
| Real Chromium | 54 passed; exit 0; 3.9 minutes; 32 AHP plus 22 ISM tests/scenario groups | [browser.txt](evidence/browser.txt) |
| Backend Persian compilation | msgfmt --check exit 0; three existing missing header metadata warnings | [locale.txt](evidence/locale.txt) |
| Migrations/runtime | No changes detected; exit 0; Python 3.12.3 / Django 4.2.11; no install or schema reset | [migrations.txt](evidence/migrations.txt), [versions.txt](evidence/versions.txt) |
| Whitespace/new-file formatting | git diff --check and installed Prettier 3.8.4 --check exit 0 | [whitespace.txt](evidence/whitespace.txt), [format.txt](evidence/format.txt) |

Final browser report: `apps/web/e2e/reports/index.html`; all 54 successful test traces retained beneath `apps/web/test-results/` as `trace.zip`. Failure/network/delay interception supplements persisted real API scenarios; the actual viewer identity and bypass requests also use the real backend. The complete existing AHP suite passed after shared editor/coordinator changes. SAW and TOPSIS returned actual successful mixed-method runs in each locale; DEMATEL remains the tested server placeholder.

The expanded late-case test caught a real duplicate-panel regression: sibling method panels used identical project/case keys. [Behavioral red](evidence/method-key-red.txt) and [focused green](evidence/method-key-green.txt) retain the defect and the method suffix fix. Five old operation types (AHP, SAW, TOPSIS, global save, ISM) now return without changing the newer case's judgments/result or releasing its pending gate. Initial running-label assertions and resource URL mismatches were test instrumentation corrections, not implementation red.

## SC-008 visible-result measurement

The table and raw primary artifact now reflect the final T080–T081 combined run. Original T001–T076 samples are preserved in [pre-convergence-performance.json](evidence/pre-convergence-performance.json); T077–T079 samples are preserved in [phase8-performance.json](evidence/phase8-performance.json).

Browser resource `startTime` for the actual execution POST through browser monotonic time after the matching returned-run layer became visible. Preparation, draft PATCH and criterion entry are excluded. Automation visibility polling is included. Each locale has ten single, ten sparse ten-node chain, ten branching ten-node and ten dense ten-node cycle trials. Raw durations, all run IDs, error/failure fields, timing boundary and collected OS/CPU/memory/Node/Chromium/Python/Django/PostgreSQL versions and database counts are in [validation-performance.json](validation-performance.json).

| Locale | Trials within 2000 ms | Failures | Median ms | p95 ms |
| --- | --- | --- | --- | --- |
| en | 40/40 | 0 | 101.1 | 196.0 |
| fa | 40/40 | 0 | 107.8 | 201.5 |

Normal conditions here mean the running local Vite and single-process Django `runserver --nothreading`, one Playwright worker, loopback HTTP and no artificial latency/throttling. Each trial appended a real run. These results establish the bounded local acceptance criterion, not production, mobile, other-browser or all-network latency. The initial instrumentation attempted the setup host URL rather than the browser's actual response URL; all 80 analyses succeeded but timings were unavailable. That invalid measurement remains in `/tmp/ism-timing-instrumentation-failure.json` and is excluded from the corrected final samples.

## Requirement reconciliation

| Requirements/outcomes | Behavioral evidence |
| --- | --- |
| FR-001 / SC-001 | ISM-only API and persisted EN/FA single/chain/diamond/zero reference scenarios; no ranking inputs or dependent engine |
| FR-002–FR-003 / SC-003 | Strict names/count/shape/native numeric binary validator tests; nonfinite/overflow/text/bool/fraction/blank issues; API failures append zero; valid zero/cycles accepted |
| FR-004 | Finite incomplete/invalid save/reload and deliberate correction; independent opposite cells; keyboard typing and rename/move/add/remove directed-axis remapping; actual aligned saved matrix |
| FR-005–FR-008 / SC-002 | Literal references, separate traversal oracle over all 512 three-node matrices, ten-chain/ten-cycle; exact identity/closure, simultaneous active-set extraction, membership once, at most n levels; direct inputs unchanged |
| FR-009–FR-011 / SC-004 | Maximal two-/three-/ten-node and separate cycle groups; disconnected/same-layer nodes not grouped; persisted browser groups/direct/derived matrices and translated structural/no-removal explanations |
| FR-012–FR-014 / SC-005 | Distinct immutable append-only snapshots with frozen names/direct/derived/layers/groups/actor/time; edit/rerun/language/history equality; unrelated method inputs/results preserved; no implicit ranking or execution |
| FR-015 | Named pair focus and correction; malformed retained JSON reset; actual validation denial and intercepted save/run 403/404/429/non-JSON/network failures preserve drafts with no stale displayed success; defensive no-progress error |
| FR-016 / SC-007 | Real viewer/read permission plus denied create/PATCH/POST, no-view override/unauthenticated/nonmember/foreign case and nested run; zero new runs/data disclosure; existing creator/administrator policy, read-only mixed-method browser controls |
| FR-017 / SC-006 | EN/FA labels/options/errors/direction/layer numbers/date formatting; switched locale leaves method IDs, stored names, memberships, actor and timestamp unchanged |
| FR-018 / SC-006 | Native keyboard ArrowDown/Tab/Enter, stable multi-character typing/caret, ten-axis horizontal navigation, all criterion operations and directed error focus; each mixed-method/global pending gate and each late case response tested in EN/FA |
| SC-008 | 40/40 within two seconds per locale in documented normal local environment; final raw monotonic browser timings above |

Source/key audits and test counts supplement this behavior; they alone do not prove mathematical correctness, permission enforcement or keyboard/timing acceptance. No separate human usability sign-off is claimed. The older AHP human timing tasks remain as originally recorded; this implementation does not alter them.

## Scope preservation and completion

[evidence/preservation.json](evidence/preservation.json) compares all 2663 baseline files: none removed, 28 intentionally changed. All 42 protected decision source/specification/plan/research/model/contract/checklist and earlier AHP/DEM feature files are byte-identical, including their existing dirty work. Changed shared files are limited to ISM validation/execution/draft isolation, test support, localized presentation, criterion operation metadata, frozen viewer and method/permission/operation adapters. Existing AHP math and reciprocity and SAW/TOPSIS math remain unchanged. No dependency file or migration changed. No tracked file outside this bounded list changed during implementation.

The four typecheck failure source files are byte-identical to the implementation baseline. Typecheck remains a failed repository check, although it reports no Decision Support error. Backend warnings concern existing ReportLab/pandas dependencies; the local Redis rate-limit support warning is also pre-existing.

Post-implementation hooks checked: `.specify/extensions.yml` absent, so no hooks to execute. Checklist markers remained read-only. Final task and relative artifact links checked; no task gaps remain within this feature's automated acceptance scope.

- T072,T074,T075,T076: Final 54-browser combined suite passed after all production changes; all 80 visible-result timing trials passed. Final FR/SC mapping and limits, 42 protected files unchanged among 2663 baseline files, 28 scoped changes/no removals, typecheck attribution, final logs, whitespace/format and absent after_implement hooks recorded in validation.md and evidence/. No commit/push/deployment.

- T077: RED: EN/FA current-case reselect enabled title during pending request. GREEN: focused browser run 6 passed (36 new method/phase/navigation cases across EN/FA plus delayed mixed and late-case regressions), /tmp/ism-t077-red.txt and /tmp/ism-t077-green.txt. Pending identities are now retained per case and returning cases hydrate committed saved state after release.

- T078: RED: 4/5 root-null PostgreSQL tests failed (create/general coercion, matrix-only IntegrityError, AHP snapshot coercion); persisted JSON-null execution rejected correctly. GREEN: 62 ISM/AHP API and immutable-run tests passed, plus EN/FA root-null save/reset/correct browser scenarios (2 passed). JSON null is deliberately retained using JSONField Value storage and frozen snapshots preserve raw drafts; no migration/dependency change. Logs /tmp/ism-t078-red.txt, /tmp/ism-t078-green.txt, /tmp/ism-t079-red-browser.txt.

- T079: RED: all four EN/FA committed-run lost-response/history success-or-failure scenarios exposed enabled same-case title/save during held history recovery. GREEN: 10 focused failure/null/recovery scenarios passed, including EN/FA ten-second bounded timeout and case B isolation; final 64 combined ISM/AHP browser tests passed with 80/80 visible-result timing trials. Recovery now holds the captured-case gate through one bounded authoritative history fetch, retains case-specific localized feedback across navigation, and never automatically retries POST. Final backend 205 passed, helpers 66 passed, no migration changes; typecheck has the same five unrelated baseline errors. Final logs retained under evidence/convergence-*.txt.


## Phase 8 implementation verification (T077–T079)

All 79 tasks available in Phase 8 were checked. The original implementation evidence above remains available; this section records that phase after the first three convergence fixes. The current final verification is recorded in Phase 9 below. Requirements, plan, research, contracts and reviewer checklist were not changed.

| Check | Final result | Retained evidence |
| --- | --- | --- |
| PostgreSQL Decision Support tests | 205 passed, exit 0, 43.43 seconds | [backend](evidence/convergence-backend.txt) |
| Frontend helpers, guards, localization and calculation boundaries | 66 passed, exit 0 | [frontend](evidence/convergence-frontend.txt) |
| Combined Chromium desktop EN/FA ISM/AHP | 64 passed, exit 0, 5.3 minutes; 32 AHP and 32 ISM scenario groups | [browser](evidence/convergence-browser.txt) |
| Visible-result timing | 40/40 within 2000 ms in each language, zero failures | [Phase 8 raw timings and environment](evidence/phase8-performance.json) |
| Migration dry run | Exit 0, no changes detected | [migrations](evidence/convergence-migrations.txt) |
| Typecheck | Exit 2, same five unrelated errors in four unchanged files; no Decision Support errors | [typecheck](evidence/convergence-typecheck.txt) |
| Scoped TypeScript formatting / tracked whitespace | Exit 0 | [format](evidence/convergence-format.txt), [whitespace](evidence/convergence-whitespace.txt) |

- **F1 / T077 closed (FR-018, US4/AC5):** The per-case pending token survives both current-case reselection and A→B→A. Thirty-six new held-request scenarios cover both languages, all four methods' PATCH/POST and global PATCH; returning cases hydrate their committed row after release. Another case remains independent, and the combined suite retains old-response isolation and frozen history access. [Behavioral red](evidence/convergence-t077-red.txt) → [focused green](evidence/convergence-t077-green.txt).
- **F2 / T078 closed (FR-004/FR-015, US2/AC1/AC6):** Explicit root null remains JSON null on create, matrix-only and shared PATCH. Persisted JSON-null drafts reject execution with `dimension_invalid` at `ism_matrix`, append zero runs, and recover by explicit correction. AHP execution retains that unrelated malformed ISM draft in its immutable snapshot. Both languages save the raw null and explicitly reset/correct it before a successful run. Missing-field and legacy-empty initialization and unfinished null cells remain covered. [PostgreSQL red](evidence/convergence-t078-red.txt) → [62 focused regressions](evidence/convergence-t078-green.txt), then final API/browser suites.
- **F3 / T079 closed (FR-015, US2/AC6):** Tests forward the POST to the real server, verify its 201 committed ID, then abort only the response. One bounded authoritative history read occurs while the case stays locked. Successful recovery exposes the committed history entry; HTTP failure or a ten-second timeout gives explicit EN/FA unresolved-history feedback. Drafts persist, current results clear, another case can run, and no POST repeats until the user explicitly retries. Recovery feedback is cached by project/case across panel navigation. [Behavioral red](evidence/convergence-t079-red.txt) → [10 focused scenarios](evidence/convergence-t079-green.txt), then final combined suite. The first green attempt needed an explicit test locale selection after reload; this was fixture correction, with no corresponding application change.

Recovery inspects history; it does not claim an idempotency or server revision guarantee. An explicit retry can create another run, as verified by the retained tests. Timing evidence remains limited to the documented local environment. No human usability sign-off, production or other-browser claim is made.

[Convergence preservation](evidence/convergence-preservation.json) compares 2691 baseline files, with no deletions and only the listed scoped changes. All 42 protected decision documents, feature requirements/design/contracts/checklists and earlier AHP/DEMATEL artifacts remain byte-identical. The four sources of existing typecheck errors and dependency/migration files remain unchanged. Original evidence logs are retained. Checklist markers were read-only; no dependency installation, database reset, commit, push or deployment occurred.

Mandatory post-implementation hook check: `.specify/extensions.yml` is absent, so no `after_implement` hooks are registered. [Completion checks](evidence/convergence-completion.json) retain task, checklist, link and preservation assertions.

- T080: Behavioral RED: Node parsing assertion Missing expected rejection; EN/FA malformed PATCH continued to POST (permission denial from intercepted unexpected POST), and malformed POST 201 unlocked title while held history GET remained pending. GREEN: all 4 malformed-response browser groups passed (32 EN/FA phase/corruption combinations including empty/html/truncated/null/object/identity/snapshot/result; each run commits exactly once), 6 focused API/guard tests and 70 helper tests passed. Prior focused run passed all 12 existing AHP/ISM denial/network/bounded-recovery groups. Test alert locator and request synchronization were corrected without additional application changes. Logs /tmp/ism-t080-red-{node,browser}.txt, /tmp/ism-t080-green-{node,helpers,malformed}.txt.


## Final Phase 9 implementation verification (T080–T081)

All 81 ISM tasks are checked. Both new convergence findings have behavioral red → minimal fix → green evidence. Final checks below ran after all application changes; prior phase evidence remains retained separately.

| Check | Final result | Retained evidence |
| --- | --- | --- |
| PostgreSQL Decision Support | 205 passed, exit 0, 40.81 seconds | [backend](evidence/phase9-backend.txt) |
| Frontend helpers, response guards, localization and calculation boundaries | 70 passed, exit 0 | [frontend](evidence/phase9-frontend.txt) |
| Combined Chromium desktop EN/FA | 78 passed, exit 0; 32 AHP plus 46 ISM scenario groups | [browser](evidence/phase9-browser.txt) |
| Visible-result timing | 80/80 within 2000 ms, zero failures; EN p95 196 ms, FA p95 201.5 ms | [raw timing/environment](validation-performance.json) |
| Migration dry run | Exit 0, no changes detected | [migrations](evidence/phase9-migrations.txt) |
| Repository typecheck | Exit 2, five unchanged errors in four unrelated files; zero Decision Support diagnostics | [typecheck](evidence/phase9-typecheck.txt) |
| Scoped formatting / tracked whitespace | Exit 0 | [format](evidence/phase9-format.txt), [whitespace](evidence/phase9-whitespace.txt) |

**F4 / T080 closed (FR-015/FR-018, US2/AC6):** Empty, HTML, truncated, null, empty-object, wrong-identity, missing-snapshot and invalid-result successful responses are covered for both save and execute in both languages: 32 phase/corruption combinations in four browser groups. Each corrupt run response follows a real committed POST. Successful HTTP bodies must parse as JSON; ISM saved metadata and completed run method/provenance/frozen binary input/structural result are guarded within the acquired operation. Unconfirmed saves keep the draft and send zero POSTs; unconfirmed run responses clear current output and hold the gate through bounded history recovery, including held and failed lookup. Tests verify no callback crash, no automatic duplicate and a subsequent explicit valid retry. Raw malformed drafts and unrelated method inputs remain supported; no scientific computation was added to the client. [Node parsing red](evidence/phase9-t080-red-node.txt), [browser red](evidence/phase9-t080-red-browser.txt) → [six focused guard tests](evidence/phase9-t080-green-node.txt), [four browser groups green](evidence/phase9-t080-green-malformed.txt), then all 70 helpers and the final combined browser suite. The first focused green attempt passed all 12 existing denial/network/recovery groups; ambiguous alert selectors and request synchronization in the new scenarios needed fixture-only corrections, not additional application fixes.

**F5 / T081 closed (FR-012/FR-013/FR-015, US2/AC6, US3/AC4):** Four real EN/FA filtered/page-two scenarios failed because successful recovery left the displayed filter at ISM instead of exposing the authoritative history. The panel now notifies the route only after its existing bounded history fetch succeeds; the route selects unfiltered page one only if that same case is currently selected. Localized feedback describes this visible transition. The fresh committed row and count become inspectable before manual retry. Failed reads retain the previous visible filter/page and give explicit unresolved feedback; late case A recovery cannot reset case B's filter/count or attach recovery feedback there. Frozen historical payloads remain byte-equal, inputs stay intact, and exactly one POST occurs before explicit retry. [Four behavioral failures plus six passing regressions](evidence/phase9-t081-red-browser.txt) → [all ten focused scenarios green](evidence/phase9-t081-green-browser.txt), then final 78 combined tests, including prior ten-second timeout and per-case pending regressions. Case-switch synchronization now waits for the browser's recovery response, rather than a separate API count poll.

[Phase 9 preservation](evidence/phase9-preservation.json) compares all 2738 files present at this implementation's start. No baseline file was deleted. Changes are limited to the response parser/guards, ISM panel, minimal history coordination, two localized recovery strings, tests and ISM completion evidence. All 42 protected decision requirements/design/contracts/checklists and earlier AHP/DEMATEL artifacts, every API file, AHP browser tests, dependency/migration files and four unrelated typecheck source files remain unchanged. Existing dirty work is preserved.

These results establish the documented automated local acceptance scope. Repository typecheck remains failed for the existing errors. Recovery does not supply idempotency or a server revision guarantee; explicit retry can append another run. No human usability, production, mobile or other-browser claim is made. Checklist markers stayed read-only. Mandatory after_implement hook check found no `.specify/extensions.yml`. No install, schema reset, commit, push or deployment occurred. [Completion assertions](evidence/phase9-completion.json) retain counts, links and scope checks.
