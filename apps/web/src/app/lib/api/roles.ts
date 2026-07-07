import { apiJson } from "@/app/lib/api-client";

export interface PermissionCatalogItem {
  codename: string;
  label: string;
}

export interface ProjectRole {
  id: string;
  role_name: string;
  description: string;
  permissions: string[];
  is_system: boolean;
}

export function fetchPermissionCatalog() {
  return apiJson<PermissionCatalogItem[]>("/v1/permissions/");
}

export function fetchProjectRoles() {
  return apiJson<ProjectRole[]>("/v1/roles/");
}

export function fetchProjectRole(roleId: string) {
  return apiJson<ProjectRole>(`/v1/roles/${roleId}/`);
}

export function createProjectRole(payload: {
  role_name: string;
  description?: string;
  permissions?: string[];
}) {
  return apiJson<ProjectRole>("/v1/roles/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProjectRole(
  roleId: string,
  payload: { role_name?: string; description?: string },
) {
  return apiJson<ProjectRole>(`/v1/roles/${roleId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteProjectRole(roleId: string) {
  return apiJson<void>(`/v1/roles/${roleId}/`, { method: "DELETE" });
}

export function setProjectRolePermissions(roleId: string, permissions: string[]) {
  return apiJson<ProjectRole>(`/v1/roles/${roleId}/permissions/`, {
    method: "PUT",
    body: JSON.stringify({ permissions }),
  });
}

/** Group permission codenames by module prefix for UI display. */
export const PERMISSION_MODULE_ORDER = [
  "project",
  "wbs",
  "activities",
  "reports",
  "costs",
  "contracts",
  "ipcs",
  "cashflow",
  "documents",
  "dashboard",
] as const;

export function permissionModule(codename: string): string {
  if (codename.includes("wbs")) return "wbs";
  if (codename.includes("activit")) return "activities";
  if (codename.includes("report")) return "reports";
  if (codename.includes("cost")) return "costs";
  if (codename.includes("contract")) return "contracts";
  if (codename.includes("ipc")) return "ipcs";
  if (codename.includes("cashflow")) return "cashflow";
  if (codename.includes("document")) return "documents";
  if (codename.includes("dashboard")) return "dashboard";
  return "project";
}

export function groupPermissionsByModule(
  items: PermissionCatalogItem[],
): Record<string, PermissionCatalogItem[]> {
  const groups: Record<string, PermissionCatalogItem[]> = {};
  for (const item of items) {
    const mod = permissionModule(item.codename);
    if (!groups[mod]) groups[mod] = [];
    groups[mod].push(item);
  }
  return groups;
}
