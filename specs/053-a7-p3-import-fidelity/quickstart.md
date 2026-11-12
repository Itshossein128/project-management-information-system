# Quickstart: Import Fidelity

Validate stored parents, durations, links, and warnings. Preview-only equality is not the result. Use the pytest database and project code `A7P3-IMPORT-FIDELITY`. Do not import into a shared project. Do not modify `real-data/plan.mpp`.

## Prerequisites

PostgreSQL and Redis are running. The API virtualenv is `apps/api/.venv`. Django stays on 4.2.11. From the repository root, export `DATABASE_URL` from `.env` before pytest.

The reference fixtures under `specs/051-a7-p1-project-reference/evidence/fixtures/` are read-only inputs. `branch.xml` and `branch.xer` are the parent cases. `milestone.xml` stores a zero-day milestone. `milestone.xer` stores zero days and not a milestone. `relation.xml`, `relation.xer`, and `dangling-predecessor.xml` are warning cases, not stored-link cases.

## Commands

From `apps/api/core`:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_mpp_import.py schedule/tests/test_p6_import.py schedule/tests/test_msp_import.py schedule/tests/test_a7_p2_import_safety.py -q
```

Apply the activity migration before that run. Existing activity rows must keep null percent, critical, and slack.

## Outcomes to confirm

- In the branch fixtures, each child is under the parent named in the file in both the preview and the saved rows. Reordering the same parent identifiers does not move the child.
- A leaf with no resolvable parent is `activity_without_parent` and is not stored. A finish-to-start link is stored only for a test file whose leaves have a real parent.
- `PT0H0M0S` and Primavera `0` hours are duration 0. A Microsoft Project link lag of 4800 is 1 day. A delay that is not an exact number of eight-hour days is `lag_not_whole_days` and creates no link.
- Finish-before-start, a cycle, a self-link, and an in-file duplicate code leave every project count unchanged, including when the mode is replacement.
- A new activity does not receive forecast dates. An actual date in the file is not written into the planned date. An append does not change an existing activity's actual dates. The working copy is unapproved.
- `calendar_not_applied` appears when the file has a calendar, and `working_calendar` is null.
- A summary predecessor, including a fixture shaped like employer identifiers 8055, 8084, 8102, and 8120, is `predecessor_is_summary`. The summary remains a work package.
- When the MPP converter is available, the paired MPP and XML fixture compared by `schedule/tests/test_mpp_equivalence.py` also matches on stored hierarchy, dates, durations, milestones, links, and warnings. If the converter cannot run, record that limit. Do not treat a preview subset as that proof.
- The import-safety tests above still pass.

## Browser

Sign in on the local web app. Create or open only the disposable `A7P3-IMPORT-FIDELITY` project. Import a small file that stores one milestone and reports `calendar_not_applied`.

In Persian and in English, confirm the warning text, then open the Gantt or the schedule status view and confirm the same milestone and the same planned date. Do not treat this as proof of a separately running worker.
