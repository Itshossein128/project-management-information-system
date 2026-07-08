# Frontend Routing Documentation

This document explains the routing architecture of the frontend application built with React Router v7.

## Overview

The application routing is configured programmatically rather than via traditional file-system routing. This configuration lives in the `apps/web/src/app/` directory.

### Core Files
* **`routes.ts`**: The main entry point for the React Router configuration. It defines the layout wrappers (like `AUTH_LAYOUT` and `PROTECTED_LAYOUT`) and imports specific modular route segments.
* **`routeVars.ts`**: Acts as a central dictionary. It defines the `ROUTES` mapping (logical route keys to physical `.tsx` file paths) and `PATHS` (the actual URL string segments used in the browser). This separation prevents typos and makes refactoring easier.

### Modular Route Files (`routes/*.routes.ts`)

To keep `routes.ts` maintainable, routes are broken down into logical business areas:

* **`auth.routes.ts`**: Contains public authentication routes like Login and Register.
* **`business-setup.routes.ts`**: Contains administrative and setup routes for creating businesses and configuring their schemas (tables and fields). Crucially, static routes (like `businesses/create`) are defined here so they take precedence over dynamic wildcard routes (like `businesses/:businessId`).
* **`business.routes.ts`**: Contains the main workspace routes for a specific business, primarily the dashboard and dynamic data table views.
* **`hr.routes.ts`**: Contains routes specific to the Human Resources sub-application (e.g., managing global users), typically wrapped in a specific layout that enforces HR navigation elements.

## Layouts and Nesting
The application uses nested layouts to control UI shells and authentication states:
* `ROUTES.AUTH_LAYOUT` (`_auth.tsx`): Wraps public authentication pages.
* `ROUTES.PROTECTED_LAYOUT` (`_protected.tsx`): The main application shell (sidebar, topbar) that requires an authenticated user session.
* `ROUTES.HR_PROTECTED_LAYOUT` (`_protected-human-resource.tsx`): An additional layout specifically for the HR section, nested inside the main protected layout.
