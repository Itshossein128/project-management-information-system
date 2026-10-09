# Data Model: Multi-Level Budget

## BudgetVersion

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK Project | |
| kind | enum | `initial`, `approved`, `revised`, `final_forecast` |
| status | enum | `draft`, `submitted`, `approved`, `rejected` |
| version_number | int | Monotonic per project |
| name | str | Optional label |
| currency | char(3) | Default project currency |
| notes | text | |
| is_control | bool | True when this is the active ceiling baseline |
| submitted_at / submitted_by | | |
| approved_at / approved_by | | |
| rejected_at / rejected_by / rejection_reason | | |
| audit / soft-delete | | AuditSoftDeleteModel |

**Rules**: At most one `is_control=True` per project among non-deleted. Approve sets control for kinds that become control (`approved`/`revised`); approving `final_forecast` only becomes control if explicitly requested (`promote_to_control=true`).

## Budget (line) — extensions

Existing fields retained: project, activity, wbs, cbs, cost_category, budget_amount, notes.

| New field | Type | Notes |
|-----------|------|-------|
| version | FK BudgetVersion | Required after migration |
| level | enum | `project`, `phase`, `contract`, `wbs`, `cbs`, `activity` |
| contract | FK Contract | Optional; required when level=contract |
| period_start / period_end | date | Optional time bucket |
| currency | char(3) | Optional override; default version currency |

**Validation**: Level determines required FKs (project-only: no wbs/activity/contract; phase/wbs: wbs; contract: contract; cbs: cbs; activity: activity). Relax prior “wbs or activity required” for project/contract/cbs/period-only lines.

## BudgetChangeRequest

| Field | Type | Notes |
|-------|------|-------|
| project | FK | |
| status | enum | `draft`, `submitted`, `approved`, `rejected`, `cancelled` |
| reason | text | min length 10 |
| amount_delta | decimal | Net change to project total |
| project_impact | text | Impact on project outcome |
| affected_lines | JSON | Proposed line creates/updates/deletes |
| resulting_version | FK BudgetVersion | Set on approve |
| base_version | FK BudgetVersion | Control version at create time |
| requester / decision fields | | Same pattern as ProjectChangeRequest |

## BudgetTransfer

| Field | Type | Notes |
|-------|------|-------|
| project | FK | |
| version | FK BudgetVersion | Must be control approved |
| from_line / to_line | FK Budget | Same version |
| amount | decimal | &gt; 0 |
| note | text | |
| created_by / created_at | | |

## Relationships

```text
Project 1──* BudgetVersion 1──* Budget (lines)
Project 1──* BudgetChangeRequest ──> resulting_version
BudgetVersion 1──* BudgetTransfer
Commitment / ActualCost ── (existing) ──> remaining calc (no new FK required)
```

## State transitions

**Version**: draft → submitted → approved | rejected; rejected/draft editable; approved immutable (lines).

**Change request**: draft → submitted → approved | rejected; draft|submitted → cancelled.
