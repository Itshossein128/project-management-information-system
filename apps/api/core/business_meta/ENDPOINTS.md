# Business Meta Endpoints

This directory manages business entities (projects), their schema definitions (tables/fields), and data (dynamic rows). It also handles business-scoped user assignments and job positions. The routes are defined in `urls.py`.

## Endpoints

### Business Management
- `GET/POST /api/businesses/`: List or create businesses.
- `GET /api/businesses/templates/`: List available business templates.
- `POST /api/businesses/from_template/`: Create a new business based on an existing template.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:pk>/`: Retrieve, update, or delete a specific business.

### Job Positions
- `GET/POST /api/businesses/<int:business_pk>/job-positions/`: List or create job positions for a business.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:business_pk>/job-positions/<int:pk>/`: Manage a specific job position.

### Assignments
- `GET/POST /api/businesses/<int:business_pk>/assignments/`: List or create user assignments within a business.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:business_pk>/assignments/<int:pk>/`: Manage a specific assignment.

### Dynamic Tables (Schema)
- `GET/POST /api/businesses/<int:business_pk>/tables/`: List or create dynamic tables for a business.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:business_pk>/tables/<int:pk>/`: Manage a specific table definition.
- `GET /api/businesses/<int:business_pk>/tables/by_slug/<str:table_slug>/`: Retrieve a table definition by its slug.

### Dynamic Fields (Schema)
- `GET/POST /api/businesses/<int:business_pk>/tables/<int:table_pk>/fields/`: List or create fields for a table.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:business_pk>/tables/<int:table_pk>/fields/<int:pk>/`: Manage a specific field definition.

### Dynamic Data (Rows)
- `GET/POST /api/businesses/<int:business_pk>/tables/<str:table_slug>/rows/`: Retrieve list of rows or insert new rows into a dynamic table.
- `GET/PUT/PATCH/DELETE /api/businesses/<int:business_pk>/tables/<str:table_slug>/rows/<str:row_id>/`: Manage a specific row.
- `GET /api/businesses/<int:business_pk>/tables/<str:table_slug>/rows/export/`: Export table data (e.g., to Excel).
- `POST /api/businesses/<int:business_pk>/tables/<str:table_slug>/rows/import/`: Import data into a dynamic table.

These endpoints connect to `views.py` and `data_views.py`. Sub-routes for inventory are included at the end (`inventory.business_urls`).