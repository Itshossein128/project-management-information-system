import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Clock, History, Lock, Send, XCircle } from "lucide-react";
import { useNavigate } from "react-router";
import { Badge } from "@/components/ui/badge";
import {
  type DailyReportDetail,
  fetchReportVersions,
  openCorrectionRequest,
  STATUS_BADGE,
  STATUS_LABELS,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";
import { useToast } from "@/components/ui/toast";

interface Props {
  projectId: string;
  report: DailyReportDetail;
  canApprove: boolean;
  canEdit?: boolean;
  busy?: boolean;
  onSubmit: () => void;
  onReview: () => void;
  onApprove: () => void;
  onReject: (reason: string) => void;
}

export function ApprovalStatusBar({
  projectId,
  report,
  canApprove,
  canEdit,
  busy,
  onSubmit,
  onReview,
  onApprove,
  onReject,
}: Props) {
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [correcting, setCorrecting] = useState(false);
  const [correctionReason, setCorrectionReason] = useState("");
  const [correctionBusy, setCorrectionBusy] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  const status = report.status;
  const locked = report.is_locked || status === "approved";

  const versions = useQuery({
    queryKey: ["daily-report-versions", projectId, report.report_id],
    queryFn: () => fetchReportVersions(projectId, report.report_id),
    enabled: showVersions && Boolean(projectId && report.report_id),
  });

  return (
    <div className="space-y-3 rounded-xl border border-border bg-card p-4" data-testid="approval-status-bar">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">وضعیت:</span>
          <Badge
            variant={STATUS_BADGE[status]}
            label={STATUS_LABELS[status]}
            data-testid="report-status-badge"
          />
          {locked ? (
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Lock className="size-3" />
              قفل‌شده
            </span>
          ) : null}
          {report.version_number && report.version_number > 1 ? (
            <span className="text-xs text-muted-foreground">نسخه {report.version_number}</span>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {status === "draft" || status === "rejected" ? (
            <button
              type="button"
              disabled={busy}
              onClick={onSubmit}
              data-testid="report-submit-btn"
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
              data-testid="report-review-btn"
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
                data-testid="report-approve-btn"
                className="inline-flex items-center gap-1 rounded-md bg-success-600 px-4 py-1.5 text-sm text-white hover:bg-success-700 disabled:opacity-50"
              >
                <CheckCircle2 className="size-4" />
                قفل / تأیید
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => setRejecting((v) => !v)}
                data-testid="report-reject-btn"
                className="inline-flex items-center gap-1 rounded-md bg-danger-600 px-4 py-1.5 text-sm text-white hover:bg-danger-700 disabled:opacity-50"
              >
                <XCircle className="size-4" />
                رد
              </button>
            </>
          ) : null}
          {locked && canEdit && report.is_current !== false ? (
            <button
              type="button"
              disabled={busy || correctionBusy}
              onClick={() => setCorrecting((v) => !v)}
              data-testid="report-correction-btn"
              className="inline-flex items-center gap-1 rounded-md border border-border px-4 py-1.5 text-sm hover:bg-muted/40 disabled:opacity-50"
            >
              درخواست اصلاح
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => setShowVersions((v) => !v)}
            data-testid="report-versions-btn"
            className="inline-flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-sm hover:bg-muted/40"
          >
            <History className="size-4" />
            نسخه‌ها
          </button>
        </div>
      </div>

      {rejecting ? (
        <div className="space-y-2 rounded-lg border border-danger-300 bg-danger-50 p-3 dark:bg-danger-950/30">
          <textarea
            className="min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
            placeholder="دلیل رد را وارد کنید (حداقل ۱۰ کاراکتر)"
            value={reason}
            data-testid="report-reject-reason"
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
              data-testid="report-reject-confirm-btn"
              className="rounded-md bg-danger-600 px-3 py-1 text-sm text-white disabled:opacity-50"
            >
              ثبت رد
            </button>
          </div>
        </div>
      ) : null}

      {correcting ? (
        <div className="space-y-2 rounded-lg border border-border bg-muted/30 p-3">
          <textarea
            className="min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
            placeholder="دلیل درخواست اصلاح (حداقل ۱۰ کاراکتر)"
            value={correctionReason}
            data-testid="report-correction-reason"
            onChange={(e) => setCorrectionReason(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setCorrecting(false)}
              className="rounded-md border border-border px-3 py-1 text-sm"
            >
              انصراف
            </button>
            <button
              type="button"
              disabled={correctionReason.trim().length < 10 || correctionBusy}
              data-testid="report-correction-confirm-btn"
              className="rounded-md bg-primary px-3 py-1 text-sm text-primary-foreground disabled:opacity-50"
              onClick={async () => {
                setCorrectionBusy(true);
                try {
                  const corr = await openCorrectionRequest(
                    projectId,
                    report.report_id,
                    correctionReason.trim(),
                  );
                  toast.success("نسخه اصلاحی ایجاد شد");
                  if (corr.result_report_id) {
                    navigate(`/projects/${projectId}/daily-reports/${corr.result_report_id}/edit`);
                  }
                } catch (err) {
                  toast.error(err instanceof Error ? err.message : "خطا در درخواست اصلاح");
                } finally {
                  setCorrectionBusy(false);
                }
              }}
            >
              ثبت درخواست
            </button>
          </div>
        </div>
      ) : null}

      {status === "rejected" && report.rejection_reason ? (
        <p className="rounded-md bg-danger-50 p-2 text-sm text-danger-800 dark:bg-danger-950/30 dark:text-danger-200">
          دلیل رد: {report.rejection_reason}
        </p>
      ) : null}

      {showVersions ? (
        <div
          className="space-y-2 rounded-lg border border-border bg-muted/20 p-3 text-sm"
          data-testid="report-versions-panel"
        >
          <p className="font-medium">تاریخچه نسخه‌ها</p>
          {versions.isLoading ? (
            <p className="text-muted-foreground">در حال بارگذاری…</p>
          ) : versions.isError ? (
            <p className="text-danger-700">خطا در دریافت نسخه‌ها</p>
          ) : (versions.data?.length ?? 0) === 0 ? (
            <p className="text-muted-foreground">نسخه‌ای ثبت نشده است.</p>
          ) : (
            <ul className="space-y-1">
              {versions.data!.map((v) => {
                const isActive = v.report_id === report.report_id;
                return (
                  <li
                    key={v.report_id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded border border-border/60 bg-card px-2 py-1.5"
                  >
                    <span>
                      نسخه {v.version_number}
                      {v.is_current ? " (جاری)" : ""}
                      {" · "}
                      {STATUS_LABELS[v.status]}
                      {v.is_locked ? " · قفل" : ""}
                    </span>
                    {isActive ? (
                      <span className="text-xs text-muted-foreground">نسخه فعلی</span>
                    ) : (
                      <button
                        type="button"
                        className="rounded border border-border px-2 py-0.5 text-xs hover:bg-muted/40"
                        data-testid={`report-version-open-${v.version_number}`}
                        onClick={() =>
                          navigate(
                            `/projects/${projectId}/daily-reports/${v.report_id}/${
                              v.is_locked || v.status === "approved" ? "view" : "edit"
                            }`,
                          )
                        }
                      >
                        مشاهده
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
        <span>تاریخ گزارش: {report.report_date}</span>
        {report.created_at ? (
          <span>ثبت: {formatDisplayDateTime(report.created_at)}</span>
        ) : null}
        {report.submitted_at ? (
          <span>ارسال: {formatDisplayDateTime(report.submitted_at)} — {report.submitted_by_name}</span>
        ) : null}
        {report.reviewed_at ? (
          <span>بررسی: {formatDisplayDateTime(report.reviewed_at)} — {report.reviewed_by_name}</span>
        ) : null}
        {report.approved_at ? (
          <span>قفل: {formatDisplayDateTime(report.approved_at)} — {report.approved_by_name}</span>
        ) : null}
      </div>
    </div>
  );
}
