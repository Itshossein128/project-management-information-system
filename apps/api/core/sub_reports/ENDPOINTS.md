# Sub-Reports Endpoints

Discipline sub-reports (civil, electrical, mechanical, etc.) with nested activity rows and an approval workflow. All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Action | Permission | Notes |
|--------|------------|-------|
| List / retrieve | `view_reports` + `IsProjectMember` | |
| Create / update / delete / submit | `edit_reports` | |
| Approve / reject | `approve_reports` | |

## Endpoints

Base path: `sub-reports/`

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `sub-reports/` | GET | List sub-reports. Filter: `discipline`. Ordered by `-report_date`. |
| `sub-reports/` | POST | Create sub-report with nested `activities`. |
| `sub-reports/{pk}/` | GET | Detail with prefetched activities and activity count. |
| `sub-reports/{pk}/` | PATCH | Update header. If `activities` provided, existing activities are soft-deleted and replaced. |
| `sub-reports/{pk}/` | DELETE | Soft-delete |
| `sub-reports/{pk}/submit/` | POST | Draft → `submitted` |
| `sub-reports/{pk}/approve/` | POST | Submitted → `approved` |
| `sub-reports/{pk}/reject/` | POST | Submitted → `rejected`. Body: `rejection_reason` (min 10 chars). |

### Approval workflow

```
draft ──submit──► submitted ──approve──► approved
  ▲                    │
  └────reject──────────┘
```

Workflow actions (`submit`, `approve`, `reject`) are registered by `WorkflowViewSetMixin` (`common/mixins.py`). `DisciplineSubReportViewSet` implements template methods `_submit`, `_approve`, `_reject` that delegate to `sub_reports/services.py`.

Unlike daily reports, sub-reports have no `under_review` step and no separate `review` action.

## Payload (create / update)

| Field | Notes |
|-------|-------|
| `report_date` | Jalali or Gregorian |
| `discipline` | e.g. `civil`, `electrical`, `mechanical`, `plumbing`, `hvac`, `finishing` |
| `weather_condition`, `form_code`, `revision_number` | Optional metadata |
| `linked_daily_report` | Optional FK to `field_reports.DailyReport` |
| `activities` | Array of activity progress rows (replaced wholesale on PATCH when provided) |

## Operational notes

- **Shared pattern:** same `WorkflowViewSetMixin` used by `field_reports.DailyReportViewSet`; see `field_reports/ENDPOINTS.md` for the daily-report variant (includes `review` and stricter submit validation).
- **Permissions:** list/retrieve require project membership; write paths use `HasProjectPermission` only.
