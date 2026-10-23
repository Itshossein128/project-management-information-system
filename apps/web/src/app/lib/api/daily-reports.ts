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
  | "clear"
  | "cloudy"
  | "rainy"
  | "snowy"
  | "stormy";

export type InactivityReason =
  | "weather"
  | "holiday"
  | "strike_or_dispute"
  | "client_stop_order"
  | "safety_incident";

export type SiteStatus = "active" | "inactive";
export type ReportShift = "day" | "night" | "full";
export type RowShift = "shift_1" | "shift_2" | "shift_3";
export type LaborCategory = "indirect" | "direct";

export interface DailyReportListItem {
  report_id: string;
  report_date: string;
  day_of_week: string;
  work_front?: string;
  site_status: SiteStatus;
  site_status_label: string;
  weather_condition: WeatherCondition | null;
  weather_condition_label: string | null;
  status: ReportStatus;
  status_label: string;
  is_locked?: boolean;
  is_current?: boolean;
  version_number?: number;
  prepared_by_name: string | null;
  approved_by_name: string | null;
  activity_count: number;
  labor_total: number;
  equipment_count: number;
  has_incidents: boolean;
}

export interface CompletenessMeta {
  state: "configuration_incomplete" | "partial" | "complete";
  configuration_id: string | null;
  source_template: {
    id: string;
    name: string;
  } | null;
  expected_units: string[];
  contributing_units: string[];
  missing_units: string[];
}

export interface DerivedSourceItem {
  unit: string;
  report_id: string;
  report_version: number;
  source_row_kind: string;
  source_row_id: string;
  contribution_value: string | null;
  can_view_source: boolean;
}

export interface AggregationMeta {
  is_auto_summary: boolean;
  aggregated_at: string | null;
  is_partial: boolean;
  expected_disciplines?: string[];
  contributing_disciplines?: string[];
  missing_disciplines?: string[];
  completeness?: CompletenessMeta;
  weather_source: "derived" | "override";
  site_status_source: "derived" | "override";
}

export interface ActivityRow {
  id: string;
  activity_ref: string | null;
  activity_code?: string | null;
  activity_description: string;
  shift: RowShift;
  subcontractor_name: string;
  subcontractor_ref: string | null;
  contractor_ref?: string | null;
  contractor?: string | null;
  crew_name?: string;
  foreman_count?: number | null;
  worker_count?: number | null;
  headcount: number | null;
  parcel?: string | null;
  zone: string | null;
  block: string | null;
  floor: string | null;
  location?: string | null;
  location_detail: string | null;
  quantity: string | null;
  quantity_measured: boolean;
  unit: string | null;
  execution_percentage: string | null;
  responsible_user?: string | null;
  responsible_name?: string;
  notes: string;
  photo_file: string | null;
  source_discipline?: string;
  is_derived?: boolean;
  provenance?: DerivedSourceItem[];
}

export interface LaborUnitBreakdownItem {
  unit: string;
  report_id: string;
  report_version: number;
  source_row_id: string;
  present_count: number;
  leave_count?: number;
  overtime_hours?: string;
}

export interface LaborRow {
  id: string;
  labor_category: LaborCategory;
  job_title: string;
  custom_title: string;
  title_code?: string | null;
  display_order?: number;
  shift_1_count: number;
  shift_2_count: number;
  shift_3_count: number;
  total_count: number;
  present_count?: number;
  leave_count?: number;
  work_hours?: number | null;
  overtime_hours?: number | null;
  man_hours?: string | null;
  absence_count?: number | null;
  source_discipline?: string;
  is_derived?: boolean;
  source_set_complete?: boolean;
  source_count?: number;
  has_multiple_sources?: boolean;
  per_unit_breakdown?: LaborUnitBreakdownItem[];
  provenance?: DerivedSourceItem[];
}

export interface LaborCategoryTotals {
  present_count: number;
  leave_count: number;
  overtime_hours: string;
  man_hours: string;
}

