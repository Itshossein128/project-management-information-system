# Contract: Project change requests

**Base**: `/api/v1/projects/{project_id}/change-requests/`

Distinct from schedule change requests under `/schedule/…`.

## Permissions

| Action | Permission |
|--------|------------|
| List / retrieve | Project member |
| Create / update draft / submit / cancel | `edit_project` |
| Approve / reject | `approve_project` |

## Protected field keys

`start_date`, `planned_finish_date`, `contract_amount`, `employer`, `scope_description`

## Create

`POST …/change-requests/`

```json
{
  "reason": "Employer legal name correction (min 10 chars)",
  "proposed_changes": {
    "employer": "New Employer Co"
  }
}
```

Preconditions: project status allows CR (`active` or `suspended`); no other open CR (`draft`/`submitted`).

**201** created (`status=draft`)  
**409** `change_request_already_open`  
**400** `invalid_proposed_keys` / `reason_required`

## Lifecycle

| Method | Path | Effect |
|--------|------|--------|
| PATCH | `…/change-requests/{id}/` | Update reason/proposed while draft |
| POST | `…/{id}/submit/` | draft → submitted; snapshot `previous_values` |
| POST | `…/{id}/approve/` | Apply `proposed_changes` to Project; status → approved |
| POST | `…/{id}/reject/` | status → rejected; project unchanged |
| POST | `…/{id}/cancel/` | draft/submitted → cancelled |

## List / detail

`GET …/change-requests/`  
`GET …/change-requests/{id}/`

Returns reason, status, proposed/previous, requester, decision metadata.

## Interaction with PATCH project

Direct `PATCH` of protected keys on active/suspended/completed/archived → **400** `protected_field_requires_change_request` (see lifecycle contract). Draft/pending_approval projects may still PATCH those fields without CR.

## Errors

| Code | When |
|------|------|
| `change_request_already_open` | Open CR exists |
| `reason_required` | Reason &lt; 10 chars |
| `invalid_proposed_keys` | Key outside protected set or empty payload |
| `invalid_change_request_status` | Illegal transition |
