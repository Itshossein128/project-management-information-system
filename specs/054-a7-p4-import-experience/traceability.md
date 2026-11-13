# Traceability: A.7-P4 downstream handoff

**Date**: 2026-11-12. Local integrated baseline handed to P5; no production/employer acceptance claimed.

The [2026-11-10 audit](../../output/a7-requirements-2026-11-10/report.md) is historical. Source needs below come from its assigned IDs and the original 029 requirements; final behavior is grounded in the owning sources and evidence, not audit status labels.

## I02 — Existing file-to-result journey

Source: 029 FR-003; P4 FR-001–004/007. Tasks T005–T007/T013/T021/T025. Sources: `msp-import-wizard.tsx`, `api/msp.ts`, existing schedule views/parsers. Fresh integrated pytest checks recognized kinds/no-write preview; prior final browser matrix covers actual XML/MPP/XER journeys and result links. Native success is the later corrected matrix, not the earlier failed MPP trial.

## I10 — Reconcilable figures and warnings

Source: 029 FR-007/016 and A.7.01/04; P4 FR-005–009. Tasks T008–T013/T022. Sources: `schedule/services/import_fidelity.py`, `shared_import.py`, importer/result code and wizard. Fresh P4/backend suite covers persisted/control relationship figures, duplicate/omission meaning, unchanged results and protected replacement; prior browser/DB observations corroborate visible stored figures. No separate discrepancy export is added.

## I15 — Active language and recoverable error

Source: 029 FR-012/016; P4 FR-008/010/011/014. Tasks T003–T004/T014–T016/T019/T021. Sources: frontend API error code preservation, English/Persian catalogs, wizard and P6 error envelope. Fresh tests cover shared catalog/validation behavior; prior bilingual matrix records warnings, wrong-file rejection, refused replace, interrupted status and choose-another flow. This does not prove every failure originated in a real worker.

## I16 — Busy state and second submission prevention

Source: 029 FR-015; P4 FR-012–014. Tasks T017–T019/T021. Sources: wizard request lock/scope guards and `import-attempt-session.ts`, existing backend in-flight matching. Fresh backend tests cover same-job in-flight replay and read-only finished status; prior browser matrix holds the preview while dropping another file and checks one request, then status retry without a second start. Live account/project-switch browser observation is still missing; source guards are not represented as that trial.

## I17 — Keyboard, RTL/LTR and phone width

Source: 029 FR-017/SC-008; P4 FR-015/016. Tasks T020–T021/T025. Prior final browser matrix covers success/rejection/actions in English/Persian at 1280 and 390 width; screenshots exist. No new date picker was added. Fresh typecheck passed; it does not replace browser accessibility evidence. Native OS file chooser and employer-alone guide review remain unproven.

## Combined handoff evidence

[Fresh recheck](evidence/handoff-recheck.md): 93 passed, no skips/errors/failures on isolated PostgreSQL, and fresh typecheck exit 0, on HEAD `ea38dda2eda939184afd502fa027680b40af7870`. [Browser evidence](evidence/browser.md) is prior-session and explicitly labeled. P4 tasks remain unchanged; this note does not silently close missing acceptance trials. Real worker/containment/file-lifecycle delivery evidence remains P5 work.
