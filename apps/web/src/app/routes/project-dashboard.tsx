import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  fetchProjectDashboardPack,
  figureTitleKey,
  type DashboardFigure,
} from "@/app/lib/api/dashboards";
import { PATHS } from "@/app/routeVars";
import { DashboardFigureGrid } from "@/components/dashboard/DashboardFigureGrid";
import { FigureDrillDrawer } from "@/components/dashboard/FigureDrillDrawer";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
function ProjectDashboardContent() {
  const { t } = useTranslation();
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard");

  const [drillFigure, setDrillFigure] = useState<DashboardFigure | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["project-dashboard-pack", projectId],
    queryFn: () => fetchProjectDashboardPack(projectId),
    enabled: canView && Boolean(projectId),
  });

  if (projectLoading) {
    return <LoadingSkeleton rows={8} />;
  }

  if (!project) {
    return <NotFoundState />;
  }

  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("dashboard.accessDeniedDescription")}
      />
    );
  }

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("dashboard.projectTitle") },
        ]}
      />
      <PageHeader
        title={t("dashboard.projectTitle")}
        subtitle={t("dashboard.projectSubtitle", {
          pack: data?.pack_id ?? "—",
          asOf: data?.as_of ?? "—",
        })}
      />

      {isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : isLoading ? (
        <LoadingSkeleton rows={10} />
      ) : (
        <div className="space-y-8" data-testid="project-role-dashboard">
          {data?.groups.map((group) => (
            <section key={group.group_key}>
              <h2 className="mb-4 text-lg font-semibold">{group.title}</h2>
              <DashboardFigureGrid
                figures={group.figures}
                onFigureClick={(fig) => setDrillFigure(fig)}
              />
            </section>
          ))}
        </div>
      )}

      <FigureDrillDrawer
        projectId={projectId}
        figureKey={drillFigure?.figure_key ?? null}
        figureLabel={
          drillFigure
            ? t(figureTitleKey(drillFigure.figure_key), drillFigure.figure_key)
            : undefined
        }
        asOf={data?.as_of}
        isOpen={Boolean(drillFigure)}
        onClose={() => setDrillFigure(null)}
      />
    </main>
  );
}

export default function ProjectDashboardPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <ProjectDashboardContent />
    </ProjectProvider>
  );
}
