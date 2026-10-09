# Data Model: WBS Structure

**Feature**: `004-wbs-structure`  
**Date**: 2026-10-08

## Entities

### WBS (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | existing |
| project_id | FK → Project | existing, CASCADE |
| wbs_code | Char(30) | unique per project among non-deleted (soft-delete remaps code) |
| wbs_name | Char(200) | title |
| description | Text | existing |
| weight_physical / weight_financial | Decimal nullable | existing |
| path / depth / numchild | treebeard | existing |
| is_deleted / deleted_at | soft-delete | existing |
| created_by / updated_by / timestamps | audit | existing |
| **responsible** | FK → User, null | **NEW** — package owner |
| **acceptance_criteria** | Text, blank | **NEW** |
| **status** | Char choices | **NEW** — e.g. `draft`, `active`, `completed`, `on_hold` |

**Invariants**:

- No cycles (enforced on move/create parent assignment).
- Unique `(project, wbs_code)` for active rows.
- Soft-delete frees code via tombstone rename (existing).

### Work package (logical)

Not a separate table in v1. A work package is a WBS node that is a leaf (or UI-designated control node) where responsible + acceptance_criteria are expected for progress/budget workflows.

### ProjectTemplate / ProjectTemplateWBS (existing)

Template definition tree. Apply copies into `WBS` (+ optional template activities → `Activity`). No live FK from project WBS back to template nodes required for immutability (copy-on-write).

Optional audit field (out of scope unless needed): `source_template_id` on Project for “last applied template” metadata only — must not cascade template edits.

## Relationships

```text
Project 1──* WBS (tree)
User 1──* WBS.responsible (optional)
WBS 1──* Activity
WBS 1──* Budget / ActualCost (optional cbs elsewhere)
WBS 1──* Document.related_wbs
ProjectTemplate 1──* ProjectTemplateWBS (tree)
apply → copies into Project.WBS
```

## State transitions (status)

- `draft` → `active` (default on meaningful use)
- `active` → `completed` | `on_hold`
- Soft-delete independent of status (status retained for history)

## Validation rules

| Rule | Enforcement |
|------|-------------|
| Unique code in project | DB + service |
| Parent same project | service |
| Cycle on move | service pre-check |
| Delete with children/activities/cost/progress/docs | service conflict |
| Template edit ≠ project mutate | by absence of live sync + tests |
