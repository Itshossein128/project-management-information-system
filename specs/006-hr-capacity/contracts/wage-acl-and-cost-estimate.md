# Contract: Wage ACL & approved-rate cost estimate

## Wage / rate field ACL

Applies to any response that historically included monetary employee rates:

- Project membership serializers that expose `wage`, `wage_type`, totals
- `ApprovedLaborRate` list/detail
- Daily-report `daily_rate` where treated as confidential labor rate (display)

### Rule

- Caller **with** `view_wage`: fields included as today.
- Caller **without** `view_wage`: fields omitted (or null) — never returned in cleartext. Writes to wage/rate require `edit_wage` or `edit_hr` + `view_wage` (implement chooses one; document in ENDPOINTS.md).

### Membership example (without permission)

Response must not contain `wage` / `wage_type` keys with values (omit preferred).

### Errors

| Code | When |
|------|------|
| `permission_denied` | PATCH wage without wage edit permission |

## Approved labor rates

**Base**: `/api/v1/projects/{project_id}/approved-labor-rates/`

- Read: `view_hr` + amounts only if `view_wage`
- Write: `edit_hr` (+ wage permission)

```json
{
  "person_id": "uuid|null",
  "amount": "1500000.00",
  "currency": "IRR",
  "effective_from": "2026-01-01",
  "effective_to": null
}
```

## Cost estimate

`POST /api/v1/projects/{project_id}/labor-cost-estimate/`

```json
{
  "person_id": "uuid",
  "approved_hours": "8.00",
  "as_of": "2026-04-10"
}
```

### Success with rate

```json
{
  "amount": "12000000.00",
  "currency": "IRR",
  "rate_amount": "1500000.00",
  "hours": "8.00",
  "warning": null
}
```

(`rate_amount` omitted if caller lacks `view_wage`; `amount` may still be shown to cost viewers with `view_costs` — product default: require `view_wage` to see estimate amount as well, or allow `view_costs` to see amount only. **Decision**: estimate `amount` requires `view_costs` OR `view_wage`; `rate_amount` requires `view_wage`.)

### Missing approved rate

```json
{
  "amount": null,
  "currency": null,
  "rate_amount": null,
  "hours": "8.00",
  "warning": "missing_approved_rate"
}
```

**Never** invent a rate from membership wage or daily_rate under the label “approved.”

## Progress isolation (regression)

No endpoint in this feature updates activity physical progress. Allocation and estimate APIs MUST NOT call progress recalculation.
