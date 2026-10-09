import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { ActivitiesGrid } from "@/components/activities/activities-grid";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { NotFoundState } from "@/components/layout/empty-state";
import { WorkingCalendarPanel } from "@/components/schedule/WorkingCalendarPanel";
import { WbsEmptyBanner } from "@/components/wbs/wbs-empty-banner";

function ActivitiesPageContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;

  return (
    <>
      <Breadcrumb
        items={[
          { label: t("nav.sidebarProjects"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("nav.projectActivities") },
        ]}
      />
      <PageHeader
        title={t("pages.activities.title")}
        subtitle={t("pages.activities.subtitle")}
      />
      <div className="mb-4">
        <WbsEmptyBanner projectId={projectId} />
      </div>
      <div className="mb-6">
        <WorkingCalendarPanel projectId={projectId} />
      </div>
      <ActivitiesGrid projectId={projectId} />
    </>
  );
}

export default function ProjectActivitiesPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <ActivitiesPageContent />
      </ProjectProvider>
    </main>
  );
}
