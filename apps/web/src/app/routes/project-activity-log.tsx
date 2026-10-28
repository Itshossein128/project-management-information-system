import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Download, ExternalLink, Users } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  fetchActivityLog,
  fetchActivityLogFilters,
} from "@/app/lib/api/reports";
import { fetchActivityLogExcel } from "@/app/lib/api/daily-reports";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Button } from "@/components/ui/sprint-button";

function monthStartIso() {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10);
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function ActivityLogContent() {
  const { t } = useTranslation();
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();

  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");

  const [exportingExcel, setExportingExcel] = useState(false);

  const dateRange = useMemo(
    () => ({
      from: searchParams.get("date_from") || monthStartIso(),
      to: searchParams.get("date_to") || todayIso(),
    }),
    [searchParams]
  );

  const discipline = useMemo(() => {
    const raw = searchParams.get("discipline");
    return raw ? raw.split(",").filter(Boolean) : [];
  }, [searchParams]);

  const parcel = useMemo(() => {
    const raw = searchParams.get("parcel");
    return raw ? raw.split(",").filter(Boolean) : [];
  }, [searchParams]);

  const zone = searchParams.get("zone") || "";
  const block = searchParams.get("block") || "";
  const subcontractor = searchParams.get("subcontractor") || "";
  const page = Number(searchParams.get("page")) || 1;

  const updateFilters = useCallback(
    (updates: Record<string, string | string[] | number | undefined>) => {
      setSearchParams(
        (prev) => {
          const sp = new URLSearchParams(prev);
          Object.entries(updates).forEach(([k, v]) => {
            if (
              v === undefined ||
              v === null ||
              v === "" ||
              (Array.isArray(v) && v.length === 0)
            ) {
              sp.delete(k);
            } else if (Array.isArray(v)) {
              sp.set(k, v.join(","));
            } else {
              sp.set(k, String(v));
            }
          });
          return sp;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  const { data: filters } = useQuery({
    queryKey: ["activity-log-filters", projectId],
    queryFn: () => fetchActivityLogFilters(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data, isLoading } = useQuery({
    queryKey: [
      "activity-log",
      projectId,
      dateRange,
      discipline,
      parcel,
      zone,
      block,
      subcontractor,
      page,
    ],
    queryFn: () =>
      fetchActivityLog(projectId, {
        date_from: dateRange.from,
        date_to: dateRange.to,
        source_discipline: discipline.length ? discipline : undefined,
        parcel: parcel.length ? parcel : undefined,
        zone: zone || undefined,
        block: block || undefined,
        subcontractor: subcontractor || undefined,
        page,
        page_size: 50,
      }),
    enabled: canView && Boolean(projectId),
  });

  const rows = data?.results ?? [];
  const totalPages = data ? Math.ceil(data.count / 50) : 1;

  const totalHeadcount = useMemo(() => {
    return rows.reduce((acc, r) => acc + (Number(r.headcount) || 0), 0);
  }, [rows]);

  const quantitiesByUnit = useMemo(() => {
    const map: Record<string, number> = {};
    for (const r of rows) {
      if (r.unit && r.quantity != null && !isNaN(Number(r.quantity))) {
        map[r.unit] = (map[r.unit] || 0) + Number(r.quantity);
      }
    }
    return map;
  }, [rows]);

  const handleExportExcel = async () => {
    if (!projectId) return;
    setExportingExcel(true);
    try {
      const blob = await fetchActivityLogExcel(projectId, {
        date_from: dateRange.from,
        date_to: dateRange.to,
        discipline: discipline.length ? discipline.join(",") : undefined,
        parcel: parcel.length ? parcel.join(",") : undefined,
        zone: zone || undefined,
        block: block || undefined,
        subcontractor: subcontractor || undefined,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `activity-database-${dateRange.from}-to-${dateRange.to}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      toast.error((e as Error).message || "خطا در دانلود اکسل دیتابیس فعالیت‌ها");
    } finally {
      setExportingExcel(false);
    }
  };

  if (projectLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;

  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("pages.activityLog.accessDeniedDescription", {
          defaultValue: "نقش شما مجوز مشاهده گزارش‌ها را ندارد.",
        })}
      />
    );
  }

  return (
    <div className='space-y-6'>
      <PageHeader title={t("pages.activityLog.title")} subtitle={project.project_name} />

      {/* Multidimensional Filters */}
      <div className='flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card p-4'>
        <div className='min-w-[260px] flex-1'>
          <JalaliDateRangePicker
            name='activity_log_range'
            label='بازه تاریخ'
            value={dateRange}
            onChange={(v) => {
              updateFilters({ date_from: v.from, date_to: v.to, page: undefined });
            }}
          />
        </div>
        <label className='flex flex-col gap-1 text-sm'>
          <span>دیسیپلین</span>
          <select
            className='rounded-md border border-input bg-background px-3 py-2'
            multiple
            value={discipline}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, (option) => option.value);
              updateFilters({ discipline: selected, page: undefined });
            }}
          >
            {(filters?.disciplines ?? []).map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <label className='flex flex-col gap-1 text-sm'>
          <span>قطعه</span>
          <select
            className='rounded-md border border-input bg-background px-3 py-2'
            multiple
            value={parcel}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, (option) => option.value);
              updateFilters({ parcel: selected, page: undefined });
            }}
          >
            {(filters?.parcels ?? []).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className='flex flex-col gap-1 text-sm'>
          <span>زون</span>
          <select
            className='rounded-md border border-input bg-background px-3 py-2'
            value={zone}
            onChange={(e) => {
              updateFilters({ zone: e.target.value, page: undefined });
            }}
          >
            <option value=''>همه</option>
            {(filters?.zones ?? []).map((z) => (
              <option key={z} value={z}>
                {z}
              </option>
            ))}
          </select>
        </label>
        <label className='flex flex-col gap-1 text-sm'>
          <span>بلوک</span>
          <select
            className='rounded-md border border-input bg-background px-3 py-2'
            value={block}
            onChange={(e) => {
              updateFilters({ block: e.target.value, page: undefined });
            }}
          >
            <option value=''>همه</option>
            {(filters?.blocks ?? []).map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </label>
        <label className='flex flex-col gap-1 text-sm'>
          <span>پیمانکار</span>
          <select
            className='rounded-md border border-input bg-background px-3 py-2'
            value={subcontractor}
            onChange={(e) => {
              updateFilters({ subcontractor: e.target.value, page: undefined });
            }}
          >
            <option value=''>همه</option>
            {(filters?.subcontractors ?? []).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Prominent Aggregate Summary Bar & FILE 1 Export Button */}
      <div className='flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-card p-4'>
        <div className='flex flex-wrap items-center gap-6 text-sm'>
          <div className='flex items-center gap-2'>
            <Users className='size-5 text-primary' />
            <span className='text-muted-foreground'>مجموع نفرات (نفر-روز):</span>
            <span className='font-bold text-foreground'>{totalHeadcount}</span>
          </div>
          {Object.keys(quantitiesByUnit).length > 0 ? (
            <div className='flex flex-wrap items-center gap-2'>
              <BarChart3 className='size-5 text-primary' />
              <span className='text-muted-foreground'>احجام اجرایی:</span>
              {Object.entries(quantitiesByUnit).map(([unitName, totalQty]) => (
                <span
                  key={unitName}
                  className='inline-flex items-center gap-1 rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-foreground'
                >
                  <span>{unitName}:</span>
                  <span className='font-bold'>
                    {Number(totalQty.toFixed(2)).toLocaleString()}
                  </span>
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <Button
          variant='outline'
          size='sm'
          disabled={exportingExcel}
          onClick={handleExportExcel}
          className='inline-flex items-center gap-1.5'
        >
          <Download className='size-4' />
          خروجی اکسل دیتابیس جامع فعالیت‌ها (FILE 1)
        </Button>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : (
        <>
          <div className='overflow-x-auto rounded-lg border border-border'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50'>
                <tr>
                  {[
                    "تاریخ",
                    "روز",
                    "دیسیپلین",
                    "قطعه",
                    "شیفت",
                    "فعالیت",
                    "شرح",
                    "زون",
                    "بلوک",
                    "طبقه",
                    "پیمانکار",
                    "نفر",
                    "مقدار",
                    "واحد",
                    "مکان",
                    "گزارش",
                  ].map((h) => (
                    <th key={h} className='px-3 py-2 text-start'>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td
                      colSpan={16}
                      className='px-3 py-6 text-center text-muted-foreground'
                    >
                      فعالیتی یافت نشد
                    </td>
                  </tr>
                ) : (
                  rows.map((r) => (
                    <tr key={r.id} className='border-t border-border'>
                      <td className='px-3 py-2 whitespace-nowrap'>
                        {r.report_date}
                      </td>
                      <td className='px-3 py-2 whitespace-nowrap'>{r.day_name}</td>
                      <td className='px-3 py-2 whitespace-nowrap font-medium'>
                        {r.source_discipline || "—"}
                      </td>
                      <td className='px-3 py-2 whitespace-nowrap'>
                        {r.parcel || "—"}
                      </td>
                      <td className='px-3 py-2 whitespace-nowrap'>{r.shift || "—"}</td>
                      <td className='px-3 py-2'>
                        {r.activity_code ? (
                          <span title={r.activity_name ?? ""}>
                            {r.activity_code}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td
                        className='px-3 py-2 max-w-[180px] truncate'
                        title={r.activity_description}
                      >
                        {r.activity_description || "—"}
                      </td>
                      <td className='px-3 py-2'>{r.zone || "—"}</td>
                      <td className='px-3 py-2'>{r.block || "—"}</td>
                      <td className='px-3 py-2'>{r.floor || "—"}</td>
                      <td className='px-3 py-2'>{r.subcontractor || "—"}</td>
                      <td className='px-3 py-2'>{r.headcount ?? "—"}</td>
                      <td className='px-3 py-2'>
                        {r.quantity != null
                          ? r.quantity
                          : "—"}
                      </td>
                      <td className='px-3 py-2'>{r.unit || "—"}</td>
                      <td className='px-3 py-2 max-w-[180px] truncate' title={r.location}>
                        {r.location || "—"}
                      </td>
                      <td className='px-3 py-2'>
                        <Link
                          to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${r.report_id}/view`}
                          className='inline-flex items-center gap-1 text-primary hover:underline'
                        >
                          <ExternalLink className='size-3.5' />
                          مشاهده
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 ? (
            <div className='flex items-center justify-center gap-2'>
              <Button
                variant='secondary'
                size='sm'
                disabled={page <= 1}
                onClick={() => updateFilters({ page: page - 1 })}
              >
                قبلی
              </Button>
              <span className='text-sm text-muted-foreground'>
                صفحه {page} از {totalPages}
              </span>
              <Button
                variant='secondary'
                size='sm'
                disabled={page >= totalPages}
                onClick={() => updateFilters({ page: page + 1 })}
              >
                بعدی
              </Button>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

export default function ProjectActivityLogPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "بانک فعالیت‌ها" },
          ]}
        />
        <ActivityLogContent />
      </ProjectProvider>
    </main>
  );
}
