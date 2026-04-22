import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";

import { PATHS, ROUTES } from "../routeVars";

import { authRoutes } from "./auth.routes";
import { businessRoutes } from "./business.routes";
import { businessSetupRoutes } from "./business-setup.routes";
import { hrRoutes } from "./hr.routes";

export default [
  index(ROUTES.INDEX),

  ...authRoutes,

  layout(ROUTES.PROTECTED_LAYOUT, [
    route(PATHS.HOME, ROUTES.HOME),

    ...businessSetupRoutes,

    ...businessRoutes,

    ...hrRoutes,
  ]),
] satisfies RouteConfig;
