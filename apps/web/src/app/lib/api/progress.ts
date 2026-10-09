import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/progress`;
const activitiesBase = (projectId: string) =>
  `/${PATHS.API_PROJECTS}/${projectId}/activities`;
const reportsBase = (projectId: string) =>
  `/${PATHS.API_PROJECTS}/${projectId}/progress-reports`;

export type MeasurementMethod = "quantity" | "weighted_milestones" | "evidence_percent";
export type MeasurementStatus = "draft" | "approved" | "not_defined";

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
  wbs_id?: string | null;
  wbs_name: string;
  weight: number | null;
  period_progress_pct?: number;
  cumulative_progress_pct?: number;
  planned_progress_pct: number;
  actual_progress_pct: number;
  approved_progress_pct?: number;
  variance_pct: number;
  total_quantity: number | null;
  cumulative_quantity: number | null;
  unit: string;
  status: string;
  is_behind: boolean;
  last_update_date: string | null;
  measurement_method?: MeasurementMethod | null;
  measurement_status?: MeasurementStatus;
  measurement_version_id?: string | null;
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

export interface ActivityMeasurement {
  activity_id: string;
  method: MeasurementMethod;
  status: MeasurementStatus | "draft" | "approved";
  total_quantity: number | string | null;
  unit_id: string | null;
  milestones: { name: string; weight: number }[];
  evidence_rules: string;
  current_version_id: string | null;
  pending_change_reason?: string;
}

export interface PeriodReportFigure {
  id: string;
  section: string;
  label_key: string;
  value: unknown;
  value_status: "recorded" | "not_recorded";
  source_type: string;
  source_id: string | null;
  source_path: string;
  source_approved: boolean;
  last_updated_at: string | null;
  override_count?: number;
}

export interface PeriodReport {
  id: string;
  project_id: string;
  kind: "weekly" | "monthly";
  title: string;
  period_start: string;
  period_end: string;
  status: "generated" | "superseded";
  generated_at: string;
  generated_by: string | null;
  superseded_by: string | null;
  figures?: PeriodReportFigure[];
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
  params: {
    wbs_id?: string;
    status?: string;
    is_behind?: boolean;
    as_of?: string;
    period_start?: string;
    period_end?: string;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.wbs_id) search.set("wbs_id", params.wbs_id);
  if (params.status) search.set("status", params.status);
  if (params.is_behind) search.set("is_behind", "true");
  if (params.as_of) search.set("as_of", params.as_of);
  if (params.period_start) search.set("period_start", params.period_start);
  if (params.period_end) search.set("period_end", params.period_end);
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

export function fetchActivityMeasurement(projectId: string, activityId: string) {
  return apiJson<ActivityMeasurement>(
    `${activitiesBase(projectId)}/${activityId}/measurement/`,
  );
}

export function updateActivityMeasurement(
  projectId: string,
  activityId: string,
  body: Partial<{
    method: MeasurementMethod;
    total_quantity: number | null;
    unit_id: string | null;
    milestones: { name: string; weight: number }[];
    evidence_rules: string;
  }>,
) {
  return apiJson<ActivityMeasurement>(
    `${activitiesBase(projectId)}/${activityId}/measurement/`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export function approveActivityMeasurement(
  projectId: string,
  activityId: string,
  reason?: string,
) {
  return apiJson<ActivityMeasurement>(
    `${activitiesBase(projectId)}/${activityId}/measurement/approve/`,
    { method: "POST", body: JSON.stringify(reason ? { reason } : {}) },
  );
}

export function changeActivityMeasurement(
  projectId: string,
  activityId: string,
  body: {
    reason: string;
    method?: MeasurementMethod;
    total_quantity?: number | null;
    unit_id?: string | null;
    milestones?: { name: string; weight: number }[];
    evidence_rules?: string;
  },
) {
  return apiJson<ActivityMeasurement>(
    `${activitiesBase(projectId)}/${activityId}/measurement/change/`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function technicalApproveProgress(projectId: string, activityId: string) {
  return apiJson(`${base(projectId)}/${activityId}/technical-approve/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function fetchPeriodReports(
  projectId: string,
  params: { kind?: "weekly" | "monthly" } = {},
) {
  const search = new URLSearchParams();
  if (params.kind) search.set("kind", params.kind);
  const qs = search.toString();
  return apiJson<PeriodReport[]>(`${reportsBase(projectId)}/${qs ? `?${qs}` : ""}`);
}

export function generatePeriodReport(
  projectId: string,
  body: { kind: "weekly" | "monthly"; period_start: string; period_end: string },
) {
  return apiJson<PeriodReport>(`${reportsBase(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchPeriodReport(projectId: string, reportId: string) {
  return apiJson<PeriodReport>(`${reportsBase(projectId)}/${reportId}/`);
}

export function overridePeriodReportFigure(
  projectId: string,
  figureId: string,
  body: { new_value: unknown; reason: string },
) {
  return apiJson(`${reportsBase(projectId)}/figures/${figureId}/overrides/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
