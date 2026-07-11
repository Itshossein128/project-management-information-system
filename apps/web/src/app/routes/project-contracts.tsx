import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  CONTRACT_TYPE_LABELS,
  fetchContracts,
  formatFaAmount,
  IPC_STATUS_LABELS,
} from "@/app/lib/api/contracts";
import { fetchIPCs } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

type Tab = "contracts" | "ipcs";

function ContractsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");
  const [tab, setTab] = useState<Tab>("contracts");

  const { data: contracts, isLoading: cloading } = useQuery({
    queryKey: ["contracts", projectId],
    queryFn: () => fetchContracts(projectId),
    enabled: canView,
  });

  const { data: ipcs, isLoading: iloading } = useQuery({
    queryKey: ["ipcs", projectId],
    queryFn: () => fetchIPCs(projectId),
    enabled: canView && tab === "ipcs",
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) {
    return (
      <p className="rounded-lg border p-8 text-center text-muted-foreground">
        دسترسی به قراردادها ندارید.
      </p>
    );
  }

  const rows = contracts?.results ?? [];
  const overdueIpcs = (ipcs?.results ?? []).filter((i) => i.days_overdue != null).length;
  const mainTotal = rows.filter((c) => c.contract_type === "main").reduce((s, c) => s + c.effective_amount, 0);
  const subTotal = rows.filter((c) => c.contract_type === "subcontract").reduce((s, c) => s + c.effective_amount, 0);

  return (
    <div className="space-y-6">
      <PageHeader title="قراردادها" subtitle={project.project_name} />

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">قرارداد اصلی</p>
          <p className="text-lg font-semibold">{formatFaAmount(mainTotal)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">پیمانکاران فرعی</p>
          <p className="text-lg font-semibold">{formatFaAmount(subTotal)}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">IPC معوق</p>
          <p className="text-lg font-semibold text-red-600">{overdueIpcs}</p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">ضمانت‌نامه در شرف انقضا</p>
          <p className="text-lg font-semibold">
            {rows.filter((c) => c.guarantee_expiry_alert).length}
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <Button variant={tab === "contracts" ? "primary" : "secondary"} onClick={() => setTab("contracts")}>
          قراردادها
        </Button>
        <Button variant={tab === "ipcs" ? "primary" : "secondary"} onClick={() => setTab("ipcs")}>
          صدور موقت
        </Button>
      </div>

      {tab === "contracts" && (
        cloading ? <LoadingSkeleton rows={6} /> : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["شماره", "طرف مقابل", "نوع", "مبلغ", "وضعیت", "عملیات"].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id} className="border-t">
                    <td className="px-3 py-2">{c.contract_number || "—"}</td>
                    <td className="px-3 py-2">{c.counterparty}</td>
                    <td className="px-3 py-2">{CONTRACT_TYPE_LABELS[c.contract_type] ?? c.contract_type}</td>
                    <td className="px-3 py-2">{formatFaAmount(c.effective_amount)}</td>
                    <td className="px-3 py-2">{c.status}</td>
                    <td className="px-3 py-2">
                      <Link
                        className="text-primary underline"
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
      )}

      {tab === "ipcs" && (
        iloading ? <LoadingSkeleton rows={6} /> : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["شماره", "قرارداد", "ناخالص", "خالص", "وضعیت", "تأخیر"].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(ipcs?.results ?? []).map((i) => (
                  <tr key={i.id} className="border-t">
                    <td className="px-3 py-2">{i.ipc_number}</td>
                    <td className="px-3 py-2">{i.contract_number}</td>
                    <td className="px-3 py-2">{formatFaAmount(i.gross_amount)}</td>
                    <td className="px-3 py-2">{formatFaAmount(i.net_amount ?? 0)}</td>
                    <td className="px-3 py-2">{IPC_STATUS_LABELS[i.status] ?? i.status}</td>
                    <td className="px-3 py-2">
                      {i.days_overdue != null ? (
                        <span className="rounded bg-red-100 px-2 py-0.5 text-red-800">{i.days_overdue} روز</span>
                      ) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
}

export default function ProjectContractsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb items={[{ label: "پروژه‌ها", href: `/${PATHS.PROJECT}` }, { label: "قراردادها" }]} />
        <ContractsContent />
      </main>
    </ProjectProvider>
  );
}
