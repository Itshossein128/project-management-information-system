import { PATHS } from "@/app/routeVars";
import type { NavigationItem } from "@/types/navigation";
import { ROLES } from "./roles";

export const navigation: NavigationItem[] = [
  {
    label: "داشبورد",
    icon: "dashboard",
    path: PATHS.HOME,
    activeExact: true,
  },

  {
    label: "کسب و کار",
    icon: "business",
    path: PATHS.HOME,
  },

  {
    label: "منابع انسانی",
    icon: "users",
    path: PATHS.USERS,
    roles: [ROLES.ADMIN, ROLES.HR],
  },

  {
    label: "مدیریت کسب‌وکار",
    icon: "settings",
    path: PATHS.BUSINESS,
    roles: [ROLES.BUSINESS_SETUP],
    activePathPrefix: PATHS.BUSINESS,
    activePathExclude: "^/businesses/\\d+$",
  },
];
