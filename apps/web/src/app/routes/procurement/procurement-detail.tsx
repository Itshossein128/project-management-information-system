import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import {
  fetchRequisition,
  fetchApprovalLogs,
  submitRequisition,
  approveRequisition,
  rejectRequisition,
  returnRequisition,
  partialApprove,
  assignItems,
  holdRequisitionItem,
  type ApprovalLog,
} from "~/lib/api/procurement";
import { fetchMembers } from "@/app/lib/api/members";
import { PATHS } from "~/routeVars";
import { useToast } from "@/components/ui/toast";
import { Drawer } from "@/components/ui/drawer";
import { ProcurementWorkflowStepper } from "@/components/procurement/ProcurementWorkflowStepper";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";

function isTerminalStatus(status: string): boolean {
  return status === "approved" || status === "rejected";
}

function ApprovalLogEntry({ log }: { log: ApprovalLog }) {
  const { t } = useTranslation();
  const isCreate = log.action === "create";
  const isPartial = log.action === "partial_approve";
  const hasDetails = isPartial && log.details && log.details.length > 0;

  return (
    <div className="relative mb-4">
      <div
        className={`absolute -left-[21px] top-1 h-3 w-3 rounded-full ring-4 ring-background ${
          isPartial ? "bg-warning-500" : isCreate ? "bg-muted-foreground" : "bg-info-500"
        }`}
      />
      <div className="space-y-1">
        <p className="text-sm font-medium">
          {log.performed_by_name}{" "}
          <span className="font-normal text-muted-foreground">({log.action_display})</span>
        </p>
        {!isCreate ? (
          <p className="text-xs text-muted-foreground">
            {t("pages.procurement.approval.statusChange")}: {log.step_from_display} &rarr; {log.step_to_display}
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">{t("pages.procurement.approval.createEntry")}</p>
        )}
        <p className="text-xs text-muted-foreground">{formatDisplayDateTime(log.performed_at)}</p>
        {log.comments ? <p className="mt-1 rounded bg-muted p-2 text-sm">{log.comments}</p> : null}
        {hasDetails ? (
          <Collapsible>
            <CollapsibleTrigger className="mt-2 flex items-center gap-1 text-xs text-primary hover:underline [&[data-state=open]>svg]:rotate-180">
              <ChevronDown className="size-3 transition-transform" />
              {t("pages.procurement.approval.partialDetails", { count: log.details!.length })}
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 overflow-x-auto rounded border border-border text-xs">
                <table className="w-full text-start">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-2 py-1">{t("pages.procurement.approval.partialColLine")}</th>
                      <th className="px-2 py-1">{t("pages.procurement.approval.partialColMaterial")}</th>
                      <th className="px-2 py-1">{t("pages.procurement.approval.partialColRequested")}</th>
                      <th className="px-2 py-1">{t("pages.procurement.approval.partialColApproved")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {log.details!.map((d) => (
                      <tr key={d.item_id} className="border-t border-border">
                        <td className="px-2 py-1">{d.line_number}</td>
                        <td className="px-2 py-1">{d.material_code}</td>
                        <td className="px-2 py-1">{d.requested_qty}</td>
                        <td className="px-2 py-1 font-medium text-success-700">{d.approved_qty}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CollapsibleContent>
          </Collapsible>
        ) : null}
      </div>
    </div>
  );
}

function ProcurementDetailContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-detail",
    steps: [
      {
        element: "[data-tour='workflow-stepper']",
        popover: {
          title: t("tour.procurementDetail.step1Title"),
          description: t("tour.procurementDetail.step1Desc"),
        },
      },
      {
        element: "[data-tour='requisition-overview']",
        popover: {
          title: t("tour.procurementDetail.step2Title"),
          description: t("tour.procurementDetail.step2Desc"),
        },
      },
      {
        element: "[data-tour='approval-waiting']",
        popover: {
          title: t("tour.procurementDetail.step3Title"),
          description: t("tour.procurementDetail.step3Desc"),
        },
      },
      {
        element: "[data-tour='line-items-table']",
        popover: {
          title: t("tour.procurementDetail.step4Title"),
          description: t("tour.procurementDetail.step4Desc"),
        },
      },
      {
        element: "[data-tour='line-item-assign']",
        popover: {
          title: t("tour.procurementDetail.step8Title"),
          description: t("tour.procurementDetail.step8Desc"),
        },
      },
      {
        element: "[data-tour='line-item-partial']",
        popover: {
          title: t("tour.procurementDetail.step9Title"),
          description: t("tour.procurementDetail.step9Desc"),
        },
      },
      {
        element: "[data-tour='line-item-hold']",
        popover: {
          title: t("tour.procurementDetail.step10Title"),
          description: t("tour.procurementDetail.step10Desc"),
        },
      },
      {
        element: "[data-tour='approval-timeline']",
        popover: {
          title: t("tour.procurementDetail.step5Title"),
          description: t("tour.procurementDetail.step5Desc"),
        },
      },
      {
        element: "[data-tour='workshop-approval-hint']",
        popover: {
          title: t("tour.procurementDetail.step6Title"),
          description: t("tour.procurementDetail.step6Desc"),
        },
      },
      {
        element: "[data-tour='approval-actions']",
        popover: {
          title: t("tour.procurementDetail.step7Title"),
          description: t("tour.procurementDetail.step7Desc"),
        },
      },
    ],
  });

  const { projectId, project } = useProject();
  const { reqId } = useParams();
  const qc = useQueryClient();
  const toast = useToast();

  const [comment, setComment] = useState("");
  const [actionDrawer, setActionDrawer] = useState<"approve"|"reject"|"return"|null>(null);
  const [approvedDrafts, setApprovedDrafts] = useState<Record<string, string>>({});
  const [officerDrafts, setOfficerDrafts] = useState<Record<string, string>>({});

  const { data: req, isLoading } = useQuery({
    queryKey: ["requisition", projectId, reqId],
    queryFn: () => fetchRequisition(projectId, reqId!),
    enabled: !!reqId,
  });

  const { data: logs = [] } = useQuery({
    queryKey: ["approvalLogs", projectId, reqId],
    queryFn: () => fetchApprovalLogs(projectId, reqId!),
    enabled: !!reqId,
  });

  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  const actionMut = useMutation({
    mutationFn: async ({ action, msg }: { action: string, msg: string }) => {
      if (action === 'submit') return submitRequisition(projectId, reqId!, msg);
      if (action === 'approve') return approveRequisition(projectId, reqId!, msg);
      if (action === 'reject') return rejectRequisition(projectId, reqId!, msg);
      if (action === 'return') return returnRequisition(projectId, reqId!, msg);
    },
    onSuccess: () => {
      toast.success("عملیات با موفقیت انجام شد.");
      setActionDrawer(null);
      setComment("");
      void qc.invalidateQueries({ queryKey: ["requisition", projectId, reqId] });
      void qc.invalidateQueries({ queryKey: ["approvalLogs", projectId, reqId] });
    },
    onError: (e: any) => toast.error(e.message || "خطا در انجام عملیات"),
  });

  const handleAction = () => {
    if (actionDrawer) {
      actionMut.mutate({ action: actionDrawer, msg: comment });
    }
  };

  const partialMut = useMutation({
    mutationFn: (approvals: { item_id: string; approved_qty: number | null }[]) =>
      partialApprove(projectId, reqId!, approvals),
    onSuccess: () => {
      toast.success(t("pages.procurement.approval.partialSuccess"));
      void qc.invalidateQueries({ queryKey: ["requisition", projectId, reqId] });
      void qc.invalidateQueries({ queryKey: ["approvalLogs", projectId, reqId] });
    },
    onError: (e: Error) => toast.error(e.message || t("common.error")),
  });

  const assignMut = useMutation({
    mutationFn: (assignments: { item_id: string; assigned_to_id: string | null }[]) =>
      assignItems(projectId, reqId!, assignments),
    onSuccess: () => {
      toast.success(t("pages.procurement.approval.assignSuccess"));
      void qc.invalidateQueries({ queryKey: ["requisition", projectId, reqId] });
    },
    onError: (e: Error) => toast.error(e.message || t("common.error")),
  });

  const holdMut = useMutation({
    mutationFn: (itemId: string) => holdRequisitionItem(projectId, itemId),
    onSuccess: () => {
      toast.success(t("pages.procurement.approval.holdSuccess"));
      void qc.invalidateQueries({ queryKey: ["requisition", projectId, reqId] });
    },
    onError: (e: Error) => toast.error(e.message || t("common.error")),
  });

  useEffect(() => {
    if (!req?.items) return;
    const nextApproved: Record<string, string> = {};
    const nextOfficers: Record<string, string> = {};
    for (const item of req.items) {
      nextApproved[item.id] = item.approved_qty ?? item.requested_qty;
      nextOfficers[item.id] = item.assigned_to ?? "";
    }
    setApprovedDrafts(nextApproved);
    setOfficerDrafts(nextOfficers);
  }, [req]);

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!req || !project) return <p>یافت نشد</p>;

  // A simple representation of whether partial approval is allowed (in FINAL_APPROVAL)
  const canPartialApprove = req.status === "final_approval";
  const canAssignOfficers = req.status === "procurement_queue" || req.status === "hq_control_approval" || req.status === "final_approval" || req.status === "approved";
  const activeMembers = members.filter((m) => m.user_id && m.status === "active");

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <PageHeader
          title={`${t("pages.procurement.workshop.detailTitle")} ${req.requisition_number}`}
          subtitle={`${project.project_name} — ${
            req.scope === "workshop"
              ? t("pages.procurement.workshop.badgeWorkshop")
              : `${t("pages.procurement.workshop.blockColumn")} ${req.block_code}`
          }`}
        />
        <ProductTourButton onClick={startTour} />
      </div>

      {req.workflow_timeline && req.workflow_timeline.length > 0 ? (
        <div data-tour="workflow-stepper">
          <ProcurementWorkflowStepper timeline={req.workflow_timeline} scope={req.scope} status={req.status} />
        </div>
      ) : null}

      {!isTerminalStatus(req.status) && req.next_approver ? (
        <div
          className="rounded-lg border border-warning-200 bg-warning-50 p-4 dark:border-warning-900 dark:bg-warning-950/30"
          data-tour="approval-waiting"
        >
          <p className="text-sm font-medium text-warning-900 dark:text-warning-100">
            {t("pages.procurement.approval.waitingFor", { role: req.next_approver.role_label })}
          </p>
          {req.approval_summary?.workflow_step_label ? (
            <p className="mt-1 text-xs text-warning-800/80 dark:text-warning-200/80">
              {t("pages.procurement.approval.currentStep")}: {req.approval_summary.workflow_step_label}
            </p>
          ) : null}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-4 p-4 bg-muted/20 rounded-lg border border-border" data-tour="requisition-overview">
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">{t("pages.procurement.workshop.scopeColumn")}</p>
          <p className="font-medium">
            {req.scope === "workshop"
              ? t("pages.procurement.workshop.scopeWorkshop")
              : t("pages.procurement.workshop.scopeBlock")}
          </p>
        </div>
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">{t("pages.procurement.workshop.currentStatus")}</p>
          <p className="font-semibold text-info-700">{req.status_display}</p>
        </div>
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">نوع / اولویت</p>
          <p className="font-medium">{req.requisition_type_display} / {req.priority_display}</p>
        </div>
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">درخواست دهنده</p>
          <p className="font-medium">{req.requested_by_name}</p>
        </div>
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">تاریخ درخواست</p>
          <p className="font-medium">{req.request_date}</p>
        </div>
      </div>

      <div className="space-y-4" data-tour="line-items-table">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-lg font-medium">{t("pages.procurement.workshop.itemsTitle")}</h3>
          <div className="flex flex-wrap gap-2">
            {canAssignOfficers && (
              <Button
                variant="outline"
                size="sm"
                data-tour="line-item-assign"
                disabled={assignMut.isPending}
                onClick={() => {
                  const assignments = (req.items ?? []).map((item) => ({
                    item_id: item.id,
                    assigned_to_id: officerDrafts[item.id] || null,
                  }));
                  assignMut.mutate(assignments);
                }}
              >
                {t("pages.procurement.approval.saveAssignments")}
              </Button>
            )}
            {canPartialApprove && (
              <Button
                variant="outline"
                size="sm"
                data-tour="line-item-partial"
                disabled={partialMut.isPending}
                onClick={() => {
                  const approvals = (req.items ?? []).map((item) => {
                    const raw = approvedDrafts[item.id];
                    const qty = raw === "" ? null : Number(raw);
                    return { item_id: item.id, approved_qty: qty && qty > 0 ? qty : null };
                  });
                  partialMut.mutate(approvals);
                }}
              >
                {t("pages.procurement.approval.savePartial")}
              </Button>
            )}
          </div>
        </div>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm text-start">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.partialColLine")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.material")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.quantity")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.partialColApproved")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.colPurchased")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colStatus")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.approval.assignedOfficer")}</th>
                <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colActions")}</th>
              </tr>
            </thead>
            <tbody>
              {req.items?.map((item, itemIndex) => (
                <tr key={item.id} className="border-t border-border">
                  <td className="px-3 py-2">{item.line_number}</td>
                  <td className="px-3 py-2">
                    {item.material_code} — {item.material_name}
                  </td>
                  <td className="px-3 py-2">{item.requested_qty}</td>
                  <td className="px-3 py-2">
                    {canPartialApprove ? (
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="w-24 rounded-md border px-2 py-1"
                        value={approvedDrafts[item.id] ?? ""}
                        onChange={(e) =>
                          setApprovedDrafts((prev) => ({ ...prev, [item.id]: e.target.value }))
                        }
                      />
                    ) : (
                      <span className="font-medium text-success-700">{item.approved_qty || "-"}</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-info-700">{item.purchased_qty}</td>
                  <td className="px-3 py-2">{item.status_display}</td>
                  <td className="px-3 py-2">
                    {canAssignOfficers ? (
                      <select
                        className="min-w-40 rounded-md border px-2 py-1"
                        value={officerDrafts[item.id] ?? ""}
                        onChange={(e) =>
                          setOfficerDrafts((prev) => ({ ...prev, [item.id]: e.target.value }))
                        }
                      >
                        <option value="">{t("pages.procurement.approval.unassigned")}</option>
                        {activeMembers.map((member) => (
                          <option key={member.user_id!} value={member.user_id!}>
                            {member.full_name || member.email || member.user_id}
                          </option>
                        ))}
                      </select>
                    ) : (
                      item.assigned_to_name || "—"
                    )}
                  </td>
                  <td className="px-3 py-2">
                    {canPartialApprove ? (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={holdMut.isPending}
                        onClick={() => holdMut.mutate(item.id)}
                        {...(itemIndex === 0 ? { "data-tour": "line-item-hold" } : {})}
                      >
                        {t("pages.procurement.approval.onHold")}
                      </Button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {canPartialApprove ? (
          <p className="text-xs text-muted-foreground">{t("pages.procurement.approval.partialHint")}</p>
        ) : null}
      </div>

      <div className="space-y-4" data-tour="approval-timeline">
        <h3 className="text-lg font-medium">{t("pages.procurement.approval.timelineTitle")}</h3>
        {logs.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("pages.procurement.approval.timelineEmpty")}</p>
        ) : (
          <div className="space-y-2 border-l-2 border-border pl-4">
            {logs.map((log) => (
              <ApprovalLogEntry key={log.id} log={log} />
            ))}
          </div>
        )}
      </div>

        {req.scope === "workshop" && req.status === "technical_review" && (
          <div
            className="rounded-lg border border-info-200 bg-info-50 p-3 text-sm text-info-900"
            data-tour="workshop-approval-hint"
          >
            {t("pages.procurement.workshop.skipWorkshopApprovalHint")}
          </div>
        )}

      <div className="flex gap-4 border-t border-border pt-4" data-tour="approval-actions">
        {req.status === 'draft' && (
          <Button variant="default" onClick={() => actionMut.mutate({ action: 'submit', msg: '' })} disabled={actionMut.isPending}>
            ارسال برای بررسی فنی (Submit)
          </Button>
        )}
        {req.status !== 'draft' && req.status !== 'approved' && req.status !== 'rejected' && (
          <>
            <Button variant="default" onClick={() => setActionDrawer('approve')}>تایید (Approve)</Button>
            <Button variant="outline" onClick={() => setActionDrawer('return')}>بازگشت (Return)</Button>
            <Button variant="destructive" onClick={() => setActionDrawer('reject')}>رد (Reject)</Button>
          </>
        )}
      </div>

      <Drawer
        isOpen={!!actionDrawer}
        onClose={() => setActionDrawer(null)}
        title={
          actionDrawer === 'approve' ? 'تایید درخواست' :
          actionDrawer === 'reject' ? 'رد درخواست' : 'بازگشت به مرحله قبل'
        }
        footer={
          <Button variant={actionDrawer === 'reject' ? 'destructive' : 'default'} onClick={handleAction} disabled={actionMut.isPending}>
            ثبت عملیات
          </Button>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">در صورت نیاز توضیحات خود را برای این عملیات وارد کنید:</p>
          <textarea
            className="w-full rounded-md border p-3 text-sm"
            rows={4}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="یادداشت / دستور..."
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProcurementDetailPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: "جزئیات درخواست" },
          ]}
        />
        <ProcurementDetailContent />
      </main>
    </ProjectProvider>
  );
}
