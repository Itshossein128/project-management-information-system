import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { BarriersGrid } from "@/components/barriers/BarriersGrid";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";

function BarriersContent() {
  const { projectId, project, isLoading } = useProject();
  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  return (
    <>
      <PageHeader title='موانع و مشکلات' subtitle='ثبت و پیگیری موانع پروژه' />
      <BarriersGrid projectId={projectId} />
    </>
  );
}

export default function ProjectBarriersPage() {
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
