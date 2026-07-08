# Inventory Endpoints

This document outlines the endpoints defined in the `inventory` Django application. These endpoints manage generic inventory items as well as business-scoped activity records and material requests.

## Base Path
Routes defined in `urls.py` are typically mounted at the API root `/api/`.
Routes defined in `business_urls.py` are dynamically included under the business namespace (e.g., `/api/businesses/`).

## Endpoints

### Global Inventory Management (`urls.py`)
* **`/api/items/` (GET, POST)**: List all items or create a new inventory item.
* **`/api/items/<id>/` (GET, PUT, PATCH, DELETE)**: Retrieve, update, or delete a specific inventory item.

### Business-Scoped Inventory Operations (`business_urls.py`)

These endpoints are prefixed with `/api/businesses/<business_pk>/` when included in the main routing configuration.

#### Space Material Requests
* **`.../space-material-requests/` (GET, POST)**: List or create space material requests for a specific business.
* **`.../space-material-requests/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific space material request.

#### Department Activity Records
* **`.../department-activity-records/` (GET, POST)**: List or create department activity records within a business.
* **`.../department-activity-records/<id>/` (GET, PUT, PATCH, DELETE)**: Manage a specific department activity record.
* **`.../department-activity-records/export/` (GET)**: Export department activity records data.
* **`.../department-activity-records/import/` (POST)**: Import department activity records data.
* **`.../department-activity-records/reports/daily/` (GET)**: Retrieve daily reports for department activities.
* **`.../department-activity-records/reports/weekly/` (GET)**: Retrieve weekly reports for department activities.
