import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import type { ListResponse } from "@/app/lib/api-types";

export type ProjectCurrency = "IRR" | "IRT";

export type ProjectLifecycleStatus =
  | "draft"
  | "pending_approval"
  | "active"
  | "suspended"
  | "completed"
  | "archived"
  | "handed_over";

export interface ProjectListItem {
  project_id: string;
  project_code: string;
  project_name: string;
  employer: string;
  status: ProjectLifecycleStatus | string;
  start_date: string | null;
  planned_finish_date: string | null;
  contract_amount: string | null;
  member_count: number;
  currency?: ProjectCurrency;
  purpose?: string;
  scope_description?: string;
}

export interface ProjectDetail extends ProjectListItem {
  contractor: string;
  consultant: string;
  project_manager: string | null;
  location: string;
  contract_type: string;
  contract_number?: string;
  purpose?: string;
  scope_description?: string;
  main_deliverables?: string;
  owning_unit?: string | null;
  cut_off_date: string | null;
  budget_approved_at?: string | null;
  budget_approved_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  project_code: string;
  project_name: string;
  employer: string;
  contractor?: string;
  consultant?: string;
  contract_type?: string;
  contract_number?: string;
  purpose?: string;
  scope_description?: string;
  main_deliverables?: string;
  location?: string;
  start_date: string;
  planned_finish_date?: string;
  contract_amount?: string;
  currency?: ProjectCurrency;
  owning_unit?: string | null;
  project_manager?: string | null;
}

export interface KickoffCharter {
  id?: string;
  justification: string;
  success_criteria: string;
  constraints: string;
  assumptions: string;
  key_stakeholders_summary: string;
  pm_authority: string;
}

export interface ProjectChangeRequest {
  id: string;
  reason: string;
  status: string;
  proposed_changes: Record<string, unknown>;
  previous_values: Record<string, unknown>;
  requested_by: string;
  requested_at: string;
  decided_by: string | null;
  decided_at: string | null;
  decision_notes: string;
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export function fetchProjects(params?: { status?: string }) {
  const q = params?.status ? `?status=${encodeURIComponent(params.status)}` : "";
  return apiJson<ListResponse<ProjectListItem>>(`/${PATHS.API_PROJECTS}/${q}`);
}

export function fetchProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/`);
}

export function createProject(payload: CreateProjectPayload) {
  return apiJson<ProjectDetail>(`/${PATHS.API_PROJECTS}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProject(projectId: string, payload: Partial<CreateProjectPayload>) {
  return apiJson<ProjectDetail>(`${base(projectId)}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteProject(projectId: string) {
  return apiJson<void>(`${base(projectId)}/`, {
    method: "DELETE",
  });
}

export function submitProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/submit/`, { method: "POST" });
}

export function approveProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/approve/`, { method: "POST" });
}

export function rejectProject(projectId: string, reason = "") {
  return apiJson<ProjectDetail>(`${base(projectId)}/reject/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function suspendProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/suspend/`, { method: "POST" });
}

export function resumeProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/resume/`, { method: "POST" });
}

export function completeProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/complete/`, { method: "POST" });
}

export function archiveProject(projectId: string) {
  return apiJson<ProjectDetail>(`${base(projectId)}/archive/`, { method: "POST" });
}

export function fetchKickoffCharter(projectId: string) {
  return apiJson<KickoffCharter>(`${base(projectId)}/kickoff-charter/`);
}

export function saveKickoffCharter(projectId: string, payload: KickoffCharter) {
  return apiJson<KickoffCharter>(`${base(projectId)}/kickoff-charter/`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchProjectChangeRequests(projectId: string) {
  return apiJson<ProjectChangeRequest[]>(`${base(projectId)}/change-requests/`);
}

export function createProjectChangeRequest(
  projectId: string,
  reason: string,
  proposed_changes: Record<string, unknown>,
) {
  return apiJson<ProjectChangeRequest>(`${base(projectId)}/change-requests/`, {
    method: "POST",
    body: JSON.stringify({ reason, proposed_changes }),
  });
}

export function submitProjectChangeRequest(projectId: string, crId: string) {
  return apiJson<ProjectChangeRequest>(`${base(projectId)}/change-requests/${crId}/submit/`, {
    method: "POST",
  });
}

export function approveProjectChangeRequest(projectId: string, crId: string, decision_notes = "") {
  return apiJson<ProjectChangeRequest>(`${base(projectId)}/change-requests/${crId}/approve/`, {
    method: "POST",
    body: JSON.stringify({ decision_notes }),
  });
}

export function rejectProjectChangeRequest(projectId: string, crId: string, decision_notes = "") {
  return apiJson<ProjectChangeRequest>(`${base(projectId)}/change-requests/${crId}/reject/`, {
    method: "POST",
    body: JSON.stringify({ decision_notes }),
  });
}
