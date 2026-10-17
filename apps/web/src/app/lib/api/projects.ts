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
  can_resume_with_confirmation?: boolean;
  can_undo_completion?: boolean;
  can_view_status_undo_history?: boolean;
  suspension_event_id?: string | null;
  completion_event_id?: string | null;
  completed_from_status?: "active" | "suspended" | null;
  status_undo_remediation?: {operation:StatusUndoOperation;source_event_id:string;can_edit_manager:boolean;can_create_change_request:boolean} | null;
  can_restore_from_archive?: boolean;
  can_edit_manager_for_restore?: boolean;
  can_create_restore_remediation?: boolean;
  can_view_restore_history?: boolean;
  archived_from_status?: RestoreTarget|null;
  archive_cycle_id?: string|null;
  lifecycle_version?: number;
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
  restore_completion_event_id?: string | null;
  restore_archive_cycle_id?: string | null;
  restore_remediation_actions?: ("update"|"submit"|"approve"|"reject"|"cancel")[];
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

export function resumeProject(projectId: string, payload: StatusUndoPayload) {
  return apiJson<StatusUndoResult>(`${base(projectId)}/resume/`, { method: "POST", body: JSON.stringify(payload) });
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

export type RestoreTarget = "active" | "suspended" | "completed";
export interface RestorePreview {
  project_id: string; project_name: string; from_status: "archived"; to_status: RestoreTarget;
  archive_cycle_id: string; lifecycle_version: number; confirmation_token: string; can_confirm: boolean;
  missing: string[]; remediation: {field:string;action:"project_settings"|"project_change_request"}[];
}
export interface RestorePayload { request_id: string; confirmation_token: string; reason: string }
export interface RestoreReceipt {
  id:string;project_id:string;project_name:string;archive_cycle_id:string;request_id:string;
  actor:{id:string;display_name:string};restored_at:string;reason:string;from_status:"archived";to_status:RestoreTarget;
}
export interface RestoreResult {
  outcome:"restored"|"replayed";
  receipt:RestoreReceipt;
  current_project:{project_id:string;project_name:string;status:string;archive_cycle_id:string|null;lifecycle_version:number};
}
export function fetchRestorePreview(projectId:string) {
  return apiJson<RestorePreview>(`${base(projectId)}/restore-preview/`);
}
export function restoreProject(projectId:string,payload:RestorePayload) {
  return apiJson<RestoreResult>(`${base(projectId)}/restore/`,{method:"POST",body:JSON.stringify(payload)});
}
export function cancelProjectChangeRequest(projectId:string,crId:string) {
  return apiJson<ProjectChangeRequest>(`${base(projectId)}/change-requests/${crId}/cancel/`,{method:"POST"});
}
export interface RestoreAttemptResult {
  outcome:"completed"|"not_recorded";receipt:RestoreReceipt|null;current_project:RestoreResult["current_project"];
}
export function fetchRestoreAttempt(projectId:string,requestId:string) {
  return apiJson<RestoreAttemptResult>(`${base(projectId)}/restore-attempts/${requestId}/`);
}

export interface RestoreHistoryPage {
  count:number;next:string|null;previous:string|null;results:RestoreReceipt[];
}
export function fetchRestoreHistory(projectId:string,page=1) {
  return apiJson<RestoreHistoryPage>(`${base(projectId)}/restore-history/?page=${page}`);
}


export type StatusUndoOperation = "resume" | "undo_completion";
export interface StatusUndoPayload { request_id:string; confirmation_token:string; reason:string }
export interface StatusUndoPreview {
  project_id:string;project_name:string;operation:StatusUndoOperation;source_event_id:string;
  from_status:"suspended"|"completed";to_status:"active"|"suspended";lifecycle_version:number;
  confirmation_token:string;can_confirm:boolean;missing:string[];
  remediation:{field:string;action:"project_settings"|"project_change_request";can_perform:boolean}[];
}
export interface StatusUndoSource {
  id:string;kind:"suspend"|"complete";from_status:"active"|"suspended";to_status:"suspended"|"completed";
  occurred_at:string;actor:{id:string;display_name:string};project_name:string;
}
export interface StatusUndoReceipt {
  id:string;project_id:string;project_name:string;operation:StatusUndoOperation;source_event_id:string;request_id:string;
  actor:{id:string;display_name:string};performed_at:string;reason:string;
  from_status:"suspended"|"completed";to_status:"active"|"suspended";source_event:StatusUndoSource;
}
export interface StatusUndoCurrent {
  project_id:string;project_name:string;status:string;lifecycle_version:number;
  suspension_event_id:string|null;completion_event_id:string|null;completed_from_status:"active"|"suspended"|null;archive_cycle_id:string|null;
}
export interface StatusUndoResult { outcome:"applied"|"replayed";receipt:StatusUndoReceipt;current_project:StatusUndoCurrent }
export function fetchStatusUndoPreview(projectId:string,operation:StatusUndoOperation) {
  return apiJson<StatusUndoPreview>(`${base(projectId)}/${operation==="resume"?"resume-preview":"undo-completion-preview"}/`);
}
export function undoProjectCompletion(projectId:string,payload:StatusUndoPayload) {
  return apiJson<StatusUndoResult>(`${base(projectId)}/undo-completion/`,{method:"POST",body:JSON.stringify(payload)});
}
export function applyStatusUndo(projectId:string,operation:StatusUndoOperation,payload:StatusUndoPayload) {
  return operation==="resume"?resumeProject(projectId,payload):undoProjectCompletion(projectId,payload);
}

export interface StatusUndoAttemptResult {outcome:"completed"|"not_recorded";receipt:StatusUndoReceipt|null;current_project:StatusUndoCurrent}
export function fetchStatusUndoAttempt(projectId:string,operation:StatusUndoOperation,requestId:string) {
 return apiJson<StatusUndoAttemptResult>(`${base(projectId)}/status-undo-attempts/${operation}/${requestId}/`);
}

export interface StatusUndoHistoryPage {count:number;next:string|null;previous:string|null;results:StatusUndoReceipt[]}
export function fetchStatusUndoHistory(projectId:string,page=1) {
 return apiJson<StatusUndoHistoryPage>(`${base(projectId)}/status-undo-history/?page=${page}`);
}
