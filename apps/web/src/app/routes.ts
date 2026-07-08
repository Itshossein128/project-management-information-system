import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";
import { PATHS, ROUTES } from "./routeVars";
import { businessSetupRoutes } from "./routes/business-setup.routes";

/**
 * Main application routing configuration.
 * Uses React Router v7 standard `route` and `layout` definitions.
 * The paths map to component files defined in ROUTES.
 */
export default [
  // Root index route
  index(ROUTES.INDEX),

  // Public authentication routes
  route(PATHS.LOGIN, ROUTES.LOGIN),
  route(PATHS.REGISTER, ROUTES.REGISTER),
  route(PATHS.FORGOT_PASSWORD, ROUTES.FORGOT_PASSWORD),
  route(PATHS.RESET_PASSWORD, ROUTES.RESET_PASSWORD),

  // Auth → app shell: fixed sidebar (Home + HR); workflows use in-page links under `/hr/*` and `/businesses/:id/*`.
  layout(ROUTES.AUTH_LAYOUT, [
    layout(ROUTES.PROTECTED_LAYOUT, [
      // Main authenticated landing page
      route(PATHS.HOME, ROUTES.HOME),

      // Admin/Setup routes for business creation and schema setup
      ...businessSetupRoutes,

      // Business-specific workspace routes
      route(`${PATHS.BUSINESS}/:businessId/tables/:tableSlug`, ROUTES.BUSINESS_TABLE),
      route(`${PATHS.BUSINESS}/:businessId/job-positions`, ROUTES.BUSINESS_JOB_POSITIONS),
      route(`${PATHS.BUSINESS}/:businessId/users`, ROUTES.BUSINESS_USERS),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.BUILDINGS}`, ROUTES.BUSINESS_BUILDINGS),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.MECHANICAL}`, ROUTES.BUSINESS_MECHANICAL),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.SECURITY}`, ROUTES.BUSINESS_SECURITY),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.MACHINERY}`, ROUTES.BUSINESS_MACHINERY),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.WAREHOUSE}`, ROUTES.BUSINESS_WAREHOUSE),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.ELECTRICAL}`, ROUTES.BUSINESS_ELECTRICAL),

      // Business dashboard (root of a specific business workspace)
      route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

      // Human Resources sub-application layout and routes
      layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(`${PATHS.HR}/${PATHS.HR_JOB_POSITIONS}`, ROUTES.HR_JOB_POSITIONS),
        route(PATHS.USERS, ROUTES.USERS),
        route(PATHS.HR, ROUTES.HR_HUB),
      ]),
    ]),
  ]),
] satisfies RouteConfig;
