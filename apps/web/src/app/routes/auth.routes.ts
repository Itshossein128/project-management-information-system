import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Routing configuration for public authentication pages.
 * Includes routes for user login and registration.
 */
export const authRoutes = [
    route(PATHS.LOGIN, ROUTES.LOGIN),
    route(PATHS.REGISTER, ROUTES.REGISTER),
];
