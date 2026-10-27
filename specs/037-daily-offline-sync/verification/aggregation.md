# US4 evidence (T039–T044)

Targeted edits, derived summary refusal, and aggregation were already implemented. These runs are GREEN proof. No legacy destructive assertion had to be replaced.

Commands, from `apps/api/core`, with `--reuse-db`:

- `pytest sub_reports/tests/test_offline_target_isolation.py`
- `pytest field_reports/tests/test_daily_report_derived_readonly.py`
- `pytest field_reports/tests/test_unit_report_aggregation_eligibility.py field_reports/tests/test_summary_attachment_counts.py field_reports/tests/test_offline_legacy_protection.py`

Results: isolation, derived, and the new repeated-rebuild assertion passed together (6). The eligibility, attachment-count, and legacy-protection suites then passed (29).

Covered behavior:

- Updating one activity keeps its server id and leaves another row, including a row added outside the batch, unchanged.
- A stale `base_revision` returns `stale_target_revision` and does not change the row.
- An empty list payload returns `snapshot_replacement_forbidden`.
- A header update aimed at another project's report does not change that report.
- Versioned `project_metadata` creates return `derived_readonly` and leave derived rows and provenance ids unchanged.
- Legacy child POST/PATCH/DELETE, summary PATCH, and sync-batch still return `derived_readonly` without rewriting rows.
- Rebuilding a summary twice keeps one derived contribution per source row. Eligibility still excludes drafts, rejected, deleted, superseded, quarantined, and other project or date sources.
