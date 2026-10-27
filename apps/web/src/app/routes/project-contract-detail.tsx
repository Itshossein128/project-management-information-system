import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  contractDetailToForm,
  ContractForm,
  formToContractPayload,
  type ContractFormValues,
} from "@/components/contracts/ContractForm";
import { fetchContract, updateContract } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { ChangeOrderPanel } from "@/components/contracts/ChangeOrderPanel";
import { ContractBoQGrid } from "@/components/contracts/ContractBoQGrid";
import { ContractSummaryCards } from "@/components/contracts/ContractSummaryCards";
import { IPCWizard } from "@/components/contracts/IPCWizard";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useProductTour } from "@/components/tour/useProductTour";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type Tab = "info" | "boq" | "changes";

function ContractDetailContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading: projectLoading } = useProject();
  const { contractId = "" } = useParams();
  const qc = useQueryClient();
  const toast = useToast();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");
  const canEdit = has("edit_contracts");
  const canEditIpc = has("edit_ipcs");
  const [tab, setTab] = useState<Tab>("info");
  const [editing, setEditing] = useState(false);
  const [values, setValues] = useState<ContractFormValues | null>(null);
  const [wizardOpen, setWizardOpen] = useState(false);

  const {
    data: contract,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["contract", projectId, contractId],
    queryFn: () => fetchContract(projectId, contractId),
    enabled: canView && Boolean(contractId),
  });

  const save = useMutation({
    mutationFn: () =>
      updateContract(projectId, contractId, formToContractPayload(values!)),
    onSuccess: () => {
      toast.success("قرارداد ذخیره شد");
      setEditing(false);
      void qc.invalidateQueries({
        queryKey: ["contract", projectId, contractId],
      });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (projectLoading || isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("pages.contracts.accessDeniedDescription", {
          defaultValue: "برای مشاهده قراردادها به مجوز مربوطه نیاز است.",
        })}
      />
    );
  }
  if (isError) return <QueryErrorState onRetry={() => void refetch()} />;
  if (!contract) return <NotFoundState title={t("pages.contracts.notFound", { defaultValue: "قرارداد یافت نشد" })} />;

  const startEdit = () => {
    setValues(contractDetailToForm(contract));
    setEditing(true);
  };

  const { startTour } = useProductTour({
    tourId: "project-contract-detail",
    steps: [
      {
        element: '[data-tour="contract-detail-header"]',
        popover: {
          title: t("tour.projectContractDetail.headerTitle", {
            defaultValue: "شناسنامه و اقدامات قرارداد",
          }),
          description: t("tour.projectContractDetail.headerDesc", {
            defaultValue:
              "شماره قرارداد، پروژه مربوطه و کلیدهای اقدام سریع مانند صدور موقت جدید یا ویرایش اطلاعات را مدیریت کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="contract-summary-cards"]',
        popover: {
          title: t("tour.projectContractDetail.summaryTitle", {
            defaultValue: "خلاصه وضعیت مالی",
          }),
          description: t("tour.projectContractDetail.summaryDesc", {
            defaultValue:
              "ارزش موثر، مبالغ ناخالص/خالص پرداخت‌شده، سپرده حسن انجام کار و وضعیت ضمانت‌نامه را مشاهده کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="contract-detail-tabs"]',
        popover: {
          title: t("tour.projectContractDetail.tabsTitle", {
            defaultValue: "تب‌های جزئیات قرارداد",
          }),
          description: t("tour.projectContractDetail.tabsDesc", {
            defaultValue:
              "بین اطلاعات شناسنامه‌ای، جدول فهرست بها (BoQ) و تغییر مقادیر/دستورکارها جابه‌جا شوید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="contract-info-tab"]',
        popover: {
          title: t("tour.projectContractDetail.infoTitle", {
            defaultValue: "اطلاعات شناسنامه‌ای و شرایط پیمان",
          }),
          description: t("tour.projectContractDetail.infoDesc", {
            defaultValue:
              "مشخصات پیمانکار، تاریخ‌های شروع/پایان، مبالغ اولیه و شرایط پرداخت را مشاهده یا ویرایش کنید.",
          }),
          side: "top",
        },
      },
      {
        element: '[data-tour="contract-issue-ipc"]',
        popover: {
          title: t("tour.projectContractDetail.issueIpcTitle", {
            defaultValue: "صدور موقت جدید",
          }),
          description: t("tour.projectContractDetail.issueIpcDesc", {
            defaultValue:
              "جهت ثبت صورت‌وضعیت کارکرد جدید برای این قرارداد، از wizard صدور موقت استفاده نمایید.",
          }),
          side: "bottom",
        },
      },
    ],
  });

  return (
    <div className='space-y-6'>
      <div data-tour='contract-detail-header'>
        <PageHeader
          title={contract.contract_number || contract.counterparty}
          subtitle={project.project_name}
          actions={
            <div className='flex flex-wrap gap-2 items-center'>
              <ProductTourButton onClick={startTour} />
              {canEditIpc ? (
                <Button
                  variant='primary'
                  onClick={() => setWizardOpen(true)}
                  data-tour='contract-issue-ipc'
                >
                  صدور موقت جدید
                </Button>
              ) : null}
              {canEdit && !editing ? (
                <Button variant='secondary' onClick={startEdit}>
                  ویرایش
                </Button>
              ) : null}
              <Link
                to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}`}
              >
                <Button variant='secondary'>بازگشت</Button>
              </Link>
            </div>
          }
        />
      </div>

      <div data-tour='contract-summary-cards'>
        <ContractSummaryCards contract={contract} />
      </div>

      <div className='flex flex-wrap gap-2' data-tour='contract-detail-tabs'>
        {(
          [
            ["info", "اطلاعات"],
            ["boq", "فهرست بها"],
            ["changes", "تغییر مقادیر"],
          ] as const
        ).map(([id, label]) => (
          <Button
            key={id}
            size='sm'
            variant={tab === id ? "primary" : "secondary"}
            onClick={() => setTab(id)}
          >
            {label}
          </Button>
        ))}
      </div>

      {tab === "info" && (
        <div className='space-y-4' data-tour='contract-info-tab'>
          {editing && values ? (
            <>
              <ContractForm
                values={values}
                onChange={(patch) => setValues({ ...values, ...patch })}
              />
              <div className='flex gap-2'>
                <Button
                  variant='primary'
                  loading={save.isPending}
                  onClick={() => save.mutate()}
                >
                  ذخیره
                </Button>
                <Button variant='secondary' onClick={() => setEditing(false)}>
                  انصراف
                </Button>
              </div>
            </>
          ) : (
            <ContractForm
              values={contractDetailToForm(contract)}
              onChange={() => {}}
              disabled
            />
          )}
        </div>
      )}

      {tab === "boq" && (
        <ContractBoQGrid
          projectId={projectId}
          contractId={contractId}
          items={contract.items}
          canEdit={canEdit}
          onSaved={() =>
            void qc.invalidateQueries({
              queryKey: ["contract", projectId, contractId],
            })
          }
        />
      )}

      {tab === "changes" && (
        <ChangeOrderPanel
          projectId={projectId}
          contractId={contractId}
          changeOrders={contract.change_orders}
          canEdit={canEdit}
          onChanged={() =>
            void qc.invalidateQueries({
              queryKey: ["contract", projectId, contractId],
            })
          }
        />
      )}

      <IPCWizard
        projectId={projectId}
        contract={contract}
        isOpen={wizardOpen}
        onClose={() => setWizardOpen(false)}
      />
    </div>
  );
}

export default function ProjectContractDetailPage() {
  const { t, i18n } = useTranslation();
  const { projectId, contractId } = useParams();
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
            { label: contractId?.slice(0, 8) ?? "جزئیات" },
          ]}
        />
        <ContractDetailContent />
      </main>
    </ProjectProvider>
  );
}
