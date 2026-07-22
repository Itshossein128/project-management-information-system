import { useQuery } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  CONTRACT_TYPE_LABELS,
  fetchContracts,
  formatFaAmount,
  IPC_STATUS_LABELS,
} from "@/app/lib/api/contracts";
import { fetchIPCs } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";

type Tab = "contracts" | "ipcs";

function ContractsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");
  const canEdit = has("edit_contracts");
  const canViewIpcs = has("view_ipcs");
  const [tab, setTab] = useState<Tab>("contracts");

  const {
    data: contracts,
    isLoading: cloading,
    isError: cError,
    refetch: refetchContracts,
  } = useQuery({
    queryKey: ["contracts", projectId],
    queryFn: () => fetchContracts(projectId),
    enabled: canView,
  });

  const {
    data: ipcs,
    isLoading: iloading,
    isError: iError,
    refetch: refetchIpcs,
  } = useQuery({
    queryKey: ["ipcs", projectId],
    queryFn: () => fetchIPCs(projectId),
    enabled: canViewIpcs && tab === "ipcs",
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) {
    return <EmptyState title='پروژه یافت نشد' />;
  }
  if (!canView) {
    return (
      <EmptyState
        title='دسترسی ندارید'
        description='برای مشاهده قراردادها به مجوز مربوطه نیاز است.'
      />
    );
  }

  const rows = contracts?.results ?? [];
  const ipcRows = ipcs?.results ?? [];
  const overdueIpcs = ipcRows.filter((i) => i.days_overdue != null).length;
  const mainTotal = rows
    .filter((c) => c.contract_type === "main")
    .reduce((s, c) => s + c.effective_amount, 0);
  const subTotal = rows
    .filter((c) => c.contract_type === "subcontract")
    .reduce((s, c) => s + c.effective_amount, 0);

  const newContractHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}/${PATHS.PROJECT_NEW}`;

  return (
    <div className='space-y-6'>
      <PageHeader
        title='قراردادها'
        subtitle={project.project_name}
        actions={
          canEdit ? (
            <Link to={newContractHref}>
              <Button variant='primary'>قرارداد جدید</Button>
            </Link>
          ) : undefined
        }
      />

      <div className='grid gap-4 md:grid-cols-4'>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>قرارداد اصلی</p>
          <p className='text-lg font-semibold'>{formatFaAmount(mainTotal)}</p>
        </div>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>پیمانکاران فرعی</p>
          <p className='text-lg font-semibold'>{formatFaAmount(subTotal)}</p>
        </div>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>IPC معوق</p>
          <p className='text-lg font-semibold text-red-600'>{overdueIpcs}</p>
        </div>
        <div className='rounded-lg border p-4'>
          <p className='text-sm text-muted-foreground'>
            ضمانت‌نامه در شرف انقضا
          </p>
          <p className='text-lg font-semibold'>
            {rows.filter((c) => c.guarantee_expiry_alert).length}
          </p>
        </div>
      </div>

      <div className='flex gap-2' role='tablist' aria-label='بخش‌های قرارداد'>
        <Button
          role='tab'
          aria-selected={tab === "contracts"}
          variant={tab === "contracts" ? "primary" : "secondary"}
          onClick={() => setTab("contracts")}
        >
          قراردادها
        </Button>
        <Button
          role='tab'
          aria-selected={tab === "ipcs"}
          variant={tab === "ipcs" ? "primary" : "secondary"}
          onClick={() => setTab("ipcs")}
        >
          صدور موقت
        </Button>
      </div>

      {tab === "contracts" ? (
        cloading ? (
          <LoadingSkeleton rows={6} />
        ) : cError ? (
          <QueryErrorState onRetry={() => void refetchContracts()} />
        ) : rows.length === 0 ? (
          <EmptyState
            icon={<FileText />}
            title='قراردادی ثبت نشده'
            description='اولین قرارداد پروژه را ایجاد کنید.'
            action={
              canEdit ? (
                <Link to={newContractHref}>
                  <Button variant='primary'>قرارداد جدید</Button>
                </Link>
              ) : null
            }
          />
        ) : (
          <div className='overflow-x-auto rounded-lg border' role='tabpanel'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50'>
                <tr>
                  {["شماره", "طرف مقابل", "نوع", "مبلغ", "وضعیت", "عملیات"].map(
                    (h) => (
                      <th key={h} className='px-3 py-2 text-start'>
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id} className='border-t'>
                    <td className='px-3 py-2'>{c.contract_number || "—"}</td>
                    <td className='px-3 py-2'>{c.counterparty}</td>
                    <td className='px-3 py-2'>
                      {CONTRACT_TYPE_LABELS[c.contract_type] ?? c.contract_type}
                    </td>
                    <td className='px-3 py-2'>
                      {formatFaAmount(c.effective_amount)}
                    </td>
                    <td className='px-3 py-2'>{c.status}</td>
                    <td className='px-3 py-2'>
                      <Link
                        className='text-primary underline'
                        to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}/${c.id}`}
                      >
                        جزئیات
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : null}

      {tab === "ipcs" ? (
        !canViewIpcs ? (
          <EmptyState
            title='دسترسی ندارید'
            description='برای مشاهده صورت‌وضعیت‌ها به مجوز مربوطه نیاز است.'
          />
        ) : iloading ? (
          <LoadingSkeleton rows={6} />
        ) : iError ? (
          <QueryErrorState onRetry={() => void refetchIpcs()} />
        ) : ipcRows.length === 0 ? (
          <EmptyState
            icon={<FileText />}
            title='صورت‌وضعیتی ثبت نشده'
            description='صورت‌وضعیت‌ها پس از ثبت روی قراردادها اینجا نمایش داده می‌شوند.'
          />
        ) : (
          <div className='overflow-x-auto rounded-lg border' role='tabpanel'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50'>
                <tr>
                  {["شماره", "قرارداد", "ناخالص", "خالص", "وضعیت", "تأخیر"].map(
                    (h) => (
                      <th key={h} className='px-3 py-2 text-start'>
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {ipcRows.map((i) => (
                  <tr key={i.id} className='border-t'>
                    <td className='px-3 py-2'>
                      <Link
                        className='text-primary underline'
                        to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_IPCS}/${i.id}`}
                      >
                        {i.ipc_number}
                      </Link>
                    </td>
                    <td className='px-3 py-2'>{i.contract_number}</td>
                    <td className='px-3 py-2'>
                      {formatFaAmount(i.gross_amount)}
                    </td>
                    <td className='px-3 py-2'>
                      {formatFaAmount(i.net_amount ?? 0)}
                    </td>
                    <td className='px-3 py-2'>
                      {IPC_STATUS_LABELS[i.status] ?? i.status}
                    </td>
                    <td className='px-3 py-2'>
                      {i.days_overdue != null ? (
                        <span className='rounded bg-red-100 px-2 py-0.5 text-red-800'>
                          {i.days_overdue} روز
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : null}
    </div>
  );
}

export default function ProjectContractsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className='page-main page-shell mx-auto  px-4 py-8'>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "قراردادها" },
          ]}
        />
        <ContractsContent />
      </main>
    </ProjectProvider>
  );
}
