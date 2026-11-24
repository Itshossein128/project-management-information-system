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
  source_discipline?: string;
  parcel?: string;
  activity_description: string;
  shift: string;
  subcontractor: string;
  contractor_id: string | null;
  headcount: number | null;
  zone: string | null;
  block: string | null;
  floor: string | null;
  location: string | null;
  quantity: number | null;
  quantity_measured: boolean;
  unit: string | null;
  activity_code: string | null;
  activity_name: string | null;
  report_status: string;
}

export interface ActivityLogFilterOptions {
  zones: string[];
  blocks: string[];
  subcontractors: string[];
  contractors: { id: string; name: string }[];
  disciplines?: string[];
  parcels?: string[];
  floors: string[];
  shifts: string[];
  units: string[];
}

export type ActivityLogMultiValue = string | string[];

export const activityLogScalarFilters = [
  "date_from", "date_to", "contractor_id", "subcontractor", "zone", "block", "floor",
  "shift", "activity_id", "status", "location", "q", "headcount", "quantity", "unit", "report_id",
] as const;

export type ActivityLogSelection = Partial<Record<(typeof activityLogScalarFilters)[number], string>> & {
  discipline?: ActivityLogMultiValue;
  source_discipline?: ActivityLogMultiValue;
  parcel?: ActivityLogMultiValue;
  approved_only?: boolean;
};

export function serializeActivityLogSelection(selection: ActivityLogSelection) {
  const search = new URLSearchParams();
  for (const field of activityLogScalarFilters) {
    const value = selection[field];
    if (value) search.set(field, value);
  }
  for (const field of ["source_discipline", "discipline", "parcel"] as const) {
    const value = selection[field];
    if (value?.length) search.set(field, Array.isArray(value) ? value.join(",") : value);
  }
  if (selection.approved_only !== undefined) search.set("approved_only", String(selection.approved_only));
  return search;
}

export interface PaginatedActivityLog {
  count: number;
  next: string | null;
  previous: string | null;
  results: ActivityLogRow[];
  aggregates: {
    headcount_sum: number;
    quantity_by_unit: {
      unit: string;
      total: string | null;
      measured_count: number;
      unknown_count: number;
    }[];
    unknown_quantity_without_unit_count: number;
  };
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
  params: ActivityLogSelection & { page?: number; page_size?: number } = {},
) {
  const search = serializeActivityLogSelection(params);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiJson<PaginatedActivityLog>(
    `${base(projectId)}/activity-log/${query ? `?${query}` : ""}`,
  );
}

export function fetchActivityLogFilters(projectId: string, approvedOnly = true) {
  const query = approvedOnly ? "" : "?approved_only=false";
  return apiJson<ActivityLogFilterOptions>(`${base(projectId)}/activity-log/filters/${query}`);
}