export interface LaborSummaryPayload {
  indirect_summary: LaborRow[];
  direct_summary: LaborRow[];
  overall_summary: LaborRow[];
  totals: {
    indirect: LaborCategoryTotals;
    direct: LaborCategoryTotals;
    overall: LaborCategoryTotals;
  };
}

export interface EquipmentRow {
  id: string;
  equipment_name: string;
  equipment_ref: string;
  equipment?: string | null;
  shift: ReportShift;
  status: "active" | "standby" | "broken";
  ownership_type: "owned" | "rented";
  work_start: string | null;
  work_end: string | null;
  repair_hours: string;
  idle_hours?: string | null;
  idle_reason?: string;
  productive_hours: string | null;
  activity_ref: string | null;
  notes: string;
}

export interface MachinerySummaryRow {
  id: string;
  equipment_type: string;
  equipment_ref: string | null;
  equipment_code?: string | null;
  equipment_name?: string | null;
  status_total: number;
  status_active: number;
  status_ready: number;
  status_inactive: number;
  status_under_repair: number;
  operating_hours: string | null;
  stoppage_hours: string | null;
  repair_hours: string | null;
  stoppage_reason_code: string;
  stoppage_reason?: {
    code: string;
    label: string;
    label_fa: string;
  } | null;
  stoppage_reason_label?: string;
  stoppage_reason_label_fa?: string;
  source_discipline?: string;
  is_derived?: boolean;
  provenance?: DerivedSourceItem[];
}

export interface MachinerySummaryPayload {
  rows: MachinerySummaryRow[];
  vocabulary_revision_marker: string;
}

export type MaterialReconciliationStatus =
  | "match"
  | "mismatch"
  | "insufficient_data"
  | "";

export interface MaterialRow {
  id: string;
  material_ref: string | null;
  material_code?: string | null;
  material_name?: string | null;
  material_description: string;
  quantity: string;
  unit_cost: string | null;
  unit: string;
  transaction_type: "receipt" | "issue" | "waste" | "return";
  consumption_location?: string;
  supplier?: string;
  warehouse_document_reference?: string;
  receipt_resolved?: boolean;
  receipt_evidence?: "resolved" | "unresolved_reference" | null;
  reconciliation_status?: MaterialReconciliationStatus;
  reconciliation_document_id?: string;
  reconciliation_checked_at?: string | null;
  activity_ref: string | null;
  notes: string;
  source_discipline?: string;
  is_derived?: boolean;
  provenance?: DerivedSourceItem[];
}

export interface MaterialsSummaryPayload {
  main_table: MaterialRow[];
  details: MaterialRow[];
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
  source_discipline?: string;
  is_derived?: boolean;
  provenance?: DerivedSourceItem[];
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
  incident_type:
    | "safety"
    | "quality"
    | "environmental"
    | "stoppage"
    | "visitor"
    | "site_instruction"
    | "barrier";
  description: string;
  corrective_action: string;
  follow_up_owner_user?: string | null;
  follow_up_owner_name?: string;
  due_date?: string | null;
}

export interface DailyReportDetail {
  report_id: string;
  report_date: string;
  day_of_week: string;
  shift: ReportShift;
  work_front?: string;
  location_notes?: string;
  weather_condition: WeatherCondition | null;
  weather_condition_label: string | null;
  temp_max: string | null;
  temp_min: string | null;
  site_status: SiteStatus;
  site_status_label: string;
  inactivity_reason?: InactivityReason | null;
  inactivity_reason_label?: string | null;
  weather_impact_notes?: string;
  general_notes: string;
  management_opinion?: string;
  weather_override?: boolean;
  site_status_override?: boolean;
  is_auto_summary?: boolean;
  aggregated_at?: string | null;
  aggregation?: AggregationMeta;
  status: ReportStatus;
  status_label: string;
  is_locked?: boolean;
  status_label_key?: string;
  lineage_id?: string;
  version_number?: number;
  supersedes?: string | null;
  is_current?: boolean;
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
  labor_summary?: LaborSummaryPayload;
  equipment: EquipmentRow[];
  machinery_rows?: MachinerySummaryRow[];
  machinery?: MachinerySummaryPayload;
  materials: MaterialRow[];
  materials_summary?: MaterialsSummaryPayload;
  concrete_logs: ConcreteRow[];
  labor_camp: LaborCampRow[];
  incidents: IncidentRow[];
  submit_warnings?: string[];
}

