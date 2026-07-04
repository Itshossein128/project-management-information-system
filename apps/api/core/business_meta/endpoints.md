# Business Meta Endpoints

This module manages the core entities such as Businesses, Templates, and Job Positions.

## Endpoints

- `GET /api/v1/businesses/`: List all businesses accessible by the current user.
- `POST /api/v1/businesses/`: Create a new business.
- `GET /api/v1/businesses/{id}/`: Get detailed information about a specific business.
- `GET /api/v1/businesses/templates/`: List available templates for business creation.
- `POST /api/v1/businesses/from_template/`: Create a business from a predefined template.
- `GET /api/v1/businesses/{id}/tables/`: List all custom tables defined for a business.
- `GET /api/v1/businesses/{id}/positions/`: List job positions defined for this business.
