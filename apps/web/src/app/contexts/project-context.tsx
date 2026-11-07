import { createContext, useContext, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProject, type ProjectDetail } from "@/app/lib/api/projects";
import { fetchMemberPermissions, fetchMembers } from "@/app/lib/api/members";
import { useAuth } from "@/app/contexts/auth-context";
import { ApiRequestError } from "@/app/lib/api-client";
import { ROLES } from "@/config/roles";

interface ProjectContextValue {
  project: ProjectDetail | undefined;
  isLoading: boolean;
  projectId: string;
}

const ProjectContext = createContext<ProjectContextValue | null>(null);

export function ProjectProvider({
  projectId,
  children,
}: {
  projectId: string;
  children: React.ReactNode;
}) {
  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => fetchProject(projectId),
  });

  const value = useMemo(
    () => ({ project, isLoading, projectId }),
    [project, isLoading, projectId],
  );

  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>;
}

export function useProject() {
  const ctx = useContext(ProjectContext);
  if (!ctx) throw new Error("useProject must be used within ProjectProvider");
  return ctx;
}

const OBSERVATION_SENSITIVE = new Set([
  "view_wage",
  "view_sensitive_contacts",
  "view_person_contacts",
  "edit_wage",
]);

export function usePermission(projectId: string) {
  const { user } = useAuth();
  const userId = user?.id != null ? String(user.id) : undefined;
  const isObserver =
    user?.roles?.includes(ROLES.ADMIN) === true || user?.is_superuser === true;

  const { data: members } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
    enabled: Boolean(projectId && userId),
  });
  const membershipStatus = members?.find((m) => String(m.user_id) === userId)
    ?.status;
  const isActiveMember = membershipStatus === "active";

  const { data, error, isFetched } = useQuery({
    queryKey: ["member-permissions", projectId, userId],
    queryFn: () => fetchMemberPermissions(projectId, userId!),
    enabled: Boolean(projectId && userId && isActiveMember),
    retry: false,
  });

  const permissionFetchBlocked =
    error instanceof ApiRequestError && error.status === 404;
  const effectiveUnavailable =
    isActiveMember &&
    isFetched &&
    (permissionFetchBlocked || data === undefined);

  const has = (codename: string) => {
    if (!isActiveMember) {
      if (
        isObserver &&
        codename.startsWith("view_") &&
        !OBSERVATION_SENSITIVE.has(codename)
      ) {
        return true;
      }
      return false;
    }
    if (!isFetched) {
      return false;
    }
    if (effectiveUnavailable) {
      if (
        isObserver &&
        codename.startsWith("view_") &&
        !OBSERVATION_SENSITIVE.has(codename)
      ) {
        return true;
      }
      return false;
    }
    if (data?.effective?.[codename] === true) return true;
    // Assistive UI only: organizational observers may see general view_*
    // affordances without write/sensitive controls. Server remains authoritative.
    if (
      isObserver &&
      codename.startsWith("view_") &&
      !OBSERVATION_SENSITIVE.has(codename)
    ) {
      return true;
    }
    return false;
  };

  return {
    has,
    permissions: data?.permissions ?? [],
    effective: data?.effective ?? {},
    permissionFetchBlocked: Boolean(permissionFetchBlocked),
  };
}

/** Project mutations requiring active membership must not use retained grants
 * from an inactive member, including an organizational observer. */
export function useActiveProjectPermission(projectId: string) {
  const { user } = useAuth();
  const { has } = usePermission(projectId);
  const userId = user?.id != null ? String(user.id) : undefined;
  const { data: members } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
    enabled: Boolean(projectId && userId),
  });
  const isActiveMember = members?.some(
    (member) => String(member.user_id) === userId && member.status === "active",
  ) === true;
  return { has: (codename: string) => isActiveMember && has(codename) };
}
