import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import {
  approveIPC,
  downloadIPCPdf,
  formatFaAmount,
  IPC_STATUS_LABELS,
  payIPC,
  populateIPC,
  rejectIPC,
  submitIPC,
  type IPCDetail,
} from "@/app/lib/api/contracts";
import { JalaliDatePicker } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function IPCWorkflowBar({
  projectId,
  ipc,
  canEditIpc,
  canApprove,
  onUpdated,
}: {
  projectId: string;
  ipc: IPCDetail;
  canEditIpc: boolean;
  canApprove: boolean;
  onUpdated: () => void;
}) {
  const toast = useToast();
  const [payDate, setPayDate] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [showReject, setShowReject] = useState(false);

  const invalidate = () => onUpdated();

  const populate = useMutation({
    mutationFn: () => populateIPC(projectId, ipc.id),
    onSuccess: () => {
      toast.success("IPC از پیشرفت به‌روز شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const submit = useMutation({
    mutationFn: () => submitIPC(projectId, ipc.id),
    onSuccess: () => {
      toast.success("IPC ارسال شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approve = useMutation({
    mutationFn: () => approveIPC(projectId, ipc.id),
    onSuccess: () => {
      toast.success("IPC تأیید شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const pay = useMutation({
    mutationFn: () => payIPC(projectId, ipc.id, payDate || undefined),
    onSuccess: () => {
      toast.success("پرداخت ثبت شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const reject = useMutation({
    mutationFn: () => rejectIPC(projectId, ipc.id, rejectReason),
    onSuccess: () => {
      toast.success("IPC رد شد");
      setShowReject(false);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const pdf = useMutation({
    mutationFn: () => downloadIPCPdf(projectId, ipc.id),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ipc-${ipc.ipc_number}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4 rounded-lg border p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-muted-foreground">وضعیت</p>
          <p className="text-lg font-semibold">{IPC_STATUS_LABELS[ipc.status] ?? ipc.status}</p>
        </div>
        <div className="text-end">
          <p className="text-sm text-muted-foreground">خالص پرداختی</p>
          <p className="text-lg font-semibold">{formatFaAmount(ipc.net_amount ?? ipc.net_amount_computed)}</p>
        </div>
      </div>

      {ipc.rejection_reason ? (
        <p className="rounded bg-danger-50 px-3 py-2 text-sm text-danger-800 dark:bg-danger-950/40">
          دلیل رد: {ipc.rejection_reason}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" size="sm" loading={pdf.isPending} onClick={() => pdf.mutate()}>
          دانلود PDF
        </Button>
        {canEditIpc && ipc.status === "draft" ? (
          <>
            <Button variant="secondary" size="sm" loading={populate.isPending} onClick={() => populate.mutate()}>
              بازخوانی از پیشرفت
            </Button>
            <Button variant="primary" size="sm" loading={submit.isPending} onClick={() => submit.mutate()}>
              ارسال
            </Button>
          </>
        ) : null}
        {canApprove && ipc.status === "submitted" ? (
          <>
            <Button variant="primary" size="sm" loading={approve.isPending} onClick={() => approve.mutate()}>
              تأیید
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setShowReject((v) => !v)}>
              رد
            </Button>
          </>
        ) : null}
        {canApprove && ipc.status === "approved" ? (
          <>
            <JalaliDatePicker
              name="pay_date"
              label="تاریخ پرداخت"
              value={payDate}
              onChange={setPayDate}
            />
            <Button variant="primary" size="sm" loading={pay.isPending} onClick={() => pay.mutate()}>
              ثبت پرداخت
            </Button>
          </>
        ) : null}
      </div>

      {showReject ? (
        <div className="flex flex-wrap items-end gap-2">
          <input
            className="min-w-[200px] flex-1 rounded border px-3 py-2 text-sm"
            placeholder="دلیل رد"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
          />
          <Button variant="primary" size="sm" loading={reject.isPending} onClick={() => reject.mutate()}>
            تأیید رد
          </Button>
        </div>
      ) : null}
    </div>
  );
}
