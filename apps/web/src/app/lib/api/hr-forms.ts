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

export function supervisorApproveOvertime(
  projectId: string,
  id: string,
  approved = true,
  notes = "",
) {
  return apiJson(`${base(projectId)}/overtime-requests/${id}/supervisor-approve/`, {
    method: "POST",
    body: JSON.stringify({ approved, notes }),
  });
}

export function managerApproveOvertime(
  projectId: string,
  id: string,
  approved = true,
  approvedHours?: number,
) {
  return apiJson(`${base(projectId)}/overtime-requests/${id}/manager-approve/`, {
    method: "POST",
    body: JSON.stringify({ approved, approved_hours: approvedHours }),
  });
}

export function fetchLeaveRequests(projectId: string, myOnly = false) {
  const qs = myOnly ? "?my_requests=true" : "";
  return apiJson<{ results: unknown[] }>(`${base(projectId)}/leave-requests/${qs}`);
}

export function createLeaveRequest(projectId: string, body: Record<string, unknown>) {
  return apiJson(`${base(projectId)}/leave-requests/`, { method: "POST", body: JSON.stringify(body) });
}

export function submitLeave(projectId: string, id: string) {
  return apiJson(`${base(projectId)}/leave-requests/${id}/submit/`, { method: "POST" });
}

export function supervisorApproveLeave(projectId: string, id: string, approved = true) {
  return apiJson(`${base(projectId)}/leave-requests/${id}/supervisor-approve/`, {
    method: "POST",
    body: JSON.stringify({ approved }),
  });
}

export function managerApproveLeave(projectId: string, id: string, approved = true) {
  return apiJson(`${base(projectId)}/leave-requests/${id}/manager-approve/`, {
    method: "POST",
    body: JSON.stringify({ approved }),
  });
}

export function securityApproveLeave(projectId: string, id: string, approved = true) {
  return apiJson(`${base(projectId)}/leave-requests/${id}/security-approve/`, {
    method: "POST",
    body: JSON.stringify({ approved }),
  });
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
