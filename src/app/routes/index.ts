import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";

import { PATHS, ROUTES } from "../routeVars";

import { authRoutes } from "./auth.routes";
import { businessRoutes } from "./business.routes";
import { hrRoutes } from "./hr.routes";

export default [
  index(ROUTES.INDEX),

  ...authRoutes,

  layout(ROUTES.PROTECTED_LAYOUT, [
    route(PATHS.HOME, ROUTES.HOME),

    ...businessRoutes,

    ...hrRoutes,
  ]),

  layout(ROUTES.BUSINESS_SETUP_LAYOUT, [
    route(PATHS.BUSINESS_SETUP, ROUTES.BUSINESS_SETUP),

    route(
      `${PATHS.BUSINESS_SETUP}/businesses/:businessId`,
      ROUTES.BUSINESS_SETUP_SCHEMA,
    ),
  ]),
] satisfies RouteConfig;
