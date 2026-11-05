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
  project_id?: string | null;
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
  origin?: "inherit" | "grant" | "deny";
}

export function fetchMembers(projectId: string) {
  return apiJson<ProjectMember[]>(`/${PATHS.API_PROJECTS}/${projectId}/members/`);
}

export function addMember(
  projectId: string,
  payload: { user_id?: string; email?: string; role_ids: string[]; position_ids?: string[] },
) {
  return apiJson<ProjectMember>(`/${PATHS.API_PROJECTS}/${projectId}/members/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateMember(
  projectId: string,
  userId: string,
  payload: { role_ids?: string[]; status?: string; position_ids?: string[] },
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

export function fetchAssignableRoles(projectId: string) {
  return apiJson<Role[]>(`/${PATHS.API_PROJECTS}/${projectId}/roles/`);
}

export function fetchLocalRoleImpact(projectId: string, roleId: string) {
  return apiJson<{ assignment_count: number }>(
    `/${PATHS.API_PROJECTS}/${projectId}/roles/${roleId}/impact/`,
  );
}

export function setLocalRolePermissions(
  projectId: string,
  roleId: string,
  permissions: string[],
) {
  return apiJson<Role>(`/${PATHS.API_PROJECTS}/${projectId}/roles/${roleId}/permissions/`, {
    method: "PUT",
    body: JSON.stringify({ permissions }),
  });
}

export function deleteLocalRole(projectId: string, roleId: string) {
  return apiJson<void>(`/${PATHS.API_PROJECTS}/${projectId}/roles/${roleId}/`, {
    method: "DELETE",
  });
}

export function updateLocalRole(
  projectId: string,
  roleId: string,
  payload: { role_name?: string; description?: string },
) {
  return apiJson<Role>(`/${PATHS.API_PROJECTS}/${projectId}/roles/${roleId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function createLocalRole(
  projectId: string,
  payload: { role_name: string; description?: string },
) {
  return apiJson<Role>(`/${PATHS.API_PROJECTS}/${projectId}/roles/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface AccessChange {
  id: string;
  action: string;
  role_name: string;
  actor_name: string;
  subject_name: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  created_at: string;
}

export function fetchAccessChanges(projectId: string) {
  return apiJson<AccessChange[]>(`/${PATHS.API_PROJECTS}/${projectId}/access-changes/`);
}

export interface SelectablePosition {
  id: string;
  position_name: string;
  label?: string;
}

export function fetchSelectablePositions(projectId: string) {
  return apiJson<SelectablePosition[] | { results: SelectablePosition[] }>(
    `/${PATHS.API_PROJECTS}/${projectId}/positions/?selectable=1`,
  );
}

export function lookupUsers(q: string) {
  return apiJson<UserLookupResult[]>(`/v1/users/lookup/?q=${encodeURIComponent(q)}`);
}
