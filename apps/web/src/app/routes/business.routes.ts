import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Standard business workspace routes.
 * Defines the main dashboard and dynamically driven data tables for a business.
 */
export const businessRoutes = [
    // Main dashboard/overview for a specific business workspace
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

    // Dynamic table route for viewing/managing rows in a specific table
    route(
        `${PATHS.BUSINESS}/:businessId/tables/:tableSlug`,
        ROUTES.BUSINESS_TABLE
    ),
];
