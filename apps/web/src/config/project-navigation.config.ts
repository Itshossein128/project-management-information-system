import { PATHS } from "@/app/routeVars";
import type { IconName } from "@/components/icons";
import type { NavigationItem } from "@/types/navigation";

export function buildProjectNavItems(projectId: string): NavigationItem[] {
  const base = `/${PATHS.PROJECT}/${projectId}`;
  return [
    {
      label: "Overview",
      labelI18nKey: "nav.projectOverview",
      icon: "dashboard" as IconName,
      path: `${base}/${PATHS.PROJECT_OVERVIEW}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_OVERVIEW}`,
    },
    {
      label: "WBS",
      labelI18nKey: "nav.projectWbs",
      icon: "building" as IconName,
      path: `${base}/${PATHS.PROJECT_WBS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_WBS}`,
    },
    {
      label: "Members",
      labelI18nKey: "nav.projectMembers",
      icon: "users" as IconName,
      path: `${base}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`,
    },
    {
      label: "Weather",
      labelI18nKey: "nav.projectWeather",
      icon: "bolt" as IconName,
      path: `${base}/${PATHS.PROJECT_WEATHER}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_WEATHER}`,
    },
  ];
}
