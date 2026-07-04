import { createContext, useContext, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProject, type ProjectDetail } from "@/app/lib/api/projects";
import { fetchMemberPermissions } from "@/app/lib/api/members";
import { useAuth } from "@/app/contexts/auth-context";

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

export function usePermission(projectId: string) {
  const { user } = useAuth();
  const userId = user?.id != null ? String(user.id) : undefined;

  const { data } = useQuery({
    queryKey: ["member-permissions", projectId, userId],
    queryFn: () => fetchMemberPermissions(projectId, userId!),
    enabled: Boolean(projectId && userId),
  });

  const has = (codename: string) => {
    if (!data?.effective) return false;
    return data.effective[codename] === true;
  };

  return { has, permissions: data?.permissions ?? [], effective: data?.effective ?? {} };
}
