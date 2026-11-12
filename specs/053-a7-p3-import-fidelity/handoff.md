# Handoff: A.7-P3 Import Fidelity

**Date**: 2026-11-12  
**Feature directory**: `specs/053-a7-p3-import-fidelity`  
**Phase map key**: `a7-p3-import-fidelity`  
**Status**: The integrated import-fidelity baseline is ready for A.7-P4 implementation on the local tree, with the verification limits below. This is not production or employer acceptance.

## Verified baseline

- MSP XML/native MPP and Primavera XER use the shared resolved plan and the P2 safety gate. Parent identifiers, rather than row order or dotted WBS codes, determine stored parents.
- Blocking diagnostics preserve row identity and leave the project unchanged. Empty and fully omitted replacement plans do not clear existing work.
- Supported duration, milestone, planned percent, critical, and slack values reach Activity. Exact eight-hour-day conversion is used. Planned, actual, forecast, and approved baseline dates remain distinct; imported working copies remain unapproved.
- Calendars are reported as not applied. Summary predecessors are reported and omitted as activity links. No guessed package, weight, calendar, or relationship is substituted.
- Final-tree integrated pytest: **49 passed, no skips** on 2026-11-12. Native MPP conversion and nonempty stored MPP/XML equality ran, including supported facts and warning codes/row identities. Full command, schema checks, historical browser observations, and limitations are in [evidence/verification.md](evidence/verification.md).
- Django remains **4.2.11**. No new runtime code or migration was introduced for this handoff. `real-data/plan.mpp` retains SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`.

## Resolved gate: T034 scope decision

[FR-003](spec.md) and the parent contract require omission of activities without a resolvable parent. The actual employer-file activities شروع and پایان have no parent and are therefore omitted with `activity_without_parent`.

On 2026-11-12 the user explicitly chose: “Keep omitting them with row warnings; store zero duration only for activities with a valid parent.” FR-015, US6/AC5, and the [support contract](contracts/import-fidelity.md) now record that decision. No storage or parent rule changed, and no parent was invented.

The employer-file regression verifies that both actual rows parse as zero days, have no parent, are omitted, and carry their own `activity_without_parent` row identities through preview and the saved result. The separate parented fixture verifies storage of zero-day activities with a valid source parent. The unchanged-fingerprint assertion remains in place.

The final integrated rerun after these assertions passed **49 tests, no skips**, in 7.29 seconds using the isolated reused pytest database. T034 is complete. Together with the [P2 handoff](../052-a7-p2-import-safety/handoff.md), this satisfies P4 T002. P4 T003–T022 remain separate implementation work; resume `/speckit-implement` for that feature.

## Verification limits carried forward

- This handoff is not deployment or employer acceptance. Browser checks in the verification note are historical, not repeated for the handoff.
- The pytest task calls are synchronous, and the cache fixture is in-memory; a separate worker and Redis integration were not verified.
- The historical populated-database WBS path collision recorded in the verification note was not reproduced or fixed here.
- Accurate relationship/control figures, remaining localized file errors, interrupted-attempt recovery, and keyboard/mobile journeys remain P4 scope. This handoff must not be read as their completion.
