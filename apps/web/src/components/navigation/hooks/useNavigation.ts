import { useMemo } from "react";
import { useLocation } from "react-router";
import { buildBusinessNavItems } from "@/config/business-departments.config";
import { buildProjectNavItems } from "@/config/project-navigation.config";
import { mainSidebarNavigation } from "@/config/navigation.config";
import type { ROLES } from "@/config/roles";
import type { NavigationItem } from "@/types/navigation";

/** Matches `/projects/:uuid` and any sub-path (excludes `new`). */
const PROJECT_WITH_ID = /^\/projects\/([0-9a-f-]{36})(?:\/|$)/i;

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

  const projectId = pathname.match(PROJECT_WITH_ID)?.[1];

  return useMemo(() => {
    if (!projectId) return filtered;
    return [...filtered, ...buildProjectNavItems(projectId), ...buildBusinessNavItems(projectId)];
  }, [filtered, projectId]);
}
