import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router";
import {
  CloudOff,
  Download,
  Eye,
  FileText,
  Pencil,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import { usePermission } from "@/app/contexts/project-context";
import { useTranslation } from "react-i18next";
import { PATHS } from "@/app/routeVars";
import { getStoredActorId } from "@/app/lib/auth-storage";
import { warmProjectCache } from "@/app/lib/offlineCache";
import {
  getFailedQueue,
  getOfflineReportsByProject,
  getQueueStats,
  isOfflineDBAvailable,
  type OfflineReport,
  type QueueItem,
} from "@/app/lib/offlineDB";
import { syncPendingQueue } from "@/app/lib/syncService";
import {
  type DailyReportListParams,
  type ReportStatus,
  STATUS_BADGE,
  WEATHER_META,
  deleteDailyReport,
  downloadDailyReportWorkbook,
  ensureDailyReportByDate,
  fetchDailyReportByDate,
  fetchDailyReports,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDate, isPersianLanguage, isoToJalali, jalaliToIso } from "@/app/lib/jalali-utils";
import { fetchActivityLogFilters } from "@/app/lib/api/reports";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Input, Select } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";

const STATUS_FILTERS = ["draft", "submitted", "under_review", "approved", "rejected"] as const;

function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: string;
}) {
  return (
    <div className='rounded-xl border border-border bg-card p-4'>
      <p className='text-sm text-muted-foreground'>{label}</p>
      <p className={`mt-1 text-2xl font-bold ${tone}`}>{value}</p>
    </div>
  );
}

function ReportDateFilter({
  name, label, value, onCommit,
}: {
  name: string;
  label: string;
  value: string;
  onCommit: (value: string | null) => void;
}) {
  const { i18n, t } = useTranslation();
  const persian = isPersianLanguage(i18n.language);
  const displayed = persian ? isoToJalali(value) || value : value;
  const [text, setText] = useState(displayed);
  const [invalid, setInvalid] = useState(false);
  useEffect(() => {
    setText(displayed);
    setInvalid(false);
  }, [displayed]);

  const commit = () => {
    const local = text.trim()
      .replace(/[۰-۹]/g, (digit) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit)))
      .replace(/[٠-٩]/g, (digit) => String("٠١٢٣٤٥٦٧٨٩".indexOf(digit)));
    const jalaliInput = /^\d{4}\/\d{2}\/\d{2}$/.test(local);
    const iso = jalaliInput ? jalaliToIso(local) : local;
    const parsed = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? new Date(`${iso}T00:00:00Z`) : null;
    const valid = !local || (
      parsed !== null && Number.isFinite(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === iso &&
      (!jalaliInput || isoToJalali(iso) === local)
    );
    setInvalid(!valid);
    onCommit(valid ? iso : null);
  };

  return (
    <label className="grid gap-1.5 text-sm font-medium">
      <span>{label}</span>
      <Input name={name} dir="ltr" value={text} placeholder={persian ? "۱۴۰۶/۰۳/۰۱" : "YYYY-MM-DD"}
        aria-invalid={invalid || undefined}
        aria-describedby={invalid ? `${name}-error` : undefined}
        onChange={(event) => setText(event.target.value)}
        onBlur={commit}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            event.currentTarget.blur();
          }
        }}
      />
      {invalid ? <span id={`${name}-error`} className="text-destructive">{t("dailyReports.referenceHeader.invalidDate")}</span> : null}
    </label>
  );
}

