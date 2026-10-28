import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router";
import { usePermission } from "@/app/contexts/project-context";
import { technicalApproveProgress } from "@/app/lib/api/progress";
import { PATHS } from "@/app/routeVars";
import { isoToJalali } from "@/app/lib/jalali-utils";
import type { ActivityProgressRow } from "@/app/lib/api/progress";
import { EmptyState } from "@/components/layout/empty-state";
import { Badge } from "@/components/ui/badge";
import { MiniProgressBar } from "@/components/progress/MiniProgressBar";
import { cn } from "@/app/lib/utils";
import { Button } from "@/components/ui/sprint-button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

const STATUS_LABELS: Record<string, { label: string; variant: "neutral" | "info" | "warning" | "success" }> = {
  not_started: { label: "شروع نشده", variant: "neutral" },
  in_progress: { label: "در حال اجرا", variant: "info" },
  suspended: { label: "متوقف", variant: "warning" },
  completed: { label: "تکمیل شده", variant: "success" },
};

export function ActivityProgressTable({
  projectId,
  rows,
}: {
  projectId: string;
  rows: ActivityProgressRow[];
}) {
  const { has } = usePermission(projectId);
  const canApprove = has("approve_reports");
  const qc = useQueryClient();
  const [selected, setSelected] = useState<ActivityProgressRow | null>(null);
  const [approvedPct, setApprovedPct] = useState("");
  const [evidenceRef, setEvidenceRef] = useState("");
  const approve = useMutation({
    mutationFn: () => technicalApproveProgress(projectId, selected!.activity_id, {
      report_date: selected?.last_update_date ?? undefined,
      approved_progress_pct: Number(approvedPct),
      basis: "engineering_documents",
      evidence_refs: evidenceRef.trim() ? { reference: evidenceRef.trim() } : undefined,
    }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["progress-activities", projectId] });
      setSelected(null);
      setApprovedPct("");
      setEvidenceRef("");
    },
  });
  if (rows.length === 0) {
    return (
      <EmptyState
        title="فعالیتی با وزن تعریف‌شده یافت نشد"
        description="برای نمایش پیشرفت، وزن فعالیت‌ها را در فهرست فعالیت‌ها تنظیم کنید."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-[1100px] text-sm">
        <thead className="bg-muted/50">
          <tr>
            {[
              "کد",
              "نام فعالیت",
              "WBS",
              "وزن",
              "دوره‌ای٪",
              "تجمعی٪",
              "برنامه٪",
              "تأییدشده٪",
              "حجم دوره",
              "انحراف",
              "روش",
              "مقدار کل",
              "مقدار انجام شده",
              "واحد",
              "وضعیت",
              "آخرین به‌روزرسانی",
              ...(canApprove ? ["عملیات"] : []),
            ].map((h) => (
              <th key={h} className="px-3 py-2 text-start font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const status = STATUS_LABELS[row.status] ?? { label: row.status, variant: "neutral" as const };
            return (
              <tr key={row.activity_id} className="border-t border-border hover:bg-muted/30">
                <td className="px-3 py-2">
                  <Link
                    to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_ACTIVITIES}`}
                    className="text-primary hover:underline"
                  >
                    {row.activity_code}
                  </Link>
                </td>
                <td className="px-3 py-2">{row.activity_name}</td>
                <td className="px-3 py-2">{row.wbs_name || "—"}</td>
                <td className="px-3 py-2">
                  {row.weight != null ? `${(row.weight * 100).toFixed(2)}٪` : "—"}
                </td>
                <td className="px-3 py-2" data-testid={`period-pct-${row.activity_code}`}>
                  {(row.period_progress_pct ?? 0).toFixed(1)}٪
                </td>
                <td className="px-3 py-2" data-testid={`cumulative-pct-${row.activity_code}`}>
                  <div className="flex min-w-[120px] flex-col gap-1">
                    <span>
                      {(row.cumulative_progress_pct ?? row.actual_progress_pct).toFixed(1)}٪
                    </span>
                    <MiniProgressBar
                      plannedPct={row.planned_progress_pct}
                      actualPct={row.cumulative_progress_pct ?? row.actual_progress_pct}
                    />
                  </div>
                </td>
                <td className="px-3 py-2" data-testid={`planned-pct-${row.activity_code}`}>
                  {row.planned_progress_pct.toFixed(1)}٪
                </td>
                <td className="px-3 py-2" data-testid={`approved-pct-${row.activity_code}`}>
                  {(row.approved_progress_pct ?? 0).toFixed(1)}٪
                </td>
                <td className="px-3 py-2" data-testid={`period-quantity-${row.activity_code}`}>
                  {row.period_quantity != null ? `${row.period_quantity} ${row.unit || ""}` : "—"}
                </td>
                <td
                  className={cn(
                    "px-3 py-2 font-medium",
                    row.variance_pct < 0 ? "text-danger-600" : row.variance_pct > 0 ? "text-success-600" : "",
                  )}
                >
                  {row.variance_pct > 0 ? "+" : ""}
                  {row.variance_pct.toFixed(1)}٪
                </td>
                <td className="px-3 py-2 text-xs text-muted-foreground">
                  {row.measurement_status === "not_defined"
                    ? "—"
                    : row.measurement_method ?? "—"}
                  {row.measurement_status === "draft" ? " (draft)" : ""}
                </td>
                <td className="px-3 py-2">{row.total_quantity ?? "—"}</td>
                <td className="px-3 py-2">{row.cumulative_quantity ?? "—"}</td>
                <td className="px-3 py-2">{row.unit || "—"}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap items-center gap-1">
                    <Badge variant={status.variant} label={status.label} />
                    {row.is_behind ? <Badge variant="danger" label="تأخیر" /> : null}
                  </div>
                </td>
                <td className="px-3 py-2">
                  {row.last_update_date ? isoToJalali(row.last_update_date) : "—"}
                </td>
                {canApprove ? (
                  <td className="px-3 py-2">
                    <Button
                      size="xs"
                      variant="secondary"
                      disabled={!row.last_update_date || (row.cumulative_progress_pct ?? row.actual_progress_pct) <= 0}
                      onClick={() => {
                        setSelected(row);
                        setApprovedPct(String(row.approved_progress_pct ?? row.cumulative_progress_pct ?? row.actual_progress_pct));
                      }}
                    >
                      تأیید فنی پیشرفت
                    </Button>
                  </td>
                ) : null}
              </tr>
            );
          })}
        </tbody>
      </table>
      <Dialog open={Boolean(selected)} onOpenChange={(open) => !open && setSelected(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>تأیید فنی پیشرفت</DialogTitle>
            <DialogDescription>
              درصد تأییدشده باید بر مبنای بررسی مهندسی و مستندات فنی ثبت شود؛ عکس به‌تنهایی قابل قبول نیست.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <label className="space-y-1 text-sm">
              <span>درصد پیشرفت تأییدشده</span>
              <input className="w-full rounded-md border border-border bg-background px-3 py-2" type="number" min="0" max="100" step="0.01" value={approvedPct} onChange={(e) => setApprovedPct(e.target.value)} />
            </label>
            <label className="space-y-1 text-sm">
              <span>مرجع مستند فنی</span>
              <textarea className="min-h-20 w-full rounded-md border border-border bg-background px-3 py-2" value={evidenceRef} onChange={(e) => setEvidenceRef(e.target.value)} placeholder="شماره آزمایش، نقشه‌برداری یا صورتجلسه" />
            </label>
            {approve.isError ? <p className="text-sm text-danger-600">{(approve.error as Error).message}</p> : null}
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setSelected(null)}>انصراف</Button>
            <Button loading={approve.isPending} disabled={!approvedPct || Number(approvedPct) < 0 || Number(approvedPct) > 100} onClick={() => approve.mutate()}>ثبت تأیید</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
