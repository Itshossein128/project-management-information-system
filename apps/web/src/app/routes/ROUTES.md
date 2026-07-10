# Modular Route Configurations

This directory contains segmented routing definitions imported by the main `src/app/routes.ts` file to keep the routing architecture scalable and maintainable.

## Route Chunks

### `auth.routes.ts`
- **Purpose**: Defines public-facing authentication routes.
- **Routes Exported**:
  - `login` -> `ROUTES.LOGIN`
  - `register` -> `ROUTES.REGISTER`

### `hr.routes.ts`
- **Purpose**: Manages routes protected specifically for HR operations.
- **Behavior**: It wraps internal HR features (like the `USERS` view) inside the `HR_PROTECTED_LAYOUT` to enforce specific access boundaries.

### `business.routes.ts`
- **Purpose**: Maps URL patterns for standard business workspace viewing and interaction.
- **Routes Exported**:
  - `/businesses/:businessId` -> Base overview for a specific business workspace.
  - `/businesses/:businessId/tables/:tableSlug` -> Dynamic view for interacting with specific data tables within a business.

### `business-setup.routes.ts`
- **Purpose**: Dedicated to the administrative and structural setup of business entities.
- **Important Note**: Order matters here. Static segments like `create` and dynamic setups like `:businessId/setup` are registered explicitly before fallback dynamic business routes to prevent client/server matching conflicts.
- **Routes Exported**:
  - `/businesses/create` -> Interface to create a new business workspace.
  - `/businesses/:businessId/setup` -> Administrative view for managing schema (tables/fields) for a business.
  - `/businesses` -> Base setup hub.
