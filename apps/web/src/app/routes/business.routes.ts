import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Configuration array for businessRoutes routing.
export const businessRoutes = [
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),

    route(
        `${PATHS.BUSINESS}/:businessId/tables/:tableSlug`,
        ROUTES.BUSINESS_TABLE
    ),
];
