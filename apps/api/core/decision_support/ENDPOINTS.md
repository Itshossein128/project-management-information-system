# Decision Support API

Base: `/api/v1/projects/{project_id}/`

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `decision-cases/` | view / edit `*_decision_support` |
| GET/PATCH/DELETE | `decision-cases/{id}/` | view / edit |
| GET/POST | `decision-cases/{id}/runs/` | view / edit |
| GET | `decision-cases/{id}/runs/{run_id}/` | view |
| PUT/PATCH/DELETE | `decision-cases/{id}/runs/{run_id}/` | `run_immutable` |

## Validation error (interim O03)

```json
{
  "error": {
    "code": "decision_input_invalid",
    "message": "…",
    "details": {
      "issues": [
        { "code": "empty_cell", "path": "performance_matrix.0.1", "message": "Cell cannot be empty." },
        { "code": "benefit_column_all_zero", "path": "criteria.0", "message": "…" }
      ]
    }
  }
}
```

## SAW run (Phase 2)

`POST …/runs/` with `{"method":"saw"}` validates ranking inputs, runs pure SAW (never TOPSIS), and appends an immutable run.

**Success `result`** (interim ordinal ranks — O01/O02 remain open as final product policy):

```json
{
  "status": "ok",
  "engine": "saw",
  "ranking": [
    { "option": "پیمانکار الف", "score": 1.0, "rank": 1 },
    { "option": "پیمانکار ب", "score": 0.5, "rank": 2 }
  ]
}
```

**Snapshot** includes live frozen inputs plus `weights_normalized` for audit.

SAW, TOPSIS, AHP and ISM execute independently. DEMATEL alone remains a placeholder: `{ "status": "stub", "engine": null }`.

## ISM run

`POST …/runs/` with `{"method":"ism"}` requires ISM selection and edit permission on the URL project. It locks the active case and reads its current ordered criteria and `ism_matrix`; no ranking inputs or other engine execution are needed.

Draft saves accept incomplete and finite-invalid JSON judgments for correction. Nonfinite numbers cannot be persisted. Execution requires one to ten unique nonempty trimmed names and an exact square matrix of numeric zero or one. Booleans, text, unanswered and other numeric values produce locatable issues such as `ism_relation_invalid` at `ism_matrix.0.1`; unsuccessful analyses append no run. Matrix-only PATCH preserves unrelated method inputs.

Successful `result` has `status: "ok"`, `engine: "ism"`, binary `reachability_matrix`, ordered `layers` (`level`, `criteria`), `mutual_groups` (`level`, `criteria`) and versioned `derivation_policy`. Derived self-reachability is one; the direct snapshot retains its original zero or one diagonal. Layers start with the top layer, and each criterion belongs to exactly one layer. Maximal mutually reachable groups contain at least two criteria and remain within their shared layer. Structural position does not prescribe importance, ranking or removal.

Every successful request appends a distinct immutable record containing frozen direct inputs, computed output, initiating actor and extraction time. Later draft edits, reruns and locale changes do not alter earlier records. There is no idempotency or client revision guarantee.

Read endpoints require `view_decision_support`; case changes and execution require `edit_decision_support`. View-only members can inspect frozen results but cannot create, edit or execute. Parent case and nested run queries are scoped to the URL project, including failed cross-project requests. Existing administrator policy applies. Localized messages retain stable method IDs, issue codes, paths and stored criterion names.

### Shared record lifecycle and history review

All five dispatch paths reload and lock the active project-scoped parent inside
one transaction before method selection, validation, computation and append.
Case PATCH merges/validates and writes only submitted fields under the same
parent lock; case soft deletion also takes that lock. Separate PATCH and POST
requests are not one transaction or a browser revision guarantee.

History filters precede pagination; fixed-set ordering is `-extracted_at,-id`.
The UUID tie break is deterministic, not an execution chronology. Individual
records remain immutable; repeated explicit requests append distinct records.
Actor identity and time are stored; actor display name reflects the account.

The bilingual review shows frozen named inputs and stored outputs independently
of live drafts/current results. Partial legacy inputs/output remain readable
with unavailable sections; normalized weights are never reconstructed. Completed
DEMATEL examples are review fixtures: the live DEMATEL dispatch remains a stub.

The four live panels guard the saved case before POST and the completed method
response before publishing success. An unconfirmed POST awaits one validated
unfiltered first-page history GET, with no retry and a ten-second deadline,
before releasing its case token. There is no automatic POST retry, exactly-once
or page-one absence guarantee. Review history before an explicit retry.

Current proof and exact commands: `specs/024-decision-execution-records/validation.md`.
