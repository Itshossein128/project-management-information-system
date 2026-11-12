# WBS path collision: diagnosis and selected correction

Date: 2026-11-12. Scope: local development database and isolated pytest database.

The user confirmed that existing development/test data need not constrain the solution.

## Reproduced cause

`WBS.node_order_by = ['wbs_code']` made treebeard 4.7.1 assume siblings were physically ordered by that field. Two established operations violate this invariant: `WBS.soft_delete()` rewrites the code to `d_<uuid>`, and `propagate_project_wbs_codes()` renumbers codes in place according to structural path order.

In the local database, the deleted root at `005L` had a `d_...` code, followed by a live root at `005M` with code `1`. Adding another root with code `1` caused treebeard's sorted insertion to select codes greater than `1`. It included the deleted root but omitted the following equal-code live root. Its branch shift therefore attempted `005L → 005M`, violating the unique path constraint. Equal root codes across different projects are valid; the materialized-path forest is shared across all projects.

A small PostgreSQL regression with three roots in separate projects reproduced the same error at `0003` before the correction. This establishes an application ordering invariant violation, independent of the employer file or the size of the database. `find_problems()` returned five empty lists: that check covers path/depth/parent/child-count consistency, not sort-key consistency.

Reference: treebeard documents that changing an ordering attribute after insertion makes tree ordering inconsistent: https://django-treebeard.readthedocs.io/en/latest/mp_tree.html#treebeard.mp_tree.MP_Node.fix_tree

## Selected correction

Use structural path order for WBS and derive display codes from it. Disable `node_order_by` for WBS. Additions append without sorting by mutable display codes. The move service now honors first-child, last-child, left and right. The existing `sorted_child` API spelling is retained as an append alias. CBS behavior is unchanged.

Existing path encoding, parent relationships, and row identifiers are retained. No path rebuild, deletion, schema migration, dependency upgrade, or database reset is required for this database, whose structural consistency check is clean. The regression also verifies that adding a root leaves existing paths unchanged.

A reset alone would only remove the current trigger; the next soft delete or renumber could recreate it. Retrying the same insert does not repair the invariant. Re-sorting/rebuilding on each code change would add global cross-project path rewrites and would continue to conflict with user-controlled structural order. A separate immutable sort field is unnecessary for structural append/move ordering.

## Automated validation

Before correction, the isolated multi-project tombstone regression failed with `wbs_path_key` at `0003`.

After correction:

```bash
cd apps/api/core
../.venv/bin/python -m pytest wbs/tests/test_tree_ordering.py wbs/tests/test_services.py schedule/tests/test_a7_p4_import_experience.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py schedule/tests/test_mpp_import.py --reuse-db -q
```

Result: **74 passed**, no skips, 2 dependency deprecation warnings, 94.29 seconds. The regression tests cover cross-project insertion after soft deletion, children after a tombstone, and first-child movement with renumbering. The import safety/fidelity/experience suites remain green.

`manage.py makemigrations projects --check --dry-run`: no changes. A repository-wide dry run separately detects an existing `storage.StoredFile.source` change; no migration was generated or applied. Local WBS structural checks remained clean. This does not establish concurrent-writer stress behavior.

## Populated-database browser verification

The local API needed a restart to load the new model configuration; an old cached login response also needed replacing with a fresh sign-in. With the updated process, the same previously failing `real-data/plan.mpp` succeeded on the existing disposable project. The first import stored 6 WBS packages, 72 activities and 72 relations from 80 rows. The following three imports stored zero and reported unchanged work. The XML/MPP/XER matrix passed in English and Persian at desktop and phone widths. See `browser-results.json` and `browser.md`. No database rows were deleted to obtain this pass.
