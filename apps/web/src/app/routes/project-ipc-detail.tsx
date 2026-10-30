import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import { fetchIPC, formatFaAmount } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { IPCCollectionsPanel } from "@/components/contracts/IPCCollectionsPanel";
import { IPCDeductionsTable } from "@/components/contracts/IPCDeductionsTable";
import { IPCLineItemsTable } from "@/components/contracts/IPCLineItemsTable";
import { IPCWorkflowBar } from "@/components/contracts/IPCWorkflowBar";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useProductTour } from "@/components/tour/useProductTour";
import { Button } from "@/components/ui/sprint-button";

function IPCDetailContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading: projectLoading } = useProject();
  const { ipcId = "" } = useParams();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);
  const canView = has("view_ipcs");
  const canEditIpc = has("edit_ipcs");
  const canApprove = has("approve_ipcs");

  const {
    data: ipc,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["ipc", projectId, ipcId],
    queryFn: () => fetchIPC(projectId, ipcId),
    enabled: canView && Boolean(ipcId),
  });

  const refresh = () =>
    void qc.invalidateQueries({ queryKey: ["ipc", projectId, ipcId] });

  if (projectLoading || isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("pages.ipc.accessDeniedDescription", {
          defaultValue: "برای مشاهده صورت‌وضعیت‌ها به مجوز مربوطه نیاز است.",
        })}
      />
    );
  }
  if (isError) return <QueryErrorState onRetry={() => void refetch()} />;
  if (!ipc) return <NotFoundState title={t("pages.ipc.notFound", { defaultValue: "صدور موقت یافت نشد" })} />;

  const canEditLines = canEditIpc && ipc.status === "draft";

  const { startTour } = useProductTour({
    tourId: "project-ipc-detail",
    steps: [
      {
        element: '[data-tour="ipc-detail-header"]',
        popover: {
          title: t("tour.projectIpcDetail.headerTitle", {
            defaultValue: "شناسنامه صورت‌وضعیت (IPC)",
          }),
          description: t("tour.projectIpcDetail.headerDesc", {
            defaultValue:
              "شماره صورت‌وضعیت، قرارداد مربوطه و بازگشت به لیست قراردادها را مدیریت کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="ipc-amounts-summary"]',
        popover: {
          title: t("tour.projectIpcDetail.amountsTitle", {
            defaultValue: "خلاصه مبالغ ناخالص، کسورات و خالص",
          }),
          description: t("tour.projectIpcDetail.amountsDesc", {
            defaultValue:
              "مبلغ ناخالص صورت‌وضعیت، مجموع کسورات قانونی و قراردادی و مبلغ خالص قابل پرداخت را مشاهده نمایید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="ipc-workflow-bar"]',
        popover: {
          title: t("tour.projectIpcDetail.workflowTitle", {
            defaultValue: "چرخه کار و وضعیت تأیید",
          }),
          description: t("tour.projectIpcDetail.workflowDesc", {
            defaultValue:
              "مراحل ثبت پیش‌نویس، ارسال برای بررسی، تأیید یا رد صورت‌وضعیت را کنترل و پیگیری کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="ipc-line-items-table"]',
        popover: {
          title: t("tour.projectIpcDetail.lineItemsTitle", {
            defaultValue: "جدول اقلام و مقادیر کارکرد",
          }),
          description: t("tour.projectIpcDetail.lineItemsDesc", {
            defaultValue:
              "اقلام ریز کارکرد، احجام، قیمت‌های واحد و مبالغ کل مربوط به این دوره را مشاهده یا ویرایش کنید.",
          }),
          side: "top",
        },
      },
      {
        element: '[data-tour="ipc-deductions-table"]',
        popover: {
          title: t("tour.projectIpcDetail.deductionsTitle", {
            defaultValue: "جدول کسورات قانونی و قراردادی",
          }),
          description: t("tour.projectIpcDetail.deductionsDesc", {
            defaultValue:
              "انواع کسورات از جمله پیش‌پرداخت، بیمه، مالیات و حسن انجام کار را ثبت و بازبینی کنید.",
          }),
          side: "top",
        },
      },
      {
        element: '[data-tour="ipc-collections-panel"]',
        popover: {
          title: t("tour.projectIpcDetail.collectionsTitle", {
            defaultValue: "پنل دریافتی‌ها و وصول مطالبات",
          }),
          description: t("tour.projectIpcDetail.collectionsDesc", {
            defaultValue:
              "تاریخچه‌ و تراکنش‌های وصول وجه پرداختی بابت این صورت‌وضعیت را ثبت و پیگیری نمایید.",
          }),
          side: "top",
        },
      },
    ],
  });

  return (
    <div className='space-y-6'>
      <div data-tour='ipc-detail-header'>
        <PageHeader
          title={`صدور موقت #${ipc.ipc_number}`}
          subtitle={`${ipc.contract_number} — ${project.project_name}`}
          actions={
            <div className='flex flex-wrap gap-2 items-center'>
              <ProductTourButton onClick={startTour} />
              <Link
                to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}`}
              >
                <Button variant='secondary'>بازگشت به قراردادها</Button>
              </Link>
            </div>
          }
        />
      </div>

      <div className='grid gap-4 md:grid-cols-3' data-tour='ipc-amounts-summary'>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>مبلغ ناخالص</p>
          <p className='text-lg font-semibold'>
            {formatFaAmount(ipc.gross_amount)}
          </p>
        </div>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>کسورات</p>
          <p className='text-lg font-semibold'>
            {formatFaAmount(ipc.deductions_total)}
          </p>
        </div>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>خالص</p>
          <p className='text-lg font-semibold'>
            {formatFaAmount(ipc.net_amount ?? ipc.net_amount_computed)}
          </p>
        </div>
      </div>

      <div data-tour='ipc-workflow-bar'>
        <IPCWorkflowBar
          projectId={projectId}
          ipc={ipc}
          canEditIpc={canEditIpc}
          canApprove={canApprove}
          onUpdated={refresh}
        />
      </div>

      <section className='space-y-2' data-tour='ipc-line-items-table'>
        <h2 className='text-lg font-medium'>اقلام</h2>
        <IPCLineItemsTable
          projectId={projectId}
          ipc={ipc}
          canEdit={canEditLines}
          onUpdated={refresh}
        />
      </section>

      <section className='space-y-2' data-tour='ipc-deductions-table'>
        <h2 className='text-lg font-medium'>کسورات</h2>
        <IPCDeductionsTable
          projectId={projectId}
          ipc={ipc}
          canEdit={canEditLines}
          onUpdated={refresh}
        />
      </section>

      <div data-tour='ipc-collections-panel'>
        <IPCCollectionsPanel
          projectId={projectId}
          ipcId={ipcId}
          canEdit={canEditIpc}
        />
      </div>
    </div>
  );
}

export default function ProjectIPCDetailPage() {
  const { t, i18n } = useTranslation();
  const { projectId, ipcId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className='page-main page-shell mx-auto  px-4 py-8'>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            {
              label: "قراردادها",
              href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}`,
            },
            { label: `IPC ${ipcId?.slice(0, 8) ?? ""}` },
          ]}
        />
        <IPCDetailContent />
      </main>
    </ProjectProvider>
  );
}
