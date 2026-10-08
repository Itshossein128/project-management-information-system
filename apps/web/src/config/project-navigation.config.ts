import { PATHS } from "@/app/routeVars";
import type { IconName } from "@/components/icons";
import type { NavigationChildItem, NavigationItem } from "@/types/navigation";

/** Path segment (last URL part) → capability_key for FR-CORE-012 nav hiding. */
export const NAV_PATH_CAPABILITY: Record<string, string> = {
  "risk-register": "risk",
  economic: "economic",
  procurement: "procurement",
  "cash-flow": "cash_flow",
  documents: "documents",
  alerts: "alerts",
  subcontractors: "subcontractors",
  manpower: "hr",
  "leave-requests": "hr",
  "overtime-requests": "hr",
  "labor-camp": "hr",
  "labor-productivity": "hr",
  "personnel-summary": "hr",
  "resource-allocations": "hr",
};

function pathCapability(path: string): string | undefined {
  const segment = path.split("/").filter(Boolean).pop() ?? "";
  return NAV_PATH_CAPABILITY[segment];
}

export function filterNavByCapabilities(
  items: NavigationItem[],
  disabledKeys: Set<string>,
): NavigationItem[] {
  if (disabledKeys.size === 0) return items;
  return items
    .map((item) => {
      const children = item.children?.filter((child: NavigationChildItem) => {
        const key = pathCapability(child.path);
        return !key || !disabledKeys.has(key);
      });
      if (item.children && (!children || children.length === 0)) {
        return null;
      }
      const selfKey = pathCapability(item.path);
      if (selfKey && disabledKeys.has(selfKey) && !item.children) {
        return null;
      }
      return children ? { ...item, children } : item;
    })
    .filter((item): item is NavigationItem => item != null);
}

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
      label: "Planning",
      labelI18nKey: "nav.projectPlanning",
      icon: "building" as IconName,
      path: `${base}/${PATHS.PROJECT_WBS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!wbs|activities|schedule|progress|activity-log)`,
      children: [
        { label: "WBS", labelI18nKey: "nav.projectWbs", path: `${base}/${PATHS.PROJECT_WBS}` },
        {
          label: "Activities",
          labelI18nKey: "nav.projectActivities",
          path: `${base}/${PATHS.PROJECT_ACTIVITIES}`,
        },
        {
          label: "Gantt",
          labelI18nKey: "nav.projectGantt",
          path: `${base}/schedule/${PATHS.PROJECT_GANTT}`,
        },
        {
          label: "Schedule status",
          labelI18nKey: "nav.scheduleStatus",
          path: `${base}/schedule/${PATHS.PROJECT_SCHEDULE_STATUS}`,
        },
        {
          label: "Progress",
          labelI18nKey: "nav.projectProgress",
          path: `${base}/${PATHS.PROJECT_PROGRESS}`,
        },
        {
          label: "Activity bank",
          labelI18nKey: "nav.projectActivityLog",
          path: `${base}/${PATHS.PROJECT_ACTIVITY_LOG}`,
        },
      ],
    },
    {
      label: "Field",
      labelI18nKey: "nav.projectField",
      icon: "clipboard" as IconName,
      path: `${base}/${PATHS.PROJECT_DAILY_REPORTS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!daily-reports|sync-conflicts|weather|barriers|risk-register|alerts)`,
      children: [
        {
          label: "Daily reports",
          labelI18nKey: "nav.projectDailyReports",
          path: `${base}/${PATHS.PROJECT_DAILY_REPORTS}`,
        },
        {
          label: "Sync conflicts",
          labelI18nKey: "nav.projectSyncConflicts",
          path: `${base}/${PATHS.PROJECT_SYNC_CONFLICTS}`,
        },
        {
          label: "Weather",
          labelI18nKey: "nav.projectWeather",
          path: `${base}/${PATHS.PROJECT_WEATHER}`,
        },
        {
          label: "Barriers",
          labelI18nKey: "nav.projectBarriers",
          path: `${base}/${PATHS.PROJECT_BARRIERS}`,
        },
        {
          label: "Risk & delay",
          labelI18nKey: "nav.projectRiskRegister",
          path: `${base}/${PATHS.PROJECT_RISK_REGISTER}`,
          capabilityKey: "risk",
        },
        {
          label: "Alerts",
          labelI18nKey: "nav.projectAlerts",
          path: `${base}/${PATHS.PROJECT_ALERTS}`,
          capabilityKey: "alerts",
        },
      ],
    },
    {
      label: "Commercial",
      labelI18nKey: "nav.projectCommercial",
      icon: "business" as IconName,
      path: `${base}/${PATHS.PROJECT_CONTRACTS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!contracts|subcontractors|documents|cash-flow|costs|material-balance|procurement|economic)`,
      children: [
        {
          label: "Contracts",
          labelI18nKey: "nav.projectContracts",
          path: `${base}/${PATHS.PROJECT_CONTRACTS}`,
        },
        {
          label: "Subcontractors",
          labelI18nKey: "nav.projectSubcontractors",
          path: `${base}/${PATHS.PROJECT_SUBCONTRACTORS}`,
          capabilityKey: "subcontractors",
        },
        {
          label: "Documents",
          labelI18nKey: "nav.projectDocuments",
          path: `${base}/${PATHS.PROJECT_DOCUMENTS}`,
          capabilityKey: "documents",
        },
        {
          label: "Cash flow",
          labelI18nKey: "nav.projectCashFlow",
          path: `${base}/${PATHS.PROJECT_CASH_FLOW}`,
          capabilityKey: "cash_flow",
        },
        {
          label: "Cost control",
          labelI18nKey: "nav.projectCosts",
          path: `${base}/${PATHS.PROJECT_COSTS}`,
        },
        {
          label: "Material balance",
          labelI18nKey: "nav.projectMaterialBalance",
          path: `${base}/${PATHS.PROJECT_MATERIAL_BALANCE}`,
        },
        {
          label: "Procurement",
          labelI18nKey: "nav.projectProcurement",
          path: `${base}/${PATHS.PROJECT_PROCUREMENT}`,
          capabilityKey: "procurement",
        },
        {
          label: "Economic analysis",
          labelI18nKey: "nav.projectEconomic",
          path: `${base}/${PATHS.PROJECT_ECONOMIC}`,
          capabilityKey: "economic",
        },
      ],
    },
    {
      label: "Resources",
      labelI18nKey: "nav.projectResources",
      icon: "users" as IconName,
      path: `${base}/${PATHS.PROJECT_EQUIPMENT_UTILIZATION}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!equipment-utilization|equipment-log|labor-productivity|personnel-summary|manpower|labor-camp|leave-requests|overtime-requests|resource-allocations)`,
      children: [
        {
          label: "Equipment utilization",
          labelI18nKey: "nav.projectEquipmentUtilization",
          path: `${base}/${PATHS.PROJECT_EQUIPMENT_UTILIZATION}`,
        },
        {
          label: "Equipment log",
          labelI18nKey: "nav.projectEquipmentLog",
          path: `${base}/${PATHS.PROJECT_EQUIPMENT_LOG}`,
        },
        {
          label: "Labor productivity",
          labelI18nKey: "nav.projectLaborProductivity",
          path: `${base}/${PATHS.PROJECT_LABOR_PRODUCTIVITY}`,
        },
        {
          label: "Personnel summary",
          labelI18nKey: "nav.projectPersonnelSummary",
          path: `${base}/${PATHS.PROJECT_PERSONNEL_SUMMARY}`,
          capabilityKey: "hr",
        },
        {
          label: "Manpower",
          labelI18nKey: "nav.projectManpower",
          path: `${base}/${PATHS.PROJECT_MANPOWER}`,
          capabilityKey: "hr",
        },
        {
          label: "Labor camp",
          labelI18nKey: "nav.projectLaborCamp",
          path: `${base}/${PATHS.PROJECT_LABOR_CAMP}`,
          capabilityKey: "hr",
        },
        {
          label: "Allocations",
          labelI18nKey: "nav.projectAllocations",
          path: `${base}/${PATHS.PROJECT_ALLOCATIONS}`,
          capabilityKey: "hr",
        },
        {
          label: "Leave",
          labelI18nKey: "nav.projectLeave",
          path: `${base}/${PATHS.PROJECT_LEAVE}`,
          capabilityKey: "hr",
        },
        {
          label: "Overtime",
          labelI18nKey: "nav.projectOvertime",
          path: `${base}/${PATHS.PROJECT_OVERTIME}`,
          capabilityKey: "hr",
        },
      ],
    },
    {
      label: "Settings",
      labelI18nKey: "nav.projectAdmin",
      icon: "settings" as IconName,
      path: `${base}/${PATHS.PROJECT_SETTINGS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_SETTINGS}`,
      children: [
        {
          label: "Project settings",
          labelI18nKey: "nav.projectSettings",
          path: `${base}/${PATHS.PROJECT_SETTINGS}`,
        },
        {
          label: "Members",
          labelI18nKey: "nav.projectMembers",
          path: `${base}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`,
        },
      ],
    },
  ];
}
