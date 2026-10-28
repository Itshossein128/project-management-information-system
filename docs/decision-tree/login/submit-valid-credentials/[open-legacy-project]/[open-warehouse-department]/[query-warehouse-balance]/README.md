# Decision: Query warehouse stock balance

## Context & Screen

- **Route**: `/projects/:businessId/warehouse` (API endpoint: `/api/v1/projects/:businessId/department-activity-records/warehouse-balance/`)
- **Component**: `WarehouseBalanceView`
- **Initial State**: The authenticated user or client service requests real-time cumulative warehouse inventory levels.

## Action Taken

- **Trigger**: Programmatic web service request (or inventory dashboard widget).
- **Inputs**:
  - `as_of_date` (optional query parameter, ISO `YYYY-MM-DD` or Jalali, defaults to current date).
  - `search` (optional query parameter, case-insensitive substring search for material type).

## Authorization & Permissions

- **Required Permissions**: `view_reports` permission alongside project membership (`IsProjectMember`, `HasProjectPermission`, `CanViewBusinessAssignments`, `IsVisitorReadOnly`, `IsHrOrAdminOrReadOnly`).
- **Required Roles / Groups**: Project member with report view rights (e.g. project manager, warehouse auditor, site engineer).
- **Protection notation**: Permission-gated decision node; directory uses brackets `[query-warehouse-balance]`.

## Desired Result

- **API Call**: GET `/api/v1/projects/:businessId/department-activity-records/warehouse-balance/?as_of_date=YYYY-MM-DD&search=...`
- **State Change**: Read-only query; no persistent state changes.
- **Navigation**: None (headless API / inline query).
- **UI Feedback**: HTTP 200 with JSON array of inventory items:
  ```json
  [
    {
      "material_type": "سیمان تیپ 2",
      "unit": "کیسه",
      "total_in": 700.0,
      "total_out": 150.0,
      "current_balance": 550.0,
      "last_movement_date": "2026-10-25"
    }
  ]
  ```
- Returns HTTP 403 Forbidden if user lacks `view_reports` or project access.

## Resulting Route / Screen

- **Route**: `/projects/:businessId/warehouse`

## Outcomes & Guards

- Historical movements after `as_of_date` are strictly excluded from balance sums.
- Empty result sets return `[]` with HTTP 200.
- Unauthorized cross-tenant inquiries are rejected with HTTP 403.

## Subsequent Decisions

- [Return to Warehouse department activity](../README.md)

## Source Evidence

- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/api/core/inventory/project_urls.py](../../../../../../../apps/api/core/inventory/project_urls.py)
