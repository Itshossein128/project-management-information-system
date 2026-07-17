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
      label: "برنامه‌ریزی",
      labelI18nKey: "nav.projectPlanning",
      icon: "building" as IconName,
      path: `${base}/${PATHS.PROJECT_WBS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!wbs|activities|schedule|progress|activity-log)`,
      children: [
        { label: "ساختار شکست کار", path: `${base}/${PATHS.PROJECT_WBS}` },
        { label: "فعالیت‌ها", path: `${base}/${PATHS.PROJECT_ACTIVITIES}` },
        { label: "گانت", path: `${base}/schedule/${PATHS.PROJECT_GANTT}` },
        { label: "پیشرفت", path: `${base}/${PATHS.PROJECT_PROGRESS}` },
        { label: "بانک فعالیت‌ها", path: `${base}/${PATHS.PROJECT_ACTIVITY_LOG}` },
      ],
    },
    {
      label: "کارگاه",
      labelI18nKey: "nav.projectField",
      icon: "clipboard" as IconName,
      path: `${base}/${PATHS.PROJECT_DAILY_REPORTS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!daily-reports|sync-conflicts|weather|barriers|alerts)`,
      children: [
        { label: "گزارش روزانه", path: `${base}/${PATHS.PROJECT_DAILY_REPORTS}` },
        {
          label: "تعارض‌های همگام‌سازی",
          path: `${base}/${PATHS.PROJECT_SYNC_CONFLICTS}`,
        },
        { label: "وضعیت جوی", path: `${base}/${PATHS.PROJECT_WEATHER}` },
        { label: "موانع", path: `${base}/${PATHS.PROJECT_BARRIERS}` },
        { label: "هشدارها", path: `${base}/${PATHS.PROJECT_ALERTS}` },
      ],
    },
    {
      label: "بازرگانی",
      labelI18nKey: "nav.projectCommercial",
      icon: "business" as IconName,
      path: `${base}/${PATHS.PROJECT_CONTRACTS}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!contracts|subcontractors|documents|cash-flow|costs|material-balance|economic)`,
      children: [
        { label: "قراردادها", path: `${base}/${PATHS.PROJECT_CONTRACTS}` },
        {
          label: "پیمانکاران فرعی",
          path: `${base}/${PATHS.PROJECT_SUBCONTRACTORS}`,
        },
        { label: "مدارک و مکاتبات", path: `${base}/${PATHS.PROJECT_DOCUMENTS}` },
        { label: "جریان نقدی", path: `${base}/${PATHS.PROJECT_CASH_FLOW}` },
        { label: "کنترل هزینه", path: `${base}/${PATHS.PROJECT_COSTS}` },
        {
          label: "بالانس مصالح",
          path: `${base}/${PATHS.PROJECT_MATERIAL_BALANCE}`,
        },
        { label: "تحلیل اقتصادی", path: `${base}/${PATHS.PROJECT_ECONOMIC}` },
      ],
    },
    {
      label: "منابع",
      labelI18nKey: "nav.projectResources",
      icon: "users" as IconName,
      path: `${base}/${PATHS.PROJECT_EQUIPMENT_UTILIZATION}`,
      activePathPrefix: base,
      activePathExclude: `${base}/(?!equipment-utilization|equipment-log|labor-productivity|personnel-summary|manpower|labor-camp|leave-requests|overtime-requests)`,
      children: [
        {
          label: "بهره‌وری ماشین‌آلات",
          path: `${base}/${PATHS.PROJECT_EQUIPMENT_UTILIZATION}`,
        },
        {
          label: "کارکرد ماشین‌آلات",
          path: `${base}/${PATHS.PROJECT_EQUIPMENT_LOG}`,
        },
        {
          label: "بهره‌وری نیروی انسانی",
          path: `${base}/${PATHS.PROJECT_LABOR_PRODUCTIVITY}`,
        },
        {
          label: "گزارش نفرات",
          path: `${base}/${PATHS.PROJECT_PERSONNEL_SUMMARY}`,
        },
        {
          label: "نیروی انسانی",
          path: `${base}/${PATHS.PROJECT_MANPOWER}`,
        },
        {
          label: "کمپ کارگری",
          path: `${base}/${PATHS.PROJECT_LABOR_CAMP}`,
        },
        {
          label: "مرخصی",
          path: `${base}/${PATHS.PROJECT_LEAVE}`,
        },
        {
          label: "اضافه‌کار",
          path: `${base}/${PATHS.PROJECT_OVERTIME}`,
        },
      ],
    },
    {
      label: "تنظیمات",
      labelI18nKey: "nav.projectAdmin",
      icon: "settings" as IconName,
      path: `${base}/${PATHS.PROJECT_SETTINGS}`,
      activePathPrefix: `${base}/${PATHS.PROJECT_SETTINGS}`,
      children: [
        { label: "تنظیمات پروژه", path: `${base}/${PATHS.PROJECT_SETTINGS}` },
        {
          label: "اعضا",
          path: `${base}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`,
        },
      ],
    },
  ];
}
