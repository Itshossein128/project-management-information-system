# Contract: Documents & Correspondence

## APIs

Base: `/api/v1/projects/{project_id}/`

### Documents

`GET|POST /documents/`  
`GET|DELETE /documents/{id}/`  
`POST /documents/{id}/revisions/`

Permission: `view_documents` (GET), `upload_documents` (POST/DELETE/revise).

#### Query (GET list) — extended

| Param | Meaning |
|-------|---------|
| doc_type | existing |
| status | `draft` \| `in_review` \| `approved` \| `superseded` \| `obsolete` |
| date_from / date_to | on revision_date (or document revision_date) |
| search | title / doc_code / tags |
| related_activity / related_wbs / discipline / access_level | existing |

#### Create/update fields (extras)

```json
{
  "title": "Foundation plan",
  "doc_code": "DWG-001",
  "doc_type": "drawing",
  "status": "draft",
  "approver": "<user-uuid|null>"
}
```

#### Revise

`POST /documents/{id}/revisions/` multipart: file + `revision_label` + `revision_date` + optional `change_description`.

**Rules**:

- Creates a new `DocumentRevision` row; previous revisions remain listable and their `file_url` remains valid.
- Updates parent current revision fields; prior revision is not physically deleted.
- Unauthorized revise → 403; existing versions unchanged.

#### Detail includes revisions

```json
{
  "id": "<uuid>",
  "doc_code": "DWG-001",
  "status": "approved",
  "approver": "<uuid|null>",
  "revision": "B",
  "revisions": [
    { "revision_label": "A", "revision_date": "2026-09-01", "file_url": "..." },
    { "revision_label": "B", "revision_date": "2026-10-01", "file_url": "..." }
  ]
}
```

### Correspondence

`GET|POST /correspondence/`  
`PATCH|DELETE /correspondence/{id}/`  
`POST /correspondence/{id}/respond/`

Permission: `view_correspondence` / `edit_correspondence`.

#### Body extras

```json
{
  "corr_type": "outgoing",
  "subject": "RFI-12",
  "from_party": "Contractor",
  "to_party": "Employer",
  "corr_date": "2026-10-09",
  "status": "open",
  "related_contract": "<uuid|null>",
  "file_url": "..."
}
```

**Rules**: `related_contract` MUST belong to the same project or validation fails.

## Compatibility

Existing document/correspondence clients that ignore new fields keep working. New filters are additive.
