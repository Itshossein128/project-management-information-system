# Verification: WBS Structure (FR-WBS)

**Feature**: `004-wbs-structure`  
**Date**: 2026-10-08

| SC | Criterion | Tests |
|----|-----------|-------|
| SC-001 | ≥3-level tree + responsible/acceptance on work package | `wbs/tests/test_wbs_structure_fields.py` |
| SC-002 | Delete with cost/progress/document rejected | `wbs/tests/test_wbs_delete_guards.py` |
| SC-003 | Template edit does not rewrite applied project | `project_templates/tests/test_wbs_template_immutability.py` |
| SC-004 | Cycle move rejected | `wbs/tests/test_wbs_cycle_move.py` |

## Soft-delete / force replace

- WBS soft-delete retained; force template replace soft-deletes when safe and refuses on cost/progress/documents.
