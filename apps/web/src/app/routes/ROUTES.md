# Modular Route Configurations

This directory contains segmented routing definitions. Only some chunks are imported by the main `src/app/routes.ts` file today.

## Route Chunks

### `business-setup.routes.ts` (active)
- **Purpose**: Business admin/setup routes under `/businesses`.
- **Imported by**: `routes.ts` via `...businessSetupRoutes`.
- **Important**: Static segments (`create`, `.../setup`) are registered before dynamic `:businessId` routes to avoid client/server matching conflicts.

### `auth.routes.ts` (not imported yet)
- **Purpose**: Partial auth route chunk (`login`, `register` only).
- **Note**: `routes.ts` still declares auth routes inline, including `forgot-password` and `reset-password`.

### `hr.routes.ts` (not imported yet)
- **Purpose**: Partial HR route chunk (`USERS` only).
- **Note**: `routes.ts` still declares the full HR layout inline (`HR_HUB`, `HR_JOB_POSITIONS`, etc.).

### `business.routes.ts` (not imported yet)
- **Purpose**: Partial business workspace routes (`:businessId`, `:businessId/tables/:tableSlug`).
- **Note**: `routes.ts` still declares department and admin business routes inline.
