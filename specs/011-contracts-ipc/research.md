# Research: Contracts & IPC Gap Closure

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `Contract`, `ChangeOrder`, `IPC`, `IPCDeduction`, `IPCCollection` models and workflows already exist under `apps/api/core/contracts/`.
- Partial collections + `remaining_receivable` + cash-flow receivables summary shipped in 003-central-data-model.
- IPC statuses: draft → submitted → approved → paid (and rejected/cancelled variants as implemented).
- Overdue filter `?overdue=true` on IPC list already exists.

### Gaps to close

1. **payment_terms**: Spec doc requires explicit payment terms text; model has retention/advance percentages but no free-text terms clause.
2. **Submitted vs approved amounts**: Spec distinguishes مبلغ اعلامی vs مبلغ تأییدشده. Today only `gross_amount` (and computed `net_amount`). Risk: approve-with-reduction loses the contractor’s submitted figure.
3. **Collection ≠ status**: Behavior exists but lacks a dedicated regression test; ensure no code path auto-sets PAID when remaining hits zero via collection alone (pay remains explicit).
4. **Near-due report**: Overdue filter alone is insufficient for FR-CON-005; need overdue + near-due bands with remaining &gt; 0.

### Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Amount fields | Add `submitted_amount` + `approved_amount` DecimalFields; keep `gross_amount` as working draft/edit value until submit | Backward compatible; backfill both from gross |
| Snapshot timing | On **submit**: freeze `submitted_amount = gross_amount`. On **approve**: set `approved_amount` (default = submitted; may reduce with note) and recompute deductions/net from approved | Matches FR-CON-002 |
| Variance note | `approval_variance_note` required when `approved_amount < submitted_amount` | Auditability |
| Near-due window | Query param `near_due_days` default **7** | Configurable without settings churn |
| Report location | `GET .../contracts/ipcs/receivables-report/` under contracts | FR-CON native; cash_flow stays aggregate |
| Auto-pay on full collection | **Do not** auto-transition to paid | FR-CON-003; user marks paid separately |
| Change orders | No model change; document as “الحاقیه” | Already satisfy addenda history |

### Alternatives considered

- Replace `gross_amount` with submitted/approved only → breaks existing API clients; rejected.
- Put near-due only in cash_flow → weaker FR-CON ownership; rejected for this feature (cash_flow may still consume later).
