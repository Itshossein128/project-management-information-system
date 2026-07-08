import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Human Resources sub-application routes.
 * Wrapped in the HR_PROTECTED_LAYOUT to enforce specific HR navigation and access.
 */
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        // Route for managing all global users
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
