import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type { ReactNode } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  Award,
  CheckCircle2,
  FileCheck,
  History,
  Layers,
} from "lucide-react";
import {
  approvePeriodReport,
  fetchFigureSources,
  fetchPeriodReport,
  fetchPeriodReports,
  generatePeriodReport,
  overridePeriodReportFigure,
  type FigureSourceItem,
  type PeriodReport,
  type PeriodReportFigure,
} from "@/app/lib/api/progress";
import {
  formatDisplayDate,
  getSolarHijriMonthBounds,
  getSolarHijriWorkweekBounds,
} from "@/app/lib/jalali-utils";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { Input } from "@/components/form";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

export function PeriodReportsPanel({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [overrideFigure, setOverrideFigure] = useState<PeriodReportFigure | null>(null);
  const [overrideValue, setOverrideValue] = useState("");
  const [overrideReason, setOverrideReason] = useState("");
  const [provenanceFigure, setProvenanceFigure] = useState<PeriodReportFigure | null>(null);

  const { data: reports = [] } = useQuery({
    queryKey: ["progress-reports", projectId],
    queryFn: () => fetchPeriodReports(projectId),
  });

  const { data: detail } = useQuery({
    queryKey: ["progress-report", projectId, selectedId],
    queryFn: () => fetchPeriodReport(projectId, selectedId!),
    enabled: Boolean(selectedId),
  });

  const { data: figureSources = [], isLoading: loadingSources } = useQuery({
    queryKey: ["figure-sources", projectId, provenanceFigure?.id],
    queryFn: () => fetchFigureSources(projectId, provenanceFigure!.id),
    enabled: Boolean(provenanceFigure?.id),
  });

  const generateMutation = useMutation({
    mutationFn: (kind: "weekly" | "monthly") => {
      const bounds =
        kind === "weekly"
          ? getSolarHijriWorkweekBounds()
          : getSolarHijriMonthBounds();
      return generatePeriodReport(projectId, {
        kind,
        period_start: bounds.start,
        period_end: bounds.end,
      });
    },
    onSuccess: (report) => {
      toast.success(t("progressReports.generated"));
      setSelectedId(report.id);
      void qc.invalidateQueries({ queryKey: ["progress-reports", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approveMutation = useMutation({
    mutationFn: (reportId: string) => approvePeriodReport(projectId, reportId),
    onSuccess: (report) => {
      toast.success(
        report.serial_number
          ? `گزارش با شماره سریال رسمی ${report.serial_number} تأیید گردید.`
          : "گزارش با موفقیت تأیید شد.",
      );
      void qc.invalidateQueries({ queryKey: ["progress-report", projectId, selectedId] });
      void qc.invalidateQueries({ queryKey: ["progress-reports", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const overrideMutation = useMutation({
    mutationFn: () =>
      overridePeriodReportFigure(projectId, overrideFigure!.id, {
        new_value: overrideValue,
        reason: overrideReason.trim(),
      expected_version: overrideFigure!.version,
      }),
    onSuccess: () => {
      toast.success(t("progressReports.overrideSaved"));
      setOverrideFigure(null);
      setOverrideValue("");
      setOverrideReason("");
      void qc.invalidateQueries({ queryKey: ["progress-report", projectId, selectedId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const isApproved = detail?.status === "approved";
  const overriddenFigures = (detail?.figures || []).filter((f) => f.is_overridden);

  return (
    <section
      className="space-y-4 rounded-xl border border-border bg-card p-4"
      data-testid="period-reports-panel"
    >
      {/* Header with generation buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
        <div>
          <h2 className="text-lg font-semibold">{t("progressReports.title")}</h2>
          <p className="text-xs text-muted-foreground">
            تولید خودکار گزارش‌های هفتگی (شنبه تا جمعه) و ماهانه بر اساس گزارش‌های روزانه تأییدشده
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="secondary"
            loading={generateMutation.isPending}
            onClick={() => generateMutation.mutate("weekly")}
            data-testid="generate-weekly-report"
          >
            {t("progressReports.generateWeekly")} (شنبه تا جمعه)
          </Button>
          <Button
            size="sm"
            variant="secondary"
            loading={generateMutation.isPending}
            onClick={() => generateMutation.mutate("monthly")}
            data-testid="generate-monthly-report"
          >
            {t("progressReports.generateMonthly")} (ماه شمسی)
          </Button>
        </div>
      </div>

      {/* Reports picker */}
      <div className="flex flex-wrap gap-2">
        {reports.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("progressReports.empty")}</p>
        ) : (
          reports.map((r: PeriodReport) => (
            <Button
              key={r.id}
              size="sm"
              variant={selectedId === r.id ? "primary" : "ghost"}
              onClick={() => setSelectedId(r.id)}
              className="flex items-center gap-1.5"
            >
              {r.kind === "weekly" ? "هفتگی" : "ماهانه"}
              <span className="text-xs opacity-75">
                ({formatDisplayDate(r.period_start)} تا {formatDisplayDate(r.period_end)})
              </span>
              {r.status === "approved" && (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              )}
            </Button>
          ))
        )}
      </div>

      {/* Report details view */}
      {detail ? (
        <div className="space-y-4">
          {/* Metadata & Official Approval Banner */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/20 p-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-base">{detail.title}</span>
                <Badge
                  variant={detail.status === "approved" ? "success" : "neutral"}
                  label={detail.status === "approved" ? "تأیید رسمی شده" : "پیش‌نویس سیستمی"}
                />
              </div>
              <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                <span>بازه: {formatDisplayDate(detail.period_start)} تا {formatDisplayDate(detail.period_end)}</span>
                {detail.serial_number && (
                  <span className="flex items-center gap-1 font-mono font-medium text-foreground">
                    <Award className="h-3.5 w-3.5 text-amber-500" />
                    شماره سریال رسمی: {detail.serial_number}
                  </span>
                )}
                <span>استخراج: {new Date(detail.generated_at).toLocaleString("fa-IR")}</span>
              </div>
            </div>

            {/* Approval Action */}
            <div>
              {detail.status !== "approved" && (
                <Button
                  size="sm"
                  variant="primary"
                  loading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate(detail.id)}
                  className="flex items-center gap-1.5"
                >
                  <FileCheck className="h-4 w-4" />
                  تأیید رسمی و صدور شماره سریال
                </Button>
              )}
            </div>
          </div>

          {/* Header Warnings */}
          {detail.warnings && detail.warnings.length > 0 && (
            <div
              className="space-y-1.5 rounded-lg border border-amber-300 bg-amber-50 p-3 text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200"
              data-testid="report-warnings-banner"
            >
              <div className="flex items-center gap-2 font-medium text-sm">
                <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                اخطارهای هدر گزارش (عدم انطباق یا گزارش‌های روزانه تأییدنشده):
              </div>
              <ul className="list-inside list-disc space-y-0.5 text-xs">
                {detail.warnings.map((w: string, idx: number) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Structured Figures Display */}
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[700px] text-sm">
              <thead className="bg-muted/50 text-xs text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 text-start">بخش گزارش</th>
                  <th className="px-3 py-2 text-start">مقادیر و خلاصه داده‌ها</th>
                  <th className="px-3 py-2 text-start">منبع داده‌ها</th>
                  <th className="px-3 py-2 text-start">آخرین به‌روزرسانی</th>
                  <th className="px-3 py-2 text-start">عملیات</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(detail.figures || []).map((f) => (
                  <tr key={f.id} className="hover:bg-muted/20">
                    <td className="px-3 py-2.5 font-medium">
                      <div className="flex items-center gap-1">
                        <span>{f.section}</span>
                        {f.is_overridden && (
                          <span
                            className="font-bold text-amber-600"
                            title="این مقدار بازنویسی شده است (دارای پی‌نوشت)"
                          >
                            *
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2.5">
                      {renderStructuredFigureValue(f)}
                    </td>
                    <td className="px-3 py-2.5 text-xs">
                      {f.source_path ? (
                        <Link className="text-primary underline" to={f.source_path}>
                          {f.source_type}
                          {f.source_approved ? " (تأییدشده)" : ""}
                        </Link>
                      ) : (
                        f.source_type || "—"
                      )}
                    </td>
                    <td className="px-3 py-2.5 text-xs text-muted-foreground">
                      {f.last_updated_at
                        ? new Date(f.last_updated_at).toLocaleString("fa-IR")
                        : "—"}
                    </td>
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-1.5">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setProvenanceFigure(f)}
                          title="مشاهده ردپای داده‌ها و ریز اقلام روزانه"
                          className="flex items-center gap-1 text-xs"
                        >
                          <History className="h-3.5 w-3.5" />
                          ردپا
                        </Button>
                        {!isApproved && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setOverrideFigure(f);
                              setOverrideValue(
                                typeof f.value === "string" || typeof f.value === "number"
                                  ? String(f.value)
                                  : "",
                              );
                              setOverrideReason("");
                            }}
                            className="text-xs"
                          >
                            بازنویسی
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Footnotes for overridden figures */}
          {overriddenFigures.length > 0 && (
            <div
              className="space-y-1 rounded-lg border border-border bg-muted/10 p-3 text-xs text-muted-foreground"
              data-testid="overridden-footnotes"
            >
              <div className="font-semibold text-foreground">پی‌نوشت‌های بازنویسی ارقام (*):</div>
              <ul className="space-y-1">
                {overriddenFigures.map((of) => (
                  <li key={of.id}>
                    * بخش <strong>{of.section}</strong>: مقدار اولیه محاسبه‌شده:{" "}
                    <code className="rounded bg-muted px-1 py-0.5 font-mono">
                      {renderNestedValue(of.calculated_value)}
                    </code>
                    {of.override_count ? ` (تعداد ممیزی: ${of.override_count})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : null}

      {/* Override Dialog / Form */}
      {overrideFigure && (
        <div className="space-y-3 rounded-lg border border-amber-300 bg-amber-50/50 p-4 dark:border-amber-800 dark:bg-amber-950/20">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">
              بازنویسی کنترل‌شده شاخص: {overrideFigure.section}
            </h3>
            <span className="text-xs text-muted-foreground">
              حفظ مقدار اولیه:{" "}
              {String(overrideFigure.calculated_value ?? overrideFigure.value ?? "—")}
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="text-xs font-medium">مقدار جدید</label>
              <Input
                value={overrideValue}
                onChange={(e) => setOverrideValue(e.target.value)}
                placeholder="مقدار بازنویسی‌شده را وارد کنید"
              />
            </div>
            <div>
              <label className="text-xs font-medium">
                دلیل بازنویسی (الزاماً حداقل ۱۰ کاراکتر)
              </label>
              <Input
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="مثلاً: توافق صورت‌جلسه کارگاهی با مشاور"
              />
              <div className="mt-1 flex justify-between text-[11px] text-muted-foreground">
                <span>تعداد کاراکتر: {overrideReason.trim().length} / ۱۰</span>
                {overrideReason.trim().length > 0 && overrideReason.trim().length < 10 && (
                  <span className="text-destructive">حداقل ۱۰ کاراکتر الزامی است</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              size="sm"
              variant="primary"
              disabled={overrideReason.trim().length < 10}
              loading={overrideMutation.isPending}
              onClick={() => overrideMutation.mutate()}
            >
              ثبت بازنویسی با ردپای ممیزی
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setOverrideFigure(null)}>
              {t("common.cancel")}
            </Button>
          </div>
        </div>
      )}

      {/* Figure Provenance Breakdown Modal */}
      <Dialog
        open={Boolean(provenanceFigure)}
        onOpenChange={(open) => {
          if (!open) setProvenanceFigure(null);
        }}
      >
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary" />
              ردپای داده‌ها و ریز اقلام مبنا (Figure Provenance)
            </DialogTitle>
            <DialogDescription>
              ریز اقلام و رکوردهای گزارش روزانه که مبنای محاسبه شاخص «
              {provenanceFigure?.section}» بوده‌اند (محافظت‌شده در برابر حذف).
            </DialogDescription>
          </DialogHeader>

          {loadingSources ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              در حال واکشی اطلاعات ردپای داده‌ها...
            </div>
          ) : figureSources.length === 0 ? (
            <div className="py-6 text-center text-sm text-muted-foreground">
              هیچ آیتم زیرمجموعه‌ای برای این شاخص یافت نشد.
            </div>
          ) : (
            <div className="max-h-[60vh] overflow-y-auto">
              <table className="w-full text-xs">
                <thead className="bg-muted text-muted-foreground">
                  <tr>
                    <th className="p-2 text-start">تاریخ ثبت (شمسی)</th>
                    <th className="p-2 text-start">کد گزارش روزانه</th>
                    <th className="p-2 text-start">نوع رکورد منبع</th>
                    <th className="p-2 text-start">مقدار مشارکت‌یافته</th>
                    <th className="p-2 text-start">ثبت‌کننده</th>
                    <th className="p-2 text-start">تأییدکننده ناظر</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {figureSources.map((item: FigureSourceItem) => (
                    <tr key={item.id} className="hover:bg-muted/30">
                      <td className="p-2 font-medium">{item.source_date_jalali || "—"}</td>
                      <td className="p-2 font-mono">{item.source_code || "—"}</td>
                      <td className="p-2">{item.source_type}</td>
                      <td className="p-2">
                        {renderNestedValue(item.contributed_quantity)}
                      </td>
                      <td className="p-2 text-muted-foreground">{item.created_by_name || "سیستمی"}</td>
                      <td className="p-2 text-emerald-600 font-medium">
                        {item.approved_by_name || "ناظر کارگاه"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
}

/** Helper rendering structured tables and cards for complex report sections */
function renderStructuredFigureValue(figure: PeriodReportFigure) {
  if (figure.value_status === "not_recorded") {
    return <span className="text-xs text-muted-foreground">ثبت‌نشده</span>;
  }
  const val = figure.value as Record<string, unknown> | null;
  if (!val || typeof val !== "object") {
    return (
      <span className="font-semibold text-foreground">
        {String(figure.value ?? "—")} {figure.unit_of_measure}
      </span>
    );
  }

  // Section 1: labor_machinery
  if (figure.section === "labor_machinery") {
    const labor = (val.labor_breakdown as Array<Record<string, unknown>>) || [];
    const equip = (val.machinery_breakdown as Array<Record<string, unknown>>) || [];
    return (
      <div className="space-y-2 text-xs">
        <div className="flex flex-wrap gap-3 font-medium">
          <span className="rounded bg-primary/10 px-2 py-0.5 text-primary">
            ساعات کارکرد عادی: {String(val.total_regular_hours ?? 0)} ساعت
          </span>
          <span className="rounded bg-amber-500/10 px-2 py-0.5 text-amber-700 dark:text-amber-400">
            اضافه‌کار: {String(val.total_overtime_hours ?? 0)} ساعت
          </span>
          <span className="rounded bg-blue-500/10 px-2 py-0.5 text-blue-700 dark:text-blue-400">
            کارکرد ماشین‌آلات: {String(val.total_machinery_operating_hours ?? 0)} ساعت
          </span>
        </div>

        {labor.length > 0 && (
          <div className="rounded border bg-muted/10 p-1.5">
            <span className="font-semibold text-muted-foreground">نیروی انسانی:</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {labor.map((l, idx) => (
                <span key={idx} className="rounded bg-card px-2 py-0.5 border text-[11px]">
                  {String(l.contractor)} - {String(l.job_title)}: {String(l.regular_hours)}h (نفرات: {String(l.total_headcount)})
                </span>
              ))}
            </div>
          </div>
        )}

        {equip.length > 0 && (
          <div className="rounded border bg-muted/10 p-1.5">
            <span className="font-semibold text-muted-foreground">ماشین‌آلات:</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {equip.map((e, idx) => (
                <span key={idx} className="rounded bg-card px-2 py-0.5 border text-[11px]">
                  {String(e.equipment_name)}: {String(e.operating_hours)}h مفید ({String(e.idle_hours)}h توقف)
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Section 2: materials
  if (figure.section === "materials") {
    const items = (val.items as Array<Record<string, unknown>>) || [];
    if (items.length === 0) return <span className="text-xs text-muted-foreground">مصالحی ثبت نشده</span>;
    return (
      <div className="flex flex-wrap gap-2 text-xs">
        {items.map((m, idx) => (
          <div key={idx} className="rounded border bg-card px-2.5 py-1 text-[11px] shadow-sm">
            <span className="font-semibold">{String(m.material_name)}: </span>
            <span className="text-emerald-600">وارده: {String(m.delivered_quantity)} {String(m.unit)}</span> |{" "}
            <span className="text-amber-600">مصرفی: {String(m.consumed_quantity)} {String(m.unit)}</span>
          </div>
        ))}
      </div>
    );
  }

  // Section 3: completed_activities
  if (figure.section === "completed_activities") {
    const activities = (val.completed_activities as Array<Record<string, unknown>>) || [];
    if (activities.length === 0) return <span className="text-xs text-muted-foreground">فعالیتی تکمیل نشده</span>;
    return (
      <div className="space-y-1 text-xs">
        <span className="font-semibold text-emerald-600">تعداد تکمیل‌شده: {activities.length}</span>
        <div className="flex flex-wrap gap-1.5">
          {activities.map((a, idx) => (
            <span key={idx} className="rounded border bg-card px-2 py-0.5 text-[11px]">
              {String(a.activity_code)}: {String(a.activity_name)} (اتمام: {formatDisplayDate(String(a.actual_finish))})
            </span>
          ))}
        </div>
      </div>
    );
  }

  // Section 4: hse_summary
  if (figure.section === "hse_summary") {
    const incidents = (val.incidents as Array<Record<string, unknown>>) || [];
    return (
      <div className="space-y-1.5 text-xs">
        <div className="flex flex-wrap gap-2 font-medium">
          <span className="rounded bg-rose-500/10 px-2 py-0.5 text-rose-700 dark:text-rose-400">
            حوادث اتلاف وقت: {String(val.lost_time_injuries ?? 0)}
          </span>
          <span className="rounded bg-amber-500/10 px-2 py-0.5 text-amber-700 dark:text-amber-400">
            شبه‌حوادث: {String(val.near_misses ?? 0)}
          </span>
          <span className="rounded bg-blue-500/10 px-2 py-0.5 text-blue-700 dark:text-blue-400">
            زیست‌محیطی: {String(val.environmental_events ?? 0)}
          </span>
        </div>
        {incidents.length > 0 && (
          <ul className="list-inside list-disc text-[11px] text-muted-foreground">
            {incidents.slice(0, 3).map((inc, idx) => (
              <li key={idx}>
                {String(inc.incident_type)} ({String(inc.severity)}): {String(inc.description)}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  // Section 5: qc_summary
  if (figure.section === "qc_summary") {
    return (
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded bg-primary/10 px-2 py-0.5 text-primary">
          کل بازرسی‌ها: {String(val.total_inspections ?? 0)}
        </span>
        <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-emerald-700 dark:text-emerald-400">
          تأییدشده: {String(val.passed ?? 0)}
        </span>
        <span className="rounded bg-rose-500/10 px-2 py-0.5 text-rose-700 dark:text-rose-400">
          مردود/عدم انطباق: {String(val.failed ?? val.non_conformance_reports ?? 0)}
        </span>
      </div>
    );
  }

  // Section 6: baseline_variance
  if (figure.section === "baseline_variance") {
    return (
      <div className="flex flex-wrap gap-2 text-xs">
        <span>برنامه‌ای: {String(val.planned_progress_pct ?? "—")}%</span> |{" "}
        <span>واقعی: {String(val.actual_progress_pct ?? "—")}%</span> |{" "}
        <span className="font-medium text-primary">
          SPI: {val.spi !== null && val.spi !== undefined ? Number(val.spi).toFixed(2) : "ثبت‌نشده"}
        </span> |{" "}
        <span className="font-medium text-emerald-600">
          CPI: {val.cpi !== null && val.cpi !== undefined ? Number(val.cpi).toFixed(2) : "ثبت‌نشده"}
        </span>
      </div>
    );
  }

  // Default fallback rendering cleanly formatted key-values
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      {Object.entries(val).map(([k, v]) => (
        <span key={k} className="rounded bg-muted/40 px-1.5 py-0.5">
          <span className="font-medium">{k}:</span> {renderNestedValue(v)}
        </span>
      ))}
    </div>
  );
}

function renderNestedValue(value: unknown): ReactNode {
  if (value == null || value === "") return "—";
  if (Array.isArray(value)) {
    return (
      <ul className="list-inside list-disc space-y-0.5">
        {value.map((item, index) => <li key={index}>{renderNestedValue(item)}</li>)}
      </ul>
    );
  }
  if (typeof value === "object") {
    return (
      <dl className="grid gap-x-3 gap-y-1 sm:grid-cols-2">
        {Object.entries(value as Record<string, unknown>).map(([key, nested]) => (
          <div key={key} className="rounded bg-muted/30 px-1.5 py-0.5">
            <dt className="inline font-medium">{key}: </dt>
            <dd className="inline">{renderNestedValue(nested)}</dd>
          </div>
        ))}
      </dl>
    );
  }
  return String(value);
}
