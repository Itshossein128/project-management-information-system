# Handoff: A.7-P2 Import Safety and History

**Date**: 2026-11-12  
**Feature directory**: `specs/052-a7-p2-import-safety`  
**Phase map key**: `a7-p2-import-safety`  
**Status**: The integrated import-safety baseline is ready for A.7-P4 implementation on the local tree, with the verification limits below. This is not production or employer acceptance.


**Current downstream readiness after P4 handoff (2026-11-12)**: The integrated local baseline from this phase is ready for A.7-P5 implementation on HEAD `ea38dda2eda939184afd502fa027680b40af7870`. The fresh combined [P1–P4 recheck](../054-a7-p4-import-experience/evidence/handoff-recheck.md) passed 93 tests without skips/failures/errors and typecheck. This confirms the local import prerequisites, not every original phase acceptance metric or employer/production acceptance. Earlier code versions and “P4 work remains” wording below are historical; current P4 handoff and its explicit verification limits take precedence for downstream readiness. No product code or predecessor task marker was changed for this supplement.

## Baseline handed forward

- Microsoft Project XML/native MPP and Primavera XER share the server-side safety gate in `apps/api/core/schedule/services/import_safety.py`.
- Replacement refuses protected progress, costs, linked documents, activities, and locked or approved baselines before changing schedule rows. An unprotected replacement soft-deletes existing work and reports removed and created counts.
- Preview and cancellation before confirmation do not write schedule rows. Failed writes roll back; a later valid attempt can finish.
- Apply rechecks the confirming actor and project permission. No fallback actor is chosen. The existing administrator-with-membership archive exception remains bounded by the same history protection; ordinary members cannot import into archived projects.
- An overlapping in-flight start returns the same job. Reading a finished job does not replay it. An append that creates nothing does not publish a new current schedule copy. New schedule copies are unlocked and unapproved.
- P3 uses this same gate and keeps empty or fully omitted imports from clearing the existing schedule.

## Evidence

The 2026-11-12 integrated recheck ran from `apps/api/core`, after exporting the repository `.env`:

```bash
../.venv/bin/python -m pytest \
  schedule/tests/test_a7_p2_import_safety.py \
  schedule/tests/test_a7_p3_import_fidelity.py \
  schedule/tests/test_mpp_import.py \
  schedule/tests/test_p6_import.py \
  schedule/tests/test_msp_import.py \
  schedule/tests/test_mpp_equivalence.py -q
```

Result: **49 passed, no skips**. Tests used PostgreSQL's isolated pytest database. No shared project was imported into for this recheck. Django is **4.2.11**. No application code or migration was changed while preparing this handoff.

The previous bilingual browser evidence, including refusal of replacement on a disposable project with a locked baseline, is recorded in [evidence/verification.md](evidence/verification.md). That browser observation was recorded on 2026-11-11; it was not repeated for this documentation handoff.

## Limits and next phase

- Synchronous task execution in pytest verifies the apply path, not a separately running worker or deployed delivery.
- Pytest overrides the cache to use local memory; this run is not Redis integration evidence.
- Import-screen counts, recovery, error-code presentation, and request/session binding remain P4 work. This handoff does not mark T003–T022 of P4 complete.
- Continue only after the independent [P3 handoff](../053-a7-p3-import-fidelity/handoff.md) also declares the integrated fidelity baseline ready. Preserve the contracts in [contracts/import-safety.md](contracts/import-safety.md).
