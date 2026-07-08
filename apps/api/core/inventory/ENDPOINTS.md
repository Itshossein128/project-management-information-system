# Inventory Endpoints

This directory manages inventory-related features, which include general items, space material requests, and department activity records.

URL routing is split between global endpoints (`urls.py`) and business-scoped endpoints (`business_urls.py`), which are included via `business_meta.urls`.

## Global Endpoints (`urls.py`)
- `GET/POST /api/items/`: List or create global items.
- `GET/PUT/PATCH/DELETE /api/items/<int:pk>/`: Manage a specific item.

## Business-Scoped Endpoints (`business_urls.py`)

These endpoints are nested under `/api/businesses/<int:business_pk>/`.

### Space Material Requests
- `GET/POST .../space-material-requests/`: List or create material requests within a business/project.
- `GET/PUT/PATCH/DELETE .../space-material-requests/<int:pk>/`: Manage a specific material request.

### Department Activity Records
- `GET/POST .../department-activity-records/`: List or create department activity records.
- `GET/PUT/PATCH/DELETE .../department-activity-records/<int:pk>/`: Manage a specific activity record.
- `GET .../department-activity-records/export/`: Export activity records to an Excel file.
- `POST .../department-activity-records/import/`: Import activity records from an Excel file.
- `GET .../department-activity-records/reports/daily/`: Retrieve a daily summary report of department activities.
- `GET .../department-activity-records/reports/weekly/`: Retrieve a weekly summary report of department activities.