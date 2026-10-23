# Baseline Evidence — Feature 033 (Phase 1, T002)

Recorded: 2026-10-23, before any 033 implementation work.

## Backend pytest baseline (scope: `sub_reports/tests`, `field_reports/tests`)

Command (from `apps/api/core`, Postgres 5433 + Redis running at the time of the run):

```sh
cd apps/api/core && set -a && source ../../../.env && set +a && \
../.venv/bin/python -m pytest sub_reports/tests field_reports/tests -q
```

Note: tasks.md references `/workspace/.env`; on this checkout the env file lives at the
repository root (`../../../.env` relative to `apps/api/core`).

Result of the first clean full-scope run:

- **25 failed, 197 passed, 15 skipped** in 236.61 s (0:03:56)
- failures include e.g. `test_spec_01_daily_header_weather.py::test_aggregation_weather_severity_order`,
  `...blanks_and_unknowns_ignored`, `...all_severity_pairs` and 22 others across
  `sub_reports/tests` and `field_reports/tests` — all pre-existing 032-era test failures,
  unrelated to feature 033 (no 033 code existed yet).

The other 033 RED scaffolding modules (`test_machinery_derivation.py`, `test_receipts_only_summary.py`,
`test_structured_transfer.py`, `test_section_contracts.py`, `test_labor_catalog.py`,
`test_machinery_contract.py`, `test_materials_receipt_contract.py`, `test_concrete_qc_link.py`,
`test_structured_narrative.py`) are module-level skipped; they collect and run clean from day one.

### Environment caveat (T002 evidence-bounds note)

- Postgres (cluster 16/main, port 5433) and Redis were started manually for the baseline run.
- A second, concurrent agent session was active on the same Postgres during this T002 cycle,
  colliding on the shared `test_ipcas` test database (CREATE/DROP/terminate interference visible
  in the Postgres log). All subsequent verification runs for feature 033 use an isolated test
  database (`DATABASE_URL` pointed at `ipcas_h033`, giving test database `test_ipcas_h033`) to
  avoid mutating the other session's database.
- Re-running the whole two-app scope later reproduced DB errors from that collision
  (`pytest --lf` → 25 ERROR) and one OOM kill (exit 137) under concurrent load; these were
  environment artifacts, not code regressions. Single-file runs on the isolated test DB behave
  deterministically (e.g. `field_reports/tests/test_daily_report_by_date.py` → 3 failed /
  3 passed, same pre-existing constraint-violation failures).
- The baseline number of record is therefore the first clean run above:
  **25 failed, 197 passed, 15 skipped**.

## Frontend typecheck baseline

```sh
pnpm typecheck
```

Result: **exit 0, clean**. The `main`-branch known-unrelated failure in
`apps/web/src/components/daily_reports/DailyReportForm.tsx` (`'c' is of type 'unknown'`,
documented in AGENTS.md) is **not present** in this checkout at baseline time. Any new
typecheck error appearing after 033 work starts is attributable to this feature
(T060 will enforce this).

## 032 state note

Feature 032 (`specs/032-unit-report-source-truth/`) is the delivered foundation:
canonical units, unit-page versioning/constraints, states/eligibility, current-version
selection, rebuild fingerprint, `DailyReportDerivedSource` provenance are present in the code
(`sub_reports/migrations/0007…`, `field_reports/migrations/0019…/0020…`). The 25 pre-existing
failures above are the deviation from a fully green 032 suite on this checkout; they are
recorded here as the baseline to compare against after 033 work.
