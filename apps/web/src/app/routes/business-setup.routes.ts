import { route } from "@react-router/dev/routes";
import { PATHS, ROUTES } from "../routeVars";

export const projectRoutes = [
  route(`${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`, ROUTES.BUSINESS_CREATE),
  route(`${PATHS.PROJECT}/:projectId/${PATHS.PROJECT_OVERVIEW}`, ROUTES.PROJECT_OVERVIEW),
  route(`${PATHS.PROJECT}/:projectId/${PATHS.PROJECT_WBS}`, ROUTES.PROJECT_WBS),
  route(
    `${PATHS.PROJECT}/:projectId/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`,
    ROUTES.PROJECT_MEMBERS,
  ),
  route(PATHS.PROJECT, ROUTES.PROJECT_LIST),
];

/** @deprecated use projectRoutes */
export const businessSetupRoutes = projectRoutes;
