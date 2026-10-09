# Quickstart: Risk, Quality & Safety

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB after `risk` FR-RSK migrations
- Seeded project with WBS node, project member users, optional activity / CBS / contract for link tests

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  risk/tests/test_risk_register.py \
  risk/tests/test_risk_issue_separation.py \
  risk/tests/test_risk_score_and_status.py \
  risk/tests/test_inspection_validation.py \
  risk/tests/test_quality_period_report.py \
  risk/tests/test_risk_matrix_unit.py \
  -q
```

## Manual API smoke

1. `POST .../risk-events/` with `event_type=risk`, both levels set → `composite_score` = product; list filter `?impact=schedule` returns it.
2. `POST` risk with only one level → `composite_score` null; status defaults toward `under_review` if omitted.
3. `POST` `event_type=issue` → appears under `?event_type=issue`, not in risk-only matrix.
4. Create `RiskAction` open → PATCH risk `status=closed` without acknowledge → 400 `open_actions_warning`; with `acknowledge_open_actions=true` → closed.
5. `POST .../inspections/` without wbs or responsible or date → 400; with all three → 201.
6. Fail inspection → NCR → corrective action with due date → all linked.
7. Two `hse-events` in October → `GET .../quality-safety/report/?date_from=...&date_to=...` lists them under incidents/near_misses; empty other sections are `[]`.

## UI

- Project → Risk register: Risk vs Issue tabs/filters; FR fields; impact filters; close acknowledge dialog (fa/en).
- Project → Quality & HSE: inspection/NCR capture; incident/near miss; period report panel; permit/training (P3).

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 | Register risk + status change + impact filter in &lt; 3 min on seeded project |
| SC-002 | Issue and risk distinguishable by `event_type` in list/UI |
| SC-003 | Period report returns inspections/NCRs/incidents/near misses (and permit/training when present) in-app |
| SC-004 | 100% pytest cases reject inspection missing date, responsible, or WBS |
| SC-005 | 100% pytest cases with missing level keep `composite_score` null |
