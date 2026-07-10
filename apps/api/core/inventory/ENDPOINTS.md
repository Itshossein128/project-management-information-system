# Inventory Endpoints Documentation

This application handles core inventory items natively, as well as business-scoped space/material requests and department activities.

## Base Paths
*   Global Inventory Data: `/api/`
*   Business-Scoped Operations: Delegated under `/api/businesses/<int:business_pk>/` via the `business_meta` app router.

## Endpoints

### Global Items
*   **GET/POST/PUT/PATCH/DELETE** `/api/items/`: Standard viewset endpoints to manage global catalog items not necessarily tied to a single business context.

### Business-Scoped Operations
_Note: These endpoints are nested under a specific business ID prefix._

#### Space and Material Requests
*   **GET/POST** `/<int:business_pk>/space-material-requests/`: List or create requests for spaces and materials within the business.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/space-material-requests/<int:pk>/`: Manage a specific space/material request.

#### Department Activities
*   **GET/POST** `/<int:business_pk>/department-activity-records/`: List or create daily/weekly activity records for business departments.
*   **GET/PUT/PATCH/DELETE** `/<int:business_pk>/department-activity-records/<int:pk>/`: Manage a specific department activity record.
*   **GET** `/<int:business_pk>/department-activity-records/export/`: Export department activity logs to file formats.
*   **POST** `/<int:business_pk>/department-activity-records/import/`: Import department activity logs from file formats.
*   **GET** `/<int:business_pk>/department-activity-records/reports/daily/`: Retrieve summarized daily activity reports.
*   **GET** `/<int:business_pk>/department-activity-records/reports/weekly/`: Retrieve summarized weekly activity reports.
