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
  return apiJson<{ relation_id: string }>(
    `/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/relations/`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export function deleteActivityRelation(projectId: string, activityId: string, relationId: string) {
  return apiJson<void>(
    `/${PATHS.API_PROJECTS}/${projectId}/activities/${activityId}/relations/${relationId}/`,
    { method: "DELETE" },
  );
}
