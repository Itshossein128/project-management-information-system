import { layout, route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

// Array containing routing configurations for Human Resources (HR) specific views, protected by the HR layout.
export const hrRoutes = [
    layout(ROUTES.HR_PROTECTED_LAYOUT, [
        route(PATHS.USERS, ROUTES.USERS),
    ]),
];
