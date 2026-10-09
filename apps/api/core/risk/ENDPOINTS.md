# Risk, Quality & HSE Module Endpoints

All endpoints inherit project tenancy via `ProjectScopedViewSet` / project member permissions (`view_reports` / `edit_reports`).

Base: `/api/v1/projects/{project_id}/`

## Barriers (`/barriers/`)

CRUD for `event_type=barrier`. Status values use FR set (`open`, `under_review`, `mitigated`, `closed`, `residual`); legacy `resolved` / `in_progress` are normalized on write. Closing requires `resolved_date`.

## Risk events (`/risk-events/`)

CRUD for risk, issue, delay, claim, change_order.

### Query

- `event_type` — including `risk` and `issue` (separate paths)
- `status`, `severity`, `search`, `date_from`, `date_to`
- `impact` — one of `schedule`, `cost`, `quality`, `safety`, `contract`, `liquidity`

### Body extras

- FR fields: `cause`, `consequence`, `response`, `probability_level` (1–5), `impact_severity_level` (1–5), `composite_score` (read-only product or null), `due_date`, impact booleans, optional `activity` / `cost_item` / `contract` / `related_decision_ref`
- Closing with open `RiskAction` rows without `acknowledge_open_actions: true` → **400** `{ "code": "open_actions_warning", ... }`

## Risk matrix (`/risk-events/matrix/`)

Open **risk** events only (`event_type=risk`, status not closed). Prefers level-based axes when `probability_level` and `impact_severity_level` are set.

## Risk actions (`/risk-actions/`)

CRUD child actions (`risk_event`, `description`, `due_date`, `owner`, `status` open|done).

## Inspections (`/inspections/`)

Requires `wbs`, `responsible_user`, `inspection_date`. Optional `stage`, `result`, `description`, `activity`.

## Nonconformities (`/nonconformities/`)

`inspection` (preferred), `description`, `raised_date`, `status`, optional `wbs` (copied from inspection when linked).

## Corrective actions (`/corrective-actions/`)

Requires `nonconformity`; optional `responsible_user`, `due_date`, `status`, `completed_date`.

## HSE events (`/hse-events/`)

`kind` = `incident` | `near_miss`; `event_date` + `description` required; `wbs` optional.

## Work permits (`/work-permits/`) / Safety trainings (`/safety-trainings/`)

Date-required registers included in period report.

## Quality & safety period report (`/quality-safety/report/`)

`GET ?date_from=&date_to=` (required). Returns section arrays + `counts`. Empty period → empty arrays and zero counts (no fabricated safety score). Does not merge daily-report incidents.
