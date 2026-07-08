# Business Meta Endpoints

This document outlines the endpoints defined in the `business_meta` Django application. These endpoints handle the core multitenant structure of the application, managing businesses, dynamic tables, dynamic fields, relations, and user assignments.

## Base Path
Routes defined in `urls.py` are typically mounted at `/api/businesses/`.
Routes defined in `relations_urls.py` are typically mounted at `/api/relations/`.

## Endpoints

### Business Management (`urls.py`)
* **`/api/businesses/` (GET, POST)**: List all businesses or create a new business.
* **`/api/businesses/<id>/` (GET, PUT, PATCH, DELETE)**: Retrieve, update, or delete a specific business.
* **`/api/businesses/templates/` (GET)**: Retrieve a list of business templates.
* **`/api/businesses/from_template/` (POST)**: Create a new business based on an existing template.

### Business Job Positions (`urls.py`)
* **`/api/businesses/<business_pk>/job-positions/` (GET, POST)**: List or create job positions for a specific business.
* **`/api/businesses/<business_pk>/job-positions/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific job position.

### User Business Assignments (`urls.py`)
* **`/api/businesses/<business_pk>/assignments/` (GET, POST)**: List or create user assignments to a business.
* **`/api/businesses/<business_pk>/assignments/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific user assignment.

### Dynamic Tables (`urls.py`)
* **`/api/businesses/<business_pk>/tables/` (GET, POST)**: List or create dynamic table definitions for a business.
* **`/api/businesses/<business_pk>/tables/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific table definition.
* **`/api/businesses/<business_pk>/tables/by_slug/<table_slug>/` (GET)**: Retrieve a table definition using its unique slug.

### Dynamic Fields (`urls.py`)
* **`/api/businesses/<business_pk>/tables/<table_pk>/fields/` (GET, POST)**: List or create field definitions for a specific dynamic table.
* **`/api/businesses/<business_pk>/tables/<table_pk>/fields/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific field definition.

### Dynamic Data Rows (`urls.py`)
* **`/api/businesses/<business_pk>/tables/<table_slug>/rows/` (GET, POST)**: List or create data rows for a specific dynamic table.
* **`/api/businesses/<business_pk>/tables/<table_slug>/rows/<row_id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific data row within a dynamic table.
* **`/api/businesses/<business_pk>/tables/<table_slug>/rows/export/` (GET)**: Export data rows for a specific dynamic table.
* **`/api/businesses/<business_pk>/tables/<table_slug>/rows/import/` (POST)**: Import data rows into a specific dynamic table.

### Inventory Sub-routes (`urls.py`)
* **`/api/businesses/<business_pk>/...`**: Includes business-scoped inventory URLs (like department activity records) defined in `apps/api/core/inventory/business_urls.py`.

### Relations (`relations_urls.py`)
* **`/api/relations/` (GET, POST)**: List or create relation definitions between dynamic tables.
* **`/api/relations/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific relation definition.
