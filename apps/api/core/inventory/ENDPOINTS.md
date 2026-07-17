# Inventory Endpoints Documentation

Legacy inventory APIs and project-scoped department activity logs. The blueprint materials ledger lives under `resources` at `/api/v1/projects/{uuid}/materials/`.

## Deprecation: `/api/items/`

`GET/POST/PUT/PATCH/DELETE /api/items/` exposes the legacy global `inventory.Item` model. It is **deprecated** in favor of project-scoped materials in the `resources` app:

| Legacy | Replacement |
|--------|-------------|
| `/api/items/` | `/api/v1/projects/{uuid}/materials/` |
| Global `Item` catalog | `resources.Material` + inventory transactions |

**Timeline:** `/api/items/` remains mounted for backward compatibility with legacy dynamic-table workflows. New features must use `resources`. Removal is planned after frontend callers migrate to material-balance (`/projects/:id/material-balance`).

See also: [docs/ipcas-scope-map.md](../../../../docs/ipcas-scope-map.md) (Materials ledger row).

## Base Paths

*   Legacy global items: `/api/items/` (deprecated)
*   Project-scoped inventory UX: `/api/v1/projects/{uuid}/...`

## Endpoints

### Global Items (deprecated)

*   **GET/POST/PUT/PATCH/DELETE** `/api/items/`: Legacy global catalog items.

### Project-Scoped Operations

#### Space and Material Requests

*   **GET/POST** `/api/v1/projects/{uuid}/space-material-requests/`
*   **GET/PUT/PATCH/DELETE** `/api/v1/projects/{uuid}/space-material-requests/{id}/`

#### Department Activities

*   **GET/POST** `/api/v1/projects/{uuid}/department-activity-records/`
*   **GET/PUT/PATCH/DELETE** `/api/v1/projects/{uuid}/department-activity-records/{id}/`
*   **GET** `/api/v1/projects/{uuid}/department-activity-records/export/`
*   **POST** `/api/v1/projects/{uuid}/department-activity-records/import/`
*   **GET** `/api/v1/projects/{uuid}/department-activity-records/reports/daily/`
*   **GET** `/api/v1/projects/{uuid}/department-activity-records/reports/weekly/`
