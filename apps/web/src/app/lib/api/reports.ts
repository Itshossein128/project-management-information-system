import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface PersonnelSummary {
  job_titles: string[];
  dates: string[];
  data: Record<string, Record<string, number>>;
  totals_by_title: Record<string, number>;
  totals_by_date: Record<string, number>;
}

export interface ActivityLogRow {
  id: string;
  report_id: string;
  report_date: string;
  day_name: string;
  activity_description: string;
  shift: string;
  subcontractor: string;
  headcount: number | null;
  zone: string;
  block: string;
  floor: string;
  location: string;
  quantity: number | null;
  unit: string;
  activity_code: string | null;
  activity_name: string | null;
  report_status: string;
}

export interface ActivityLogFilterOptions {
  zones: string[];
  blocks: string[];
  subcontractors: string[];
}

export interface PaginatedActivityLog {
  count: number;
  next: string | null;
  previous: string | null;
  results: ActivityLogRow[];
}

export function fetchPersonnelSummary(
  projectId: string,
  params: {
    date_from?: string;
    date_to?: string;
    category?: "all" | "indirect" | "direct";
    group_by?: "daily" | "monthly";
  } = {},
) {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  if (params.category) search.set("category", params.category);
  if (params.group_by) search.set("group_by", params.group_by);
  const qs = search.toString();
  return apiJson<PersonnelSummary>(
    `${base(projectId)}/personnel-summary/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchActivityLog(
  projectId: string,
  params: {
    date_from?: string;
    date_to?: string;
    subcontractor?: string;
    zone?: string;
    block?: string;
    floor?: string;
    shift?: string;
    activity_id?: string;
    approved_only?: boolean;
    page?: number;
    page_size?: number;
  } = {},
) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== "") search.set(k, String(v));
  }
  const qs = search.toString();
  return apiJson<PaginatedActivityLog>(
    `${base(projectId)}/activity-log/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchActivityLogFilters(projectId: string) {
  return apiJson<ActivityLogFilterOptions>(`${base(projectId)}/activity-log/filters/`);
}
