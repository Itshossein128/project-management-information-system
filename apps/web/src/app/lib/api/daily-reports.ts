import { apiBlob, apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import type { ListResponse } from "@/app/lib/api-types";

export type ReportStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "approved"
  | "rejected";

export type WeatherCondition =
  | "sunny"
  | "cloudy"
  | "partly_cloudy"
  | "rainy"
  | "stormy"
  | "snowy"
  | "foggy";

export type SiteStatus = "active" | "inactive";
export type ReportShift = "day" | "night" | "full";
export type RowShift = "shift_1" | "shift_2" | "shift_3";
export type LaborCategory = "indirect" | "direct";

export interface DailyReportListItem {
  report_id: string;
  report_date: string;
  day_of_week: string;
  site_status: SiteStatus;
  site_status_label: string;
  weather_condition: WeatherCondition | null;
  weather_condition_label: string | null;
  status: ReportStatus;
  status_label: string;
  prepared_by_name: string | null;
  approved_by_name: string | null;
  activity_count: number;
  labor_total: number;
  equipment_count: number;
  has_incidents: boolean;
}

export interface ActivityRow {
  id: string;
  activity_ref: string | null;
  activity_code?: string | null;
  activity_description: string;
  shift: RowShift;
  subcontractor_name: string;
  subcontractor_ref: string | null;
  headcount: number | null;
  zone: string | null;
  block: string | null;
  floor: string | null;
  location_detail: string | null;
  quantity: string | null;
  quantity_measured: boolean;
  unit: string | null;
  execution_percentage: string | null;
  notes: string;
}

export interface LaborRow {
  id: string;
  labor_category: LaborCategory;
  job_title: string;
  custom_title: string;
  shift_1_count: number;
  shift_2_count: number;
  shift_3_count: number;
  total_count: number;
}

export interface EquipmentRow {
  id: string;
  equipment_name: string;
  equipment_ref: string;
  shift: ReportShift;
  status: "active" | "standby" | "broken";
  ownership_type: "owned" | "rented";
  work_start: string | null;
  work_end: string | null;
  repair_hours: string;
  productive_hours: string | null;
  activity_ref: string | null;
  notes: string;
}

export interface MaterialRow {
  id: string;
  material_ref: string | null;
  material_description: string;
  quantity: string;
  unit: string;
  transaction_type: "receipt" | "issue" | "waste";
  activity_ref: string | null;
  notes: string;
}

export interface ConcreteRow {
  id: string;
  concrete_description: string;
  volume_m3: string;
  activity_ref: string | null;
  zone: string | null;
  block: string | null;
  floor: string | null;
  notes: string;
}

export interface LaborCampRow {
  id: string;
  connex_number: string;
  subcontractor_name: string;
  total_residents: number;
  present_count: number;
  on_leave_count: number;
  capacity: number;
}

export interface IncidentRow {
  id: string;
  incident_type: "safety" | "quality" | "environmental" | "stoppage" | "visitor";
  description: string;
  corrective_action: string;
}

export interface DailyReportDetail {
  report_id: string;
  report_date: string;
  day_of_week: string;
  shift: ReportShift;
  weather_condition: WeatherCondition | null;
  weather_condition_label: string | null;
  temp_max: string | null;
  temp_min: string | null;
  site_status: SiteStatus;
  site_status_label: string;
  general_notes: string;
  status: ReportStatus;
  status_label: string;
  prepared_by_name: string | null;
  submitted_by_name: string | null;
  reviewed_by_name: string | null;
  approved_by_name: string | null;
  submitted_at: string | null;
  reviewed_at: string | null;
  approved_at: string | null;
  rejection_reason: string;
  synced_from_offline: boolean;
  local_id: string | null;
  created_at: string;
  updated_at: string;
  activities: ActivityRow[];
  labor: LaborRow[];
  equipment: EquipmentRow[];
  materials: MaterialRow[];
  concrete_logs: ConcreteRow[];
  labor_camp: LaborCampRow[];
  incidents: IncidentRow[];
}

export interface HeaderPayload {
  report_date: string;
  shift?: ReportShift;
  weather_condition?: WeatherCondition | null;
  temp_max?: string | number | null;
  temp_min?: string | number | null;
  site_status?: SiteStatus;
  general_notes?: string;
  local_id?: string | null;
}

export interface JobTitle {
  id: string;
  category: LaborCategory;
  title: string;
  display_order: number;
}

export interface DailyReportListParams {
  page?: number;
  per_page?: number;
  date_from?: string;
  date_to?: string;
  status?: ReportStatus;
  prepared_by?: string;
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/daily-reports`;

function buildQuery(params: DailyReportListParams = {}) {
  const q = new URLSearchParams();
  if (params.page) q.set("page", String(params.page));
  if (params.per_page) q.set("per_page", String(params.per_page));
  if (params.date_from) q.set("date_from", params.date_from);
  if (params.date_to) q.set("date_to", params.date_to);
  if (params.status) q.set("status", params.status);
  if (params.prepared_by) q.set("prepared_by", params.prepared_by);
  const s = q.toString();
  return s ? `?${s}` : "";
}

export function fetchDailyReports(projectId: string, params?: DailyReportListParams) {
  return apiJson<ListResponse<DailyReportListItem>>(`${base(projectId)}/${buildQuery(params)}`);
}

export function fetchDailyReport(projectId: string, reportId: string) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/`);
}

