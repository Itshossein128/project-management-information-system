import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Array containing routing configurations for public authentication pages (Login and Register).
export const authRoutes = [
    route(PATHS.LOGIN, ROUTES.LOGIN),
    route(PATHS.REGISTER, ROUTES.REGISTER),
];
