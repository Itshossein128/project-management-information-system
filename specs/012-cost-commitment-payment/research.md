# Research: Cost Commitment & Payment Gap Closure

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `Commitment`, `ActualCost`, `Payment` under `apps/api/core/cost_control/` with project tenancy and soft-delete.
- Commitment approve already requires WBS or CBS (`wbs_or_cbs_required`).
- Payment linked to commitment and/or actual cost; commitment `remaining` = amount − posted payments (`cbs_services.posted_payments_total`).
- `budgets/remaining/` returns approved / committed / consumed / remaining per heading (010).
- Actual-cost duplicate `invoice_number` uses warn + `acknowledge_warnings` (core principles tests).
- Procurement `RequisitionHeader` multi-stage workflow including `CONTROL_CHECK` / `HQ_CONTROL_APPROVAL` / `FINAL_APPROVAL` → `APPROVED`.
- Contracts module (011) owns employer IPC collections — **not** this feature’s payment ledger.

### Gaps to close

1. **payment_terms** missing on Commitment; party is free-text only (optional contract FK missing).
2. **ActualCost** has single `cost_date`, `approved_by` without status workflow; no occurrence vs register split.
3. **Payment** has no duplicate-`document_ref` guard (unlike actual costs).
4. **Remaining math** subtracts full committed + full consumed → double-count when actual is linked to the same commitment.
5. **Contract/order remaining** not exposed via cost_payments ledger.
6. **No unified document-traceable ledger report** on costs UI; payments UI absent.
7. **Requisition → commitment** handoff missing; financial review is implicit in control/HQ steps but conversion action does not exist.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Implementation method | **TDD** (failing pytest → minimal fix → refactor) | Explicit user constraint for tasks; aligns with constitution VI |
| Ledger spine | Extend Commitment / ActualCost / Payment | Spec assumption; avoids parallel ledgers |
| Remaining formula | `open_committed = max(0, approved_commitment − sum(actuals linked to that commitment))`; heading `remaining = approved − sum(actuals) − sum(open_committed for commitments on heading)` | Removes double-count; SC-006; still reduces remaining when only a commitment exists |
| Unlinked actuals | Count fully in consumed | Standalone actuals (policy-allowed) still consume budget |
| payment_terms | `TextField` on Commitment | Mirrors Contract.payment_terms (011) |
| Contract link | Optional `ForeignKey(contracts.Contract)` on Commitment | FR origin; remaining rolls payments through linked commitments |
| Requisition origin | Optional `ForeignKey(procurement.RequisitionHeader)` on Commitment | Traceability for convert action |
| Financial review | Reuse existing control/HQ/final stages; **block create-commitment unless status = APPROVED** | Avoid new status enum churn; map “financial review complete” to approved requisition |
| Actual dates | Keep `cost_date` as **occurrence**; add `registered_at` (DateField, default=today on create) | Minimal rename risk; FR-CST-003 |
| Actual approval | Add `status`: draft / approved / void; `approve` action sets approved_by + status | Aligns with commitment-style workflow |
| Document required | Project capability or cost settings flag `require_cost_document` (default false); when true, block finalize without `invoice_number`/`document_ref` | Spec policy; sensible default |
| Payment duplicate | Within project, non-empty `document_ref`, status posted: second create → error `duplicate_payment_document` unless `acknowledge_duplicate_exception` + `exception_reason` stored | Mirrors actual-cost ack pattern; SC-002 |
| Exception audit | Store `duplicate_exception_reason`, `duplicate_exception_by` on Payment when exception used | Authorized exception trail |
| Contract remaining | Derived: contract.amount (− approved change orders as already modeled) − sum(posted payments on commitments with that contract_id) | FR-009 without mixing IPC collections |
| Order remaining | For commitments with requisition origin and no contract: remaining = commitment.amount − posted payments (existing); expose on convert response and ledger | Spec “order” ≈ commitment from requisition until a dedicated PO model is linked |
| Legacy `resources.PurchaseOrder` | Out of scope for new handoffs | Spec assumption |
| Ledger report | `GET .../costs/ledger-report/` returning rows typed commitment \| actual \| payment with document refs | FR-011 / SC-003 |
| UI | Extend `/projects/{id}/costs` — payment terms on commitment form; Payments tab/panel; ledger report panel | No new top-level route |
| IPC payments | Do not use `cost_control.Payment` for employer IPC | Owned by 011 |

## Alternatives considered

- **Replace remaining with committed-only until paid** — rejects actual consume too late; rejected.
- **New PurchaseOrder financial entity** — larger than gap closure; rejected for v1 (commitment is the order financial spine).
- **New FINANCIAL_REVIEW requisition status** — workflow churn; rejected in favor of APPROVED gate.
- **Soft-warn only on duplicate payments** — too weak for SC-002; hard block + explicit exception chosen.
- **Auto-reduce commitment amount when actual posts** — mutates pledge history; rejected; use open_committed derivation instead.

## NEEDS CLARIFICATION

None remaining — all Technical Context unknowns resolved above.
