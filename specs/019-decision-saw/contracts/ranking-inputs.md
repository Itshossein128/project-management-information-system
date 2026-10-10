# Contract: Ranking Inputs (SAW Phase 2)

**Sources**: [02-decision-inputs.md](../../../docs/decision-support/02-decision-inputs.md), [018 input-validation](../../018-decision-case-shell/contracts/input-validation.md)  
**UI inventory**: WeightVectorEditor, CriterionTypeToggle, RectangularMatrixEditor

## Persistence (case)

Live fields on `DecisionCase` (existing Phase 1 API):

| Field | Editor | Rules at SAW run |
|-------|--------|------------------|
| `weights` | WeightVectorEditor | `n` finite ≥ 0; sum > 0; optional live normalize preview (display only) |
| `types` | CriterionTypeToggle | `n` values `benefit` \| `cost` |
| `performance_matrix` | RectangularMatrixEditor | `m`×`n`; finite ≥ 0; empty/null invalid at run; empty ≠ 0 |

`PATCH /decision-cases/{id}/` accepts partial updates of these fields. Saving incomplete drafts MAY be allowed; **running SAW** requires the full ranking contract.

## Structural rules

All Phase 1 ranking rules (AC05–AC12) apply. Additionally at SAW execution:

| ID | Rule | code | path |
|----|------|------|------|
| AC09 | Cost cell ≤ 0 | `cost_zero` | `performance_matrix.{i}.{j}` |
| AC10 | Negative / all-zero weights | `weight_negative` / `weights_all_zero` | `weights.{j}` / `weights` |
| AC13 | Benefit column all zeros | `benefit_column_all_zero` | `criteria.{j}` |

Error envelope unchanged: `decision_input_invalid` + `issues[{code,path,message}]` (AC26).

## UI contract (product surface)

| Surface | Responsibility |
|---------|----------------|
| WeightVectorEditor | Edit `n` weights; MAY show normalized preview from client arithmetic for UX only — **not** source of truth for scores |
| CriterionTypeToggle | Per-criterion benefit/cost |
| RectangularMatrixEditor | m×n grid; reject empty cells in UI when possible; server still enforces |
| RunActionBar | Validate (surface issues) → Run SAW (POST run) |
| SawMethodPanel | Compose shared editors + RunActionBar + RankingResultTable |
| RankingResultTable | Columns: option, score, rank from `result.ranking`; method=`saw` |
| ValidationIssueList | Render `issues` with paths |

**MUST NOT**: implement SAW normalization/scoring in React; call TOPSIS as part of SAW run; blend method scores.

## Non-goals

- TopsisMethodPanel (Phase 3)
- Square matrices (AHP/DEMATEL/ISM)
- Excel import
