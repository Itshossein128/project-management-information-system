# Main Application Routes

This document outlines the high-level routing structure managed by React Router v7 at the root level of the `apps/web/src/app` directory.

## Core Routing Files

### `routes.ts`
This is the central route configuration file. It exports an array of routes utilizing React Router's mapping functions (`route`, `layout`, `index`).

**Structure:**
- **Public/Auth Routes:** Standalone routes for `login`, `register`, `forgot-password`, and `reset-password`.
- **Authenticated Shell:** A wrapper layout (`AUTH_LAYOUT`) ensures users are authenticated before accessing nested features.
- **Protected Business Area:** A layout wrapper (`PROTECTED_LAYOUT`) that includes paths specifically tailored to business operations:
  - Homepage (`HOME`).
  - Business setup and admin configurations.
  - Department specific routes (Buildings, Mechanical, Security, Machinery, Warehouse, Electrical).
  - Dynamic Table interfaces.
- **Human Resources (HR) Hub:** A deeply nested protected layout (`HR_PROTECTED_LAYOUT`) tailored to internal company management:
  - HR Dashboard/Hub.
  - User management (`USERS`).
  - Job Position management (`HR_JOB_POSITIONS`).

### `routeVars.ts`
This file serves as a single source of truth for string variables associated with routing.
- **`ROUTES`**: An object linking logical route constants to physical React component filepaths within the `routes` directory (e.g., `LOGIN: "routes/login.tsx"`).
- **`PATHS`**: URL segment strings representing the client-facing browser path (e.g., `LOGIN: "login"`).

## Sub-Route Configurations
Route modularization occurs within the `src/app/routes/` directory. Check `src/app/routes/ROUTES.md` for specifics on the modularized routing chunks.
