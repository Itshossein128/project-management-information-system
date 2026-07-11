import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import {
  CloudOff,
  Eye,
  FileText,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import { usePermission } from "@/app/contexts/project-context";
import { useTranslation } from "react-i18next";
import { PATHS } from "@/app/routeVars";
import {
  getOfflineReportsByProject,
  getQueueStats,
  isOfflineDBAvailable,
  type OfflineReport,
} from "@/app/lib/offlineDB";
import { syncPendingQueue } from "@/app/lib/syncService";
import {
  type DailyReportListParams,
  type ReportStatus,
  STATUS_BADGE,
  STATUS_LABELS,
  WEATHER_META,
  deleteDailyReport,
  fetchDailyReports,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";

const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: "", label: "همه وضعیت‌ها" },
  { value: "draft", label: STATUS_LABELS.draft },
  { value: "submitted", label: STATUS_LABELS.submitted },
  { value: "under_review", label: STATUS_LABELS.under_review },
  { value: "approved", label: STATUS_LABELS.approved },
  { value: "rejected", label: STATUS_LABELS.rejected },
];

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

export default function DailyReportsListPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");

  const isOnline = useOnlineStatus();
  const [filters, setFilters] = useState<DailyReportListParams>({
    page: 1,
    per_page: 20,
  });
  const [offlineRows, setOfflineRows] = useState<OfflineReport[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);

  const listQuery = useQuery({
    queryKey: ["daily-reports", projectId, filters],
    queryFn: () => fetchDailyReports(projectId, filters),
  });

  const loadOffline = useCallback(async () => {
    if (!isOfflineDBAvailable() || !projectId) return;
    try {
      const [rows, stats] = await Promise.all([
        getOfflineReportsByProject(projectId),
        getQueueStats(),
      ]);
      setOfflineRows(rows.filter((r) => r._offline));
      setPendingCount(stats.pending + stats.failed);
    } catch {
      /* db not ready */
    }
  }, [projectId]);

  useEffect(() => {
    void loadOffline();
  }, [loadOffline, listQuery.data]);

  const syncNow = async () => {
    setSyncing(true);
    try {
      const result = await syncPendingQueue();
      if (result.synced > 0)
        toast.success(`${result.synced} مورد همگام‌سازی شد`);
      if (result.conflicts > 0)
        toast.error(`${result.conflicts} تعارض شناسایی شد`);
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
  const setFilter = (patch: Partial<DailyReportListParams>) =>
    setFilters((prev) => ({ ...prev, page: 1, ...patch }));

  return (
    <main className='page-main page-shell mx-auto  px-4 py-6'>
      <Breadcrumb
        items={[
          {
            label: "پروژه",
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: "گزارش‌های روزانه" },
        ]}
      />
      <PageHeader
        title='گزارش‌های روزانه'
        actions={
          canEdit ? (
            <Link
              to={`${base}/${PATHS.PROJECT_NEW}`}
              className='inline-flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90'
            >
              <Plus className='size-4' />
              گزارش جدید
            </Link>
          ) : null
        }
      />

      {pendingCount > 0 ? (
        <div className='mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-200'>
          <span className='flex items-center gap-2'>
            <CloudOff className='size-4' />
            {`${pendingCount} تغییر همگام‌سازی نشده در این دستگاه وجود دارد`}
          </span>
          <button
            type='button'
            disabled={!isOnline || syncing}
            onClick={syncNow}
            className='inline-flex items-center gap-1 rounded-md bg-amber-600 px-3 py-1.5 text-white hover:bg-amber-700 disabled:opacity-50'
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
                <span className='flex items-center gap-1 text-amber-600'>
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
          tone='text-emerald-600'
        />
        <StatCard
          label='در انتظار'
          value={stats.pending}
          tone='text-amber-600'
        />
        <StatCard
          label='پیش‌نویس'
          value={stats.draft}
          tone='text-muted-foreground'
        />
      </div>

      <div className='mb-4 grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-3'>
        <div>
          <label className='mb-1 block text-xs text-muted-foreground'>
            از تاریخ
          </label>
          <JalaliDatePicker
            name='date_from'
            value={filters.date_from ?? ""}
            onChange={(iso) => setFilter({ date_from: iso || undefined })}
          />
        </div>
        <div>
          <label className='mb-1 block text-xs text-muted-foreground'>
            تا تاریخ
          </label>
          <JalaliDatePicker
            name='date_to'
            value={filters.date_to ?? ""}
            onChange={(iso) => setFilter({ date_to: iso || undefined })}
          />
        </div>
        <div>
          <label className='mb-1 block text-xs text-muted-foreground'>
            وضعیت
          </label>
          <select
            className='h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm'
            value={filters.status ?? ""}
            onChange={(e) =>
              setFilter({
                status: (e.target.value || undefined) as
                  | ReportStatus
                  | undefined,
              })
            }
          >
            {STATUS_FILTERS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {listQuery.isLoading ? (
        <LoadingSkeleton rows={6} />
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
              {rows.length === 0 ? (
                <tr>
                  <td
                    colSpan={9}
                    className='px-3 py-8 text-center text-muted-foreground'
                  >
                    گزارشی یافت نشد
                  </td>
                </tr>
              ) : null}
              {rows.map((r) => {
                const canEditRow =
                  r.status === "draft" || r.status === "rejected";
                return (
                  <tr
                    key={r.report_id}
                    className='border-t border-border hover:bg-muted/20'
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
                          className='rounded p-1 text-muted-foreground hover:bg-muted'
                        >
                          <Eye className='size-4' />
                        </Link>
                        {canEdit && canEditRow ? (
                          <Link
                            to={`${base}/${r.report_id}/edit`}
                            title='ویرایش'
                            className='rounded p-1 text-blue-600 hover:bg-muted'
                          >
                            <Pencil className='size-4' />
                          </Link>
                        ) : null}
                        <Link
                          to={`${base}/${r.report_id}/view`}
                          title='خروجی PDF'
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
                            className='rounded p-1 text-red-600 hover:bg-muted'
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
              setFilters((p) => ({ ...p, page: (p.page ?? 1) - 1 }))
            }
            className='rounded-md border border-border px-3 py-1 text-sm disabled:opacity-40'
          >
            قبلی
          </button>
          <span className='text-sm text-muted-foreground'>
            صفحه {filters.page ?? 1}
          </span>
          <button
            type='button'
            disabled={(filters.page ?? 1) * (filters.per_page ?? 20) >= total}
            onClick={() =>
              setFilters((p) => ({ ...p, page: (p.page ?? 1) + 1 }))
            }
            className='rounded-md border border-border px-3 py-1 text-sm disabled:opacity-40'
          >
            بعدی
          </button>
        </div>
      ) : null}
    </main>
  );
}