export default function DailyReportsListPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");

  const isOnline = useOnlineStatus();
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo<DailyReportListParams>(() => {
    const page = Number(searchParams.get("page")) || 1;
    const date_from = searchParams.get("date_from") || undefined;
    const date_to = searchParams.get("date_to") || undefined;
    const status = (searchParams.get("status") || undefined) as ReportStatus | undefined;
    return {
      page,
      per_page: 20,
      date_from,
      date_to,
      status,
      discipline: searchParams.get("discipline") || undefined,
      contractor: searchParams.get("contractor") || undefined,
      block: searchParams.get("block") || undefined,
    };
  }, [searchParams]);

  const setFilter = useCallback((patch: Partial<DailyReportListParams>) => {
    // A date field can commit while React is still rendering the previous
    // location. Preserve the filters already present in the browser URL.
    const sp = new URLSearchParams(window.location.search);
    Object.entries(patch).forEach(([k, v]) => {
      if (v === undefined || v === null || v === "" || v === "all" || v === "__all__") {
        sp.delete(k);
      } else {
        sp.set(k, String(v));
      }
    });
    if (!("page" in patch)) {
      sp.delete("page");
    }
    setSearchParams(sp);
  }, [setSearchParams]);
  const [openDate, setOpenDate] = useState("");
  const [openingDate, setOpeningDate] = useState(false);
  const [offlineRows, setOfflineRows] = useState<OfflineReport[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [downloadingRange, setDownloadingRange] = useState(false);
  const [dateErrors, setDateErrors] = useState({ date_from: false, date_to: false });

  const commitDate = (field: "date_from" | "date_to", date: string | null) => {
    setDateErrors((previous) => ({ ...previous, [field]: date === null }));
    if (date !== null && date !== (filters[field] ?? "")) setFilter({ [field]: date || undefined });
  };

  const exportRange = async () => {
    // Keyboard activation can follow a date blur before React rerenders.
    const committedDates = new URLSearchParams(window.location.search);
    const first = committedDates.get("date_from");
    const last = committedDates.get("date_to");
    if (dateErrors.date_from || dateErrors.date_to) {
      toast.error(t("dailyReports.referenceHeader.invalidDate"));
      return;
    }
    if (!first || !last) {
      toast.error(t("dailyReports.referenceHeader.rangeDatesRequired"));
      return;
    }
    setDownloadingRange(true);
    try {
      await downloadDailyReportWorkbook(projectId, first, last);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : t("dailyReports.referenceHeader.downloadFailed"));
    } finally {
      setDownloadingRange(false);
    }
  };

  const listQuery = useQuery({
    queryKey: ["daily-reports", projectId, filters],
    queryFn: () => fetchDailyReports(projectId, filters),
  });

  const optionsQuery = useQuery({
    queryKey: ["activity-log-filters", projectId, false],
    queryFn: () => fetchActivityLogFilters(projectId, false),
    enabled: Boolean(projectId) && has("view_reports"),
  });
  const choices = optionsQuery.data;

  const loadOffline = useCallback(async () => {
    if (!isOfflineDBAvailable() || !projectId) return;
    try {
      const actorId = getStoredActorId();
      const [rows, stats] = await Promise.all([
        getOfflineReportsByProject(projectId),
        getQueueStats(actorId),
      ]);
      setOfflineRows(rows.filter((r) => r._offline));
      setPendingCount(stats.pending + stats.failed);
    } catch {
      /* db not ready */
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) void warmProjectCache(projectId);
  }, [projectId]);

  useEffect(() => {
    void loadOffline();
  }, [loadOffline, listQuery.data]);

  const syncNow = async () => {
    setSyncing(true);
    try {
      const result = await syncPendingQueue();
      if (result.synced > 0)
        toast.success(t("toast.manualSyncSynced", { count: result.synced }));
      if (result.conflicts > 0)
        toast.error(t("toast.manualSyncConflicts", { count: result.conflicts }));
      await queryClient.invalidateQueries({
        queryKey: ["daily-reports", projectId],
      });
      await loadOffline();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setSyncing(false);
    }
  };

  const rows = listQuery.data?.results ?? [];
  const total = listQuery.data?.count ?? 0;

  const stats = useMemo(() => {
    const s = { total, approved: 0, pending: 0, draft: 0 };
    for (const r of rows) {
      if (r.status === "approved") s.approved++;
      else if (r.status === "submitted" || r.status === "under_review")
        s.pending++;
      else if (r.status === "draft") s.draft++;
    }
    return s;
  }, [rows, total]);

  const removeMutation = useMutation({
    mutationFn: (reportId: string) => deleteDailyReport(projectId, reportId),
    onSuccess: () => {
      toast.success("گزارش حذف شد");
      void queryClient.invalidateQueries({
        queryKey: ["daily-reports", projectId],
      });
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const base = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;

  return (
    <main className='page-main page-shell mx-auto  px-4 py-6' data-testid="daily-reports-list">
      <Breadcrumb
        items={[
          {
            label: "پروژه",
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: "گزارش‌های روزانه" },
        ]}
      />
      <PageHeader title={t("pages.dailyReports.title")} />

      {pendingCount > 0 ? (
        <div className='mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-warning-300 bg-warning-50 px-4 py-3 text-sm text-warning-900 dark:bg-warning-950/30 dark:text-warning-200'>
          <span className='flex items-center gap-2'>
            <CloudOff className='size-4' />
            {`${pendingCount} تغییر همگام‌سازی نشده در این دستگاه وجود دارد`}
          </span>
          <button
            type='button'
            data-testid='daily-reports-sync-now'
            disabled={!isOnline || syncing}
            onClick={syncNow}
            className='inline-flex items-center gap-1 rounded-md bg-warning-600 px-3 py-1.5 text-white hover:bg-warning-700 disabled:opacity-50'
          >
            <RefreshCw className={syncing ? "size-4 animate-spin" : "size-4"} />
            همگام‌سازی اکنون
          </button>
        </div>
      ) : null}

      {offlineRows.length > 0 ? (
        <div className='mb-4 rounded-xl border border-border bg-card p-4'>
          <p className='mb-2 text-sm font-medium text-muted-foreground'>
            گزارش‌های ذخیره‌شده آفلاین
          </p>
          <ul className='space-y-2'>
            {offlineRows.map((r) => (
              <li
                key={r.local_id}
                className='flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm'
              >
                <span className='flex items-center gap-2'>
                  <Badge variant='warning' label='آفلاین' />
                  {formatDisplayDate(r.report_date)}
                </span>
                <span className='flex items-center gap-1 text-warning-600'>
                  <CloudOff className='size-4' />
                  در انتظار همگام‌سازی
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className='mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
        <StatCard
          label='کل گزارش‌ها'
          value={stats.total}
          tone='text-foreground'
        />
        <StatCard
          label='تأیید شده'
          value={stats.approved}
          tone='text-success-600'
        />
        <StatCard
          label='در انتظار'
          value={stats.pending}
          tone='text-warning-600'
        />
        <StatCard
          label='پیش‌نویس'
          value={stats.draft}
          tone='text-muted-foreground'
        />
      </div>

      <div className='mb-4 grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-3'>
        <ReportDateFilter
          name='date_from'
          label={t("dailyReports.referenceHeader.dateFrom")}
          value={filters.date_from ?? ""}
          onCommit={(day) => commitDate("date_from", day)}
        />
        <ReportDateFilter
          name='date_to'
          label={t("dailyReports.referenceHeader.dateTo")}
          value={filters.date_to ?? ""}
          onCommit={(day) => commitDate("date_to", day)}
        />
        <Select
          name='status'
          label={t("reportFilters.status")}
          value={filters.status ?? "all"}
          onChange={(e) =>
            setFilter({
              status: (e.target.value === "all" ? undefined : e.target.value) as
                | ReportStatus
                | undefined,
            })
          }
          options={[
            { value: "all", label: t("reportFilters.all") },
            ...STATUS_FILTERS.map((status) => ({ value: status, label: t(`reportFilters.statuses.${status}`) })),
          ]}
        />
        <Select
          name="discipline"
          label={t("reportFilters.discipline")}
          value={filters.discipline ?? "__all__"}
          onChange={(event) => setFilter({ discipline: event.target.value })}
          options={[
            { value: "__all__", label: t("reportFilters.all") },
            ...(choices?.disciplines ?? []).map((value) => ({ value, label: value })),
          ]}
        />
        <Select
          name="contractor"
          label={t("reportFilters.contractor")}
          value={filters.contractor ?? "__all__"}
          onChange={(event) => setFilter({ contractor: event.target.value })}
          options={[
            { value: "__all__", label: t("reportFilters.all") },
            ...(choices?.contractors ?? []).map(({ id, name }) => ({ value: id, label: name })),
          ]}
        />
        <Select
          name="block"
          label={t("reportFilters.block")}
          value={filters.block ?? "__all__"}
          onChange={(event) => setFilter({ block: event.target.value })}
          options={[
            { value: "__all__", label: t("reportFilters.all") },
            ...(choices?.blocks ?? []).map((value) => ({ value, label: value })),
          ]}
        />
        {optionsQuery.isError && <QueryErrorState onRetry={() => void optionsQuery.refetch()} />}
        <Button type="button" disabled={downloadingRange || !isOnline} onClick={() => void exportRange()}>
          <Download aria-hidden="true" className="size-4" />
          {t(`dailyReports.referenceHeader.${downloadingRange ? "downloading" : "rangeWorkbook"}`)}
        </Button>
      </div>

      <div className='mb-4 flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card p-4'>
        <div className='min-w-[200px] flex-1'>
          <JalaliDatePicker
            name='open_date'
            label={t("dailyReports.summary.openByDate", "نمایش گزارش روز")}
            value={openDate}
            onChange={(iso) => setOpenDate(iso || "")}
          />
        </div>
        <Button
          variant='primary'
          data-testid='daily-report-open-by-date'
          disabled={!openDate || openingDate}
          onClick={async () => {
            if (!openDate || !projectId) return;
            setOpeningDate(true);
            try {
              if (canEdit) {
                const report = await ensureDailyReportByDate(projectId, openDate);
                void navigate(`${base}/${report.report_id}/view`);
              } else {
                const report = await fetchDailyReportByDate(projectId, openDate);
                void navigate(`${base}/${report.report_id}/view`);
              }
            } catch (e) {
              toast.error((e as Error).message);
            } finally {
              setOpeningDate(false);
            }
          }}
        >
          {openingDate ? "…" : t("dailyReports.summary.open", "نمایش")}
        </Button>
      </div>

      {listQuery.isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : listQuery.isError ? (
        <QueryErrorState onRetry={() => void listQuery.refetch()} />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={<FileText />}
          title={t("dailyReports.summary.emptyTitle", "گزارشی یافت نشد")}
          description={t(
            "dailyReports.summary.emptyDesc",
            "پس از ارسال گزارش‌های واحد تخصصی، جمع‌بندی روزانه اینجا دیده می‌شود. تاریخ را انتخاب کنید.",
          )}
        />
      ) : (
        <div className='overflow-x-auto rounded-xl border border-border'>
          <table className='w-full min-w-[760px] text-sm'>
            <thead>
              <tr className='bg-muted/50 text-muted-foreground'>
                <th className='px-3 py-2 text-right font-medium'>تاریخ</th>
                <th className='px-3 py-2 text-right font-medium'>روز</th>
                <th className='px-3 py-2 text-right font-medium'>
                  وضعیت کارگاه
                </th>
                <th className='px-3 py-2 text-right font-medium'>جوی</th>
                <th className='px-3 py-2 text-center font-medium'>فعالیت</th>
                <th className='px-3 py-2 text-center font-medium'>نفرات</th>
                <th className='px-3 py-2 text-right font-medium'>تهیه‌کننده</th>
                <th className='px-3 py-2 text-right font-medium'>وضعیت</th>
                <th className='px-3 py-2 text-center font-medium'>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const canEditRow =
                  r.status === "draft" || r.status === "rejected";
                return (
                  <tr
                    key={r.report_id}
                    className='border-t border-border hover:bg-muted/20'
                    data-testid={`daily-report-row-${r.report_id}`}
                  >
                    <td className='px-3 py-2'>
                      {formatDisplayDate(r.report_date)}
                    </td>
                    <td className='px-3 py-2'>{r.day_of_week}</td>
                    <td className='px-3 py-2'>
                      <Badge
                        variant={
                          r.site_status === "active" ? "success" : "neutral"
                        }
                        label={r.site_status_label}
                      />
                    </td>
                    <td className='px-3 py-2'>
                      {r.weather_condition ? (
                        <span title={r.weather_condition_label ?? ""}>
                          {WEATHER_META[r.weather_condition].icon}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className='px-3 py-2 text-center'>
                      {r.activity_count}
                    </td>
                    <td className='px-3 py-2 text-center'>{r.labor_total}</td>
                    <td className='px-3 py-2'>{r.prepared_by_name ?? "—"}</td>
                    <td className='px-3 py-2'>
                      <Badge
                        variant={STATUS_BADGE[r.status]}
                        label={r.status_label}
                      />
                    </td>
                    <td className='px-3 py-2'>
                      <div className='flex items-center justify-center gap-1'>
                        <Link
                          to={`${base}/${r.report_id}/view`}
                          title='مشاهده'
                          aria-label='مشاهده'
                          className='rounded p-1 text-muted-foreground hover:bg-muted'
                        >
                          <Eye className='size-4' />
                        </Link>
                        {canEdit && canEditRow ? (
                          <Link
                            to={`${base}/${r.report_id}/edit`}
                            title='ویرایش'
                            aria-label='ویرایش'
                            data-testid={`daily-report-edit-${r.report_id}`}
                            className='rounded p-1 text-info-600 hover:bg-muted'
                          >
                            <Pencil className='size-4' />
                          </Link>
                        ) : null}
                        <Link
                          to={`${base}/${r.report_id}/view`}
                          title='خروجی PDF'
                          aria-label='خروجی PDF'
                          className='rounded p-1 text-muted-foreground hover:bg-muted'
                        >
                          <FileText className='size-4' />
                        </Link>
                        {canEdit && r.status === "draft" ? (
                          <button
                            type='button'
                            title={t("common.delete")}
                            aria-label={t("common.delete")}
                            onClick={() => {
                              if (confirm("این گزارش حذف شود؟"))
                                removeMutation.mutate(r.report_id);
                            }}
                            className='rounded p-1 text-danger-600 hover:bg-muted'
                          >
                            <Trash2 className='size-4' />
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {total > (filters.per_page ?? 20) ? (
        <div className='mt-4 flex items-center justify-center gap-2'>
          <button
            type='button'
            disabled={(filters.page ?? 1) <= 1}
            onClick={() =>
              setFilter({ page: (filters.page ?? 1) - 1 })
            }
            className='rounded-md border border-border px-3 py-1 text-sm disabled:opacity-40'
          >
            {t("reportFilters.previousPage")}
          </button>
          <span className='text-sm text-muted-foreground'>
            {t("reportFilters.page", { page: filters.page ?? 1 })}
          </span>
          <button
            type='button'
            disabled={(filters.page ?? 1) * (filters.per_page ?? 20) >= total}
            onClick={() =>
              setFilter({ page: (filters.page ?? 1) + 1 })
            }
            className='rounded-md border border-border px-3 py-1 text-sm disabled:opacity-40'
          >
            {t("reportFilters.nextPage")}
          </button>
        </div>
      ) : null}
    </main>
  );
}
