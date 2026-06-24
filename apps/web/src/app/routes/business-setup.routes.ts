import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Admin routes under `/businesses`.
 * Static segments (`create`, `.../setup`) must be registered before `businesses/:businessId`.
 * No pathless layout wrapper — avoids client/server route matching issues.
 */
export const businessSetupRoutes = [
  route(
    `${PATHS.BUSINESS}/${PATHS.BUSINESS_CREATE}`,
    ROUTES.BUSINESS_CREATE,
  ),
  route(
    `${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_ADMIN_SETUP}`,
    ROUTES.BUSINESS_SETUP_SCHEMA,
  ),
  route(PATHS.BUSINESS, ROUTES.BUSINESS_SETUP),
];
