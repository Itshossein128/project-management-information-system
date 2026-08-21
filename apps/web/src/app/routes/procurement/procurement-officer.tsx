import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { fetchProcurementStatusReport } from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";

function OfficerDashboardContent() {
  const { projectId, project, isLoading } = useProject();

  const { data: report, isLoading: loading, isError, refetch } = useQuery({
    queryKey: ["procurementStatus", projectId],
    queryFn: () => fetchProcurementStatusReport(projectId),
  });

  if (isLoading || loading) return <LoadingSkeleton rows={10} />;
  if (isError) return <QueryErrorState onRetry={() => void refetch()} />;
  if (!project) return null;

  const summaries = report?.summary || [];

  return (
    <div className="space-y-6">
      <PageHeader title="داشبورد کارپردازان" subtitle={project.project_name} />
      
      <p className="text-sm text-muted-foreground">وضعیت ردیف‌های تخصیص‌یافته به کارپردازان (Line-item Tracking)</p>

      {summaries.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground border border-border rounded-lg bg-card">
          هیچ آیتمی به کارپردازان تخصیص داده نشده است.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {summaries.map((s: any, idx: number) => (
            <div key={`${s.assigned_to}-${s.status}-${idx}`} className="bg-card border border-border rounded-lg p-5 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold">{s.assigned_to__first_name} {s.assigned_to__last_name}</h4>
                  <p className="text-xs text-muted-foreground mt-1">شناسه کاربری: {s.assigned_to}</p>
                </div>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
                  وضعیت آیتم: {s.status}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm bg-muted/30 p-3 rounded-md">
                <div>
                  <p className="text-muted-foreground text-xs mb-1">تعداد ردیف‌ها</p>
                  <p className="font-medium text-lg">{s.item_count}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs mb-1">مجموع درخواستی</p>
                  <p className="font-medium">{s.total_requested}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-muted-foreground text-xs mb-1">خریداری شده تا الان</p>
                  <p className="font-medium text-green-700">{s.total_purchased || 0}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ProcurementOfficerPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: "داشبورد کارپردازان" },
          ]}
        />
        <OfficerDashboardContent />
      </main>
    </ProjectProvider>
  );
}
