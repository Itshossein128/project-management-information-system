# API Contract: Contractor Stakeholder Select

Base: `/api/v1/projects/{project_id}/`

Auth: JWT + project membership as today’s stakeholder / department / field-report endpoints.

## 1. List contractors (options)

`GET /stakeholders/?role=contractor&status=active`

| Query | Meaning |
|-------|---------|
| `role=contractor` | Only canonical contractor role (after any stored normalization) |
| `status=active` | Active only |

**Response** (existing list envelope):

```json
{
  "results": [
    {
      "id": "<uuid>",
      "name": "…",
      "organization_name": "…",
      "role": "contractor",
      "status": "active",
      "email": null,
      "phone": null,
      "contacts_redacted": true
    }
  ]
}
```

Contact redaction rules unchanged. Soft-deleted never listed.

**Permissions**: same as stakeholder list (`view_project`).

## 2. Create / update contractor on ذینفعان

`POST|PATCH /stakeholders/`

| Field | Contract |
|-------|----------|
| `role` | May send `contractor` or `پیمانکار`; server stores `contractor` |
| `status` | `active` \| `inactive` |
| other | Existing stakeholder fields |

## 3. Department activity write

`POST|PATCH …/department-activity-records/` (existing paths)

| Field | Required (non-warehouse) | Notes |
|-------|--------------------------|-------|
| `contractor_ref` | yes | UUID of active same-project contractor |
| `contractor` | read-only or ignored on write | Server sets from stakeholder name |

**Errors**:
- Missing / null `contractor_ref` when required → 400 field error
- Unknown / wrong project / not contractor / inactive → 400 field error (no IDOR leak of other projects)

**List filter**: `contractor_ref=<uuid>` preferred; legacy `contractor=<substring>` may still match snapshot CharField for transition.

## 4. Department activity import

Excel/CSV پیمانکار column must resolve to an existing active contractor (exact name or UUID). Unresolved → row rejected with localized message pointing to ذینفعان. No auto-create.

## 5. Daily report activity / labor camp

Write payloads accept `contractor_ref` (Stakeholder UUID). Server sets `subcontractor_name` from stakeholder. Do not require or set `subcontractor_ref` (Contract) for this picker path.

## 6. Project settings

`PATCH` project accepts optional `contractor_ref`. Server sets `contractor` CharField from stakeholder name or clears both when null.

## 7. Cross-project isolation

All FK validation uses the path `project_id`. Stakeholder IDs from another project must fail validation.
