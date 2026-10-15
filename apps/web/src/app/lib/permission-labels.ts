import type { TFunction } from "i18next";

/** Localize display text while keeping API permission codenames unchanged. */
export function formatPermissionLabel(
  codename: string,
  fallback: string,
  t: TFunction,
): string {
  return t(`permissionLabels.${codename}`, { defaultValue: fallback || codename });
}
