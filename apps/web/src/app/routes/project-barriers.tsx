import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { BarriersGrid } from "@/components/barriers/BarriersGrid";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";

function BarriersContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;
  return (
    <>
      <PageHeader title={t("pages.barriers.title")} subtitle={t("pages.barriers.subtitle")} />
      <BarriersGrid projectId={projectId} />
    </>
  );
}

export default function ProjectBarriersPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "موانع و مشکلات" },
          ]}
        />
        <BarriersContent />
      </ProjectProvider>
    </main>
  );
}
