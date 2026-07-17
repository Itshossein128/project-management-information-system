import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";
import { PATHS, ROUTES } from "./routeVars";
import { projectRoutes } from "./routes/business-setup.routes";

/**
 * Main routing configuration array for React Router v7.
 * Uses utility methods like `index`, `route`, and `layout` to construct the route hierarchy.
 * Auth routes are placed at the top level, while protected routes and layouts handle authenticated pages (HR and Business).
 */
export default [
  index(ROUTES.INDEX),
  route(PATHS.LOGIN, ROUTES.LOGIN),
  route(PATHS.REGISTER, ROUTES.REGISTER),
  route(PATHS.FORGOT_PASSWORD, ROUTES.FORGOT_PASSWORD),
  route(PATHS.RESET_PASSWORD, ROUTES.RESET_PASSWORD),

  layout(ROUTES.AUTH_LAYOUT, [
    layout(ROUTES.PROTECTED_LAYOUT, [
      route(PATHS.HOME, ROUTES.HOME),
      ...projectRoutes,

      route(`${PATHS.BUSINESS}/:businessId/tables/:tableSlug`, ROUTES.BUSINESS_TABLE),
      route(`${PATHS.BUSINESS}/:businessId/job-positions`, ROUTES.BUSINESS_JOB_POSITIONS),
      route(`${PATHS.BUSINESS}/:businessId/users`, ROUTES.BUSINESS_USERS),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.BUILDINGS}`, ROUTES.BUSINESS_BUILDINGS),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.MECHANICAL}`, ROUTES.BUSINESS_MECHANICAL),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.SECURITY}`, ROUTES.BUSINESS_SECURITY),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.MACHINERY}`, ROUTES.BUSINESS_MACHINERY),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.WAREHOUSE}`, ROUTES.BUSINESS_WAREHOUSE),
      route(`${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_DEPT.ELECTRICAL}`, ROUTES.BUSINESS_ELECTRICAL),
      route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

      layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(`${PATHS.HR}/${PATHS.HR_JOB_POSITIONS}`, ROUTES.HR_JOB_POSITIONS),
        route(PATHS.USERS, ROUTES.USERS),
        route(PATHS.HR, ROUTES.HR_HUB),
      ]),
    ]),
  ]),
] satisfies RouteConfig;
