# Frontend Routing Documentation

This directory contains the routing configuration for the React application, leveraging React Router v7. The routing is structured to separate concerns between core configuration, route path constants, and logically grouped route modules.

## Architecture & Core Files

*   **`react-router.config.ts`**: (Root level) Configuration object for React Router v7. It sets the base directory for the application source and enables Server-Side Rendering (SSR).
*   **`routeVars.ts`**: Centralized registry for all route paths. It exports two main constants:
    *   `ROUTES`: Maps logical route identifiers to their physical component file paths (e.g., `LOGIN: "routes/login.tsx"`).
    *   `PATHS`: Defines the actual URL segments used in the browser (e.g., `BUSINESS_CREATE: "create"`). This ensures consistency and prevents typos across the app.
*   **`routes.ts`**: The root routing configuration array. It composes the full application route tree by combining public routes, protected layout wrappers, and nested route modules.

## Sub-Route Modules (`/routes/`)

To keep the root `routes.ts` file maintainable, specific logical sections of the application have their routes abstracted into separate files within the `src/app/routes/` directory.

### `auth.routes.ts`
*   **Purpose**: Handles public-facing authentication pages.
*   **Routes Included**: User Login (`/login`) and Registration (`/register`).

### `hr.routes.ts`
*   **Purpose**: Manages routes specific to the Human Resources module.
*   **Routes Included**: User Management (`/hr/users`). Note that it wraps these inside a specific HR protected layout (`HR_PROTECTED_LAYOUT`).

### `business-setup.routes.ts`
*   **Purpose**: Configures administration and setup routes for businesses.
*   **Important Note**: Static segments (like `/businesses/create` and `/businesses/:businessId/setup`) are registered here. They must be loaded *before* the dynamic `:businessId` catch-all route to prevent client/server matching conflicts.

### `business-setup.routes.ts` — Project workspace routes (Sprint 9 additions)

Project routes live in `projectRoutes` exported from `business-setup.routes.ts`. Recent Sprint 9 screens:

| Route | Component | Purpose |
|-------|-----------|---------|
| `/projects/:projectId/subcontractors` | `project-subcontractors.tsx` | Registry with risk badges and filters |
| `/projects/:projectId/subcontractors/:subId` | `project-subcontractor-detail.tsx` | Scorecard, warnings, radar chart |
| `/projects/:projectId/alerts` | `project-alerts.tsx` | Alert log + rule configuration |
| `/projects/:projectId/economic` | `project-economic.tsx` | 3-layer P&L + Monte Carlo |
| `/projects/:projectId/schedule/gantt` | `project-schedule-gantt.tsx` | Read-only Gantt (frappe-gantt) + PDF export |

Navigation entries are defined in `src/config/project-navigation.config.ts` (`buildProjectNavItems`). API clients for these modules are in `src/app/lib/api/{subcontractors,alerts,economic,gantt}.ts`.

### `business.routes.ts`
*   **Purpose**: Configures the primary workspace routes for a specific business entity.
*   **Routes Included**: The business dashboard root (`/businesses/:businessId`) and dynamic table data views (`/businesses/:businessId/tables/:tableSlug`).
