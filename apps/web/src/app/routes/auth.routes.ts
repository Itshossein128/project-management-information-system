import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Public authentication routes.
 * These routes are accessible without an active session.
 */
export const authRoutes = [
    // Login page route
    route(PATHS.LOGIN, ROUTES.LOGIN),

    // User registration page route
    route(PATHS.REGISTER, ROUTES.REGISTER),
];
