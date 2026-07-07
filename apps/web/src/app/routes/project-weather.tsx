import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { WeatherLogGrid } from "@/components/weather/weather-log-grid";

function WeatherPageContent() {
  const { projectId, project, isLoading } = useProject();

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  return (
    <>
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: project.project_name, href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}` },
          { label: "وضعیت جوی" },
        ]}
      />
      <PageHeader title="وضعیت جوی" subtitle="گزارش روزانه وضعیت آب‌وهوا و کارگاه" />
      <WeatherLogGrid projectId={projectId} />
    </>
  );
}

export default function ProjectWeatherPage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <WeatherPageContent />
      </ProjectProvider>
    </main>
  );
}
