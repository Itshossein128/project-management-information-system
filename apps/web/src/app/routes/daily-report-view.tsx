import { useTranslation } from "react-i18next";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Download } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { usePermission } from "@/app/contexts/project-context";
import { dailyReportWorkflowErrorMessage } from "@/components/daily_reports/workflow-error-message";
import { PATHS } from "@/app/routeVars";
import { fetchActivities } from "@/app/lib/api/activities";
import { fetchProject } from "@/app/lib/api/projects";
import {
  approveReport,
  fetchDailyReport,
  fetchDailyReportContractHeader,
  downloadDailyReportFile,
  rejectReport,
  reviewReport,
  submitReport,
  updateDailyReport,
  type InactivityReason,
  type SiteStatus,
  type WeatherCondition,
  INACTIVITY_REASONS,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { EmptyState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ActivityTab } from "@/components/daily_reports/ActivityTab";
import { ApprovalStatusBar } from "@/components/daily_reports/ApprovalStatusBar";
import { ConcreteTab } from "@/components/daily_reports/ConcreteTab";
import { EquipmentTab } from "@/components/daily_reports/EquipmentTab";
import { WeatherSelector } from "@/components/daily_reports/WeatherSelector";
import { validateTemperatures } from "@/app/lib/temperatureValidation";
import { IncidentsTab } from "@/components/daily_reports/IncidentsTab";
import { LaborCampTab } from "@/components/daily_reports/LaborCampTab";
import { LaborTab } from "@/components/daily_reports/LaborTab";
import { MaterialsTab } from "@/components/daily_reports/MaterialsTab";
import { DailyReportSummaryView } from "@/components/daily_reports/summary/DailyReportSummaryView";
import { Button } from "@/components/ui/sprint-button";

export default function DailyReportViewPage() {
  const { t } = useTranslation();
  const { projectId = "", reportId = "" } = useParams();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canApprove = has("approve_reports");
  const canEdit = has("edit_reports");
  const [downloading, setDownloading] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [opinion, setOpinion] = useState("");
  const [weatherOverride, setWeatherOverride] = useState(false);
  const [siteOverride, setSiteOverride] = useState(false);
  const [weather, setWeather] = useState<string>("");
  const [siteStatus, setSiteStatus] = useState<string>("active");
  const [inactivityReason, setInactivityReason] = useState<string>("");
  const [tempMin, setTempMin] = useState<string>("");
  const [tempMax, setTempMax] = useState<string>("");
  const [weatherImpactNotes, setWeatherImpactNotes] = useState<string>("");
  const [serverTempErrors, setServerTempErrors] = useState<{ min?: string | null; max?: string | null }>({});

  const tempValidation = useMemo(
    () => validateTemperatures(tempMin, tempMax, { isBlurOrSubmit: false }),
    [tempMin, tempMax]
  );
  const inlineTempMinError =
    serverTempErrors.min ||
    (tempValidation.tempMinError === "min_value" || tempValidation.tempMinError === "max_value"
      ? t("errors.temp_range", "دما باید بین ۴۰- تا ۶۰+ باشد")
      : null);
  const inlineTempMaxError =
    serverTempErrors.max ||
    (tempValidation.tempMaxError === "temp_max_must_be_gte_temp_min"
      ? t("errors.temp_max_must_be_gte_temp_min", "دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.")
      : tempValidation.tempMaxError === "min_value" || tempValidation.tempMaxError === "max_value"
      ? t("errors.temp_range", "دما باید بین ۴۰- تا ۶۰+ باشد")
      : null);

  const projectQuery = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => fetchProject(projectId),
    enabled: Boolean(projectId),
  });

  const reportQuery = useQuery({
    queryKey: ["daily-report", projectId, reportId],
    queryFn: () => fetchDailyReport(projectId, reportId),
  });
  const report = reportQuery.data ?? null;
  const headerQuery = useQuery({
    queryKey: ["daily-report-header", projectId, reportId],
    queryFn: () => fetchDailyReportContractHeader(projectId, reportId),
    enabled: Boolean(report),
  });
  const header = headerQuery.data;
  const unknown = t("dailyReports.referenceHeader.unknown");
  const shiftTimestamp = (timestamp: string | null) =>
    timestamp ? `${formatDisplayDate(timestamp.slice(0, 10))} ${timestamp.slice(11, 16)}` : unknown;

  useEffect(() => {
    if (!report) return;
    setOpinion(report.management_opinion ?? "");
    setWeatherOverride(Boolean(report.weather_override));
    setSiteOverride(Boolean(report.site_status_override));
    setWeather(report.weather_condition ?? "clear");
    setSiteStatus(report.site_status ?? "active");
    setInactivityReason(report.inactivity_reason ?? "");
    setTempMin(report.temp_min != null ? String(report.temp_min) : "");
    setTempMax(report.temp_max != null ? String(report.temp_max) : "");
    setWeatherImpactNotes(report.weather_impact_notes ?? "");
  }, [report]);

  const activitiesQuery = useQuery({
    queryKey: ["activities-lite", projectId],
    queryFn: () => fetchActivities(projectId, { per_page: 500 }),
  });
  const activityOptions = useMemo(
    () =>
      (activitiesQuery.data?.results ?? []).map((a) => ({
        value: a.activity_id,
        label: `${a.activity_code} - ${a.activity_name}`,
      })),
    [activitiesQuery.data],
  );

  const refetch = () => Promise.all([
    queryClient.invalidateQueries({ queryKey: ["daily-report", projectId, reportId] }),
    queryClient.invalidateQueries({ queryKey: ["daily-report-header", projectId, reportId] }),
  ]);

  const workflow = useMutation({
    mutationFn: async (action: {
      type: "submit" | "review" | "approve" | "reject";
      reason?: string;
    }) => {
      if (action.type === "submit") return submitReport(projectId, reportId);
      if (action.type === "review") return reviewReport(projectId, reportId);
      if (action.type === "approve") return approveReport(projectId, reportId);
      return rejectReport(projectId, reportId, action.reason ?? "");
    },
    onSuccess: () => {
      toast.success("عملیات انجام شد");
      void refetch();
    },
    onError: (e) => toast.error(dailyReportWorkflowErrorMessage(e, t)),
  });

  const exportPdf = async () => {
    setDownloading(true);
    try {
      await downloadDailyReportFile(projectId, reportId, "pdf");
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setDownloading(false);
    }
  };

  const exportExcel = async () => {
    setDownloadingExcel(true);
    try {
      await downloadDailyReportFile(projectId, reportId, "excel");
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setDownloadingExcel(false);
    }
  };

  if (reportQuery.isLoading) {
    return (
      <main className='page-main page-shell mx-auto px-4 py-6'>
        <LoadingSkeleton rows={8} />
      </main>
    );
  }

  const base = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;

  if (reportQuery.isError) {
    return (
      <main className='page-main page-shell mx-auto px-4 py-6'>
        <Breadcrumb
          items={[
            { label: "گزارش‌های روزانه", href: base },
            { label: "خطا" },
          ]}
        />
        <QueryErrorState onRetry={() => void reportQuery.refetch()} />
      </main>
    );
  }

  if (!report) {
    return (
      <main className='page-main page-shell mx-auto px-4 py-6'>
        <Breadcrumb
          items={[
            { label: "گزارش‌های روزانه", href: base },
            { label: "یافت نشد" },
          ]}
        />
        <EmptyState
          title='گزارش یافت نشد'
          action={
            <Link to={base} className='text-sm text-primary underline'>
              بازگشت به فهرست
            </Link>
          }
        />
      </main>
    );
  }

  const tabProps = {
    projectId,
    reportId,
    report,
    readOnly: true,
    onChanged: () => {},
    activityOptions,
    subcontractorOptions: [],
  };

  return (
    <main className='page-main page-shell mx-auto  px-4 py-6'>
      <Breadcrumb
        items={[
          { label: "گزارش‌های روزانه", href: base },
          { label: `گزارش ${formatDisplayDate(report.report_date)}` },
        ]}
      />
      <PageHeader
        title={t("dailyReports.referenceHeader.title", {
          date: formatDisplayDate(header?.report_date ?? report.report_date),
          day: header?.day_of_week ?? report.day_of_week,
        })}
        subtitle={
          report.prepared_by_name
            ? t("dailyReports.referenceHeader.preparer", { name: header?.prepared_by_name ?? report.prepared_by_name })
            : undefined
        }
        actions={
          <div className='flex gap-2'>
            {!report.is_auto_summary &&
            (report.status === "draft" || report.status === "rejected") ? (
              <Link
                to={`${base}/${reportId}/edit`}
                className='rounded-md border border-border px-4 py-2 text-sm hover:bg-muted/40'
              >
                ویرایش
              </Link>
            ) : null}
            <button
              type='button'
              onClick={exportExcel}
              disabled={downloadingExcel}
              className='inline-flex items-center gap-1 rounded-md border border-border bg-card px-4 py-2 text-sm text-foreground hover:bg-muted disabled:opacity-50'
            >
              <Download className='size-4' />
              {t("dailyReports.referenceHeader.dailyExcel")}
            </button>
            <button
              type='button'
              onClick={exportPdf}
              disabled={downloading}
              className='inline-flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50'
            >
              <Download className='size-4' />
              {t("dailyReports.referenceHeader.dailyPdf")}
            </button>
          </div>
        }
      />

      <div className='space-y-5'>
        {headerQuery.isError ? <QueryErrorState onRetry={() => void headerQuery.refetch()} /> : null}
        {header ? (
          <div className='grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-2 lg:grid-cols-4'>
            <Info label={t("dailyReports.referenceHeader.project")} value={header.project_name} />
            <Info label={t("dailyReports.referenceHeader.contract")} value={header.contract_number ?? unknown} />
            <Info label={t("dailyReports.referenceHeader.number")} value={header.official_numbering.official_report_number ?? unknown} />
            <Info label={t("dailyReports.referenceHeader.day")} value={String(header.official_numbering.project_day ?? unknown)} />
            <Info label={t("dailyReports.referenceHeader.wind")} value={header.weather.wind_speed ?? unknown} />
            <Info label={t("dailyReports.referenceHeader.ground")} value={header.weather.soil_condition ?? unknown} />
            <Info label={t("dailyReports.referenceHeader.forecast", { provider: header.weather.forecast_provider })}
              value={header.weather.forecast_days.map(
                (day) => `${formatDisplayDate(day.date)} · ${day.air_temperature_c} °C`,
              ).join("\n") || unknown}
            />
            <Info label={t("dailyReports.referenceHeader.shifts")}
              value={header.worked_shifts.map((shift) => t("dailyReports.referenceHeader.shiftLine", {
                shift: shift.shift_id,
                start: shiftTimestamp(shift.actual_start_at),
                end: shiftTimestamp(shift.actual_end_at),
                duration: shift.actual_duration_hours ?? unknown,
              })).join("\n") || unknown}
            />
          </div>
        ) : null}
        <ApprovalStatusBar
          projectId={projectId}
          report={report}
          canApprove={canApprove}
          canEdit={canEdit}
          busy={workflow.isPending}
          onSubmit={() => workflow.mutate({ type: "submit" })}
          onReview={() => workflow.mutate({ type: "review" })}
          onApprove={() => workflow.mutate({ type: "approve" })}
          onReject={(reason) => workflow.mutate({ type: "reject", reason })}
        />

        {report.is_auto_summary ? (
          <>
            <DailyReportSummaryView
              report={report}
              projectName={projectQuery.data?.project_name}
              contractNumber={projectQuery.data?.contract_number}
              employer={projectQuery.data?.employer}
            />
            {canEdit ? (
              <div
                className='space-y-4 rounded-xl border border-border bg-card p-4'
                data-testid='summary-metadata-editor'
              >
                <div>
                  <label className='mb-2 block text-sm font-medium' htmlFor='mgmt-opinion'>
                    {t("dailyReports.summary.managementOpinion")}
                  </label>
                  <textarea
                    id='mgmt-opinion'
                    className='min-h-24 w-full rounded-md border border-border bg-background p-2 text-sm'
                    value={opinion}
                    onChange={(e) => setOpinion(e.target.value)}
                  />
                </div>
                <div className='grid gap-3 sm:grid-cols-2'>
                  <label className='flex items-center gap-2 text-sm'>
                    <input
                      type='checkbox'
                      checked={weatherOverride}
                      onChange={(e) => setWeatherOverride(e.target.checked)}
                      data-testid='weather-override-toggle'
                    />
                    {t("dailyReports.summary.weatherOverride", "لغو خودکار شرایط جوی")}
                  </label>
                  <label className='flex items-center gap-2 text-sm'>
                    <input
                      type='checkbox'
                      checked={siteOverride}
                      onChange={(e) => setSiteOverride(e.target.checked)}
                      data-testid='site-override-toggle'
                    />
                    {t("dailyReports.summary.siteOverride", "لغو خودکار وضعیت کارگاه")}
                  </label>
                  {weatherOverride ? (
                    <div className='block text-sm' data-testid='weather-override-value'>
                      <span className='mb-1 block text-muted-foreground'>{t("weather.condition")}</span>
                      <WeatherSelector
                        value={weather as WeatherCondition}
                        onChange={(w) => setWeather(w)}
                        id='summary-weather-override'
                      />
                    </div>
                  ) : null}
                  {siteOverride ? (
                    <label className='block text-sm'>
                      <span className='mb-1 block text-muted-foreground'>{t("weather.siteStatus")}</span>
                      <select
                        className='w-full rounded-md border border-border bg-background p-2'
                        value={siteStatus}
                        onChange={(e) => {
                          const next = e.target.value;
                          setSiteStatus(next);
                          if (next === "active") setInactivityReason("");
                        }}
                        data-testid='site-override-value'
                      >
                        <option value='active'>{t("common.active")}</option>
                        <option value='inactive'>{t("common.inactive")}</option>
                      </select>
                    </label>
                  ) : null}
                </div>

                <div className='grid gap-3 sm:grid-cols-2'>
                  <div>
                    <label htmlFor='summary-temp-max' className='mb-1 block text-sm text-muted-foreground'>
                      {t("weather.tempMax")} (°C)
                    </label>
                    <input
                      id='summary-temp-max'
                      type='number'
                      step='0.1'
                      min={-40}
                      max={60}
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={tempMax}
                      onChange={(e) => {
                        setTempMax(e.target.value);
                        setServerTempErrors((prev) => ({ ...prev, max: null }));
                      }}
                      aria-invalid={inlineTempMaxError ? true : undefined}
                      aria-describedby={inlineTempMaxError ? 'summary-temp-max-error' : undefined}
                    />
                    {inlineTempMaxError ? (
                      <p id='summary-temp-max-error' role='alert' className='mt-1 text-xs text-destructive'>
                        {inlineTempMaxError}
                      </p>
                    ) : null}
                  </div>
                  <div>
                    <label htmlFor='summary-temp-min' className='mb-1 block text-sm text-muted-foreground'>
                      {t("weather.tempMin")} (°C)
                    </label>
                    <input
                      id='summary-temp-min'
                      type='number'
                      step='0.1'
                      min={-40}
                      max={60}
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={tempMin}
                      onChange={(e) => {
                        setTempMin(e.target.value);
                        setServerTempErrors((prev) => ({ ...prev, min: null }));
                      }}
                      aria-invalid={inlineTempMinError ? true : undefined}
                      aria-describedby={inlineTempMinError ? 'summary-temp-min-error' : undefined}
                    />
                    {inlineTempMinError ? (
                      <p id='summary-temp-min-error' role='alert' className='mt-1 text-xs text-destructive'>
                        {inlineTempMinError}
                      </p>
                    ) : null}
                  </div>
                </div>

                {(siteOverride ? siteStatus === "inactive" : report.site_status === "inactive") ? (
                  <div>
                    <label htmlFor='summary-inactivity-reason' className='mb-1 block text-sm font-medium'>
                      {t("dailyReports.inactivityReason", "علت تعطیلی کارگاه")} <span className='text-destructive'>*</span>
                    </label>
                    <select
                      id='summary-inactivity-reason'
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={inactivityReason}
                      onChange={(e) => setInactivityReason(e.target.value)}
                      data-testid='inactivity-reason-select'
                    >
                      <option value=''>{t("dailyReports.selectInactivityReason", "-- انتخاب علت تعطیلی --")}</option>
                      {INACTIVITY_REASONS.map((r) => (
                        <option key={r.value} value={r.value}>
                          {t(`dailyReports.inactivityReasons.${r.value}`, r.label)}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}

                <div>
                  <label htmlFor='summary-weather-impact' className='mb-1 block text-sm font-medium'>
                    {t("dailyReports.weatherImpactNotes", t("weatherImpactNotes", "توضیحات و اثرات شرایط جوی"))}
                  </label>
                  <textarea
                    id='summary-weather-impact'
                    rows={2}
                    dir='auto'
                    className='w-full rounded-md border border-border bg-background p-2 text-sm'
                    placeholder={t("dailyReports.weatherImpactNotesPlaceholder", "توضیح اثر شرایط جوی بر روند کار...")}
                    value={weatherImpactNotes}
                    onChange={(e) => setWeatherImpactNotes(e.target.value)}
                  />
                </div>

                <Button
                  variant='secondary'
                  data-testid='summary-metadata-save'
                  onClick={async () => {
                    const submitVal = validateTemperatures(tempMin, tempMax, { isBlurOrSubmit: true });
                    if (!submitVal.isValid) {
                      if (submitVal.tempMaxError === "temp_max_must_be_gte_temp_min") {
                        const msg = t("errors.temp_max_must_be_gte_temp_min", "دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.");
                        setServerTempErrors({ max: msg });
                        toast.error(msg);
                        return;
                      }
                      if (submitVal.tempMinError || submitVal.tempMaxError) {
                        toast.error(t("errors.temp_range", "دما باید بین ۴۰- تا ۶۰+ باشد"));
                        return;
                      }
                    }
                    const isInactive = siteOverride
                      ? siteStatus === "inactive"
                      : report.site_status === "inactive";
                    if (isInactive && !inactivityReason) {
                      toast.error(t("dailyReports.summary.inactivityReasonRequired"));
                      return;
                    }

                    try {
                      await updateDailyReport(projectId, reportId, {
                        report_date: report.report_date,
                        management_opinion: opinion,
                        weather_override: weatherOverride,
                        site_status_override: siteOverride,
                        temp_min: tempMin === "" ? null : tempMin,
                        temp_max: tempMax === "" ? null : tempMax,
                        weather_impact_notes: weatherImpactNotes,
                        ...(isInactive ? { inactivity_reason: inactivityReason as InactivityReason } : {}),
                        ...(weatherOverride
                          ? { weather_condition: weather as WeatherCondition }
                          : {}),
                        ...(siteOverride
                          ? { site_status: siteStatus as SiteStatus }
                          : {}),
                      });
                      setServerTempErrors({});
                      toast.success(t("dailyReports.summary.metadataSaved"));
                      void refetch();
                    } catch (e: any) {
                      const code = e?.code || e?.response?.data?.error?.code;
                      const details = e?.details || e?.response?.data?.error?.details;
                      const msg =
                        e?.response?.data?.error?.message ||
                        e?.message ||
                        t("dailyReports.summary.metadataSaveFailed");
                      if (code === "temp_max_must_be_gte_temp_min" || details?.temp_max) {
                        const text = t("errors.temp_max_must_be_gte_temp_min", "دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.");
                        setServerTempErrors({ max: text });
                        toast.error(text);
                      } else if (code === "inactivity_reason_required" || msg.includes("inactivity_reason_required")) {
                        toast.error(t("dailyReports.summary.inactivityReasonRequired"));
                      } else {
                        toast.error(msg);
                      }
                    }
                  }}
                >
                  {t("dailyReports.summary.saveMetadata")}
                </Button>
              </div>
            ) : null}
          </>
        ) : (
          <>
            <div className='grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-2 lg:grid-cols-4'>
              <Info label='شیفت' value={report.shift} />
              <Info
                label='وضعیت کارگاه'
                value={
                  report.site_status === "inactive" && report.inactivity_reason_label
                    ? `${report.site_status_label} (${report.inactivity_reason_label})`
                    : report.site_status_label
                }
              />
              <Info
                label='وضعیت جوی'
                value={report.weather_condition_label ?? "—"}
              />
              <Info
                label='دما'
                value={
                  report.temp_max || report.temp_min
                    ? `${report.temp_max ?? "—"} / ${report.temp_min ?? "—"} °C`
                    : "—"
                }
              />
            </div>

            {report.weather_impact_notes ? (
              <div className='rounded-xl border border-border bg-card p-4'>
                <p className='mb-1 text-sm text-muted-foreground'>
                  {t("dailyReports.weatherImpactNotes", t("weatherImpactNotes", "توضیحات و اثرات شرایط جوی"))}
                </p>
                <p className='text-sm whitespace-pre-wrap' dir='auto'>{report.weather_impact_notes}</p>
              </div>
            ) : null}

            {report.general_notes ? (
              <div className='rounded-xl border border-border bg-card p-4'>
                <p className='mb-1 text-sm text-muted-foreground'>توضیحات کلی</p>
                <p className='text-sm'>{report.general_notes}</p>
              </div>
            ) : null}

            <Section title='فعالیت‌های اجرایی'>
              <ActivityTab {...tabProps} />
            </Section>
            <Section title='نیروی انسانی'>
              <LaborTab {...tabProps} />
            </Section>
            <Section title='ماشین‌آلات'>
              <EquipmentTab {...tabProps} />
            </Section>
            <Section title='مصالح'>
              <MaterialsTab {...tabProps} />
            </Section>
            <Section title='بتن‌ریزی'>
              <ConcreteTab {...tabProps} />
            </Section>
            <Section title='کمپ کارگری'>
              <LaborCampTab {...tabProps} />
            </Section>
            <Section title='حوادث و موانع'>
              <IncidentsTab {...tabProps} />
            </Section>
          </>
        )}
      </div>
    </main>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className='text-xs text-muted-foreground'>{label}</p>
      <p className='whitespace-pre-line text-sm font-medium' dir='auto'>{value}</p>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className='rounded-xl border border-border bg-card p-4'>
      <h3 className='mb-3 text-base font-semibold'>{title}</h3>
      {children}
    </div>
  );
}
