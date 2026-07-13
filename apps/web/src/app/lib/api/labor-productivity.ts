import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface LaborProductivityRow {
  activity_id?: string;
  activity_code?: string;
  activity_name?: string;
  executed_qty?: number;
  labor_hours?: number;
  productivity_index?: number | null;
  planned_budget_labor?: number | null;
  actual_man_days?: number;
  job_title?: string;
  headcount_days?: number;
  discipline?: string;
}

export interface LaborProductivityReport {
  group_by: string;
  total_labor_hours: number;
  total_executed_qty?: number;
  project_productivity_index?: number | null;
  rows: LaborProductivityRow[];
}

export function fetchLaborProductivity(
  projectId: string,
  params: {
    date_from?: string;
    date_to?: string;
    activity_id?: string;
    group_by?: "activity" | "discipline" | "job_title";
  } = {},
) {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  if (params.activity_id) search.set("activity_id", params.activity_id);
  if (params.group_by) search.set("group_by", params.group_by);
  const qs = search.toString();
  return apiJson<LaborProductivityReport>(
    `${base(projectId)}/labor-productivity/${qs ? `?${qs}` : ""}`,
  );
}
