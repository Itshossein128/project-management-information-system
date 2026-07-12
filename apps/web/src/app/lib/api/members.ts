import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

export interface ProjectMember {
  user_id: string | null;
  full_name: string;
  email: string;
  mobile: string;
  roles: string[];
  status: string;
  joined_at: string;
  last_login: string | null;
  invited_email?: string;
}

export interface Role {
  id: string;
  role_name: string;
  description: string;
  permissions: string[];
  is_system?: boolean;
}

export interface UserLookupResult {
  user_id: string;
  full_name: string;
  email: string;
  mobile: string;
}

export interface PermissionSummary {
  codename: string;
  label: string;
  granted: boolean | null;
}

export function fetchMembers(projectId: string) {
  return apiJson<ProjectMember[]>(`/${PATHS.API_PROJECTS}/${projectId}/members/`);
}

export function addMember(
  projectId: string,
  payload: { user_id?: string; email?: string; role_ids: string[] },
) {
  return apiJson<ProjectMember>(`/${PATHS.API_PROJECTS}/${projectId}/members/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateMember(
  projectId: string,
  userId: string,
  payload: { role_ids?: string[]; status?: string },
) {
  return apiJson<ProjectMember>(`/${PATHS.API_PROJECTS}/${projectId}/members/${userId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function fetchMemberPermissions(projectId: string, userId: string) {
  return apiJson<{ effective: Record<string, boolean | null>; permissions: PermissionSummary[] }>(
    `/${PATHS.API_PROJECTS}/${projectId}/members/${userId}/permissions/`,
  );
}

export function setMemberPermissionOverride(
  projectId: string,
  userId: string,
  payload: { permission_codename: string; is_granted: boolean },
) {
  return apiJson<{ effective: Record<string, boolean | null>; permissions: PermissionSummary[] }>(
    `/${PATHS.API_PROJECTS}/${projectId}/members/${userId}/permissions/`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export function clearMemberPermissionOverride(
  projectId: string,
  userId: string,
  permissionCodename: string,
) {
  return apiJson<{ effective: Record<string, boolean | null>; permissions: PermissionSummary[] }>(
    `/${PATHS.API_PROJECTS}/${projectId}/members/${userId}/permissions/?permission_codename=${encodeURIComponent(permissionCodename)}`,
    { method: "DELETE" },
  );
}

export function fetchRoles() {
  return apiJson<Role[]>("/v1/roles/");
}

export function lookupUsers(q: string) {
  return apiJson<UserLookupResult[]>(`/v1/users/lookup/?q=${encodeURIComponent(q)}`);
}
