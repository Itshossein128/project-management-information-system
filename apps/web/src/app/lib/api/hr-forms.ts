import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export function fetchOvertimeRequests(projectId: string, myOnly = false) {
  const qs = myOnly ? "?my_requests=true" : "";
  return apiJson<{ results: unknown[] }>(`${base(projectId)}/overtime-requests/${qs}`);
}

export function createOvertimeRequest(projectId: string, body: Record<string, unknown>) {
  return apiJson(`${base(projectId)}/overtime-requests/`, { method: "POST", body: JSON.stringify(body) });
}

export function submitOvertime(projectId: string, id: string) {
  return apiJson(`${base(projectId)}/overtime-requests/${id}/submit/`, { method: "POST" });
}

export function fetchLeaveRequests(projectId: string, myOnly = false) {
  const qs = myOnly ? "?my_requests=true" : "";
  return apiJson<{ results: unknown[] }>(`${base(projectId)}/leave-requests/${qs}`);
}

export function createLeaveRequest(projectId: string, body: Record<string, unknown>) {
  return apiJson(`${base(projectId)}/leave-requests/`, { method: "POST", body: JSON.stringify(body) });
}

export function fetchSubReports(projectId: string, discipline: string) {
  return apiJson<{ results: unknown[] }>(`${base(projectId)}/sub-reports/?discipline=${discipline}`);
}

export function createSubReport(projectId: string, body: Record<string, unknown>) {
  return apiJson(`${base(projectId)}/sub-reports/`, { method: "POST", body: JSON.stringify(body) });
}

export function submitSubReport(projectId: string, id: string) {
  return apiJson(`${base(projectId)}/sub-reports/${id}/submit/`, { method: "POST" });
}
