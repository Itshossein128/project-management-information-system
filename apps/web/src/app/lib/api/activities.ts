import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

export type ActivityStatus = "not_started" | "in_progress" | "suspended" | "completed";
export type RelationType = "FS" | "SS" | "FF" | "SF";

export interface ActivityLink {
  activity_id: string;
  activity_code: string;
  activity_name: string;
  relation_type: RelationType;
  lag_days: number;
}

export interface Activity {
  activity_id: string;
  activity_code: string;
  activity_name: string;
  unit_id: string | null;
  unit_name: string | null;
  total_quantity: string | null;
  weight: string | null;
  planned_start: string | null;
  planned_finish: string | null;
  actual_start: string | null;
  actual_finish: string | null;
  forecast_start: string | null;
  forecast_finish: string | null;
  duration_days: number | null;
  is_milestone: boolean;
  working_calendar_id: string | null;
  planned_duration: number | null;
  actual_duration: number | null;
  is_overdue: boolean;
  responsible_id: string | null;
  responsible_full_name: string | null;
  status: ActivityStatus;
  description: string;
  wbs_id: string;
  wbs_code: string;
  wbs_name: string;
  predecessor_count: number;
  successor_count: number;
  created_at: string;
  updated_at: string;
  predecessors?: ActivityLink[];
  successors?: ActivityLink[];
}

export interface PaginatedActivities {
  count: number;
  next: string | null;
  previous: string | null;
  results: Activity[];
}

export interface ActivityPayload {
  activity_code: string;
  activity_name: string;
  wbs_id: string;
  unit_id?: string | null;
  total_quantity?: number | string | null;
  weight?: number | null;
  planned_start?: string | null;
  planned_finish?: string | null;
  actual_start?: string | null;
  actual_finish?: string | null;
  forecast_start?: string | null;
  forecast_finish?: string | null;
  duration_days?: number | null;
  is_milestone?: boolean;
  working_calendar_id?: string | null;
  responsible_id?: string | null;
  status?: ActivityStatus;
  description?: string;
}

export interface WeightSummary {
  total_weight: number;
  remaining: number;
  is_balanced: boolean;
  warning: string | null;
}

export interface NetworkNode {
  id: string;
  code: string;
  name: string;
  status: ActivityStatus;
  planned_start: string | null;
  planned_finish: string | null;
  is_critical: boolean;
}

export interface NetworkEdge {
  from: string;
  to: string;
  relation_type: RelationType;
  lag_days: number;
}

export interface ActivityNetwork {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  critical_path?: {
    valid: boolean;
    reason_codes: string[];
    message_key: string | null;
    critical_activity_ids: string[];
    near_critical_activity_ids: string[];
  };
}

export interface ActivityListParams {
  page?: number;
  per_page?: number;
  wbs_id?: string;
  status?: ActivityStatus;
  responsible_id?: string;
  is_overdue?: boolean;
  search?: string;
  ordering?: string;
}

function buildQuery(params: ActivityListParams = {}) {
  const q = new URLSearchParams();
  if (params.page) q.set("page", String(params.page));
  if (params.per_page) q.set("per_page", String(params.per_page));
  if (params.wbs_id) q.set("wbs_id", params.wbs_id);
  if (params.status) q.set("status", params.status);
  if (params.responsible_id) q.set("responsible_id", params.responsible_id);
  if (params.is_overdue) q.set("is_overdue", "true");
  if (params.search) q.set("search", params.search);
  if (params.ordering) q.set("ordering", params.ordering);
  const s = q.toString();
  return s ? `?${s}` : "";
}

export function fetchActivities(projectId: string, params?: ActivityListParams) {
  return apiJson<PaginatedActivities>(
    `/${PATHS.API_PROJECTS}/${projectId}/activities/${buildQuery(params)}`,
  );
}

export function fetchActivity(projectId: string, activityId: string) {
  return apiJson<Activity>(`/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/`);
}

export function createActivity(projectId: string, payload: ActivityPayload) {
  return apiJson<Activity>(`/${PATHS.API_PROJECTS}/${projectId}/activities/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateActivity(projectId: string, activityId: string, payload: Partial<ActivityPayload>) {
  return apiJson<Activity>(`/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteActivity(projectId: string, activityId: string) {
  return apiJson<void>(`/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/`, {
    method: "DELETE",
  });
}

export function restoreActivity(projectId: string, activityId: string) {
  return apiJson<Activity>(
    `/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/restore/`,
    { method: "POST" },
  );
}

/** Build a create/update payload from a fetched activity (for undo). */
export function activityToPayload(activity: Activity): ActivityPayload {
  return {
    activity_code: activity.activity_code,
    activity_name: activity.activity_name,
    wbs_id: activity.wbs_id,
    unit_id: activity.unit_id,
    total_quantity: activity.total_quantity,
    weight:
      activity.weight != null && activity.weight !== ""
        ? parseFloat(activity.weight)
        : null,
    planned_start: activity.planned_start,
    planned_finish: activity.planned_finish,
    actual_start: activity.actual_start,
    actual_finish: activity.actual_finish,
    forecast_start: activity.forecast_start,
    forecast_finish: activity.forecast_finish,
    duration_days: activity.duration_days,
    is_milestone: activity.is_milestone,
    working_calendar_id: activity.working_calendar_id,
    responsible_id: activity.responsible_id,
    status: activity.status,
    description: activity.description ?? "",
  };
}

export function fetchWeightSummary(projectId: string) {
  return apiJson<WeightSummary>(`/${PATHS.API_PROJECTS}/${projectId}/activities/weight-summary/`);
}

export function fetchActivityNetwork(projectId: string) {
  return apiJson<ActivityNetwork>(`/${PATHS.API_PROJECTS}/${projectId}/activities/network/`);
}

export function createActivityRelation(
  projectId: string,
  activityId: string,
  payload: {
    role: "predecessor" | "successor";
    predecessor_id?: string;
    successor_id?: string;
    relation_type: RelationType;
    lag_days: number;
  },
) {
  return apiJson<{
    relation_id: string;
    activity_id: string;
    relation_type: RelationType;
    lag_days: number;
  }>(`/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/relations/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteActivityRelation(projectId: string, activityId: string, relationId: string) {
  return apiJson<void>(
    `/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/relations/${relationId}/`,
    { method: "DELETE" },
  );
}
