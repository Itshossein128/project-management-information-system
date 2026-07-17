# Config Endpoints Documentation

This directory serves as the root URL configuration module for the entire backend application.

## Endpoints

*   `/admin/`: Django administration panel.
*   `/api/auth/`: Authentication, user profile, and password management (`authentication` app).
*   `/api/v1/projects/`: Project CRUD, members, dynamic tables, and nested domain APIs (`projects` app).
*   `/api/v1/project-templates/`: Project template catalog.
*   `/api/v1/roles/`, `/api/v1/permissions/`: Role and permission catalog.
*   `/api/v1/users/lookup/`: User lookup for member assignment.
*   `/api/v1/notifications/`: In-app notifications.
*   `/api/v1/`: File storage presigned URLs (`storage` app).
*   `/api/relations/`: Dynamic relation definitions (`business_meta` app).
*   `/api/items/`: Legacy global inventory catalog (`inventory` app, deprecated — see `inventory/ENDPOINTS.md`).
*   `/api/schema/`: OpenAPI 3.0 schema (drf-spectacular).
*   `/api/docs/`: Swagger UI.
*   `/api/redoc/`: ReDoc UI.
