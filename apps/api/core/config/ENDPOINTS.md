# Main Config Endpoints

This document describes the main entry points for the Django backend API, configured in `apps/api/core/config/urls.py`.

## Endpoints

* **`/admin/`**: The Django administration panel, providing a built-in interface for managing models and users.
* **`/api/auth/`**: Base path for all authentication-related routes (e.g., login, registration, password reset). These routes are defined in `apps/api/core/authentication/urls.py`.
* **`/api/businesses/`**: Base path for business metadata routes, handling operations related to businesses, tables, fields, and assignments. These routes are defined in `apps/api/core/business_meta/urls.py`.
* **`/api/relations/`**: Base path for defining relations between different data entities. These routes are defined in `apps/api/core/business_meta/relations_urls.py`.
* **`/api/`**: The root API path, currently routing to inventory-specific endpoints. These routes are defined in `apps/api/core/inventory/urls.py`.

### Documentation Endpoints

* **`/api/schema/`**: Provides the raw OpenAPI (Swagger) schema for the entire API.
* **`/api/docs/`**: Serves the Swagger UI, allowing developers to interactively explore and test the API endpoints.
* **`/api/redoc/`**: Serves the ReDoc UI, an alternative, read-only visualization of the OpenAPI schema.
