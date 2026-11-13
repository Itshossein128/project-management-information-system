# Handoff: A.7-P1 Reference Project

**Feature directory**: `specs/051-a7-p1-project-reference`  
**Phase map**: `output/a7-implementation/phase-map.json` key `a7-p1-project-reference`  
**Status**: Ready for review. Employer acceptance stays with A.7 phase 6.  
**Next phase**: Do not start automatically. Phase 2 owns import replace safety. Phase 3 owns import fidelity against `contracts/schedule-reference.md`.


**Current downstream readiness after P4 handoff (2026-11-12)**: The integrated local baseline from this phase is ready for A.7-P5 implementation on HEAD `ea38dda2eda939184afd502fa027680b40af7870`. The fresh combined [P1–P4 recheck](../054-a7-p4-import-experience/evidence/handoff-recheck.md) passed 93 tests without skips/failures/errors and typecheck. This confirms the local import prerequisites, not every original phase acceptance metric or employer/production acceptance. Earlier code versions and “P4 work remains” wording below are historical; current P4 handoff and its explicit verification limits take precedence for downstream readiness. No product code or predecessor task marker was changed for this supplement.

The earlier “No migration” sentence is not a current schema inventory: the integrated tree includes `projects.0019_project_approval_submitted_by` and later committed migrations, applied by fresh pytest database setup. This recheck generated no migration and changed no shared schema.

## What changed

- Staff-only creation of an organization unit stays forbidden. The old test expected success; it now expects 403 and no row. The permission text matches that rule.
- A project contract type, when newly set or changed, must be an active catalog code. A blank value and an unchanged legacy value still save.
- Organization stewards can create a measurement unit from Organization references. The same writer rule as organization units applies.
- A work-breakdown parent from another project returns 400 `invalid_parent` instead of an unhandled lookup error.
- An EPC project template fills contract type `EPC` only when that code is already in the catalog.
- The employer file `real-data/plan.mpp` was not modified. Its SHA-256 is `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`.
- Submitting a project stores `approval_submitted_by`. That person cannot approve the same submission. A different member with `approve_project` still can. Migration `projects.0019_project_approval_submitted_by` adds the nullable column.
- Template creation uses the same trimmed project-code rule as ordinary create and update.
- No migration. Django stays 4.2.11. The importer was not changed. Project status was not opened into a free list. Dynamic-table workbook import was not merged with work-breakdown import.

## Code version

HEAD `b4ec9b9`. Uncommitted work for this phase:

- `apps/api/core/master_data/permissions.py`
- `apps/api/core/master_data/ref_serializers.py`
- `apps/api/core/master_data/ref_views.py`
- `apps/api/core/master_data/urls.py`
- `apps/api/core/master_data/tests/test_org_refs.py`
- `apps/api/core/master_data/tests/test_units.py`
- `apps/api/core/projects/serializers.py`
- `apps/api/core/projects/tests/test_a7_p1_reference_project.py`
- `apps/api/core/wbs/services.py`
- `apps/api/core/locale/fa/LC_MESSAGES/django.po`
- `apps/api/core/locale/fa/LC_MESSAGES/django.mo`
- `apps/web/src/app/lib/api/central-data.ts`
- `apps/web/src/app/routes/settings-org-refs.tsx`
- `apps/web/src/app/routes/project-create-wizard.tsx`
- `specs/051-a7-p1-project-reference/`
- `output/a7-implementation/phase-map.json`

`output/a7-requirements-2026-11-10/` and `graphify-out/memory/` were already untracked and were not part of this implementation.

## Open limits

- Successful WBS renumber-after-move tests in `wbs/tests/test_services.py` passed in the 2026-11-10 final pytest set (`108 passed`).
- Archive and undo screens were not clicked in the browser. Their API tests passed: 59 archive tests and the status-undo module.
- The final browser check opened `/settings/org-refs` in Persian and English and opened the contract-type list on `/projects/new` in both languages. It did not create a catalog row or a project. Empty measurement-unit names were blocked by the browser before a request. Chrome's validation bubble stayed English.
- Historical schedule mismatches H-PRED-8055, H-PRED-8084, H-PRED-8102, and H-PRED-8120 are present summary tasks, not missing identifiers. H-DUR-شروع and H-DUR-پایان remain outside the duration rule. Phase 3 must not delete links to force 83 and 79 to match.
- M03 is an interpretation, not a new status catalog. If the employer wants manageable project statuses, that needs an explicit decision and transition rules.

## Convergence

Compared with the spec, plan, and tasks after implementation, no remaining in-scope gap required a new task. The foreign-parent rejection was already inside T006.
