import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { usePermission } from "~/contexts/project-context";
import { 
  fetchRequisition, fetchApprovalLogs, 
  submitRequisition, approveRequisition, rejectRequisition, returnRequisition,
  partialApprove 
} from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { useToast } from "@/components/ui/toast";
import { Drawer } from "@/components/ui/drawer";

function ProcurementDetailContent() {
  const { t } = useTranslation();
  const { projectId, project } = useProject();
  const { reqId } = useParams();
  const qc = useQueryClient();
  const toast = useToast();
  const navigate = useNavigate();

  const [comment, setComment] = useState("");
  const [actionDrawer, setActionDrawer] = useState<"approve"|"reject"|"return"|null>(null);

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
    mutationFn: (approvals: any[]) => partialApprove(projectId, reqId!, approvals),
    onSuccess: () => {
      toast.success("تایید جزئی ثبت شد.");
      void qc.invalidateQueries({ queryKey: ["requisition", projectId, reqId] });
    },
    onError: (e: any) => toast.error(e.message || "خطا"),
  });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!req || !project) return <p>یافت نشد</p>;

  // A simple representation of whether partial approval is allowed (in FINAL_APPROVAL)
  const canPartialApprove = req.status === "final_approval";

  return (
    <div className="space-y-8">
      <PageHeader 
        title={`درخواست ${req.requisition_number}`} 
        subtitle={`${project.project_name} — بلوک ${req.block_code}`} 
      />

      <div className="flex flex-wrap gap-4 p-4 bg-muted/20 rounded-lg border border-border">
        <div className="w-full md:w-auto md:flex-1 space-y-1">
          <p className="text-xs text-muted-foreground">وضعیت فعلی</p>
          <p className="font-semibold text-blue-700">{req.status_display}</p>
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

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">آیتم‌های درخواست</h3>
          {canPartialApprove && (
            <Button variant="outline" size="sm" onClick={() => {
              const approvals = req.items?.map((i: any) => ({ item_id: i.id, approved_qty: i.requested_qty })) || [];
              partialMut.mutate(approvals);
            }}>
              تایید کامل مقادیر
            </Button>
          )}
        </div>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm text-start">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-start">ردیف</th>
                <th className="px-3 py-2 text-start">کد متریال</th>
                <th className="px-3 py-2 text-start">نام متریال</th>
                <th className="px-3 py-2 text-start">مقدار درخواستی</th>
                <th className="px-3 py-2 text-start">تایید شده</th>
                <th className="px-3 py-2 text-start">خریداری شده</th>
                <th className="px-3 py-2 text-start">وضعیت آیتم</th>
                <th className="px-3 py-2 text-start">توضیحات</th>
              </tr>
            </thead>
            <tbody>
              {req.items?.map((item) => (
                <tr key={item.id} className="border-t border-border">
                  <td className="px-3 py-2">{item.line_number}</td>
                  <td className="px-3 py-2">{item.material_code}</td>
                  <td className="px-3 py-2">{item.material_name}</td>
                  <td className="px-3 py-2">{item.requested_qty}</td>
                  <td className="px-3 py-2 text-green-700 font-medium">{item.approved_qty || '-'}</td>
                  <td className="px-3 py-2 text-blue-700">{item.purchased_qty}</td>
                  <td className="px-3 py-2">{item.status_display}</td>
                  <td className="px-3 py-2">{item.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium">تاریخچه امضاها (Audit Trail)</h3>
        {logs.length === 0 ? (
          <p className="text-sm text-muted-foreground">هنوز هیچ عملیاتی ثبت نشده است.</p>
        ) : (
          <div className="space-y-2 pl-4 border-l-2 border-border">
            {logs.map((log) => (
              <div key={log.id} className="relative mb-4">
                <div className="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-blue-500 ring-4 ring-background" />
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {log.performed_by_name} <span className="font-normal text-muted-foreground">({log.action_display})</span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    تغییر وضعیت: {log.step_from_display} &rarr; {log.step_to_display}
                  </p>
                  <p className="text-xs text-muted-foreground">{new Date(log.performed_at).toLocaleString('fa-IR')}</p>
                  {log.comments && <p className="text-sm mt-1 bg-muted p-2 rounded">{log.comments}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-4 pt-4 border-t border-border">
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
