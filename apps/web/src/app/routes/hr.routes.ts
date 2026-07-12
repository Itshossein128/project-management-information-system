import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Configuration array for hrRoutes routing.
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
