import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { usePermission } from "~/contexts/project-context";
import { fetchRequisitions, fetchBlocks, type RequisitionScope } from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { workflowProgressPercent } from "@/components/procurement/ProcurementWorkflowStepper";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";

function ScopeBadge({ scope }: { scope: RequisitionScope }) {
  const { t } = useTranslation();
  if (scope === "workshop") {
    return (
      <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-800">
        {t("pages.procurement.workshop.badge")}
      </span>
    );
  }
  return null;
}

function ProcurementListContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-list",
    steps: [
      {
        element: "[data-tour='list-filters']",
        popover: {
          title: t("tour.procurementList.step1Title"),
          description: t("tour.procurementList.step1Desc"),
        },
      },
      {
        element: "[data-tour='quick-actions']",
        popover: {
          title: t("tour.procurementList.step2Title"),
          description: t("tour.procurementList.step2Desc"),
        },
      },
      {
        element: "[data-tour='requisitions-results']",
        popover: {
          title: t("tour.procurementList.step3Title"),
          description: t("tour.procurementList.step3Desc"),
        },
      },
      {
        element: "[data-tour='requisition-row-actions']",
        popover: {
          title: t("tour.procurementList.step4Title"),
          description: t("tour.procurementList.step4Desc"),
        },
      },
      {
        element: "[data-tour='notification-bell']",
        popover: {
          title: t("tour.procurementList.step5Title"),
          description: t("tour.procurementList.step5Desc"),
          side: "bottom",
          align: "end",
        },
      },
    ],
  });

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_procurement");
  const canCreate = has("edit_reports");

  const [statusFilter, setStatusFilter] = useState("");
  const [blockFilter, setBlockFilter] = useState("");
  const [scopeFilter, setScopeFilter] = useState("");

  const { data: requisitions = [], isLoading: loadingReqs, isError, refetch } = useQuery({
    queryKey: ["procurement", projectId, statusFilter, blockFilter, scopeFilter],
    queryFn: () =>
      fetchRequisitions(projectId, {
        ...(statusFilter && { status: statusFilter }),
        ...(blockFilter && { block: blockFilter }),
        ...(scopeFilter && { scope: scopeFilter }),
      }),
    enabled: canView,
  });

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId, "standard"],
    queryFn: () => fetchBlocks(projectId, { standardOnly: true }),
    enabled: canView,
  });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>{t("project.notFound")}</p>;
  if (!canView) return <p className="p-8 text-center">{t("common.accessDenied")}</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
      <PageHeader title={t("pages.procurement.workshop.listTitle")} subtitle={project.project_name} />
      <ProductTourButton onClick={startTour} />
      </div>

      <div className="flex flex-wrap items-end gap-3" data-tour="list-filters">
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.workshop.filterScope")}</span>
          <select className="rounded-md border px-3 py-2" value={scopeFilter} onChange={(e) => setScopeFilter(e.target.value)}>
            <option value="">{t("pages.procurement.workshop.filterAll")}</option>
            <option value="block">{t("pages.procurement.workshop.scopeBlock")}</option>
            <option value="workshop">{t("pages.procurement.workshop.scopeWorkshop")}</option>
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.workshop.filterStatus")}</span>
          <select className="rounded-md border px-3 py-2" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">{t("pages.procurement.workshop.filterAll")}</option>
            <option value="draft">{t("pages.procurement.workshop.statusDraft")}</option>
            <option value="technical_review">{t("pages.procurement.workshop.statusTechnicalReview")}</option>
            <option value="workshop_approval">{t("pages.procurement.workshop.statusWorkshopApproval")}</option>
            <option value="control_check">{t("pages.procurement.workshop.statusControlCheck")}</option>
            <option value="pm_approval">{t("pages.procurement.workshop.statusPmApproval")}</option>
            <option value="procurement_queue">{t("pages.procurement.workshop.statusProcurementQueue")}</option>
            <option value="hq_control_approval">{t("pages.procurement.workshop.statusHqControl")}</option>
            <option value="final_approval">{t("pages.procurement.workshop.statusFinalApproval")}</option>
            <option value="approved">{t("pages.procurement.workshop.statusApproved")}</option>
            <option value="rejected">{t("pages.procurement.workshop.statusRejected")}</option>
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.workshop.filterBlock")}</span>
          <select className="rounded-md border px-3 py-2" value={blockFilter} onChange={(e) => setBlockFilter(e.target.value)}>
            <option value="">{t("pages.procurement.workshop.filterAll")}</option>
            {blocks.map((b) => (
              <option key={b.id} value={b.id}>
                {b.block_code} - {b.block_name}
              </option>
            ))}
          </select>
        </label>

        {canView && (
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_BLOCKS}`}>
            <Button variant="outline">{t("pages.procurement.blocks.manage")}</Button>
          </Link>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-3" data-tour="quick-actions">
          {canCreate && (
            <>
              <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_NEW}`}>
                <Button variant="default">{t("pages.procurement.workshop.newBlockRequest")}</Button>
              </Link>
              <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_NEW}?scope=workshop`}>
                <Button variant="outline">{t("pages.procurement.workshop.newWorkshopRequest")}</Button>
              </Link>
            </>
          )}

          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_OFFICER}`}>
            <Button variant="outline">{t("pages.procurement.workshop.officerDesk")}</Button>
          </Link>
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_INVENTORY}`}>
            <Button variant="outline">{t("pages.procurement.workshop.blockInventory")}</Button>
          </Link>
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_REPORTS}`}>
            <Button variant="outline">{t("pages.procurement.workshop.reports")}</Button>
          </Link>
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_TRANSFERS}`}>
            <Button variant="outline">{t("pages.procurement.transfers.nav")}</Button>
          </Link>
      </div>

      <div data-tour="requisitions-results">
        {loadingReqs ? (
          <LoadingSkeleton rows={8} />
        ) : isError ? (
          <QueryErrorState onRetry={() => void refetch()} />
        ) : requisitions.length === 0 ? (
          <p className="p-8 text-center text-muted-foreground">{t("pages.procurement.empty")}</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm text-start">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colNumber")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colScope")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colBlock")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colType")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colDate")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colItems")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colStatus")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.colProgress")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.colLastAction")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.colNextApprover")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colActions")}</th>
              </tr>
            </thead>
            <tbody>
              {requisitions.map((req) => (
                <tr key={req.id} className="border-t border-border">
                  <td className="px-3 py-2 font-medium">{req.requisition_number}</td>
                  <td className="px-3 py-2">
                    <ScopeBadge scope={req.scope} />
                    {req.scope === "block" && (
                      <span className="text-xs text-muted-foreground">{t("pages.procurement.workshop.scopeBlock")}</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    {req.scope === "workshop" ? t("pages.procurement.workshop.workshopBlockLabel") : req.block_code}
                  </td>
                  <td className="px-3 py-2">
                    <span className="flex flex-wrap items-center gap-1">
                      <span>{req.requisition_type_display}</span>
                      {req.requisition_type === "fast_track" ? (
                        <span className="rounded-full bg-danger-100 px-2 py-0.5 text-[10px] font-semibold text-danger-800">
                          {t("pages.procurement.workshop.fastTrackTag")}
                        </span>
                      ) : null}
                      {req.priority === "emergency" || req.requisition_type === "post_facto" ? (
                        <span className="rounded-full bg-warning-100 px-2 py-0.5 text-[10px] text-warning-800">
                          {t("pages.procurement.workshop.priorityEmergency")}
                        </span>
                      ) : null}
                    </span>
                  </td>
                  <td className="px-3 py-2">{req.request_date}</td>
                  <td className="px-3 py-2">{(req as any).item_count || 0}</td>
                  <td className="px-3 py-2">
                    <span className="rounded-full bg-info-100 px-2 py-1 text-xs text-info-800">{req.status_display}</span>
                  </td>
                  <td className="px-3 py-2">
                    {req.workflow_progress ? (
                      <div className="min-w-[5rem] space-y-1">
                        <span className="text-xs font-medium">{req.workflow_progress}</span>
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-primary transition-all"
                            style={{ width: `${workflowProgressPercent(req.workflow_progress)}%` }}
                          />
                        </div>
                        {req.workflow_step_label ? (
                          <p className="text-[10px] text-muted-foreground">{req.workflow_step_label}</p>
                        ) : null}
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    {req.last_action_display ? (
                      <div className="space-y-0.5">
                        <p className="text-xs font-medium">{req.last_action_display}</p>
                        {req.last_action_at ? (
                          <p className="text-[10px] text-muted-foreground">
                            {formatDisplayDateTime(req.last_action_at)}
                            {req.last_action_by_name ? ` — ${req.last_action_by_name}` : ""}
                          </p>
                        ) : null}
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    {req.next_approver_role_label ? (
                      <span className="text-xs">{req.next_approver_role_label}</span>
                    ) : (
                      <span className="text-xs text-muted-foreground">{t("pages.procurement.approval.noNextApprover")}</span>
                    )}
                  </td>
                  <td
                    className="px-3 py-2"
                    {...(req === requisitions[0] ? { "data-tour": "requisition-row-actions" } : {})}
                  >
                    <Link to={`/${PATHS.PROJECT}/${projectId}/procurement/req/${req.id}`}>
                      <Button size="sm" variant="outline">
                        {t("pages.procurement.workshop.view")}
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProcurementListPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();

  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.procurement.title") },
          ]}
        />
        <ProcurementListContent />
      </main>
    </ProjectProvider>
  );
}
