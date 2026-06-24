import { useMemo } from "react";
import { useLocation } from "react-router";
import { buildBusinessNavItems } from "@/config/business-departments.config";
import { mainSidebarNavigation } from "@/config/navigation.config";
import type { ROLES } from "@/config/roles";
import type { NavigationItem } from "@/types/navigation";

/** Matches `/businesses/:numericId` and any sub-path (excludes `create`, non-numeric ids). */
const BUSINESS_WITH_NUMERIC_ID = /^\/businesses\/(\d+)(?:\/|$)/;

export function useNavigation(roles: ROLES[] | undefined): NavigationItem[] {
  const { pathname } = useLocation();

  const filtered = useMemo(
    () =>
      mainSidebarNavigation.filter((item) => {
        if (!item.roles) return true;
        if (!roles) return false;

        return roles.some((role) => item.roles!.includes(role));
      }),
    [roles],
  );

  const businessId = pathname.match(BUSINESS_WITH_NUMERIC_ID)?.[1];

  return useMemo(() => {
    if (!businessId) return filtered;
    return [...filtered, ...buildBusinessNavItems(businessId)];
  }, [filtered, businessId]);
}
