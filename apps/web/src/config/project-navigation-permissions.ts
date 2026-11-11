import type { NavigationItem } from "../types/navigation";

// Match the read contract of each destination, not its module's enabled flag.
// Multiple codenames mean any one is sufficient, as on the owning screen/API.
const READ_PERMISSIONS: Record<string, readonly string[]> = {
  "": ["view_project"],
  overview: ["view_project"],
  dashboard: ["view_dashboard"],
  "standard-reports": ["view_dashboard", "view_reports"],
  wbs: ["view_wbs"],
  activities: ["view_activities"],
  "schedule/gantt": ["view_activities"],
  "schedule/status": ["view_activities"],
  progress: ["view_dashboard"],
  "activity-log": ["view_reports"],
  "decision-support": ["view_decision_support"],
  "daily-reports": ["view_reports"],
  "sync-conflicts": ["edit_reports"],
  "concrete-operations": ["view_reports"],
  weather: ["view_reports"],
  barriers: ["view_reports"],
  "risk-register": ["view_reports"],
  "quality-hse": ["view_reports"],
  alerts: ["view_project"],
  contracts: ["view_contracts"],
  subcontractors: ["view_contracts"],
  documents: ["view_documents"],
  "decisions-workflow": ["view_project", "view_documents"],
  "cash-flow": ["view_cashflow"],
  costs: ["view_costs"],
  "material-balance": ["view_reports"],
  procurement: ["view_procurement"],
  economic: ["view_dashboard"],
  "equipment-utilization": ["view_reports"],
  "equipment-log": ["view_reports"],
  "labor-productivity": ["view_reports"],
  "personnel-summary": ["view_reports"],
  manpower: ["view_reports"],
  "labor-camp": ["view_reports"],
  "resource-allocations": ["view_hr"],
  "leave-requests": ["view_reports"],
  "overtime-requests": ["view_reports"],
  settings: ["view_project"],
  "settings/members": ["view_project", "manage_members"],
  stakeholders: ["view_project"],
  buildings: ["view_reports"],
  mechanical: ["view_reports"],
  security: ["view_reports"],
  machinery: ["view_reports"],
  warehouse: ["view_reports"],
  electrical: ["view_reports"],
};

export function filterProjectNavByPermissions(
  items: NavigationItem[],
  has: (codename: string) => boolean,
): NavigationItem[] {
  const allowed = (path: string) => {
    const match = path.match(/^\/?projects\/[^/]+(?:\/(.*))?$/);
    const permissions = match ? READ_PERMISSIONS[match[1] ?? ""] : undefined;
    // Unknown destinations are not implicitly authorized.
    return permissions?.some(has) === true;
  };
  return items.flatMap((item) => {
    if (!item.children) return allowed(item.path) ? [item] : [];
    const children = item.children.filter((child) => allowed(child.path));
    return children.length ? [{ ...item, children }] : [];
  });
}
