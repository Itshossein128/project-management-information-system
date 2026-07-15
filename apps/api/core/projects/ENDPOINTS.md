# Projects Endpoints

This module handles the core project management functionality within IPCAS, including projects, project members, roles, templates, and dynamic data tables.

## Base URL: `/api/projects/` (or equivalent, see `urls.py`)

## Endpoints

### 1. Projects
*   **URL:** `/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Lists all projects the authenticated user has access to.
    *   `POST`: Creates a new project.
*   **Permissions:** Varies (typically requires authentication, potentially HR/Admin or specific project roles for creation)

*   **URL:** `/<project_pk>/`
*   **Methods:** `GET`, `PATCH`
*   **Description:**
    *   `GET`: Retrieves details of a specific project.
    *   `PATCH`: Partially updates project details.
*   **Permissions:** Requires access to the specific project.

### 2. Project Templates
*   **URL:** `/templates/`
*   **Method:** `GET`
*   **Description:** Lists available project templates.
*
*   **URL:** `/from_template/`
*   **Method:** `POST`
*   **Description:** Creates a new project based on an existing template.

*   **URL:** `/<project_pk>/save-as-template/`
*   **Method:** `POST`
*   **Description:** Saves an existing project as a new template for future use.

### 3. Project Positions
*   **URL:** `/<project_pk>/positions/`
*   **Methods:** `GET`, `POST`
*   **Description:** List or create organizational positions within a specific project.

*   **URL:** `/<project_pk>/positions/<pk>/`
*   **Methods:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:** Manage a specific position within a project.

### 4. Project Members
*   **URL:** `/<project_pk>/members/`
*   **Methods:** `GET`, `POST`
*   **Description:** List or add members to a specific project.

*   **URL:** `/<project_pk>/members/<user_id>/`
*   **Method:** `PATCH`
*   **Description:** Update a specific member's details or position within the project.

*   **URL:** `/<project_pk>/members/<user_id>/permissions/`
*   **Methods:** `GET`, `POST`, `DELETE`
*   **Description:** View, add, or remove granular permissions for a specific project member.

### 5. Dynamic Tables (Table Definitions)
*   **URL:** `/<project_pk>/tables/`
*   **Methods:** `GET`, `POST`
*   **Description:** List or create dynamic table definitions for storing custom business meta-data within a project.

*   **URL:** `/<project_pk>/tables/<pk>/`
*   **Methods:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:** Manage a specific table definition.

*   **URL:** `/<project_pk>/tables/by_slug/<table_slug>/`
*   **Method:** `GET`
*   **Description:** Retrieve a table definition using its unique slug.

### 6. Dynamic Fields (Field Definitions)
*   **URL:** `/<project_pk>/tables/<table_pk>/fields/`
*   **Methods:** `GET`, `POST`
*   **Description:** List or create field definitions (columns) for a specific dynamic table.

*   **URL:** `/<project_pk>/tables/<table_pk>/fields/<pk>/`
*   **Methods:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:** Manage a specific field definition within a dynamic table.

### 7. Dynamic Data (Rows)
*   **URL:** `/<project_pk>/tables/<table_slug>/rows/`
*   **Methods:** `GET`, `POST`
*   **Description:** Fetch or insert data rows for a specific dynamic table.

*   **URL:** `/<project_pk>/tables/<table_slug>/rows/<row_id>/`
*   **Methods:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:** Manage a specific data row within a dynamic table.

*   **URL:** `/<project_pk>/tables/<table_slug>/rows/export/`
*   **Method:** `GET`
*   **Description:** Export data from a dynamic table.

*   **URL:** `/<project_pk>/tables/<table_slug>/rows/import/`
*   **Method:** `POST`
*   **Description:** Import data into a dynamic table.

### 8. Nested App Endpoints
The `projects` module acts as the root for many other domain-specific endpoints, all nested under a `/<project_pk>/` prefix. These include:
*   `/inventory/`
*   `/wbs/`
*   `/schedule/`
*   `/field_reports/`
*   `/risk/`
*   `/hr/`
*   `/sub_reports/`
*   `/cost_control/`
*   `/resources/`
*   `/cash_flow/`
*   `/contracts/`
*   `/subcontractors/`
*   `/documents/`
*   `/alerts/`
*   `/economic/`
