# API Contract: MSP Family Import (XML + MPP)

Base: `/api/v1/projects/{project_id}/import/msp/`

Auth: JWT. Preview and start require project membership + **`edit_wbs`**. Status requires project membership + existing status permission (`view_wbs` as today). All lookups are project-scoped (`project_id` + job id) to prevent IDOR.

P6 XER remains under `/import/p6/` (unchanged by this feature except regression guarantee).

## 1. Preview

`POST /import/msp/preview/`  
`Content-Type: multipart/form-data`

| Field | Required | Rules |
|-------|----------|-------|
| `file` | yes | `.xml` or `.mpp`; ≤ 50 MB; content validated server-side |

**Behavior**:
- `.xml` → existing `parse_msp_xml` + `build_preview` (no project mutation).
- `.mpp` → validate → convert to MSPDI (bounded) → `parse_msp_xml` + `build_preview` (no project mutation).
- Same file bytes must yield consistent preview vs later import mapping for supported fields.

**Success** `200` — existing preview shape:

```json
{
  "wbs_tree": [],
  "activities": [],
  "warnings": []
}
```

**Errors** `400` (validation / processing) — prefer envelope:

```json
{
  "error": {
    "code": "mpp_password_protected",
    "message": "<localized>",
    "details": {}
  }
}
```

| HTTP | `error.code` | Notes |
|------|--------------|-------|
| 400 | `invalid_file_type` | Wrong type / misleading rename |
| 400 | `file_too_large` | > 50 MB |
| 400 | `mpp_corrupt` | Corrupt/unreadable MPP |
| 400 | `mpp_password_protected` | Protected; no bypass |
| 400 | `mpp_unsupported` | Genuine MPP, cannot process |
| 400 | `msp_invalid_xml` | Invalid XML (existing) |
| 400 | `processing_timeout` | Conversion exceeded bound |
| 400 | `conversion_failed` | JRE/MPXJ/internal failure |
| 403 | (permission) | No `edit_wbs` / not member |

## 2. Start import

`POST /import/msp/`  
`Content-Type: multipart/form-data`

| Field | Required | Rules |
|-------|----------|-------|
| `file` | yes | Same as preview |
| `replace` | no | `true` / `false` (default false = append) |

**Behavior**: Validate + convert/parse (same as preview path for the file family). On success, create `MspImportJob` with `file_data`, `filename`, `replace_existing`, `created_by`, queue async execute (convert-if-needed then `execute_msp_import`).

**Success** `202`:

```json
{
  "task_id": "<job-uuid>",
  "status": "queued"
}
```

**Errors**: Same codes as preview (`400` / `403`). On `403`/`400` before persistence, no job row (or no domain mutation). Failed worker execution → job `failed` with `error_code` + `error_message`; transactional domain writes rolled back.

## 3. Job status

`GET /import/msp/status/{task_id}/`

**Success** `200`:

```json
{
  "status": "pending|running|done|failed|queued",
  "progress_pct": 0,
  "result": {
    "wbs_nodes_created": 0,
    "activities_created": 0,
    "relations_created": 0,
    "warnings": []
  },
  "error": "<localized when failed>",
  "error_code": "mpp_corrupt"
}
```

`result` only when `done`. `error` / `error_code` when `failed`. Clients may omit unused keys.

**Errors**:
- `404` if job not in this project (do not leak other projects’ jobs).
- `403` if not a project member / lacking status permission.

## 4. Idempotency and isolation

- Preview never mutates WBS/activities/relations/baselines.
- Replace/append semantics identical to current MSP XML execute.
- Users cannot read another project’s upload, preview side effects, or job.

## 5. OpenAPI

Update drf-spectacular summaries/descriptions: MSP import accepts **Microsoft Project XML and native MPP**, not XML-only.
