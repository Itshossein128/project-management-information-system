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

/** Global destinations depend only on the user's roles, never on the page. */
export function useNavigation(roles: ROLES[] | undefined): NavigationItem[] {
  return useMemo(
    () => mainSidebarNavigation.filter((item) =>
      !item.roles || Boolean(roles?.some((role) => item.roles!.includes(role))),
    ),
    [roles],
  );
}

/** Contextual project tools are rendered outside the global sidebar. */
export function useProjectNavigation() {
  const { pathname } = useLocation();
  const projectId = pathname.match(PROJECT_WITH_ID)?.[1];
  const capabilities = useQuery({
    queryKey: ["project-capabilities", projectId],
    queryFn: () => listCapabilities(projectId!),
    enabled: Boolean(projectId),
    staleTime: 30_000,
  });
  const items = useMemo<NavigationItem[]>(() => {
    if (!projectId) return [];
    const projectItems = filterNavByCapabilities(buildProjectNavItems(projectId), capabilities.data);
    const departments = buildBusinessNavItems(projectId);
    return [
      ...projectItems.filter((item) => item.labelI18nKey !== "nav.projectAdmin"),
      {
        label: "Departments",
        labelI18nKey: "nav.departments",
        icon: "organization" as const,
        path: departments[0].path,
        children: departments.map(({ label, labelI18nKey, path }) => ({ label, labelI18nKey, path })),
      },
      ...projectItems.filter((item) => item.labelI18nKey === "nav.projectAdmin"),
    ];
  }, [projectId, capabilities.data]);
  return { projectId, items, capabilities };
}
