import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useLocation } from "react-router";
import {
  listCapabilities,
  type ProjectCapability,
} from "@/app/lib/api/project-core";
import { buildBusinessNavItems } from "@/config/business-departments.config";
import { buildProjectNavItems } from "@/config/project-navigation.config";
import { mainSidebarNavigation } from "@/config/navigation.config";
import type { ROLES } from "@/config/roles";
import type { NavigationChildItem, NavigationItem } from "@/types/navigation";

/** Matches `/projects/:uuid` and any sub-path (excludes `new`). */
const PROJECT_WITH_ID = /^\/projects\/([0-9a-f-]{36})(?:\/|$)/i;

function isCapabilityDisabled(
  caps: ProjectCapability[] | undefined,
  capabilityKey: string | undefined,
): boolean {
  if (!capabilityKey || !caps?.length) return false;
  const row = caps.find((c) => c.capability_key === capabilityKey);
  if (!row) return false;
  return !row.enabled || row.mode === "disabled";
}

function filterNavByCapabilities(
  items: NavigationItem[],
  caps: ProjectCapability[] | undefined,
): NavigationItem[] {
  if (!caps?.length) return items;
  return items
    .map((item) => {
      if (!item.children?.length) return item;
      const children = item.children.filter(
        (child: NavigationChildItem) =>
          !isCapabilityDisabled(caps, child.capabilityKey),
      );
      if (children.length === 0) return null;
      return { ...item, children };
    })
    .filter((item): item is NavigationItem => item != null);
}

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

  const { data: capabilities } = useQuery({
    queryKey: ["project-capabilities", projectId],
    queryFn: () => listCapabilities(projectId!),
    enabled: Boolean(projectId),
    staleTime: 30_000,
  });

  return useMemo(() => {
    if (!projectId) return filtered;
    const projectItems = filterNavByCapabilities(
      buildProjectNavItems(projectId),
      capabilities,
    );
    return [...filtered, ...projectItems, ...buildBusinessNavItems(projectId)];
  }, [filtered, projectId, capabilities]);
}
