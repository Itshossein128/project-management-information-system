import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Routing configuration for business-specific workspace pages.
 * Includes nested routes mapped dynamically by businessId (e.g., dashboard, dynamic tables).
 */
export const businessRoutes = [
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

    route(
        `${PATHS.BUSINESS}/:businessId/tables/:tableSlug`,
        ROUTES.BUSINESS_TABLE
    ),
];
