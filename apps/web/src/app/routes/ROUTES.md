# Frontend Routes Documentation

The frontend uses React Router (v7) for defining the application's routing structure. Routes are primarily defined in `routes.ts` and various `*.routes.ts` files, making use of layouts to share UI components (like sidebars and navigation) across related pages.

## Route Architecture

### Public Routes
- `/`: Index route (typically redirects or shows a landing page).
- `/login`: User login page.
- `/register`: User registration page.
- `/forgot-password`: Page to request a password reset.
- `/reset-password`: Page to reset the password.

### Protected Application Shell (`_auth.tsx` & `_protected.tsx` layouts)
All routes inside the application require authentication. The layouts handle session checks and wrap the application in a main UI shell (like a sidebar/header).

#### General
- `/home`: The dashboard home page where users can select a business (project) to work on.

#### Business/Project Scoped Routes
Defined under `/businesses/:businessId/*`. These routes are specific to a single business/project.
- `/businesses/:businessId`: Overview for a specific business.
- `/businesses/:businessId/tables/:tableSlug`: Dynamic table data view for the business.
- `/businesses/:businessId/job-positions`: Job position management for the business.
- `/businesses/:businessId/users`: User assignments for the business.
- `/businesses/:businessId/<department>`: Department-specific activity views (e.g., buildings, mechanical, security, machinery, warehouse, electrical).

#### Business Setup Workflows
Routes imported from `business-setup.routes.ts`.
- `/businesses/setup`: Starts the business setup wizard.
- `/businesses/create`: Form to create a new business.

#### HR (Human Resources) Hub
Defined under the `_protected-human-resource.tsx` layout for HR-specific tools.
- `/hr`: The main HR hub/dashboard.
- `/hr/job-positions`: Global or cross-project job position management.
- `/hr/users`: Global user management.