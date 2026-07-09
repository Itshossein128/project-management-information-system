import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Routing configuration for administration and setup routes under `/businesses`.
 * Note: Static segments (`create`, `.../setup`) must be registered before the dynamic
 * `businesses/:businessId` catch-all to ensure correct client/server route matching.
 * This array avoids using a pathless layout wrapper for the same reason.
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
