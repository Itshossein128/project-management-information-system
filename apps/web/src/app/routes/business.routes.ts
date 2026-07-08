import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Array containing routing configurations scoped to a specific business ID, defining dashboard and dynamic table views.
export const businessRoutes = [
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

    route(
        `${PATHS.BUSINESS}/:businessId/tables/:tableSlug`,
        ROUTES.BUSINESS_TABLE
    ),
];
