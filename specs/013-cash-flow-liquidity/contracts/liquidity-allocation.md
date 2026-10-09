# Contract: Liquidity Scores, Proposal, Decision, Simulation

## Priority score

`GET|PUT /api/v1/projects/{project_id}/cash-flow/priority-score/`

```json
{
  "urgency": 80,
  "return_score": 60,
  "recovery_speed": 70,
  "risk": 40,
  "composite": 67.5,
  "notes": ""
}
```

Composite = (urgency + return_score + recovery_speed + (100 − risk)) / 4.

## Allocation cycle

`POST /api/v1/cash-flow/portfolio/cycles/`

```json
{
  "name": "2026-Q4",
  "period_start": "2026-10-01",
  "period_end": "2026-12-31",
  "available_liquidity": 5000000,
  "currency": "IRR"
}
```

## Generate proposal

`POST /api/v1/cash-flow/portfolio/cycles/{id}/propose/`

- Ranks member-visible projects with **complete** scores by composite desc.
- Allocates greedily up to `available_liquidity` using each project’s suggested need for the cycle period (positive need only).
- Zero pool → `{ "lines": [], "message": "no_available_liquidity" }`.
- Incomplete scores listed in `warnings.incomplete_score_projects`.

## Save decision

`POST /api/v1/cash-flow/portfolio/cycles/{id}/decisions/`

```json
{
  "owner_id": "<uuid>",
  "rationale": "Prioritize Project A for concrete pour",
  "acknowledge_overlap": false,
  "lines": [
    {
      "project_id": "<uuid>",
      "amount": 2000000,
      "period_start": "2026-10-01",
      "period_end": "2026-10-31",
      "schedule_impact": "Keeps critical path",
      "cost_impact": "Avoids idle crew"
    }
  ]
}
```

Errors:

| Code | When |
|------|------|
| `owner_required` / `rationale_required` | Missing |
| `overlapping_allocation` | Overlap without ack |

## Simulation

`POST /api/v1/cash-flow/portfolio/cycles/{id}/simulations/` — body `{name, lines}`  
`GET .../simulations/{id}/compare/` — diff vs latest proposal.

## UI

Portfolio liquidity page: cycle form, score completeness, proposal table, decision form (owner/rationale required), overlap dialog, simulation save/compare.

## Test anchors

1. Proposal order by composite; respects pool.
2. Decision without rationale → 400.
3. Overlap without ack → 400 `overlapping_allocation`; with ack → 201.
4. available_liquidity=0 → empty lines + message.
