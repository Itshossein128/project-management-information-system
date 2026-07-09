import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Routing configuration for HR-specific pages in the application.
 * Defines routes that are nested under the HR protected layout.
 */
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
