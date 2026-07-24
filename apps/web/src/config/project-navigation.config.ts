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
        },
        {
          label: "Alerts",
          labelI18nKey: "nav.projectAlerts",
          path: `${base}/${PATHS.PROJECT_ALERTS}`,
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
        },
        {
          label: "Documents",
          labelI18nKey: "nav.projectDocuments",
          path: `${base}/${PATHS.PROJECT_DOCUMENTS}`,
        },
        {
          label: "Cash flow",
          labelI18nKey: "nav.projectCashFlow",
          path: `${base}/${PATHS.PROJECT_CASH_FLOW}`,
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
        },
        {
          label: "Economic analysis",
          labelI18nKey: "nav.projectEconomic",
          path: `${base}/${PATHS.PROJECT_ECONOMIC}`,
        },
      ],
    },
    {
      label: "Resources",
      labelI18nKey: "nav.projectResources",
      icon: "users" as IconName,
      path: `${base}/${PATHS.PROJECT_EQUIPMENT_UTILIZATION}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!equipment-utilization|equipment-log|labor-productivity|personnel-summary|manpower|labor-camp|leave-requests|overtime-requests)`,
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
        },
        {
          label: "Manpower",
          labelI18nKey: "nav.projectManpower",
          path: `${base}/${PATHS.PROJECT_MANPOWER}`,
        },
        {
          label: "Labor camp",
          labelI18nKey: "nav.projectLaborCamp",
          path: `${base}/${PATHS.PROJECT_LABOR_CAMP}`,
        },
        {
          label: "Leave",
          labelI18nKey: "nav.projectLeave",
          path: `${base}/${PATHS.PROJECT_LEAVE}`,
        },
        {
          label: "Overtime",
          labelI18nKey: "nav.projectOvertime",
          path: `${base}/${PATHS.PROJECT_OVERTIME}`,
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
