import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";
import { PATHS, ROUTES } from "./routeVars";

export default [
  index(ROUTES.INDEX),
  route(PATHS.LOGIN, ROUTES.LOGIN),
  route(PATHS.REGISTER, ROUTES.REGISTER),
  route(PATHS.FORGOT_PASSWORD, ROUTES.FORGOT_PASSWORD),
  route(PATHS.RESET_PASSWORD, ROUTES.RESET_PASSWORD),
  layout(ROUTES.PROTECTED_LAYOUT, [
    route(PATHS.HOME, ROUTES.HOME),
    route(`${PATHS.BUSINESS}/:businessId`, ROUTES.BUSINESS),
    route(`${PATHS.BUSINESS}/:businessId/tables/:tableSlug`, ROUTES.BUSINESS_TABLE),
  ]),
  layout(ROUTES.BUSINESS_SETUP_LAYOUT, [
    route(PATHS.BUSINESS_SETUP, ROUTES.BUSINESS_SETUP),
    route(`${PATHS.BUSINESS_SETUP}/businesses/:businessId`, ROUTES.BUSINESS_SETUP_SCHEMA),
  ]),
] satisfies RouteConfig;
