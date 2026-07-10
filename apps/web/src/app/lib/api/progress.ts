import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/progress`;

export interface ProgressSnapshot {
  as_of_date: string;
  planned_progress_pct: number;
  actual_progress_pct: number;
  schedule_variance_pct: number;
  spi: number | null;
  activities_total: number;
  activities_completed: number;
  activities_in_progress: number;
  activities_not_started: number;
  activities_behind_schedule: number;
  last_approved_report_date: string | null;
}

export interface SCurvePoint {
  date: string;
  planned_progress: number;
  actual_progress: number;
  variance: number;
}

export interface ActivityProgressRow {
  activity_id: string;
  activity_code: string;
  activity_name: string;
  wbs_name: string;
  weight: number | null;
  planned_progress_pct: number;
  actual_progress_pct: number;
  variance_pct: number;
  total_quantity: number | null;
  cumulative_quantity: number | null;
  unit: string;
  status: string;
  is_behind: boolean;
  last_update_date: string | null;
}

export interface EvmKpis {
  as_of_date: string;
  bac: number;
  ev: number;
  pv: number;
  ac: number;
  sv: number;
  cv: number;
  spi: number | null;
  cpi: number | null;
  eac: number | null;
  etc: number | null;
  vac: number | null;
  actual_progress_pct: number;
  planned_progress_pct: number;
  schedule_variance_pct: number;
  budget_consumption_pct: number | null;
}

export interface ProgressHistoryRow {
  date: string;
  planned_pct: number;
  actual_pct: number;
  variance_pct: number;
  approved_by_name: string;
  report_id: string;
}

export function fetchProgressSnapshot(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<ProgressSnapshot>(`${base(projectId)}/${qs}`);
}

export function fetchSCurve(
  projectId: string,
  params: {
    date_from?: string;
    date_to?: string;
    interval?: "daily" | "weekly" | "monthly";
    force_refresh?: boolean;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  if (params.interval) search.set("interval", params.interval);
  if (params.force_refresh) search.set("force_refresh", "true");
  const qs = search.toString();
  return apiJson<{ results: SCurvePoint[]; warning?: string }>(
    `${base(projectId)}/s-curve/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchActivityProgress(
  projectId: string,
  params: { wbs_id?: string; status?: string; is_behind?: boolean; as_of?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.wbs_id) search.set("wbs_id", params.wbs_id);
  if (params.status) search.set("status", params.status);
  if (params.is_behind) search.set("is_behind", "true");
  if (params.as_of) search.set("as_of", params.as_of);
  const qs = search.toString();
  return apiJson<ActivityProgressRow[]>(
    `${base(projectId)}/activities/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchProgressKpis(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<EvmKpis>(`${base(projectId)}/kpis/${qs}`);
}

export function fetchProgressHistory(projectId: string) {
  return apiJson<ProgressHistoryRow[]>(`${base(projectId)}/history/`);
}

export function postManualProgress(
  projectId: string,
  body: {
    activity_id: string;
    report_date: string;
    actual_progress: number;
    cumulative_quantity?: number;
    notes?: string;
  },
) {
  return apiJson(`${base(projectId)}/manual/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
