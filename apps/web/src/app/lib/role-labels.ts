import type { TFunction } from "i18next";

/**
 * Catalog of project role codes offered when creating a role.
 * Includes system defaults plus additional known role labels.
 */
export const AVAILABLE_PROJECT_ROLE_CODES = [
  "project_manager",
  "planning_engineer",
  "site_supervisor",
  "field_supervisor",
  "finance_manager",
  "procurement_officer",
  "document_controller",
  "viewer",
  "block_engineer",
  "technical_office",
  "workshop_supervisor",
  "ceo",
] as const;

export type AvailableProjectRoleCode =
  (typeof AVAILABLE_PROJECT_ROLE_CODES)[number];

/** Resolve a stored role code (auth group or project role) to a localized label. */
export function formatRoleLabel(roleName: string, t: TFunction): string {
  if (!roleName) return roleName;
  return t(`roleLabels.${roleName}`, { defaultValue: roleName });
}

/** Resolve a known system role description; falls back to API/DB text. */
export function formatRoleDescription(
  roleName: string,
  fallback: string,
  t: TFunction,
): string {
  if (!roleName) return fallback;
  return t(`roleDescriptions.${roleName}`, { defaultValue: fallback || "" });
}

export function formatRoleLabels(roleNames: string[], t: TFunction): string {
  return roleNames.map((name) => formatRoleLabel(name, t)).join(", ");
}
