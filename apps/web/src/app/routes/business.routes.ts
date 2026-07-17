import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Array of route configurations for the business overview and specific table views.
 * Maps dynamic business segments like `/businesses/:businessId` to their corresponding route components.
 */
export const businessRoutes = [
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

    route(
        `${PATHS.BUSINESS}/:businessId/tables/:tableSlug`,
        ROUTES.BUSINESS_TABLE
    ),
];
