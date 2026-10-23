# Contract: Unit Daily Report API

**Feature**: `032-unit-report-source-truth`  
**Base**: `/api/v1/projects/{project_id}/units/{unit}/daily-reports/`

`unit` is one of the six canonical values and is taken from the URL. It is never accepted as an editable report field.

## Endpoints

| Method | Path | Behavior |
|---|---|---|
| `GET` | `current/?date={date}` | Return the current report for project/date/unit; `404 unit_report_not_found` when absent |
| `POST` | `open/` | Idempotently return the current report or create its first draft; body `{ "report_date": "..." }`; `201` when created, `200` when existing |
| `GET` | `{report_id}/` | Current or historical version detail, scoped to URL project/unit |
| `PATCH` | `{report_id}/` | Update current draft/rejected content only |
| `DELETE` | `{report_id}/` | Soft-delete current draft/rejected version only |
| `GET` | `{report_id}/history/` | Ordered lineage versions and immutable status events |
| `POST` | `{report_id}/submit/` | Draft/rejected → submitted |
| `POST` | `{report_id}/approve/` | Submitted → approved; SoD enforced |
| `POST` | `{report_id}/reject/` | Submitted → rejected; requires `rejection_reason` |
| `POST` | `{report_id}/correct/` | Approved → new current draft version; old version remains approved history |

Dates accept the existing date-field contract: Jalali `YYYY/MM/DD` or Gregorian ISO `YYYY-MM-DD`; response presentation remains compatible with the existing localized date serializer.

## Open/current semantics

- The uniqueness key is project + date + canonical unit.
- Concurrent `open` requests resolve to one current draft. Both may return the same ID, or one may receive a stable conflict and retry `current`; no duplicate current rows are allowed.
- `open` never creates a project-level DailyReport and never changes submitted/approved content.
- If a current version exists in any state, `open` returns it and its capabilities.

## Detail response

```json
{
  "id": "unit-report-version-uuid",
  "lineage_id": "lineage-uuid",
  "version_number": 2,
  "is_current": true,
  "project_id": "project-uuid",
  "unit": "buildings",
  "report_date": "1405/08/01",
  "status": "rejected",
  "last_changed_at": "2026-10-22T14:30:00Z",
  "audit": {
    "prepared_by": {"id": "...", "display_name": "..."},
    "submitted_by": {"id": "...", "display_name": "..."},
    "submitted_at": "...",
    "approved_by": null,
    "approved_at": null,
    "rejected_by": {"id": "...", "display_name": "..."},
    "rejected_at": "...",
    "rejection_reason": "..."
  },
  "capabilities": {
    "can_edit": true,
    "can_submit": true,
    "can_approve": false,
    "can_reject": false,
    "can_correct": false,
    "can_delete": true,
    "can_view_history": true
  },
  "content": {
    "activity_records": [],
    "legacy_contributions": []
  }
}
```

Capabilities are convenience projections only; every mutation re-evaluates membership, permission, URL/object unit consistency, state, current version, and SoD on the server.

## History response

```json
{
  "lineage_id": "...",
  "current_version_id": "...",
  "versions": [
    {
      "id": "...",
      "version_number": 1,
      "status": "approved",
      "is_current": false,
      "created_at": "...",
      "superseded_by": "..."
    }
  ],
  "events": [
    {
      "event_type": "rejected",
      "from_status": "submitted",
      "to_status": "rejected",
      "actor": {"id": "...", "display_name": "..."},
      "occurred_at": "...",
      "reason": "..."
    }
  ]
}
```

Pre-feature history contains a migration baseline event and only the actors/times actually present in legacy data; missing historical facts are not invented.

## Report-owned activity records

The existing activity payload remains compatible during this feature, but mutations are nested or explicitly bound to a report version:

`/api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/activity-records/`

- List/export may read historical versions according to permissions.
- Create/update/delete/import requires current draft/rejected state.
- Parent project/date/unit is server-derived; mismatched body values are rejected.
- Unchanged row IDs survive report edits.
- Detailed per-unit section fields remain outside this contract and are designed in the next feature.

## Permission matrix

| Action | Required checks |
|---|---|
| Current/detail/history/source read | Active project membership + `view_reports` + object in URL project/unit |
| Open/create/edit/delete/correct/submit | Active membership + `edit_reports` + object in URL project/unit |
| Approve/reject | Active membership + `approve_reports` + object scope |
| Approve | Above + preparer/submitter SoD; only existing superuser break-glass may bypass |

Cross-project or wrong-unit identifiers return the normal non-disclosing not-found response.

## Stable errors

| Code | Meaning |
|---|---|
| `invalid_specialty_unit` | URL unit is outside the canonical six |
| `unit_report_not_found` | No scoped report/current report exists |
| `unit_report_not_editable` | Current status is not draft/rejected or version is historical |
| `unit_report_not_current` | Mutation targets a superseded version |
| `invalid_unit_report_transition` | Requested transition is invalid |
| `rejection_reason_required` | Rejection reason is blank |
| `sod_self_approve` | Approval violates SoD |
| `unit_report_conflict` | Concurrent operation changed the current version; client must refetch |
| `source_relation_project_mismatch` | Nested source points outside the report project |

Messages are localized; clients branch only on stable codes.

## Legacy retirement

- Browser route `/projects/{projectId}/sub-reports` is absent and renders the standard application not-found state.
- Legacy client endpoints under `/api/v1/projects/{project_id}/sub-reports/` are unregistered at cutover and return no report data or mutation surface.
- Internal table/model compatibility may remain until the retirement milestone, but it is not a second client contract.
