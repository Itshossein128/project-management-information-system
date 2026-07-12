import { PATHS } from "@/app/routeVars";
import type { NavigationItem } from "@/types/navigation";
import { ROLES } from "./roles";

/**
 * Global sidebar: Home, Projects, HR hub, and settings for admins.
 */
export const mainSidebarNavigation: NavigationItem[] = [
  {
    label: "Home",
    labelI18nKey: "nav.sidebarHome",
    icon: "dashboard",
    path: PATHS.HOME,
    activeExact: true,
  },
  {
    label: "Projects",
    labelI18nKey: "nav.sidebarProjects",
    icon: "building",
    path: PATHS.PROJECT,
    activePathPrefix: `/${PATHS.PROJECT}`,
    activePathExclude: `^/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}$`,
  },
  {
    label: "HR",
    labelI18nKey: "nav.sidebarHr",
    icon: "users",
    path: PATHS.HR,
    roles: [ROLES.ADMIN, ROLES.HR],
    activePathPrefix: PATHS.HR,
  },
  {
    label: "Templates",
    labelI18nKey: "nav.settingsTemplates",
    icon: "building",
    path: `${PATHS.SETTINGS}/${PATHS.SETTINGS_TEMPLATES}`,
    roles: [ROLES.ADMIN, ROLES.HR, ROLES.BUSINESS_SETUP],
    activePathPrefix: `${PATHS.SETTINGS}/${PATHS.SETTINGS_TEMPLATES}`,
  },
  {
    label: "Roles",
    labelI18nKey: "nav.settingsRoles",
    icon: "shield",
    path: `${PATHS.SETTINGS}/${PATHS.SETTINGS_ROLES}`,
    roles: [ROLES.ADMIN, ROLES.HR],
    activePathPrefix: `${PATHS.SETTINGS}/${PATHS.SETTINGS_ROLES}`,
  },
];
