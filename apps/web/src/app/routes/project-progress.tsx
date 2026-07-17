import { useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  fetchActivityProgress,
  fetchProgressHistory,
  fetchProgressKpis,
  fetchProgressSnapshot,
  fetchSCurve,
} from "@/app/lib/api/progress";
import { isoToJalali } from "@/app/lib/jalali-utils";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ActivityProgressTable } from "@/components/progress/ActivityProgressTable";
import { KPICard } from "@/components/progress/KPICard";
import { ManualProgressDrawer } from "@/components/progress/ManualProgressDrawer";
import { ProgressHistoryTable } from "@/components/progress/ProgressHistoryTable";
import { SCurveChart } from "@/components/progress/SCurveChart";
import { Button } from "@/components/ui/sprint-button";
import { fetchEconomicForecast, formatFaAmount } from "@/app/lib/api/economic";
import { PATHS } from "@/app/routeVars";

type Interval = "daily" | "weekly" | "monthly";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function ProgressPageContent() {
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard");
  const canEdit = has("edit_activities");
  const qc = useQueryClient();

  const [dateRange, setDateRange] = useState({ from: "", to: "" });
  const [interval, setInterval] = useState<Interval>("daily");
  const [forceRefresh, setForceRefresh] = useState(false);
  const [behindOnly, setBehindOnly] = useState(false);
  const [manualOpen, setManualOpen] = useState(false);

  const effectiveFrom = dateRange.from || project?.start_date || todayIso();
  const effectiveTo = dateRange.to || todayIso();

  const {
    data: snapshot,
    isLoading: snapshotLoading,
    isError: snapshotError,
    refetch: refetchSnapshot,
  } = useQuery({
    queryKey: ["progress-snapshot", projectId],
    queryFn: () => fetchProgressSnapshot(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: kpis } = useQuery({
    queryKey: ["progress-kpis", projectId],
    queryFn: () => fetchProgressKpis(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: economicForecast } = useQuery({
    queryKey: ["economic-forecast", projectId],
    queryFn: () => fetchEconomicForecast(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: sCurve, isLoading: curveLoading, isFetching: curveFetching } = useQuery({
    queryKey: ["progress-s-curve", projectId, effectiveFrom, effectiveTo, interval, forceRefresh],
    queryFn: () =>
      fetchSCurve(projectId, {
        date_from: effectiveFrom,
        date_to: effectiveTo,
        interval,
        force_refresh: forceRefresh,
      }),
    enabled: canView && Boolean(projectId),
  });

  useEffect(() => {
    if (!curveFetching && forceRefresh) setForceRefresh(false);
  }, [curveFetching, forceRefresh]);

  const { data: activityRows = [] } = useQuery({
    queryKey: ["progress-activities", projectId, behindOnly],
    queryFn: () => fetchActivityProgress(projectId, { is_behind: behindOnly || undefined }),
    enabled: canView && Boolean(projectId),
  });

  const { data: history = [] } = useQuery({
    queryKey: ["progress-history", projectId],
    queryFn: () => fetchProgressHistory(projectId),
    enabled: canView && Boolean(projectId),
  });

  const variance = snapshot?.schedule_variance_pct ?? 0;
  const spi = snapshot?.spi ?? kpis?.spi ?? null;

  const quickRanges = useMemo(
    () => [
      {
        label: "این ماه",
        from: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10),
        to: todayIso(),
      },
      {
        label: "سه ماه اخیر",
        from: new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10),
        to: todayIso(),
      },
      {
        label: "از ابتدا",
        from: project?.start_date || todayIso(),
        to: todayIso(),
      },
    ],
    [project?.start_date],
  );

  if (projectLoading || snapshotLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <EmptyState title="پروژه یافت نشد" />;
  if (snapshotError) {
    return <QueryErrorState onRetry={() => void refetchSnapshot()} />;
  }

  if (!canView) {
    return (
      <EmptyState
        title="دسترسی ندارید"
        description="نقش شما مجوز مشاهده داشبورد را ندارد."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <PageHeader title="گزارش پیشرفت پروژه" subtitle={project.project_name} />
        {canEdit ? (
          <Button variant="secondary" size="sm" onClick={() => setManualOpen(true)}>
            ثبت پیشرفت دستی
          </Button>
        ) : null}
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-[260px] flex-1">
          <JalaliDateRangePicker
            name="progress_range"
            label="بازه تاریخ"
            value={dateRange}
            onChange={setDateRange}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {quickRanges.map((r) => (
            <Button
              key={r.label}
              variant="secondary"
              size="sm"
              onClick={() => setDateRange({ from: r.from, to: r.to })}
            >
              {r.label}
            </Button>
          ))}
        </div>
      </div>

      <div
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-7"
        data-testid="progress-kpi-grid"
      >
        <KPICard
          title="پیشرفت فیزیکی"
          value={`${(snapshot?.actual_progress_pct ?? 0).toFixed(1)}٪`}
          subtitle={`برنامه: ${(snapshot?.planned_progress_pct ?? 0).toFixed(1)}٪`}
          trend={
            variance !== 0
              ? {
                  label: `${variance > 0 ? "↑" : "↓"} ${Math.abs(variance).toFixed(1)}٪ ${variance < 0 ? "تأخیر" : "جلوتر"}`,
                  positive: variance > 0,
                }
              : null
          }
        />
        <KPICard
          title="SPI (شاخص عملکرد زمانی)"
          value={spi != null ? spi.toFixed(2) : "—"}
          footer={spi != null && spi < 1 ? "SPI < 1 یعنی پروژه از برنامه عقب است" : undefined}
        />
        <KPICard
          title="CPI (شاخص عملکرد هزینه‌ای)"
          value={kpis?.ac ? (kpis.cpi != null ? kpis.cpi.toFixed(2) : "—") : "—"}
          footer={!kpis?.ac ? "داده هزینه در دسترس نیست" : undefined}
        />
        <KPICard
          title="EAC (برآورد هزینه تکمیل)"
          value={kpis?.ac && kpis.eac != null ? kpis.eac.toLocaleString("fa-IR") : "—"}
          footer={!kpis?.ac ? "داده هزینه در دسترس نیست" : undefined}
        />
        <KPICard
          title="ETC (باقی‌مانده تکمیل)"
          value={
            economicForecast?.etc_to_complete != null
              ? formatFaAmount(economicForecast.etc_to_complete)
              : kpis?.etc != null
                ? formatFaAmount(kpis.etc)
                : "—"
          }
          footer={
            <Link
              className="text-primary underline"
              to={`/projects/${projectId}/${PATHS.PROJECT_ECONOMIC}`}
            >
              تحلیل اقتصادی
            </Link>
          }
        />
        <KPICard
          title="VAC (انحراف تکمیل)"
          value={
            economicForecast?.vac != null
              ? formatFaAmount(economicForecast.vac)
              : kpis?.vac != null
                ? formatFaAmount(kpis.vac)
                : "—"
          }
        />
        <KPICard
          title="EAC (تعدیل تورم)"
          value={
            economicForecast?.eac_inflation_adjusted != null
              ? formatFaAmount(economicForecast.eac_inflation_adjusted)
              : "—"
          }
          footer={
            economicForecast?.inflation_factor != null ? (
              <>ضریب تورم: {economicForecast.inflation_factor.toFixed(2)}</>
            ) : (
              <Link
                className="text-primary underline"
                to={`/projects/${projectId}/${PATHS.PROJECT_ECONOMIC}`}
              >
                تحلیل اقتصادی
              </Link>
            )
          }
        />
      </div>

      <section
        className="space-y-3 rounded-xl border border-border bg-card p-4"
        data-testid="progress-s-curve"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">منحنی S</h2>
          <div className="flex flex-wrap items-center gap-2">
            {(["daily", "weekly", "monthly"] as Interval[]).map((item) => (
              <Button
                key={item}
                size="sm"
                variant={interval === item ? "primary" : "secondary"}
                onClick={() => setInterval(item)}
              >
                {item === "daily" ? "روزانه" : item === "weekly" ? "هفتگی" : "ماهانه"}
              </Button>
            ))}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setForceRefresh(true)}
              title="بازخوانی بدون کش"
              aria-label="بازخوانی بدون کش"
            >
              <RefreshCw className="size-4" />
            </Button>
          </div>
        </div>
        {sCurve?.warning ? (
          <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-100">
            {sCurve.warning}
          </p>
        ) : null}
        {curveLoading ? (
          <LoadingSkeleton rows={6} />
        ) : (
          <SCurveChart data={sCurve?.results ?? []} todayIso={todayIso()} />
        )}
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">پیشرفت فعالیت‌ها</h2>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={behindOnly}
              onChange={(e) => setBehindOnly(e.target.checked)}
            />
            فقط تأخیردار
          </label>
        </div>
        <ActivityProgressTable projectId={projectId} rows={activityRows} />
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">تاریخچه گزارش‌های تأیید شده</h2>
        <ProgressHistoryTable projectId={projectId} rows={history} />
      </section>

      <ManualProgressDrawer
        projectId={projectId}
        open={manualOpen}
        onClose={() => setManualOpen(false)}
        onSaved={() => {
          void qc.invalidateQueries({ queryKey: ["progress-snapshot", projectId] });
          void qc.invalidateQueries({ queryKey: ["progress-kpis", projectId] });
          void qc.invalidateQueries({ queryKey: ["progress-s-curve", projectId] });
          void qc.invalidateQueries({ queryKey: ["progress-activities", projectId] });
          void qc.invalidateQueries({ queryKey: ["progress-history", projectId] });
        }}
      />
    </div>
  );
}

export default function ProjectProgressPage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            {
              label: "پیشرفت",
            },
          ]}
        />
        <ProgressPageContent />
      </ProjectProvider>
    </main>
  );
}
