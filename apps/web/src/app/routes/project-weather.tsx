import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { WeatherLogGrid } from "@/components/weather/weather-log-grid";

function WeatherPageContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;

  return (
    <>
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: "وضعیت جوی" },
        ]}
      />
      <PageHeader
        title={t("pages.weather.title")}
        subtitle={t("pages.weather.subtitle")}
      />
      <WeatherLogGrid projectId={projectId} />
    </>
  );
}

export default function ProjectWeatherPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <WeatherPageContent />
      </ProjectProvider>
    </main>
  );
}
