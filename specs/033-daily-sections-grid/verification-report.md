# Verification report — feature 033 remaining stories

Date: 2026-10-25

## What was implemented

- Concrete pour validation (`volume_must_be_positive`, sampling test information, foreign batching-plant reference) and idempotent linkage to `risk.Inspection`.
- Structured narrative validation and aggregation for issues, barriers, visits, HSE incidents, and general activities, including markup stripping and HSE notifications.
- Activity image attachment checks (hostile ZIP/EXE signatures, 10 MB limit, version and project scope) with a local storage key when MinIO is not configured.
- Aggregation fingerprint coverage for the new section families, ordered derived rows, and `GET …/provenance/{derived_kind}/{derived_row}/`.
- Unit-panel editors for concrete, general activities, issues, visits, and HSE, plus summary provenance and attachment-count components. Persian and English strings were added together.

## Evidence

Focused pytest (Postgres on port 5433):

`sub_reports/tests/test_concrete_qc_link.py`, narrative transfer tests, attachment contract tests, and `field_reports/tests/test_summary_attachment_counts.py`.

Last full run of that set before the final attachment message tweak: 21 passed, 1 failed (`test_attachment_mutable_only_on_draft`). The failure was the exception text, which now includes `submitted`.

## Boundaries

- This run does not prove browser behavior. The new editors were not exercised in a running browser session.
- MinIO is not part of this local run. Attachment tests prove refusal and metadata persistence, not object-store retrieval.
- Playwright `daily-sections` was not executed in this pass.
- `pnpm typecheck` was not re-run here. The known unrelated `DailyReportForm.tsx` failure recorded in `baseline.md` is unchanged by this work.
- Usability criteria that need a person using the product are not claimed.
