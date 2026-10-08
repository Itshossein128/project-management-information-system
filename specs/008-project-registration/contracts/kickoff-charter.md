# Contract: Project kickoff charter

**Base**: `/api/v1/projects/{project_id}/kickoff-charter/`

## Permissions

- GET: project member + `view_project` (or membership alone if that is the existing retrieve rule)
- PUT/PATCH: `edit_project`; denied if project `archived` unless system admin

## Get

`GET …/kickoff-charter/`

**200** charter object  
**404** if none yet (or **200** with empty defaults — prefer **404** + UI empty form)

## Upsert

`PUT …/kickoff-charter/` (create-or-replace) or `PATCH` for partial

```json
{
  "justification": "…",
  "success_criteria": "…",
  "constraints": "…",
  "assumptions": "…",
  "key_stakeholders_summary": "…",
  "pm_authority": "…"
}
```

**200/201** saved charter  
**403** archived / no `edit_project`

## Notes

- One charter per project (OneToOne).
- No approval workflow on charter in v1 (FR-PRJ-005 storage + visibility only).
- Structured stakeholder registry remains out of scope (spec 15).
