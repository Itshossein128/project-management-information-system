# Contract: Commitment and baseline gates (FR-PRJ-004 / FR-010)

Shared project readiness helpers used by other domains — not standalone UX.

## Helpers (service layer)

```text
assert_project_allows_definitive_baseline(project) -> None
assert_project_allows_binding_commitment(project) -> None
```

**Allow** only when `project.status == 'active'`.

**Reject** with **400** when status is `draft`, `pending_approval`, `suspended`, `completed`, or `archived`:

| Code | Typical message key |
|------|---------------------|
| `project_not_active_for_baseline` | Cannot lock/create definitive baseline |
| `project_not_active_for_commitment` | Cannot create binding financial commitment |

## Call sites (implement time)

1. `apps/api/core/schedule/services/baseline_service.py` — before `approve_lock_baseline` and before creating a baseline with `is_locked=True`.
2. Binding commitment create — primary entry identified at implement (prefer Contract create in `contracts` if that is the binding commitment; else cost-control `Commitment` create). Do **not** block ordinary draft cost lines or WBS edits.

## Tests

- Draft/pending project → lock baseline → 400  
- Suspended project → lock baseline → 400  
- Active project → lock baseline still succeeds (regression)  
- Draft project → binding commitment create → 400  

Existing locked baselines remain readable regardless of later suspend/archive.
