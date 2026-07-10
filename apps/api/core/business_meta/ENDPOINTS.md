# Business Meta Endpoints Documentation

This application provides endpoints to manage business entities, schema setups (dynamic tables and fields), user assignments, and relations between business tables.

## Base Paths
*   Business Management: `/api/businesses/`
*   Dynamic Relations: `/api/relations/`

## Endpoints

### Business Entities
*   **GET/POST** `/`: List existing businesses or create a new one.
*   **GET/PUT/PATCH/DELETE** `/<int:pk>/`: Retrieve, update, or delete a specific business.
*   **GET** `/templates/`: List available business templates for quick initialization.
*   **POST** `/from_template/`: Create a new business and bootstrap its schema from a template.

### Business Settings & Staffing
*   **GET/POST** `/<int:business_pk>/job-positions/`: List or create job positions for a business.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/job-positions/<int:pk>/`: Manage a specific job position.
*   **GET/POST** `/<int:business_pk>/assignments/`: List or create user role assignments within a business.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/assignments/<int:pk>/`: Manage a specific user assignment.

### Dynamic Schema (Tables & Fields)
*   **GET/POST** `/<int:business_pk>/tables/`: List or create dynamic table definitions.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/tables/<int:pk>/`: Manage a specific dynamic table.
*   **GET** `/<int:business_pk>/tables/by_slug/<str:table_slug>/`: Retrieve table schema metadata by its slug identifier.
*   **GET/POST** `/<int:business_pk>/tables/<int:table_pk>/fields/`: List or create dynamic fields within a table.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/tables/<int:table_pk>/fields/<int:pk>/`: Manage a specific dynamic field.

### Dynamic Data (Rows)
*   **GET/POST** `/<int:business_pk>/tables/<str:table_slug>/rows/`: Retrieve data rows or add new entries to a dynamic table.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/tables/<str:table_slug>/rows/<str:row_id>/`: Manage a specific data row.
*   **GET** `/<int:business_pk>/tables/<str:table_slug>/rows/export/`: Export data rows to a file format (e.g., CSV, XLSX).
*   **POST** `/<int:business_pk>/tables/<str:table_slug>/rows/import/`: Import data rows from a file format.

### Delegated Endpoints (Inventory)
*   Routes falling under `/<int:business_pk>/...` that do not match the above are forwarded to the `inventory` app.

### Relation Definitions
*   **GET/POST/PUT/PATCH/DELETE** `/api/relations/`: Standard viewset endpoints to list, create, and manage relation definitions between dynamic tables.
