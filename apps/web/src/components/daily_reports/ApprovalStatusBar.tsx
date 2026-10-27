import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Clock, History, Lock, Send, XCircle } from "lucide-react";
import { useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  type DailyReportDetail,
  type ReportStatus,
  cancelCorrectionRequest,
  fetchCorrectionRequests,
  fetchReportVersions,
  openCorrectionRequest,
  STATUS_BADGE,
  STATUS_LABELS,
} from "@/app/lib/api/daily-reports";
import { formatLocaleDateTime } from "@/app/lib/jalali-utils";
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
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [correcting, setCorrecting] = useState(false);
  const [correctionReason, setCorrectionReason] = useState("");
  const [correctionBusy, setCorrectionBusy] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [confirmingCancellation, setConfirmingCancellation] = useState(false);
  const [cancellingCorrection, setCancellingCorrection] = useState(false);
  const [isCancelled, setIsCancelled] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  const status = report.status;
  const locked = report.is_locked || status === "approved";

  const getStatusLabel = (s: ReportStatus) => {
    return t(`status.${s}`, STATUS_LABELS[s] ?? s);
  };

  const versions = useQuery({
    queryKey: ["daily-report-versions", projectId, report.report_id],
    queryFn: () => fetchReportVersions(projectId, report.report_id),
    enabled: showVersions && Boolean(projectId && report.report_id),
  });
  const correctionRequests = useQuery({
    queryKey: ["daily-report-correction-requests", projectId, report.report_id],
    queryFn: () => fetchCorrectionRequests(projectId, report.report_id),
    enabled: Boolean(projectId && report.report_id && (report.version_number ?? 1) > 1 && !isCancelled),
  });
  const openCorrection = correctionRequests.data?.find(
    (item) =>
      item.result_report_id === report.report_id &&
      (item.status === "draft" || item.status === "submitted"),
  );

  return (
    <div className="space-y-3 rounded-xl border border-border bg-card p-4" data-testid="approval-status-bar">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{t("dailyReports.statusLabel")}</span>
          <Badge
            variant={STATUS_BADGE[status]}
            label={getStatusLabel(status)}
            data-testid="report-status-badge"
          />
          {locked ? (
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Lock className="size-3" />
              {t("dailyReports.lockedTag")}
            </span>
          ) : null}
          {report.version_number && report.version_number > 1 ? (
            <span className="text-xs text-muted-foreground">
              {t("dailyReports.version", { number: report.version_number })}
            </span>
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
              {t("dailyReports.submitForApproval")}
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
              {t("dailyReports.startReview")}
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
                {t("dailyReports.lockApprove")}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => setRejecting((v) => !v)}
                data-testid="report-reject-btn"
                className="inline-flex items-center gap-1 rounded-md bg-danger-600 px-4 py-1.5 text-sm text-white hover:bg-danger-700 disabled:opacity-50"
              >
                <XCircle className="size-4" />
                {t("dailyReports.reject")}
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
              {t("dailyReports.requestCorrection")}
            </button>
          ) : null}
          {canEdit && report.status === "draft" && report.is_current !== false && openCorrection ? (
            <button
              type="button"
              disabled={cancellingCorrection}
              onClick={() => setConfirmingCancellation(true)}
              data-testid="report-correction-cancel-btn"
              className="inline-flex items-center gap-1 rounded-md border border-danger-300 px-4 py-1.5 text-sm text-danger-700 hover:bg-danger-50 disabled:opacity-50"
            >
              {t("dailyReports.cancelCorrection")}
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => setShowVersions((v) => !v)}
            data-testid="report-versions-btn"
            className="inline-flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-sm hover:bg-muted/40"
          >
            <History className="size-4" />
            {t("dailyReports.versions")}
          </button>
        </div>
      </div>

      {rejecting ? (
        <div className="space-y-2 rounded-lg border border-danger-300 bg-danger-50 p-3 dark:bg-danger-950/30">
          <textarea
            className="min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
            placeholder={t("dailyReports.rejectReasonPlaceholder")}
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
              {t("dailyReports.cancel")}
            </button>
            <button
              type="button"
              disabled={reason.trim().length < 10 || busy}
              onClick={() => onReject(reason.trim())}
              data-testid="report-reject-confirm-btn"
              className="rounded-md bg-danger-600 px-3 py-1 text-sm text-white disabled:opacity-50"
            >
              {t("dailyReports.submitReject")}
            </button>
          </div>
        </div>
      ) : null}

      {correcting ? (
        <div className="space-y-2 rounded-lg border border-border bg-muted/30 p-3">
          <textarea
            className="min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
            placeholder={t("dailyReports.correctionReasonPlaceholder")}
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
              {t("dailyReports.cancel")}
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
                  toast.success(t("dailyReports.correctionDraftCreated"));
                  if (corr.result_report_id) {
                    navigate(`/projects/${projectId}/daily-reports/${corr.result_report_id}/edit`);
                  }
                } catch (err) {
                  toast.error(err instanceof Error ? err.message : t("dailyReports.correctionRequestError"));
                } finally {
                  setCorrectionBusy(false);
                }
              }}
            >
              {t("dailyReports.submitCorrectionRequest")}
            </button>
          </div>
        </div>
      ) : null}

      {openCorrection ? (
        <Dialog open={confirmingCancellation} onOpenChange={setConfirmingCancellation}>
          <DialogContent
            data-testid="report-correction-cancel-confirmation"
            className="sm:max-w-md"
          >
            <DialogHeader>
              <DialogTitle>{t("dailyReports.cancelCorrectionDialogTitle")}</DialogTitle>
              <DialogDescription>
                {t("dailyReports.cancelCorrectionDialogDesc")}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setConfirmingCancellation(false)}
              >
                {t("dailyReports.cancel")}
              </Button>
              <Button
                type="button"
                variant="destructive"
                disabled={cancellingCorrection}
                data-testid="report-correction-cancel-confirm-btn"
                onClick={async () => {
                  setCancellingCorrection(true);
                  setIsCancelled(true);
                  try {
                    void queryClient.cancelQueries({ queryKey: ["daily-report-correction-requests", projectId, report.report_id] });
                    const cancelled = await cancelCorrectionRequest(projectId, openCorrection.id);
                    navigate(`/projects/${projectId}/daily-reports/${cancelled.source_report_id}/view`);
                    void queryClient.cancelQueries({ queryKey: ["daily-report", projectId, report.report_id] });
                    void queryClient.cancelQueries({ queryKey: ["daily-report-correction-requests", projectId, report.report_id] });
                    void queryClient.cancelQueries({ queryKey: ["daily-report-versions", projectId, report.report_id] });
                    void queryClient.invalidateQueries({ queryKey: ["daily-report", projectId, cancelled.source_report_id] });
                    void queryClient.invalidateQueries({ queryKey: ["daily-report-correction-requests", projectId, cancelled.source_report_id] });
                    void queryClient.invalidateQueries({ queryKey: ["daily-report-versions", projectId, cancelled.source_report_id] });
                    void queryClient.invalidateQueries({ queryKey: ["daily-reports", projectId] });
                    toast.success(t("dailyReports.correctionCancelledSuccess"));
                  } catch (err) {
                    setIsCancelled(false);
                    toast.error(err instanceof Error ? err.message : t("dailyReports.correctionCancelError"));
                  } finally {
                    setCancellingCorrection(false);
                    setConfirmingCancellation(false);
                  }
                }}
              >
                {t("dailyReports.confirmCancelCorrection")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      ) : null}

      {status === "rejected" && report.rejection_reason ? (
        <p className="rounded-md bg-danger-50 p-2 text-sm text-danger-800 dark:bg-danger-950/30 dark:text-danger-200">
          {t("dailyReports.rejectionReasonLabel", { reason: report.rejection_reason })}
        </p>
      ) : null}

      {showVersions ? (
        <div
          className="space-y-2 rounded-lg border border-border bg-muted/20 p-3 text-sm"
          data-testid="report-versions-panel"
        >
          <p className="font-medium">{t("dailyReports.versionHistoryTitle")}</p>
          {versions.isLoading ? (
            <p className="text-muted-foreground">{t("dailyReports.loading")}</p>
          ) : versions.isError ? (
            <p className="text-danger-700">{t("dailyReports.errorLoadingVersions")}</p>
          ) : (versions.data?.length ?? 0) === 0 ? (
            <p className="text-muted-foreground">{t("dailyReports.noVersionsRecorded")}</p>
          ) : (
            <ul className="space-y-2">
              {versions.data!.map((v) => {
                const isActive = v.report_id === report.report_id;
                return (
                  <li
                    key={v.report_id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded border border-border/60 bg-card p-2"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium">
                        {t("dailyReports.version", { number: v.version_number })}
                      </span>
                      <Badge
                        variant={STATUS_BADGE[v.status]}
                        label={getStatusLabel(v.status)}
                        data-testid={`version-status-badge-${v.version_number}`}
                      />
                      {v.is_current ? (
                        <Badge
                          variant="info"
                          label={t("dailyReports.currentVersionTag")}
                          data-testid={`version-current-badge-${v.version_number}`}
                        />
                      ) : null}
                      {v.is_locked ? (
                        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                          <Lock className="size-3" />
                          {t("dailyReports.lockedTag")}
                        </span>
                      ) : null}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {v.modifier_name ?? t("dailyReports.unknownModifier")}
                      {" · "}
                      {v.version_number === 1
                        ? t("dailyReports.initialSubmission")
                        : v.correction_reason
                          ? t("dailyReports.correctionReasonLabel", { reason: v.correction_reason })
                          : t("dailyReports.noCorrectionReason")}
                      {` · ${
                        v.approved_at
                          ? t("dailyReports.approvalDateLabel", {
                              date: formatLocaleDateTime(v.approved_at, i18n.language),
                            })
                          : t("dailyReports.approvalDateUnavailable", "تأیید: ثبت‌نشده")
                      }`}
                    </span>
                    {isActive ? (
                      <span className="text-xs font-medium text-muted-foreground">
                        {t("dailyReports.currentVersionBadge")}
                      </span>
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
                        {t("dailyReports.viewVersion")}
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
        <span>{t("dailyReports.reportDateLabel", { date: report.report_date })}</span>
        {report.created_at ? (
          <span>
            {t("dailyReports.registeredAt", {
              date: formatLocaleDateTime(report.created_at, i18n.language),
            })}
          </span>
        ) : null}
        {report.submitted_at ? (
          <span>
            {t("dailyReports.submittedAtBy", {
              date: formatLocaleDateTime(report.submitted_at, i18n.language),
              user: report.submitted_by_name ?? "",
            })}
          </span>
        ) : null}
        {report.reviewed_at ? (
          <span>
            {t("dailyReports.reviewedAtBy", {
              date: formatLocaleDateTime(report.reviewed_at, i18n.language),
              user: report.reviewed_by_name ?? "",
            })}
          </span>
        ) : null}
        {report.approved_at ? (
          <span>
            {t("dailyReports.approvedAtBy", {
              date: formatLocaleDateTime(report.approved_at, i18n.language),
              user: report.approved_by_name ?? "",
            })}
          </span>
        ) : null}
      </div>
    </div>
  );
}
