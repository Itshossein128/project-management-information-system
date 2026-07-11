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
      label: "Activities",
      labelI18nKey: "nav.projectActivities",
      icon: "business" as IconName,
      path: `${base}/${PATHS.PROJECT_ACTIVITIES}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_ACTIVITIES}`,
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
    {
      label: "Progress",
      labelI18nKey: "nav.projectProgress",
      icon: "dashboard" as IconName,
      path: `${base}/${PATHS.PROJECT_PROGRESS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_PROGRESS}`,
    },
    {
      label: "کنترل هزینه",
      labelI18nKey: "nav.projectCosts",
      icon: "business" as IconName,
      path: `${base}/${PATHS.PROJECT_COSTS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_COSTS}`,
    },
    {
      label: "بالانس مصالح",
      labelI18nKey: "nav.projectMaterialBalance",
      icon: "building" as IconName,
      path: `${base}/${PATHS.PROJECT_MATERIAL_BALANCE}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_MATERIAL_BALANCE}`,
    },
    {
      label: "گزارش نفرات",
      labelI18nKey: "nav.projectPersonnelSummary",
      icon: "users" as IconName,
      path: `${base}/${PATHS.PROJECT_PERSONNEL_SUMMARY}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_PERSONNEL_SUMMARY}`,
    },
    {
      label: "بانک فعالیت‌ها",
      labelI18nKey: "nav.projectActivityLog",
      icon: "clipboard" as IconName,
      path: `${base}/${PATHS.PROJECT_ACTIVITY_LOG}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_ACTIVITY_LOG}`,
    },
    {
      label: "Daily Reports",
      labelI18nKey: "nav.projectDailyReports",
      icon: "clipboard" as IconName,
      path: `${base}/${PATHS.PROJECT_DAILY_REPORTS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_DAILY_REPORTS}`,
    },
  ];
}
