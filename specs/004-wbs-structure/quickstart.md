# Quickstart Validation: WBS Structure

**Feature**: `004-wbs-structure`  
**Date**: 2026-10-08

## Purpose

Validation guide for `/speckit-implement`. **Do not implement from this Spec Kit pass.**

## Prerequisites

- Features **002** / **003** patterns available (soft-delete, project tenancy)
- Postgres + Redis; migrated DB; seeded users
- Auth as project member with WBS edit permission

## Suggested test map

| Story | Automated focus |
|-------|-----------------|
| US1 Tree + package fields | 3-level create; responsible/acceptance/status; cycle move rejected |
| US2 Delete guards | cost / progress / document / children / activities |
| US3 Templates | apply then mutate template; project unchanged; force path safe |

## Smoke commands (after implement)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  wbs/tests/test_wbs_structure_*.py \
  wbs/tests/test_wbs_delete_guards.py \
  project_templates/tests/test_wbs_template_immutability.py \
  -q
pnpm typecheck
```

## Expected outcomes

- SC-001–SC-004 covered by automated tests listed in `checklists/verification.md` (created at implement polish)
- UI: WBS page shows/edits responsible, acceptance criteria, status  
