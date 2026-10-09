import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

/* ---------- Working calendars ---------- */

export interface WorkingCalendar {
  id: string;
  name: string;
  is_default: boolean;
  work_monday: boolean;
  work_tuesday: boolean;
  work_wednesday: boolean;
  work_thursday: boolean;
  work_friday: boolean;
  work_saturday: boolean;
  work_sunday: boolean;
  created_at: string;
  updated_at: string;
}

export type WorkingCalendarPayload = Omit<
  WorkingCalendar,
  "id" | "created_at" | "updated_at"
>;

export function fetchWorkingCalendars(projectId: string) {
  return apiJson<WorkingCalendar[]>(`${base(projectId)}/working-calendars/`);
}

export function createWorkingCalendar(projectId: string, payload: Partial<WorkingCalendarPayload>) {
  return apiJson<WorkingCalendar>(`${base(projectId)}/working-calendars/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateWorkingCalendar(
  projectId: string,
  calendarId: string,
  payload: Partial<WorkingCalendarPayload>,
) {
  return apiJson<WorkingCalendar>(`${base(projectId)}/working-calendars/${calendarId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteWorkingCalendar(projectId: string, calendarId: string) {
  return apiJson<void>(`${base(projectId)}/working-calendars/${calendarId}/`, {
    method: "DELETE",
  });
}

export interface CalendarException {
  id: string;
  exception_date: string;
  is_working: boolean;
  name: string;
}

export function fetchCalendarExceptions(projectId: string, calendarId: string) {
  return apiJson<CalendarException[]>(
    `${base(projectId)}/working-calendars/${calendarId}/exceptions/`,
  );
}

export function createCalendarException(
  projectId: string,
  calendarId: string,
  payload: { exception_date: string; is_working: boolean; name?: string },
) {
  return apiJson<CalendarException>(
    `${base(projectId)}/working-calendars/${calendarId}/exceptions/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteCalendarException(
  projectId: string,
  calendarId: string,
  exceptionId: string,
) {
  return apiJson<void>(
    `${base(projectId)}/working-calendars/${calendarId}/exceptions/${exceptionId}/`,
    { method: "DELETE" },
  );
}

/* ---------- Baselines ---------- */

export interface BaselineSchedule {
  id: string;
  version_name: string;
  is_current: boolean;
  is_locked: boolean;
  approved_at: string | null;
  approved_by: string | null;
  locked_at: string | null;
  locked_by: string | null;
  source_change_request_id: string | null;
}

export function fetchBaselines(projectId: string) {
  return apiJson<BaselineSchedule[]>(`${base(projectId)}/baselines/`);
}

export function createBaseline(
  projectId: string,
  payload: { version_name?: string; make_current?: boolean } = {},
) {
  return apiJson<BaselineSchedule>(`${base(projectId)}/baselines/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveLockBaseline(projectId: string, baselineId: string) {
  return apiJson<BaselineSchedule>(
    `${base(projectId)}/baselines/${baselineId}/approve-lock/`,
    { method: "POST" },
  );
}

/* ---------- Schedule change requests ---------- */

export type ChangeRequestStatus = "draft" | "submitted" | "approved" | "rejected";

export interface ScheduleChangeItem {
  id?: string;
  activity_id: string;
  proposed_planned_start?: string | null;
  proposed_planned_finish?: string | null;
  proposed_duration_days?: number | null;
  proposed_forecast_start?: string | null;
  proposed_forecast_finish?: string | null;
  notes?: string;
}

export interface ScheduleChangeRequest {
  id: string;
  reason: string;
  milestone_impact: string;
  cost_impact: string;
  contract_impact: string;
  status: ChangeRequestStatus;
  base_baseline_id: string | null;
  resulting_baseline_id: string | null;
  created_by: string;
  submitted_at: string | null;
  decided_by: string | null;
  decided_at: string | null;
  decision_notes: string;
  items: ScheduleChangeItem[];
  created_at: string;
  updated_at: string;
}

export interface ScheduleChangeRequestPayload {
  reason?: string;
  milestone_impact?: string;
  cost_impact?: string;
  contract_impact?: string;
  items?: ScheduleChangeItem[];
}

export function fetchScheduleChangeRequests(projectId: string) {
  return apiJson<ScheduleChangeRequest[]>(`${base(projectId)}/schedule-change-requests/`);
}

export function fetchScheduleChangeRequest(projectId: string, requestId: string) {
  return apiJson<ScheduleChangeRequest>(
    `${base(projectId)}/schedule-change-requests/${requestId}/`,
  );
}

export function createScheduleChangeRequest(
  projectId: string,
  payload: ScheduleChangeRequestPayload,
) {
  return apiJson<ScheduleChangeRequest>(`${base(projectId)}/schedule-change-requests/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateScheduleChangeRequest(
  projectId: string,
  requestId: string,
  payload: ScheduleChangeRequestPayload,
) {
  return apiJson<ScheduleChangeRequest>(
    `${base(projectId)}/schedule-change-requests/${requestId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function submitScheduleChangeRequest(projectId: string, requestId: string) {
  return apiJson<ScheduleChangeRequest>(
    `${base(projectId)}/schedule-change-requests/${requestId}/submit/`,
    { method: "POST" },
  );
}

export function approveScheduleChangeRequest(
  projectId: string,
  requestId: string,
  decision_notes = "",
) {
  return apiJson<ScheduleChangeRequest>(
    `${base(projectId)}/schedule-change-requests/${requestId}/approve/`,
    {
      method: "POST",
      body: JSON.stringify({ decision_notes }),
    },
  );
}

export function rejectScheduleChangeRequest(
  projectId: string,
  requestId: string,
  decision_notes = "",
) {
  return apiJson<ScheduleChangeRequest>(
    `${base(projectId)}/schedule-change-requests/${requestId}/reject/`,
    {
      method: "POST",
      body: JSON.stringify({ decision_notes }),
    },
  );
}

/* ---------- Schedule status ---------- */

export interface CriticalPathValidity {
  valid: boolean;
  reason_codes: string[];
  message_key: string;
  critical_activity_ids: string[];
  near_critical_activity_ids: string[];
}

export interface ScheduleStatusMilestone {
  activity_id: string;
  activity_code: string;
  activity_name: string;
  planned_finish: string | null;
  forecast_finish: string | null;
  actual_finish: string | null;
  baseline_finish: string | null;
  delay_days: number | null;
}

export interface ScheduleStatusDelay {
  activity_id: string;
  activity_code: string;
  is_critical: boolean;
  is_near_critical: boolean;
  planned_finish: string | null;
  forecast_finish: string | null;
  baseline_finish: string | null;
  actual_finish: string | null;
  delay_days: number | null;
}

export interface ScheduleStatusReport {
  as_of: string;
  forecast_project_finish: string | null;
  date_sets: {
    approved_baseline_id: string | null;
    has_planned: boolean;
    has_actual: boolean;
    has_forecast: boolean;
  };
  critical_path: CriticalPathValidity;
  milestones: ScheduleStatusMilestone[];
  delays: ScheduleStatusDelay[];
}

export function fetchScheduleStatus(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${asOf}` : "";
  return apiJson<ScheduleStatusReport>(`${base(projectId)}/schedule-status/${qs}`);
}
