import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

/**
 * Array of route configurations dedicated to authentication.
 * Maps paths like login and register to their respective route file components.
 */
export const authRoutes = [
    route(PATHS.LOGIN, ROUTES.LOGIN),
    route(PATHS.REGISTER, ROUTES.REGISTER),
];
