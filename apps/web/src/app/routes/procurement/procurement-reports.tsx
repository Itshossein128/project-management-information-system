import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import {
  fetchLiquidityReport,
  fetchMaterialDeviationReport,
  fetchAuditTrailReport,
  fetchRequisitions,
  type ApprovalLog,
  type RequisitionScope,
} from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";

function scopeLabel(scope: RequisitionScope | undefined, t: (key: string) => string): string {
  if (scope === "workshop") return t("pages.procurement.workshop.scopeWorkshop");
  if (scope === "block") return t("pages.procurement.workshop.scopeBlock");
  return "—";
}

function AuditLogTable({
  logs,
  projectId,
}: {
  logs: ApprovalLog[];
  projectId: string;
}) {
  const { t } = useTranslation();

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm text-start">
        <thead className="bg-muted/50">
          <tr>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColNumber")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColScope")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColFrom")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColTo")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColAction")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColUser")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColTime")}</th>
            <th className="px-3 py-2 text-start">{t("pages.procurement.approval.auditColComments")}</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-t border-border">
              <td className="px-3 py-2 font-medium">
                {log.requisition_number ? (
                  <Link
                    to={`/${PATHS.PROJECT}/${projectId}/procurement/req/${log.requisition}`}
                    className="text-primary hover:underline"
                  >
                    {log.requisition_number}
                  </Link>
                ) : (
                  "—"
                )}
              </td>
              <td className="px-3 py-2">{scopeLabel(log.requisition_scope, t)}</td>
              <td className="px-3 py-2">{log.step_from_display || "—"}</td>
              <td className="px-3 py-2">{log.step_to_display || "—"}</td>
              <td className="px-3 py-2">{log.action_display}</td>
              <td className="px-3 py-2">{log.performed_by_name}</td>
              <td className="px-3 py-2 whitespace-nowrap">{formatDisplayDateTime(log.performed_at)}</td>
              <td className="px-3 py-2 max-w-xs truncate" title={log.comments}>
                {log.comments || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportsDashboardContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-reports",
    steps: [
      {
        element: "[data-tour='reports-tabs']",
        popover: {
          title: t("tour.procurementReports.step1Title"),
          description: t("tour.procurementReports.step1Desc"),
        },
      },
      {
        element: "[data-tour='reports-metrics']",
        popover: {
          title: t("tour.procurementReports.step2Title"),
          description: t("tour.procurementReports.step2Desc"),
        },
      },
    ],
  });

  const { projectId, project } = useProject();
  const [activeTab, setActiveTab] = useState("liquidity");
  const [requisitionFilter, setRequisitionFilter] = useState("");

  const { data: liquidity, isLoading: loadL } = useQuery({
    queryKey: ["reportLiquidity", projectId],
    queryFn: () => fetchLiquidityReport(projectId),
    enabled: activeTab === "liquidity",
  });

  const { data: deviation, isLoading: loadD } = useQuery({
    queryKey: ["reportDeviation", projectId],
    queryFn: () => fetchMaterialDeviationReport(projectId),
    enabled: activeTab === "deviation",
  });

  const { data: requisitions = [] } = useQuery({
    queryKey: ["procurement", projectId, "audit-filter"],
    queryFn: () => fetchRequisitions(projectId),
    enabled: activeTab === "audit",
  });

  const { data: audit, isLoading: loadA } = useQuery({
    queryKey: ["reportAudit", projectId, requisitionFilter],
    queryFn: () =>
      fetchAuditTrailReport(projectId, requisitionFilter ? { requisition_id: requisitionFilter } : undefined),
    enabled: activeTab === "audit",
  });

  const sortedLogs = useMemo(() => {
    const logs = audit?.logs ?? [];
    return [...logs].sort(
      (a, b) => new Date(b.performed_at).getTime() - new Date(a.performed_at).getTime(),
    );
  }, [audit?.logs]);

  if (!project) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader title={t("pages.procurement.approval.reportsTitle")} subtitle={project.project_name} />
        <ProductTourButton onClick={startTour} />
      </div>

      <div className="flex border-b border-border" data-tour="reports-tabs">
        {[
          { id: "liquidity", label: t("pages.procurement.approval.tabLiquidity") },
          { id: "deviation", label: t("pages.procurement.approval.tabDeviation") },
          { id: "audit", label: t("pages.procurement.approval.tabAudit") },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="pt-4" data-tour="reports-metrics">
        {activeTab === "liquidity" && (
          <div className="space-y-4">
            {loadL ? (
              <LoadingSkeleton rows={5} />
            ) : (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {liquidity?.liquidity_status?.map((b) => (
                  <div key={b.block_code} className="rounded-lg border border-border bg-card p-4">
                    <h4 className="mb-2 font-semibold">
                      {b.block_name} ({b.block_code})
                    </h4>
                    <div className="space-y-1 text-sm">
                      <p className="flex justify-between">
                        <span>{t("pages.procurement.approval.liquidityBudget")}</span>
                        <span>{b.budget}</span>
                      </p>
                      <p className="flex justify-between">
                        <span>{t("pages.procurement.approval.liquidityRequested")}</span>
                        <span>{b.total_requested_value}</span>
                      </p>
                      <p className="flex justify-between font-medium">
                        <span>{t("pages.procurement.approval.liquidityRemaining")}</span>
                        <span className={b.remaining_liquidity < 0 ? "text-danger-600" : "text-success-600"}>
                          {b.remaining_liquidity}
                        </span>
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "deviation" && (
          <div className="space-y-4">
            {loadD ? (
              <LoadingSkeleton rows={5} />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-border">
                <table className="w-full text-sm text-start">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColBlock")}</th>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColMaterial")}</th>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColEstimated")}</th>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColRequested")}</th>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColDelta")}</th>
                      <th className="px-3 py-2 text-start">{t("pages.procurement.approval.deviationColStatus")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deviation?.deviation_data?.map((d, idx) => (
                      <tr key={idx} className="border-t border-border">
                        <td className="px-3 py-2">{d.block_code}</td>
                        <td className="px-3 py-2">{d.material_name}</td>
                        <td className="px-3 py-2">{d.estimated_qty ?? "-"}</td>
                        <td className="px-3 py-2">{d.requested_qty}</td>
                        <td className="px-3 py-2" dir="ltr">
                          {d.deviation_qty}
                        </td>
                        <td className="px-3 py-2">
                          <span
                            className={`rounded px-2 py-1 text-xs ${
                              d.deviation_percent > 0 ? "bg-danger-100 text-danger-800" : "bg-success-100 text-success-800"
                            }`}
                          >
                            {d.deviation_percent > 0 ? "+" : ""}
                            {d.deviation_percent.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "audit" && (
          <div className="space-y-4">
            {loadA ? (
              <LoadingSkeleton rows={5} />
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
                  <div className="rounded-lg border border-border bg-card p-4">
                    <p className="text-sm text-muted-foreground">{t("pages.procurement.approval.auditTotal")}</p>
                    <p className="text-2xl font-bold">{audit?.summary?.total_actions ?? 0}</p>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <p className="text-sm text-muted-foreground">{t("pages.procurement.approval.auditApproved")}</p>
                    <p className="text-2xl font-bold text-success-600">{audit?.summary?.approved_actions ?? 0}</p>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <p className="text-sm text-muted-foreground">{t("pages.procurement.approval.auditRejected")}</p>
                    <p className="text-2xl font-bold text-danger-600">{audit?.summary?.rejected_actions ?? 0}</p>
                  </div>
                </div>

                <label className="flex max-w-xs flex-col gap-1 text-sm">
                  <span>{t("pages.procurement.approval.auditFilterRequisition")}</span>
                  <select
                    className="rounded-md border px-3 py-2"
                    value={requisitionFilter}
                    onChange={(e) => setRequisitionFilter(e.target.value)}
                  >
                    <option value="">{t("pages.procurement.approval.auditFilterAll")}</option>
                    {requisitions.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.requisition_number}
                      </option>
                    ))}
                  </select>
                </label>

                {sortedLogs.length === 0 ? (
                  <p className="py-8 text-center text-sm text-muted-foreground">
                    {t("pages.procurement.approval.auditEmpty")}
                  </p>
                ) : (
                  <AuditLogTable logs={sortedLogs} projectId={projectId} />
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProcurementReportsPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();

  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.procurement.title"), href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: t("pages.procurement.approval.reportsBreadcrumb") },
          ]}
        />
        <ReportsDashboardContent />
      </main>
    </ProjectProvider>
  );
}
