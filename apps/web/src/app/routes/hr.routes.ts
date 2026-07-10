import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Array of route configurations related to Human Resources (HR) flows.
 * Uses a protected layout specific to HR to secure internal routes such as the users directory.
 */
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
