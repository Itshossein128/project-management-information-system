# Research: WBS Structure (FR-WBS)

**Feature**: `004-wbs-structure`  
**Date**: 2026-10-08

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| Multi-level tree | Present | `projects.WBS` as treebeard `MP_Node`; create/list/move/soft-delete |
| Unique code / project | Present | `unique_together (project, wbs_code)`; soft-delete renames code; `propagate_project_wbs_codes` |
| Cycle prevention | Partial | No explicit “cannot move under own descendant” guard in `move_wbs_node` — must add |
| Responsible / acceptance / status | Missing | Spec FR-WBS-004; Activity has `responsible`, WBS does not |
| Delete: children, activities | Present | `WBSConflictError` in `delete_wbs_node` |
| Delete: cost / progress / document | Missing / partial | Budget/ActualCost have `wbs` FK; Document has `related_wbs`; progress is typically via Activity → ActivityProgress (activity guard covers many cases; also block if Budget/ActualCost/Document reference node) |
| Templates | Present | `ProjectTemplate` + `ProjectTemplateWBS`; `apply_template_to_project` copies into project-owned `WBS` rows |
| Template silent rewrite | OK by design | Editing template rows does not touch project WBS; **gap**: `force=True` hard-deletes project WBS/activities — must become explicit, dependency-safe, and preferably soft-delete aligned |

## Decisions

### D1 — Additive fields on `WBS` (not a parallel entity)

**Decision**: Add `responsible` (FK user, null), `acceptance_criteria` (text), `status` (enum: e.g. `draft` / `active` / `completed` / `cancelled` or project-consistent set) on `projects.WBS`.

**Rationale**: Spec attributes belong on the node; avoids joining a 1:1 profile table for v1.

**Alternatives considered**: Separate `WBSWorkPackageProfile` (heavier); reuse Activity.responsible only (fails FR-WBS-002 for package-level ownership before activities exist).

### D2 — Work package = leaf (default) with optional future `node_kind`

**Decision**: For v1, treat leaves as work packages for UX prompts; do not require a mandatory `node_kind` column unless UI needs phase/deliverable labels — optional `level_label` or derive from depth in UI copy.

**Rationale**: Spec describes semantic levels but tree depth already exists; keep schema small.

### D3 — Delete dependency matrix

**Decision**: Reject soft-delete when any of:

1. Non-deleted children  
2. Non-deleted activities on the node  
3. Non-deleted Budget or ActualCost with `wbs_id`  
4. Non-deleted Document with `related_wbs_id`  
5. (Optional fortification) ActivityProgress on activities under the node — covered by (2) if activities cannot be deleted while progress exists; still assert progress path in tests via activity→progress

Return structured conflict: `{ code: 'wbs_has_<dependency>', message }`.

### D4 — Cycle guard on move

**Decision**: Before `node.move`, if `new_parent` is `node` or a descendant of `node`, raise `WBSValidationError` / conflict with code `wbs_cycle`.

**Rationale**: Spec SC-WBS / FR-005; treebeard may throw obscure errors otherwise.

### D5 — Templates remain copy-on-write; harden force-replace

**Decision**: Keep `ProjectTemplateWBS` as template definition. Project WBS after apply is independent. Add regression tests that mutating template does not change project nodes. Change `force=True` path to: refuse if dependency guards would block any node, or soft-delete + recreate only when safe / explicitly allowed — never silent background rewrite.

### D6 — Progress detection

**Decision**: “Progress dependency” for SC-WBS-002 = ActivityProgress rows for activities linked to the WBS node (and/or non-deleted activities). Cost = Budget/ActualCost; Document = `documents.Document.related_wbs`.

## Open points resolved by assumption

- Duration on work package: deferred to Spec 05/09 (activity duration / budget), not a required WBS column in this feature.
- Empty project warning for schedule/progress: lightweight API flag or UI banner when WBS leaf count is 0.
