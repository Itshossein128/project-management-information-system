import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { BarriersGrid } from "@/components/barriers/BarriersGrid";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { NotFoundState } from "@/components/layout/empty-state";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useProductTour } from "@/components/tour/useProductTour";

function BarriersContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();

  const { startTour } = useProductTour({
    tourId: "project-barriers",
    steps: [
      {
        element: "[data-tour='barriers-filters']",
        popover: {
          title: t("tour.projectBarriers.step1Title"),
          description: t("tour.projectBarriers.step1Desc"),
        },
      },
      {
        element: "[data-tour='barriers-add-button']",
        popover: {
          title: t("tour.projectBarriers.step2Title"),
          description: t("tour.projectBarriers.step2Desc"),
        },
      },
      {
        element: "[data-tour='barriers-table']",
        popover: {
          title: t("tour.projectBarriers.step3Title"),
          description: t("tour.projectBarriers.step3Desc"),
        },
      },
      {
        element: "[data-tour='barriers-resolve']",
        popover: {
          title: t("tour.projectBarriers.step4Title"),
          description: t("tour.projectBarriers.step4Desc"),
        },
      },
    ],
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  return (
    <>
      <PageHeader
        title={t("pages.barriers.title")}
        subtitle={t("pages.barriers.subtitle")}
        actions={<ProductTourButton onClick={startTour} />}
      />
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
