import type { TFunction } from "i18next";

import { formatPermissionLabel } from "@/app/lib/permission-labels";
import { formatRoleLabel } from "@/app/lib/role-labels";

const MEMBER_STATUSES = new Set([
  "active",
  "inactive",
  "invited",
  "suspended",
  "archived",
]);

const ORIGINS = new Set(["role", "exception", "membership", "account", "event", "inherit", "grant", "deny"]);

export function formatAccessAction(action: string, t: TFunction): string {
  return t(`projectMembers.changeActions.${action}`, { defaultValue: action });
}

const HIDDEN_WHEN_NAMED: Record<string, string> = {
  role_ids: "role_names",
  position_ids: "position_names",
};

function formatLeaf(key: string, value: string, t: TFunction): string {
  if (key === "codename" || key === "permissions") {
    return formatPermissionLabel(value, value, t);
  }
  if (key === "role_name" || key === "role_names") {
    return formatRoleLabel(value, t);
  }
  if (key === "status" && MEMBER_STATUSES.has(value)) {
    return t(`projectMembers.statuses.${value}`);
  }
  if (key === "delivery_status") {
    return t(`projectMembers.delivery.${value}`, { defaultValue: value });
  }
  if ((key === "origin" || key === "effect") && ORIGINS.has(value)) {
    return t(`projectMembers.origins.${value}`, {
      defaultValue: t(`projectMembers.${value}`, { defaultValue: value }),
    });
  }
  if (key === "granted" || key === "exception") {
    if (value === "true") return t("projectMembers.grantedYes");
    if (value === "false") return t("projectMembers.grantedNo");
  }
  return value;
}

function formatAccessValue(key: string, value: unknown, t: TFunction): string {
  if (value === null || value === undefined || value === "") {
    return t("projectMembers.unknownValue");
  }
  if (typeof value === "boolean") {
    if (key === "granted" || key === "exception") return formatLeaf(key, String(value), t);
    return value ? t("common.yes") : t("common.no");
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    return value.map((item) => formatAccessValue(key === "permissions" ? "codename" : key, item, t)).join("، ");
  }
  if (typeof value === "object") {
    return formatAccessPayload(value as Record<string, unknown>, t);
  }
  return formatLeaf(key, String(value), t);
}

export function formatAccessPayload(
  value: Record<string, unknown> | null | undefined,
  t: TFunction,
): string {
  if (!value || Object.keys(value).length === 0) return "—";
  return Object.entries(value)
    .filter(([key]) => {
      const namedKey = HIDDEN_WHEN_NAMED[key];
      return !(namedKey && Object.prototype.hasOwnProperty.call(value, namedKey));
    })
    .map(([key, item]) => {
      const label = t(`projectMembers.historyFields.${key}`, { defaultValue: key });
      return `${label}: ${formatAccessValue(key, item, t)}`;
    })
    .join("؛ ");
}
