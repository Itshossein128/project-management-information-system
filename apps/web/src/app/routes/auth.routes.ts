import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

export const authRoutes = [
    route(PATHS.LOGIN, ROUTES.LOGIN),
    route(PATHS.REGISTER, ROUTES.REGISTER),
];
