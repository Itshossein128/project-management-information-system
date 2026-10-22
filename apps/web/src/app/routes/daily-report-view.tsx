import { useTranslation } from "react-i18next";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Download } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { usePermission } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { fetchActivities } from "@/app/lib/api/activities";
import { fetchProject } from "@/app/lib/api/projects";
import {
  approveReport,
  fetchDailyReport,
  fetchReportPdf,
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
  const [opinion, setOpinion] = useState("");
  const [weatherOverride, setWeatherOverride] = useState(false);
  const [siteOverride, setSiteOverride] = useState(false);
  const [weather, setWeather] = useState<string>("");
  const [siteStatus, setSiteStatus] = useState<string>("active");
  const [inactivityReason, setInactivityReason] = useState<string>("");
  const [tempMin, setTempMin] = useState<string>("");
  const [tempMax, setTempMax] = useState<string>("");
  const [weatherImpactNotes, setWeatherImpactNotes] = useState<string>("");

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

  const refetch = () =>
    queryClient.invalidateQueries({
      queryKey: ["daily-report", projectId, reportId],
    });

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
    onError: (e) => toast.error((e as Error).message),
  });

  const exportPdf = async () => {
    setDownloading(true);
    try {
      const blob = await fetchReportPdf(projectId, reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `daily-report-${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setDownloading(false);
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
        title={`گزارش روزانه — ${formatDisplayDate(report.report_date)} (${report.day_of_week})`}
        subtitle={
          report.prepared_by_name
            ? `تهیه‌کننده: ${report.prepared_by_name}`
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
              onClick={exportPdf}
              disabled={downloading}
              className='inline-flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50'
            >
              <Download className='size-4' />
              خروجی PDF
            </button>
          </div>
        }
      />

      <div className='space-y-5'>
        <ApprovalStatusBar
          projectId={projectId}
          report={report}
          canApprove={canApprove}
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
                    نظر مدیریت
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
                    <label className='block text-sm'>
                      <span className='mb-1 block text-muted-foreground'>شرایط جوی</span>
                      <select
                        className='w-full rounded-md border border-border bg-background p-2'
                        value={weather}
                        onChange={(e) => setWeather(e.target.value)}
                        data-testid='weather-override-value'
                      >
                        <option value='clear'>صاف</option>
                        <option value='cloudy'>ابری</option>
                        <option value='rainy'>بارانی</option>
                        <option value='snowy'>برفی</option>
                        <option value='stormy'>طوفانی</option>
                      </select>
                    </label>
                  ) : null}
                  {siteOverride ? (
                    <label className='block text-sm'>
                      <span className='mb-1 block text-muted-foreground'>وضعیت کارگاه</span>
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
                        <option value='active'>فعال</option>
                        <option value='inactive'>تعطیل</option>
                      </select>
                    </label>
                  ) : null}
                </div>

                <div className='grid gap-3 sm:grid-cols-2'>
                  <div>
                    <label htmlFor='summary-temp-max' className='mb-1 block text-sm text-muted-foreground'>
                      حداکثر دما (°C)
                    </label>
                    <input
                      id='summary-temp-max'
                      type='number'
                      step='0.1'
                      min={-40}
                      max={60}
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={tempMax}
                      onChange={(e) => setTempMax(e.target.value)}
                    />
                  </div>
                  <div>
                    <label htmlFor='summary-temp-min' className='mb-1 block text-sm text-muted-foreground'>
                      حداقل دما (°C)
                    </label>
                    <input
                      id='summary-temp-min'
                      type='number'
                      step='0.1'
                      min={-40}
                      max={60}
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={tempMin}
                      onChange={(e) => setTempMin(e.target.value)}
                    />
                  </div>
                </div>

                {(siteOverride ? siteStatus === "inactive" : report.site_status === "inactive") ? (
                  <div>
                    <label htmlFor='summary-inactivity-reason' className='mb-1 block text-sm font-medium'>
                      علت تعطیلی کارگاه <span className='text-destructive'>*</span>
                    </label>
                    <select
                      id='summary-inactivity-reason'
                      className='w-full rounded-md border border-border bg-background p-2 text-sm'
                      value={inactivityReason}
                      onChange={(e) => setInactivityReason(e.target.value)}
                      data-testid='inactivity-reason-select'
                    >
                      <option value=''>-- انتخاب علت تعطیلی --</option>
                      {INACTIVITY_REASONS.map((r) => (
                        <option key={r.value} value={r.value}>
                          {r.label}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}

                <div>
                  <label htmlFor='summary-weather-impact' className='mb-1 block text-sm font-medium'>
                    تأثیرات شرایط جوی بر کارگاه
                  </label>
                  <textarea
                    id='summary-weather-impact'
                    rows={2}
                    className='w-full rounded-md border border-border bg-background p-2 text-sm'
                    placeholder='توضیح اثر شرایط جوی بر روند کار...'
                    value={weatherImpactNotes}
                    onChange={(e) => setWeatherImpactNotes(e.target.value)}
                  />
                </div>

                <Button
                  variant='secondary'
                  data-testid='summary-metadata-save'
                  onClick={async () => {
                    const minN = tempMin !== "" ? Number(tempMin) : null;
                    const maxN = tempMax !== "" ? Number(tempMax) : null;
                    if (minN !== null && (minN < -40 || minN > 60)) {
                      toast.error("حداقل دما باید بین ۴۰- تا ۶۰+ باشد");
                      return;
                    }
                    if (maxN !== null && (maxN < -40 || maxN > 60)) {
                      toast.error("حداکثر دما باید بین ۴۰- تا ۶۰+ باشد");
                      return;
                    }
                    if (minN !== null && maxN !== null && maxN < minN) {
                      toast.error("حداکثر دما باید بزرگتر یا مساوی حداقل دما باشد");
                      return;
                    }
                    const isInactive = siteOverride
                      ? siteStatus === "inactive"
                      : report.site_status === "inactive";
                    if (isInactive && !inactivityReason) {
                      toast.error("علت تعطیلی کارگاه الزامی است");
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
                        inactivity_reason: isInactive ? (inactivityReason as InactivityReason) : null,
                        ...(weatherOverride
                          ? { weather_condition: weather as WeatherCondition }
                          : {}),
                        ...(siteOverride
                          ? { site_status: siteStatus as SiteStatus }
                          : {}),
                      });
                      toast.success("ذخیره شد");
                      void refetch();
                    } catch (e: any) {
                      const msg =
                        e?.response?.data?.error?.message ||
                        e?.message ||
                        "خطا در ثبت اطلاعات";
                      if (msg.includes("temp_max_must_be_gte_temp_min")) {
                        toast.error("حداکثر دما باید بزرگتر یا مساوی حداقل دما باشد");
                      } else if (msg.includes("inactivity_reason_required")) {
                        toast.error("علت تعطیلی کارگاه الزامی است");
                      } else {
                        toast.error(msg);
                      }
                    }
                  }}
                >
                  ذخیره نظر و سربرگ
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
                <p className='mb-1 text-sm text-muted-foreground'>تأثیرات جوی بر کارگاه</p>
                <p className='text-sm whitespace-pre-wrap'>{report.weather_impact_notes}</p>
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
      <p className='text-sm font-medium'>{value}</p>
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
