import { PATHS } from "@/app/routeVars";
import type { NavigationItem } from "@/types/navigation";
import { ROLES } from "./roles";

/**
 * Global sidebar: identical on every page. In-app workflow uses cards and
 * in-page back links (`businesses/:id/...`, `/hr/...`); the sidebar only
 * exposes Home and the HR hub.
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
    label: "HR",
    labelI18nKey: "nav.sidebarHr",
    icon: "users",
    path: PATHS.HR,
    roles: [ROLES.ADMIN, ROLES.HR],
    activePathPrefix: PATHS.HR,
  },
];
