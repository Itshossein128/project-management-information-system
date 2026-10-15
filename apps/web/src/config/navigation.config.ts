import { PATHS } from "@/app/routeVars";
import type { NavigationItem } from "@/types/navigation";
import { ROLES } from "./roles";

/**
 * Daily work first; organization configuration and access management last.
 */
export const mainSidebarNavigation: NavigationItem[] = [
  {
    label: "Projects",
    section: "workspace",
    labelI18nKey: "nav.sidebarProjects",
    icon: "projects",
    path: PATHS.PROJECT,
    activePathPrefix: PATHS.PROJECT,
    activePathExclude: `^/${PATHS.PROJECT}/setup(?:/|$)`,
  },
  {
    label: "Portfolio dashboard",
    section: "workspace",
    labelI18nKey: "nav.executiveDashboard",
    icon: "dashboard",
    path: PATHS.EXECUTIVE_DASHBOARD,
  },
  {
    label: "Portfolio liquidity",
    section: "workspace",
    labelI18nKey: "nav.portfolioLiquidity",
    icon: "cashflow",
    path: PATHS.PORTFOLIO_LIQUIDITY,
  },
  {
    label: "HR",
    section: "workspace",
    labelI18nKey: "nav.sidebarHr",
    icon: "users",
    path: PATHS.HR,
    roles: [ROLES.ADMIN, ROLES.HR],
    activePathPrefix: PATHS.HR,
  },
  {
    label: "Data administration",
    section: "administration",
    labelI18nKey: "nav.dataAdministration",
    icon: "settings",
    path: `${PATHS.PROJECT}/setup`,
    roles: [ROLES.BUSINESS_SETUP],
    activeExact: true,
  },
  {
    label: "Organization references",
    section: "administration",
    labelI18nKey: "nav.settingsOrgRefs",
    icon: "organization",
    path: `${PATHS.SETTINGS}/${PATHS.SETTINGS_ORG_REFS}`,
    roles: [ROLES.ADMIN, ROLES.HR, ROLES.BUSINESS_SETUP],
  },
  {
    label: "Templates",
    section: "administration",
    labelI18nKey: "nav.settingsTemplates",
    icon: "templates",
    path: `${PATHS.SETTINGS}/${PATHS.SETTINGS_TEMPLATES}`,
    roles: [ROLES.ADMIN, ROLES.HR, ROLES.BUSINESS_SETUP],
    activePathPrefix: `${PATHS.SETTINGS}/${PATHS.SETTINGS_TEMPLATES}`,
  },
  {
    label: "Roles",
    section: "administration",
    labelI18nKey: "nav.settingsRoles",
    icon: "shield",
    path: `${PATHS.SETTINGS}/${PATHS.SETTINGS_ROLES}`,
    roles: [ROLES.ADMIN, ROLES.HR],
    activePathPrefix: `${PATHS.SETTINGS}/${PATHS.SETTINGS_ROLES}`,
  },
];
