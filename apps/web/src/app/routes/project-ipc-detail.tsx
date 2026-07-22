import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchIPC, formatFaAmount } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { IPCDeductionsTable } from "@/components/contracts/IPCDeductionsTable";
import { IPCLineItemsTable } from "@/components/contracts/IPCLineItemsTable";
import { IPCWorkflowBar } from "@/components/contracts/IPCWorkflowBar";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Button } from "@/components/ui/sprint-button";

function IPCDetailContent() {
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { ipcId = "" } = useParams();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);
  const canView = has("view_ipcs");
  const canEditIpc = has("edit_ipcs");
  const canApprove = has("approve_ipcs");

  const { data: ipc, isLoading } = useQuery({
    queryKey: ["ipc", projectId, ipcId],
    queryFn: () => fetchIPC(projectId, ipcId),
    enabled: canView && Boolean(ipcId),
  });

  const refresh = () => void qc.invalidateQueries({ queryKey: ["ipc", projectId, ipcId] });

  if (projectLoading || isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title="پروژه یافت نشد" />;
  if (!canView) {
    return (
      <AccessDenied description="برای مشاهده صورت‌وضعیت‌ها به مجوز مربوطه نیاز است." />
    );
  }
  if (!ipc) return <NotFoundState title="صدور موقت یافت نشد" />;

  const canEditLines = canEditIpc && ipc.status === "draft";

  return (
    <div className="space-y-6">
      <PageHeader
        title={`صدور موقت #${ipc.ipc_number}`}
        subtitle={`${ipc.contract_number} — ${project.project_name}`}
        actions={
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}`}>
            <Button variant="secondary">بازگشت به قراردادها</Button>
          </Link>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">مبلغ ناخالص</p>
          <p className="text-lg font-semibold">{formatFaAmount(ipc.gross_amount)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">کسورات</p>
          <p className="text-lg font-semibold">{formatFaAmount(ipc.deductions_total)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">خالص</p>
          <p className="text-lg font-semibold">
            {formatFaAmount(ipc.net_amount ?? ipc.net_amount_computed)}
          </p>
        </div>
      </div>

      <IPCWorkflowBar
        projectId={projectId}
        ipc={ipc}
        canEditIpc={canEditIpc}
        canApprove={canApprove}
        onUpdated={refresh}
      />

      <section className="space-y-2">
        <h2 className="text-lg font-medium">اقلام</h2>
        <IPCLineItemsTable
          projectId={projectId}
          ipc={ipc}
          canEdit={canEditLines}
          onUpdated={refresh}
        />
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-medium">کسورات</h2>
        <IPCDeductionsTable
          projectId={projectId}
          ipc={ipc}
          canEdit={canEditLines}
          onUpdated={refresh}
        />
      </section>
    </div>
  );
}

export default function ProjectIPCDetailPage() {
  const { projectId, ipcId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "قراردادها", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}` },
            { label: `IPC ${ipcId?.slice(0, 8) ?? ""}` },
          ]}
        />
        <IPCDetailContent />
      </main>
    </ProjectProvider>
  );
}
