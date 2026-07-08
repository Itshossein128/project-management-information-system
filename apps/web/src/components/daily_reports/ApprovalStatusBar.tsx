import { useState } from "react";
import { CheckCircle2, Clock, Send, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  type DailyReportDetail,
  STATUS_BADGE,
  STATUS_LABELS,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";

interface Props {
  report: DailyReportDetail;
  canApprove: boolean;
  busy?: boolean;
  onSubmit: () => void;
  onReview: () => void;
  onApprove: () => void;
  onReject: (reason: string) => void;
}

export function ApprovalStatusBar({
  report,
  canApprove,
  busy,
  onSubmit,
  onReview,
  onApprove,
  onReject,
}: Props) {
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const status = report.status;

  return (
    <div className="space-y-3 rounded-xl border border-border bg-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">وضعیت:</span>
          <Badge variant={STATUS_BADGE[status]} label={STATUS_LABELS[status]} />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {status === "draft" || status === "rejected" ? (
            <button
              type="button"
              disabled={busy}
              onClick={onSubmit}
              className="inline-flex items-center gap-1 rounded-md bg-primary px-4 py-1.5 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              <Send className="size-4" />
              ارسال برای تأیید
            </button>
          ) : null}
          {canApprove && status === "submitted" ? (
            <button
              type="button"
              disabled={busy}
              onClick={onReview}
              className="inline-flex items-center gap-1 rounded-md border border-border px-4 py-1.5 text-sm hover:bg-muted/40 disabled:opacity-50"
            >
              <Clock className="size-4" />
              شروع بررسی
            </button>
          ) : null}
          {canApprove && (status === "submitted" || status === "under_review") ? (
            <>
              <button
                type="button"
                disabled={busy}
                onClick={onApprove}
                className="inline-flex items-center gap-1 rounded-md bg-emerald-600 px-4 py-1.5 text-sm text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                <CheckCircle2 className="size-4" />
                تأیید
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => setRejecting((v) => !v)}
                className="inline-flex items-center gap-1 rounded-md bg-red-600 px-4 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                <XCircle className="size-4" />
                رد
              </button>
            </>
          ) : null}
        </div>
      </div>

      {rejecting ? (
        <div className="space-y-2 rounded-lg border border-red-300 bg-red-50 p-3 dark:bg-red-950/30">
          <textarea
            className="min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
            placeholder="دلیل رد را وارد کنید (حداقل ۱۰ کاراکتر)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setRejecting(false)}
              className="rounded-md border border-border px-3 py-1 text-sm"
            >
              انصراف
            </button>
            <button
              type="button"
              disabled={reason.trim().length < 10 || busy}
              onClick={() => onReject(reason.trim())}
              className="rounded-md bg-red-600 px-3 py-1 text-sm text-white disabled:opacity-50"
            >
              ثبت رد
            </button>
          </div>
        </div>
      ) : null}

      {status === "rejected" && report.rejection_reason ? (
        <p className="rounded-md bg-red-50 p-2 text-sm text-red-800 dark:bg-red-950/30 dark:text-red-200">
          دلیل رد: {report.rejection_reason}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
        {report.submitted_at ? (
          <span>ارسال: {formatDisplayDateTime(report.submitted_at)} — {report.submitted_by_name}</span>
        ) : null}
        {report.reviewed_at ? (
          <span>بررسی: {formatDisplayDateTime(report.reviewed_at)} — {report.reviewed_by_name}</span>
        ) : null}
        {report.approved_at ? (
          <span>تأیید: {formatDisplayDateTime(report.approved_at)} — {report.approved_by_name}</span>
        ) : null}
      </div>
    </div>
  );
}
