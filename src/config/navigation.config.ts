import { PATHS } from "@/app/routeVars";
import { ROLES } from "./roles";

export const navigation = [
  {
    label: "داشبورد",
    icon: "dashboard",
    path: PATHS.HOME,
  },

  {
    label: "کسب و کار",
    icon: "business",
    path: PATHS.BUSINESS,
    children: [
      {
        label: "جداول",
        path: `${PATHS.BUSINESS}/:businessId/tables`,
      },
    ],
  },

  {
    label: "منابع انسانی",
    icon: "users",
    path: PATHS.USERS,
    roles: [ROLES.ADMIN, ROLES.HR],
  },
];
