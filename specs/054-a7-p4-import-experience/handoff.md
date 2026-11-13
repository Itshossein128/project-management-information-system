# Handoff: A.7-P4 Schedule Import Experience

**Date**: 2026-11-12
**Feature directory**: `specs/054-a7-p4-import-experience`
**Phase map key**: `a7-p4-import-experience`
**Code baseline**: `develop`, `ea38dda2eda939184afd502fa027680b40af7870`
**Status**: Integrated local P1–P4 import baseline ready for A.7-P5 implementation, with the limits below. This is not production deployment, full browser acceptance, or employer acceptance.

## Baseline handed forward

- Existing XML/native MPP/XER journey retains recognized filename/kind/mode, no-write preview, blocking/refused-replacement feedback, confirmed start, progress/status and stored-result links.
- Control figures distinguish source rows, created packages/activities, actual kept relationships, duplicates and omitted rows. Unchanged additions report no change; protected replacement remains refused under P2.
- Stable error/warning codes have Persian/English presentation. Unknown internal exceptions are not the wizard's displayed message. Existing keyboard/mobile layout is retained.
- In-flight actions are guarded against second clicks/files/drops. Attempt storage binds account/project/task; interrupted status is recoverable by rereading that same task. Late request callbacks check their originating context. A live project/account-switch browser trial remains a verification limit, not a newly asserted pass.
- The WBS materialized-path collision was traced to sorting on mutable display codes, corrected by structural ordering/move semantics, and covered by the fresh WBS/import regression set. No reset, tree rebuild or schema change was used for that correction.
- Preserve P3's deliberate omissions: parentless employer rows remain warnings/omissions, calendars are not applied, summary predecessors are not invented activity links. P5 must retain P2 authorization/history/concurrency behavior and P4 figures/feedback.

## Evidence supporting this handoff

Fresh [integrated recheck](evidence/handoff-recheck.md): **93 passed, no skips/failures/errors**, 101.72 seconds, plus fresh **passing typecheck**. This includes selected P1 catalogs/reference rules, WBS ordering/moves, P2/P3/P4 and MSP/P6/native-equivalence tests on a new phase-specific PostgreSQL test database. [JUnit results](evidence/handoff-pytest.xml).

Prior final [browser matrix](evidence/browser.md) and [machine-readable results](evidence/browser-results.json) show XML/actual native MPP/XER success in both languages and widths, with held preview/drop, interrupted status and keyboard checks. These browser trials were not repeated for this handoff; source/artifact correspondence was checked against the unchanged committed code. See [root-cause evidence](evidence/wbs-path-root-cause.md) and [audit traceability](traceability.md).

The employer file is unchanged, SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Earlier “T021 remains blocked” sections document historical failures; their later correction sections and fresh regression are the current basis. Task ticks alone are not the evidence.

## Limits carried forward

- Actual independent worker/broker, resource containment, interruption/retry/restart safety and file-retention cleanup are unverified here and explicitly owned by P5.
- Pytest task execution is synchronous and cache is in-memory. Native MPP conversion/equivalence passes do not turn that into real-worker evidence.
- Existing browser evidence uses automated file attachment; native OS file chooser, live account/project-switch trial and employer-alone guide review remain unproven. They are not waived or marked accepted by this handoff. The local code baseline is handed forward for the P5 operational extension, not certified against every P4 acceptance criterion.
- This handoff authorizes no production action or destructive shared-data test. P5 must use its isolated environment and preserve existing scopes.

## Next step

P5 can verify T001 against this handoff and the refreshed P1/P2/P3 readiness notes, then follow its existing tasks. Keep the separate P5 environment/containment/runtime-evidence gates open until actually demonstrated. Do not start P6 automatically.
