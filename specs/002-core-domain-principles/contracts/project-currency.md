# Contract: Project Currency

**Feature**: `002-core-domain-principles`  
**Base path**: `/api/v1/projects/{project_id}/`

## Project resource fields

`GET/PATCH /api/v1/projects/{project_id}/` and create payloads include:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `currency` | string enum `IRR` \| `IRT` | yes (default `IRR`) | Project base unit |

## Money presentation rule

Any API money field in responses touched by this feature SHOULD include either:

- implicit project currency via project payload, or
- explicit `currency` alongside the amount when multi-currency values appear.

## Aggregate guard (service contract)

```text
sum_amounts(items, target_currency, rate=None)
```

- If all items share one currency equal to `target_currency` → OK.
- If currencies differ and `rate` is missing → raise validation error `currency_mix_forbidden`.
- If `rate` provided → convert explicitly and return amount in `target_currency`.

## Errors

| Code | HTTP | When |
|------|------|------|
| `currency_mix_forbidden` | 400 | Mixed IRR/IRT without rate |
| `invalid_currency` | 400 | Value not in enum |

## Permissions

- Read: existing `view_project` (or equivalent)
- Update currency: `edit_project` (or project settings permission already used for project PATCH)
