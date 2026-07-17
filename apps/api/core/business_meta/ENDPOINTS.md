# Business Meta Endpoints Documentation

Dynamic schema (tables, fields, rows) and relation definitions. All project-scoped routes live under the projects router.

## Base Paths

*   Project dynamic schema: `/api/v1/projects/{uuid}/tables/...`
*   Dynamic relations: `/api/relations/`

> Legacy `/api/businesses/` routes were removed. Use `/api/v1/projects/` (UUID) instead.

## Project-Scoped Dynamic Schema

### Tables & Fields

*   **GET/POST** `/api/v1/projects/{uuid}/tables/`: List or create table definitions (`business-setup` group required for writes).
*   **GET/PUT/PATCH/DELETE** `/api/v1/projects/{uuid}/tables/{id}/`: Manage a table definition.
*   **GET** `/api/v1/projects/{uuid}/tables/by_slug/{table_slug}/`: Table metadata with fields.
*   **GET/POST** `/api/v1/projects/{uuid}/tables/{table_id}/fields/`: List or create fields.
*   **GET/PUT/PATCH/DELETE** `/api/v1/projects/{uuid}/tables/{table_id}/fields/{id}/`: Manage a field.

### Dynamic Data (Rows)

*   **GET/POST** `/api/v1/projects/{uuid}/tables/{table_slug}/rows/`: List or create rows.
*   **GET/PUT/PATCH/DELETE** `/api/v1/projects/{uuid}/tables/{table_slug}/rows/{row_id}/`: Manage a row.
*   **GET** `/api/v1/projects/{uuid}/tables/{table_slug}/rows/export/`: Export rows as `.xlsx`.
*   **POST** `/api/v1/projects/{uuid}/tables/{table_slug}/rows/import/`: Import rows from `.xlsx`.

### Relation Definitions

*   **GET/POST/PUT/PATCH/DELETE** `/api/relations/`: Manage cross-table relation definitions (`business-setup` group required for writes).
