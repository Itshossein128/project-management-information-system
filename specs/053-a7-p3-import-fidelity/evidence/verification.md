# Verification: A.7-P3 import fidelity

**Date**: 2026-11-11

## Pytest

From `apps/api/core`, with `DATABASE_URL` loaded from the repository `.env`:

`../.venv/bin/python -m pytest schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_mpp_import.py -q`

Result: **19 passed**.

An earlier run of `schedule/tests/test_a7_p3_import_fidelity.py::test_blocking_cases_write_nothing_even_on_replace` together with `test_msp_import.py`, `test_p6_import.py`, `test_mpp_equivalence.py`, and `test_a7_p2_import_safety.py` was **22 passed**.

The new tests use project codes that start with `A7P3-IMPORT-FIDELITY` only inside the pytest database. They cover parents for the branch fixtures, unattached root leaves, blocking errors before replacement, depth and missing-predecessor warnings, zero-duration milestones, a link lag of 4800 as 1 day, calendar non-application, separate planned and actual dates, the critical-path gate, and the four summary-predecessor shape. The paired MPP and XML file matched on stored rows. Django stayed on 4.2. Calling the import function inside pytest is not a separately running worker.

Migration `projects.0020_activity_import_fidelity_fields` adds nullable `planned_percent`, `is_critical`, `total_slack_days`, and `free_slack_days`. Existing rows stay null.

## Browser

Signed-in admin session on `http://localhost:5173`, isolated from the other open tab. Disposable project `A7P3-IMPORT-FIDELITY` (`a03a8598-9e9a-4303-a6d5-bee531afccfb`). The existing UAT projects were not imported into.

On `/projects/a03a8598-9e9a-4303-a6d5-bee531afccfb/wbs`, the import wizard previewed a small XML file that contains a calendar and one zero-duration milestone.

- Persian: the preview showed «تقویم فایل اعمال نشد.»
- English: the same preview showed “The file calendar was not applied.”

Confirm stored 1 work-breakdown node, 1 activity, and 1 warning. The working copy name is `MSP Import — a7p3-mile2.xml — 2026-11-11 19:53` and it is unlocked.

On `/projects/a03a8598-9e9a-4303-a6d5-bee531afccfb/schedule/gantt` in Persian, the chart label is `ZZ1 — Start milestone · نقطه عطف` and the comparison table shows planned start and finish `1404/12/10`. The same activity and date were visible in English before the language switch.

A first attempt whose work-package code was `1` failed on this populated database with `wbs_path_key` path `005M`. That path already belongs to another project's root. `WBS.add_root` sorts new roots by code, and code `1` collides. The successful check used code `ZZ1`. This is the existing tree insertion behavior, not a second importer.

## Convergence recheck

Pytest on 2026-11-12, same command environment:

`../.venv/bin/python -m pytest schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py -q`

Result: **28 passed**. A later employer-file rerun was **1 passed**.

- An empty file and a file whose only row has no parent, both in replace mode, leave an existing work package in place and report `nothing_changed`.
- A reordered nested Microsoft Project file and a Primavera file keep each stored child under the parent named in the file after sorted tree insertion.
- A dotted WBS code with no outline number stays `activity_without_parent`.
- The unchanged employer file `real-data/plan.mpp` still has SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Predecessor identifiers 8055, 8084, 8102, and 8120 are `predecessor_is_summary`. The tasks شروع and پایان are not stored, because they have no parent in the file. That follows the rule that a leaf without a parent is not given an invented package. Storing their zero duration would require that invented package.
- The native employer file and the XML produced from it store the same nonempty hierarchy, activities, and links.
- Wizard labels and the final warning list use the active language. Failed-job codes are translated in the browser from the stable code, not from the worker's message text.

## Integrated handoff recheck — 2026-11-12

From `apps/api/core`, with the repository `.env` exported:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_mpp_import.py schedule/tests/test_p6_import.py schedule/tests/test_msp_import.py schedule/tests/test_mpp_equivalence.py -q --reuse-db
```

Final result: **49 passed, no skips, 2 dependency deprecation warnings**, in 94.10 seconds. Native MPP conversion ran. The stored twin comparison now includes actual/forecast dates, planned percent, critical/slack values, calendar assignment, weight, and normalized warning codes/row identities, in addition to nonempty hierarchy, activities, and relationships. Known missing converter configuration/runtime can skip; corrupt, unsupported, timeout, and unexpected conversion failures cannot silently skip these reference checks.

Django reports **4.2.11**. The existing `projects.0020_activity_import_fidelity_fields` migration is applied. `manage.py makemigrations projects schedule --check --dry-run` exits 0 with no changes. A separate repository-wide check detects unrelated `storage.StoredFile.source` drift; no migration was generated or applied. No application runtime code changed for this handoff work.

The employer-file fingerprint remains `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. Tests use PostgreSQL's pytest database and the in-memory cache fixture. This run does not repeat the historical browser check, prove Redis integration, a separate worker, production deployment, or employer acceptance. The historical populated-database WBS path collision above was not reproduced or fixed by this recheck.

At this recheck T034 still required a scope decision: code omitted the parentless employer rows under FR-003, while FR-015 and US6/AC5 requested their stored zero duration. That conflict was subsequently resolved as recorded below.

## T034 decision and final verification — 2026-11-12

The user explicitly confirmed: “Keep omitting them with row warnings; store zero duration only for activities with a valid parent.” FR-015, US6/AC5, the spec's Clarifications, and the employer-file support contract now agree with this decision. No runtime storage or parent rule changed.

The actual employer-file regression now asserts that both شروع and پایان parse as zero days without an inexact-duration flag, have no parent, and each appears with its source UID and `activity_without_parent` in preview, structured result warnings, and final warning text. Neither activity is stored. The existing parented fixture separately asserts that zero-day شروع and پایان activities with a valid source package are stored as zero. This does not substitute a synthetic fixture for the employer-file omission proof.

The same six-module command above was rerun after the new assertions: **49 passed, no skips, 2 dependency deprecation warnings**, in **7.29 seconds**, using the isolated reused pytest database. Native conversion ran, and the employer-file fingerprint assertion passed with SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. T034 is complete and the [handoff](../handoff.md) declares the integrated baseline ready for P4, subject to the verification limits already stated.
