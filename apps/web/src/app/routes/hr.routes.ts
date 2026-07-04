import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Variable holding hrRoutes
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
