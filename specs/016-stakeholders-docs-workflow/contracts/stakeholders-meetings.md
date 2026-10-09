# Contract: Stakeholders, Communication Plan & Meeting Actions

## APIs

Base: `/api/v1/projects/{project_id}/`

### Stakeholders

`GET|POST /stakeholders/`  
`GET|PATCH|DELETE /stakeholders/{id}/`

Permission: `view_project` (GET), `edit_project` (mutate).

#### Create/update body (extras)

```json
{
  "name": "Owner Rep",
  "organization_name": "Client Co",
  "role": "Employer",
  "email": "a@example.com",
  "phone": "+10000000000",
  "influence": 5,
  "interest": 4,
  "communication_need": "Weekly progress",
  "relationship_owner": "<user-uuid>",
  "status": "active"
}
```

#### Contact redaction

- Without `view_sensitive_contacts` or `edit_project`: response sets `email`/`phone` to `null` (or omits) and may include `"contacts_redacted": true`.
- With permission: full values returned.

### Influence–interest matrix

`GET /stakeholders/matrix/`

Permission: `view_project`.

```json
{
  "cells": [
    { "influence": 5, "interest": 4, "stakeholders": [{ "id": "<uuid>", "name": "..." }] }
  ]
}
```

### Communication plan

`GET|POST /communication-plans/`  
`GET|PATCH|DELETE /communication-plans/{id}/`

Permission: `view_project` / `edit_project`.

```json
{
  "audience": "Employer team",
  "message": "Monthly KPI pack",
  "channel_type": "report",
  "frequency": "monthly",
  "owner": "<user-uuid>",
  "stakeholder": "<uuid|null>",
  "status": "active"
}
```

### Meetings (existing, extended)

`GET|POST /meetings/`  
`GET|PATCH|DELETE /meetings/{id}/`

Permission: `view_documents` / `upload_documents` (existing DocScoped pattern).

### Meeting actions

`GET|POST /meetings/{meeting_id}/actions/`  
`PATCH /meeting-actions/{id}/` (mark done)

Nested create:

```json
{
  "description": "Issue RFI for slab edge",
  "owner": "<user-uuid>",
  "due_date": "2026-10-20",
  "status": "open"
}
```

### Open-actions report

`GET /meeting-actions/open/?overdue=true`

Permission: `view_documents`.

```json
{
  "results": [
    {
      "id": "<uuid>",
      "meeting": "<uuid>",
      "description": "...",
      "owner": "<uuid>",
      "due_date": "2026-10-20",
      "status": "open",
      "is_overdue": true
    }
  ]
}
```

## Rules

- Influence/interest remain 1–5 when set.
- Completing an action sets `status=done` and `completed_at`; it leaves the open report.
- Soft-delete via existing destroy behavior where applicable.
