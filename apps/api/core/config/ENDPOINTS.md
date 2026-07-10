# Core Config Endpoints

This document describes the main entrypoint URL configurations for the Django backend API.

## Endpoints

- `/admin/`
  - **Purpose**: Django builtin administration panel for superusers.
- `/api/auth/`
  - **Purpose**: Routes all authentication-related endpoints (register, login, password resets, roles, and profiles) to the `authentication` app.
- `/api/businesses/`
  - **Purpose**: Routes all endpoints related to business workspaces, templates, job positions, and table/field definitions to the `business_meta` app.
- `/api/relations/`
  - **Purpose**: Routes endpoint paths dealing with relational links and definitions inside business workspaces to the `relations_urls` module of the `business_meta` app.
- `/api/`
  - **Purpose**: Maps remaining API routes, specifically inventory items and business-scoped resources, to the `inventory` app.

### API Schema & Documentation
- `/api/schema/`
  - **Purpose**: Exposes the OpenAPI schema defining the complete API structure.
- `/api/docs/`
  - **Purpose**: Exposes the Swagger UI for interactive API documentation and testing.
- `/api/redoc/`
  - **Purpose**: Exposes the ReDoc user-interface for viewing API documentation.
