import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { ActivitiesGrid } from "@/components/activities/activities-grid";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";

function ActivitiesPageContent() {
  const { projectId, project, isLoading } = useProject();

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  return (
    <>
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: project.project_name, href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}` },
          { label: "فعالیت‌ها" },
        ]}
      />
      <PageHeader title="فعالیت‌ها" subtitle="مدیریت فعالیت‌های زمان‌بندی پروژه" />
      <ActivitiesGrid projectId={projectId} />
    </>
  );
}

export default function ProjectActivitiesPage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <ActivitiesPageContent />
      </ProjectProvider>
    </main>
  );
}
