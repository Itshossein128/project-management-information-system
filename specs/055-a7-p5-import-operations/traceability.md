# Traceability: A.7-P5 Import Operations

**Current status, 2026-11-13**: the rebuilt acceptance image (`sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`, schedule-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`) passed the 13-group matrix, broker restoration, two-importer duplicate delivery, 4/4 browser retry suite, 110 host pytest regressions, and `pnpm typecheck` both in the implementer run and in the clean independent second-operator reproduction (`T049` complete; all tasks `T001`–`T064` checked). See [verification](evidence/verification.md) and [independent reproduction](evidence/reproduction.md).

## Current observed evidence

- I09 / FR-001–004/006–008 / SC-001–003: `import_operations.py` claims/fences and atomically commits domain+DONE, independent real workers process both families, before/during/post-commit and failure-recording SIGKILL tests preserve rollback/one-time application. Retained native/admitted-failure/duplicate/worker-loss groups and broker-outage evidence identify attempts, deadlines and healthy follow-ups. Maintenance republish uses the bounded publication helper and keeps the original dispatch deadline. T017–T034/T051/T055/T057/T064.
- I19 / FR-009–012 / SC-004/006: original-byte purge after terminal+168h keeps action metadata/digest/results; ≥201 two-family rows drain; active/unexpired bytes and unrelated artifacts survive. Exact boundary tests cover both outcomes/families. Bilingual browser retry uses fresh upload and preserved predecessor; scratch resource cleanup runs against real private storage. T035–T043/T056/T061–T064.
- I20 / FR-005–008/010 / SC-001–004: narrow real cgroup controls, memory OOM, output/disk exhaustion, actual75s timeout and process death terminate helpers; subsequent imports work. Both native JPype and configured Java CLI convert the unchanged employer file with matching6/72/72 stored figures. Profile/settings, versions, source identity and resource observations are kept separately from inline regression evidence. T005/T012–T016/T026/T030–T034/T047/T048/T059/T060/T064.
- D02 / FR-013/014 / SC-005: private delivery image/services build/start, guarded preflight and real 13-group matrix pass; normal-user bilingual browser trials pass. `ops/a7-p5/README.md` and quickstart use actual commands/names and document isolation/rollback. A separately contextualized second agent operator completed the clean independent reproduction in `evidence/reproduction.md` (`## Fifth clean run`). T044–T050/T054/T064. This is local technical delivery rehearsal and independent agent reproduction, not production deployment or human/employer acceptance.
- Migrations: schedule `0016_import_operations_lifecycle` depends on `0015_periodreportfigure_version`; `0017_import_retry_related_name` follows0016. Additive schema and conservative legacy anchors preserve history; already purged bytes cannot be recovered by schema rollback.

## Authority and source distinctions

- User instruction: [phase prompt](../../output/a7-requirements-2026-11-10/speckit-prompts/05-import-operations.md), predecessor gate and acceptance section.
- Approved boundary: [R0](../../docs/delivery/R0-scope-and-reports-contract.md), section 1.2/reference fixtures; [delivery plan](../../output/delivery-plan-2026-11-03/delivery-plan.md), A.7.02; [reviewer corrections](../../output/delivery-plan-2026-11-03/reviewer-corrections.md), existing preview and CSV exclusions.
- Governance: [Constitution](../../.specify/memory/constitution.md), principles I–VI and quality gates.
- Historical findings: [audit report](../../output/a7-requirements-2026-11-10/report.md), I09/I19/I20/D02; [structured requirements](../../output/a7-requirements-2026-11-10/requirements.json). Historical statuses are neither current verification nor new stakeholder decisions.
- Current product decision: user selected seven days of original-file diagnostic retention, then deletion; recorded verbatim in spec Clarifications. Clock semantics in Assumptions are specification interpretations.

## I09 — Background job and progress

- Source need: [029 spec](../029-native-mpp-import/spec.md), FR-007/011; audit report lines 347–352.
- Expected behavior: independent processing with traceable progress and terminal outcomes; failures permit healthy subsequent imports.
- Design: US1/US2; FR-001–004/006–008; SC-001–003.
- Observed code: `apps/api/core/schedule/tasks.py:46–78` loads an attempt, skips done jobs, sets running/task identity, applies under a project lock, then separately records success. The commit-to-result interval identifies a recovery case to test, not a reproduced failure.
- Planned tasks: T017–T024, T025/T027–T030/T033 and T051–T053. Test evidence: source inspection only; actual broker/worker, interruption, duplicate delivery, and healthy retry remain unrun.

## I19 — Original and derived file lifecycle

- Source need: [029 spec](../029-native-mpp-import/spec.md), FR-019; audit report lines 417–422.
- Expected behavior: distinguish original bytes, temporary conversion artifacts, and action history; enforce seven-day terminal diagnostic retention and confidential access, then delete expired bytes without erasing accountability.
- Design: US3; FR-009–012; SC-004/006.
- Observed code: `apps/api/core/schedule/tasks.py:54` reads `job.file_data`; `apps/api/core/schedule/services/mpp_convert.py:154–157` creates temporary input/output. Normal temporary-directory cleanup is not restart cleanup proof. No explicit original-byte expiry rule was found in reviewed schedule/029 sources.
- Planned tasks: T009/T011, T035–T043 and T051–T053. Test evidence: source inspection only. Expiry boundaries, access isolation, repeated/restarted cleanup, active-input protection, and surviving history remain unrun. No real/shared file deletion authorized for testing.

## I20 — Time and resource bounds

- Source need: [029 spec](../029-native-mpp-import/spec.md), FR-020/SC-006; audit report lines 424–429.
- Expected behavior: excessive work actually stops, resources are released, no partial schedule persists, and later healthy work succeeds.
- Design: US2; FR-003–008/010; SC-001–004.
- Observed code: `apps/api/core/schedule/services/mpp_convert.py:34–35` has a configurable 60-second default; lines 107–114 wait on a daemon thread and raise if it remains alive. Lines 167–178 configure subprocess timeout; lines 208–227 choose JPype or Java fallback. Stopping the wait is not proof that Java work stopped; separate route bounds do not establish a combined bound.
- Existing [029 plan](../029-native-mpp-import/plan.md) describes 60 seconds and a 50 MB upload cap. These are design/configuration references, not a new SLA or demonstrated memory/output/concurrency control. Planning must resolve effective missing bounds.
- Planned tasks: T005/T012–T016, T026/T030–T034 and T051–T053. Test evidence: source inspection only; actual resource enforcement, combined fallback bound, interruption, and healthy subsequent import unrun.

## D02 — Delivery environment

- Source need: delivery plan A.7.02 and 029 FR-020; audit report lines 454–459. This is the audit's D02, not the delivery-plan communications decision with the same identifier.
- Expected behavior: actual employer-file preview/import using delivery configuration and independent processing, with reproducible versions, route, settings, and secret-free commands.
- Design: US4; FR-013/014; SC-005 and the full operational acceptance set.
- Observed sources: conversion routes above and [fixture README](../../apps/api/core/schedule/tests/fixtures/mpp/README.md). Existence is not runtime proof. P2/P3 handoffs explicitly exclude actual worker evidence.
- Planned tasks: T016, T044–T050 and T051–T054. Test evidence: none in this invocation. JRE/classpath/JPype/fallback inventory, actual broker/worker startup, real-file smoke test, failure matrix, and reproduction remain unrun.

## Knowledge retrieval interpretation

Hybrid retrieval was fresh but broad. The generic report-type question is inapplicable because the exact linked audit/phase prompt identifies this work. Its flagged `embedding_job` identifier was resolved by actual `cli.py status`, which reported `state: complete`. These retrieval observations establish neither product intent beyond the exact sources nor runtime correctness. Retention was resolved directly with the user; predecessor readiness remains open.

## Planning artifact mapping — 2026-11-12

- I09: research R1/R2, data-model transitions, import-operations dispatch/apply/retry contract; quickstart matrix 1/4/5/6.
- I19: research R5, lifecycle/backfill model, import-operations maintenance/expiry contract; quickstart matrix 7/8/10.
- I20: research R3/R4, runtime-containment profile/protocol; quickstart matrix 2/3/8 plus healthy follow-up.
- D02: research R6, technical context/runtime prerequisites and full quickstart, including actual image/version/route evidence.

At planning time task references were deferred; the task-generation mapping below now supplies IDs. All mappings describe proposed tests, not passed acceptance. P4 handoff gate remains open.

## Requirement-to-task mapping — 2026-11-12

T001 is now evidence-backed complete; all mapped product/runtime tasks T002–T054 remain unchecked. Shared schema fields T006–T011 support all stories.

- FR-001: T017–T022/T024; FR-002: T016/T018/T020–T024.
- FR-003: T018/T021/T025/T030/T033; FR-004: T017/T019/T021/T022/T025/T030/T040.
- FR-005: T005/T012–T016/T026/T030/T031/T034; FR-006: T025/T027–T031/T033.
- FR-007: T019/T021/T025/T027/T033/T035/T040; FR-008: T024/T033/T034/T042/T047/T048.
- FR-009: T009/T011/T035/T037/T039/T042; FR-010: T031/T036–T039/T042.
- FR-011: T013/T017/T023/T036/T038/T041/T042; FR-012: T023/T024/T040/T043.
- FR-013: T016/T024/T033/T034/T042–T049/T051; FR-014: T002/T003/T044–T050/T052/T053.
- SC-001: T024/T025–T034/T047; SC-002: T018/T021/T025/T030/T033.
- SC-003: T024/T033/T034/T042/T047/T048; SC-004: T035–T039/T041/T042.
- SC-005: T046–T050; SC-006: T023/T024/T040/T043.

Audit ownership: I09 → US1 plus US2 dispatch/commit/duplicate recovery; I19 → US3 plus shared retention/backfill; I20 → containment foundation plus US2; D02 → US4 plus isolated configuration. T051–T054 close evidence/traceability/handoff/workflow only after implementation, not during this invocation.

## Authorized analysis remediation mapping — 2026-11-12

- I1 (retry linkage): FR-007/US2-AC5, request intent=new/retry and conditional predecessor rule in import-operations/data-model, explicit API-client/wizard forwarding in T040; T035/T043/T047 exercise missing-link/fresh-import/status-refresh separation. The nullable DB foreign key remains compatible with fresh imports/legacy rows; explicit Retry is not optional linkage.
- I2 (in-flight versus capacity): FR-004 and ordered start contract; T017/T019/T020/T022/T047 verify authorized digest matching before a slot and a project-locked recheck after preparation, including sole-slot saturation. Existing permission checks precede identifier disclosure.
- U1 (backlog bounds): FR-006/FR-010/SC-001/SC-004 and finite-cohort runtime protocol; T012/T025/T027/T028/T033/T035/T039/T042/T047 cover stable cutoff, N/C/B/G, oldest-first fairness, deferred rows, ≥201 items, immediate successive pages, independent maintenance leadership and failed/blocked budgets. Initial formulas are engineering safety budgets under stated service-health assumptions, not a new customer SLA.
- I3 (validation versus admitted failure): US1-AC2/FR-001/SC-001/SC-006, intake model and start/error contract; T017/T018/T020/T024/T047 distinguish jobless validation/capacity/dependency rejection, existing persisted safety refusal and a separately admitted background failure with durable identity.

Original task IDs/counts remain unchanged and all are unchecked. These corrections supply missing design/test obligations; no implementation/runtime result is inferred. P4 handoff remains required by T001.

## Verified predecessor gate — 2026-11-12

The later user request authorized preparation of the missing P4 handoff. [P4 handoff](../054-a7-p4-import-experience/handoff.md), its [fresh 93-test/typecheck recheck](../054-a7-p4-import-experience/evidence/handoff-recheck.md), actual JUnit results and current P1/P2/P3 readiness supplements resolve P5 T001 for the local integrated code baseline at ea38dda2eda939184afd502fa027680b40af7870. Earlier “handoff absent” notes above are historical. Browser observations remain prior-session; actual worker/containment/recovery/cleanup/reproduction remains unverified and owned by T002–T054. No P5 product task was marked complete.
