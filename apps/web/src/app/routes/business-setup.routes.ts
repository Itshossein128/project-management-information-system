import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Admin routes under `/businesses`.
 * Static segments (`create`, `.../setup`) must be registered before dynamic segments like `businesses/:businessId`
 * to ensure correct route resolution. No pathless layout wrapper is used to avoid client/server mismatch.
 */
export const businessSetupRoutes = [
  // Route to create a new business
  route(
    `${PATHS.BUSINESS}/${PATHS.BUSINESS_CREATE}`,
    ROUTES.BUSINESS_CREATE,
  ),

  // Route for configuring the schema (tables and fields) for a specific business
  route(
    `${PATHS.BUSINESS}/:businessId/${PATHS.BUSINESS_ADMIN_SETUP}`,
    ROUTES.BUSINESS_SETUP_SCHEMA,
  ),

  // Fallback/overview route for business setup
  route(PATHS.BUSINESS, ROUTES.BUSINESS_SETUP),
];