export interface HeaderPayload {
  report_date: string;
  shift?: ReportShift;
  work_front?: string;
  location_notes?: string;
  weather_condition?: WeatherCondition | null;
  temp_max?: string | number | null;
  temp_min?: string | number | null;
  site_status?: SiteStatus;
  inactivity_reason?: InactivityReason | null;
  weather_impact_notes?: string;
  general_notes?: string;
  management_opinion?: string;
  weather_override?: boolean;
  site_status_override?: boolean;
  local_id?: string | null;
}

export interface CorrectionRequest {
  id: string;
  source_report_id: string;
  result_report_id: string | null;
  reason: string;
  status: string;
  requested_at: string | null;
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
  // Project daily reports are auto-summaries; prefer ensure-by-date.
  return ensureDailyReportByDate(projectId, payload.report_date);
}

export function ensureDailyReportByDate(projectId: string, date: string) {
  return apiJson<DailyReportDetail>(`${base(projectId)}/by-date/`, {
    method: "POST",
    body: JSON.stringify({ date, report_date: date }),
  });
}

export function fetchDailyReportByDate(projectId: string, date: string) {
  const q = new URLSearchParams({ date });
  return apiJson<DailyReportDetail>(`${base(projectId)}/by-date/?${q.toString()}`);
}

export const getDailyReportByDate = fetchDailyReportByDate;

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
    server_payload?: Record<string, unknown> | null;
    conflict_fields?: string[];
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
  submitted: "تأیید سرپرست / ارسال‌شده",
  under_review: "در حال بررسی",
  approved: "قفل‌شده",
  rejected: "رد شده",
};

export function openCorrectionRequest(projectId: string, reportId: string, reason: string) {
  return apiJson<CorrectionRequest>(`${base(projectId)}/${reportId}/correction-requests/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function fetchReportVersions(projectId: string, reportId: string) {
  return apiJson<
    Array<{
      report_id: string;
      version_number: number;
      is_current: boolean;
      status: ReportStatus;
      is_locked: boolean;
    }>
  >(`${base(projectId)}/${reportId}/versions/`);
}

export function fetchMaterialReconciliation(projectId: string, reportId: string) {
  return apiJson<{
    items: Array<{
      material_entry_id: string;
      status: "match" | "mismatch" | "insufficient_data";
      consumed_qty: string;
      available_balance: string | null;
    }>;
  }>(`${base(projectId)}/${reportId}/materials/reconciliation/`);
}

export const WEATHER_META: Record<WeatherCondition, { label: string; icon: string }> = {
  clear: { label: "آفتابی / صاف", icon: "☀️" },
  cloudy: { label: "ابری", icon: "☁️" },
  rainy: { label: "بارانی", icon: "🌧️" },
  snowy: { label: "برفی", icon: "❄️" },
  stormy: { label: "طوفانی / گرد و غبار", icon: "🌩️" },
};

export const INACTIVITY_REASONS: { value: InactivityReason; label: string }[] = [
  { value: "weather", label: "نامساعد بودن شرایط جوی" },
  { value: "holiday", label: "تعطیل رسمی / تقویمی" },
  { value: "strike_or_dispute", label: "اختلاف یا اعتصاب" },
  { value: "client_stop_order", label: "دستور توقف کارفرما / مشاور" },
  { value: "safety_incident", label: "حادثه ایمنی" },
];