export function createDailyReport(projectId: string, payload: HeaderPayload) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateDailyReport(
  projectId: string,
  reportId: string,
  payload: Partial<HeaderPayload>,
) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteDailyReport(projectId: string, reportId: string) {
  return apiJson<void>(`${base(projectId)}/${reportId}/`, { method: "DELETE" });
}

// Workflow -----------------------------------------------------------------

export function submitReport(projectId: string, reportId: string) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/submit/`, { method: "POST" });
}
export function reviewReport(projectId: string, reportId: string, notes = "") {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/review/`, {
    method: "POST",
    body: JSON.stringify({ notes }),
  });
}
export function approveReport(projectId: string, reportId: string) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/approve/`, { method: "POST" });
}
export function rejectReport(projectId: string, reportId: string, reason: string) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/${reportId}/reject/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

// Child rows ----------------------------------------------------------------

export type ChildResource =
  | "activities"
  | "labor"
  | "equipment"
  | "materials"
  | "concrete-logs"
  | "labor-camp"
  | "incidents";

export function createChildRow<T>(
  projectId: string,
  reportId: string,
  resource: ChildResource,
  payload: unknown,
) {
  return apiJson<T>(`${base(projectId)}/${reportId}/${resource}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateChildRow<T>(
  projectId: string,
  reportId: string,
  resource: ChildResource,
  rowId: string,
  payload: unknown,
) {
  return apiJson<T>(`${base(projectId)}/${reportId}/${resource}/${rowId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteChildRow(
  projectId: string,
  reportId: string,
  resource: ChildResource,
  rowId: string,
) {
  return apiJson<void>(`${base(projectId)}/${reportId}/${resource}/${rowId}/`, {
    method: "DELETE",
  });
}

export function batchSaveLabor(projectId: string, reportId: string, rows: unknown[]) {
  return apiJson<LaborRow[]>(`${base(projectId)}/${reportId}/labor/`, {
    method: "POST",
    body: JSON.stringify(rows),
  });
}

// Reference + PDF ------------------------------------------------------------

export function fetchJobTitles(projectId: string, category?: LaborCategory) {
  const q = category ? `?category=${category}` : "";
  return apiJson<JobTitle[]>(`/${PATHS.API_PROJECTS}/${projectId}/manpower/job-titles/${q}`);
}

export function fetchReportPdf(projectId: string, reportId: string) {
  return apiBlob(`${base(projectId)}/${reportId}/pdf/`);
}

export interface SyncBatchResult {
  results: Array<{
    local_id: string | null;
    status: "created" | "merged" | "skipped" | "conflict" | "error";
    server_id: string | null;
    conflict_reason: string | null;
    child_errors?: unknown[];
  }>;
  summary: {
    created: number;
    merged: number;
    skipped: number;
    conflicts: number;
    errors: number;
  };
}

export function syncBatch(projectId: string, reports: unknown[]) {
  return apiJson<SyncBatchResult>(`${base(projectId)}/sync-batch/`, {
    method: "POST",
    body: JSON.stringify(reports),
  });
}

export const STATUS_BADGE: Record<ReportStatus, "neutral" | "info" | "warning" | "success" | "danger"> = {
  draft: "neutral",
  submitted: "info",
  under_review: "warning",
  approved: "success",
  rejected: "danger",
};

export const STATUS_LABELS: Record<ReportStatus, string> = {
  draft: "پیش‌نویس",
  submitted: "ارسال شده",
  under_review: "در حال بررسی",
  approved: "تأیید شده",
  rejected: "رد شده",
};

export const WEATHER_META: Record<WeatherCondition, { label: string; icon: string }> = {
  sunny: { label: "آفتابی", icon: "☀️" },
  cloudy: { label: "ابری", icon: "☁️" },
  partly_cloudy: { label: "نیمه‌ابری", icon: "⛅" },
  rainy: { label: "بارانی", icon: "🌧️" },
  stormy: { label: "طوفانی", icon: "🌩️" },
  snowy: { label: "برفی", icon: "❄️" },
  foggy: { label: "مه‌آلود", icon: "🌫️" },
};
