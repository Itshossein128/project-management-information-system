import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowUp, CalendarDays, CloudOff, LayoutList, Plus } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import DateObject from "react-date-object";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import {
  createWeatherLog,
  deleteWeatherLog,
  fetchWeatherLogs,
  updateWeatherLog,
  type WeatherLog,
} from "@/app/lib/api/weather";
import { isoToJalali } from "@/app/lib/jalali-utils";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { Modal } from "@/components/overlay/modal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { WeatherIcon, WEATHER_CALENDAR_COLORS } from "@/components/weather/weather-icons";
import { WeatherLogDrawer, formToPayload } from "@/components/weather/weather-log-drawer";

type ViewMode = "table" | "calendar";
type SortKey = "log_date" | "temp_max" | "temp_min";

export interface WeatherLogGridProps {
  projectId: string;
}

export function WeatherLogGrid({ projectId }: WeatherLogGridProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();

  const [viewMode, setViewMode] = useState<ViewMode>("table");
  const [page, setPage] = useState(1);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });
  const [sortKey, setSortKey] = useState<SortKey>("log_date");
  const [sortAsc, setSortAsc] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<WeatherLog | null>(null);
  const [presetDateIso, setPresetDateIso] = useState<string | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<WeatherLog | null>(null);

  const [calendarMonth, setCalendarMonth] = useState(() =>
    new DateObject({ calendar: persian, locale: persian_fa }),
  );

  const ordering = sortAsc ? sortKey : `-${sortKey}`;

  const calendarRange = useMemo(() => {
    const start = calendarMonth.toFirstOfMonth();
    const end = calendarMonth.toLastOfMonth();
    return {
      from: start.convert(undefined as unknown as never).format("YYYY-MM-DD"),
      to: end.convert(undefined as unknown as never).format("YYYY-MM-DD"),
    };
  }, [calendarMonth]);

  const listParams = viewMode === "calendar"
    ? { page: 1, per_page: 100, date_from: calendarRange.from, date_to: calendarRange.to, ordering: "-log_date" as const }
    : { page, per_page: 50, date_from: dateRange.from, date_to: dateRange.to, ordering };

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["weather-logs", projectId, listParams],
    queryFn: () => fetchWeatherLogs(projectId, listParams),
  });

  const logs = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const perPage = viewMode === "calendar" ? 100 : 50;
  const totalPages = Math.max(1, Math.ceil(totalCount / perPage));

  const logsByJalaliDate = useMemo(() => {
    const map = new Map<string, WeatherLog>();
    for (const log of logs) map.set(log.log_date, log);
    return map;
  }, [logs]);

  const saveMutation = useMutation({
    mutationFn: async ({ form, id }: { form: ReturnType<typeof formToPayload>; id?: string }) => {
      if (id) return updateWeatherLog(projectId, id, form);
      return createWeatherLog(projectId, form);
    },
    onSuccess: () => {
      toast.success(editTarget ? "گزارش جوی به‌روزرسانی شد" : "گزارش جوی ثبت شد");
      setDrawerOpen(false);
      setEditTarget(null);
      void qc.invalidateQueries({ queryKey: ["weather-logs", projectId] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteWeatherLog(projectId, id),
    onSuccess: () => {
      toast.success("گزارش جوی حذف شد");
      setDeleteTarget(null);
      void qc.invalidateQueries({ queryKey: ["weather-logs", projectId] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc((v) => !v);
    else {
      setSortKey(key);
      setSortAsc(key !== "log_date");
    }
    setPage(1);
  };

  const openCreate = (dateIso?: string) => {
    setEditTarget(null);
    setPresetDateIso(dateIso);
    setDrawerOpen(true);
  };

  const SortHeader = ({ label, col }: { label: string; col: SortKey }) => (
    <button
      type="button"
      className="inline-flex items-center gap-1 font-medium hover:text-foreground"
      onClick={() => toggleSort(col)}
    >
      {label}
      {sortKey === col ? (sortAsc ? <ArrowUp className="size-3.5" /> : <ArrowDown className="size-3.5" />) : null}
    </button>
  );

  const calendarDays = useMemo(() => {
    const start = calendarMonth.toFirstOfWeek();
    const end = calendarMonth.toLastOfWeek();
    const days: DateObject[] = [];
    let cursor = start;
    while (cursor.toDays() <= end.toDays()) {
      days.push(cursor);
      cursor = cursor.add(1, "day");
    }
    return days;
  }, [calendarMonth]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        {viewMode === "table" ? (
          <div className="min-w-[240px] flex-1">
            <JalaliDateRangePicker
              name="weather_date_range"
              label="بازه تاریخ"
              value={dateRange}
              onChange={(v) => {
                setDateRange(v);
                setPage(1);
              }}
              placeholder="از تاریخ تا تاریخ"
            />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setCalendarMonth((m) => m.subtract(1, "month"))}
            >
              ماه قبل
            </Button>
            <span className="min-w-[8rem] text-center font-medium">
              {calendarMonth.format("MMMM YYYY")}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setCalendarMonth((m) => m.add(1, "month"))}
            >
              ماه بعد
            </Button>
          </div>
        )}
        <div className="flex gap-2">
          <Button
            variant={viewMode === "table" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setViewMode("table")}
          >
            <LayoutList className="size-4" />
            جدول
          </Button>
          <Button
            variant={viewMode === "calendar" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setViewMode("calendar")}
          >
            <CalendarDays className="size-4" />
            تقویم
          </Button>
          <Button variant="primary" size="sm" onClick={() => openCreate()}>
            <Plus className="size-4" />
            افزودن
          </Button>
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : viewMode === "table" ? (
        logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center text-muted-foreground">
            <CloudOff className="mb-3 size-10 opacity-50" />
            <p>گزارش جویی برای این بازه ثبت نشده است</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full min-w-[720px] text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/50">
                    <th className="px-4 py-3 text-start"><SortHeader label="تاریخ" col="log_date" /></th>
                    <th className="px-4 py-3 text-start">روز</th>
                    <th className="px-4 py-3 text-start"><SortHeader label="حداکثر دما" col="temp_max" /></th>
                    <th className="px-4 py-3 text-start"><SortHeader label="حداقل دما" col="temp_min" /></th>
                    <th className="px-4 py-3 text-start">وضعیت جوی</th>
                    <th className="px-4 py-3 text-start">وضعیت کارگاه</th>
                    <th className="px-4 py-3 text-start">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((row) => (
                    <tr key={row.id} className="border-b border-border last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3">{row.log_date}</td>
                      <td className="px-4 py-3">{row.day_of_week}</td>
                      <td className="px-4 py-3">{row.temp_max ?? "—"}</td>
                      <td className="px-4 py-3">{row.temp_min ?? "—"}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center gap-1.5">
                          <WeatherIcon condition={row.weather_condition} className="size-4" />
                          {row.weather_condition_label}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={row.site_status === "active" ? "success" : "neutral"}
                          label={row.site_status_label}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm" onClick={() => { setEditTarget(row); setDrawerOpen(true); }}>
                            ویرایش
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => setDeleteTarget(row)}>
                            حذف
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>
                {t("grid.pageInfo", {
                  page,
                  totalPages,
                  count: totalCount,
                })}
              </span>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm" disabled={page <= 1 || isFetching} onClick={() => setPage((p) => p - 1)}>
                  {t("grid.prev")}
                </Button>
                <Button variant="secondary" size="sm" disabled={page >= totalPages || isFetching} onClick={() => setPage((p) => p + 1)}>
                  {t("grid.next")}
                </Button>
              </div>
            </div>
          </>
        )
      ) : (
        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 grid grid-cols-7 gap-1 text-center text-xs text-muted-foreground">
            {["ش", "ی", "د", "س", "چ", "پ", "ج"].map((d) => (
              <div key={d}>{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {calendarDays.map((day) => {
              const iso = day.convert(undefined as unknown as never).format("YYYY-MM-DD");
              const jalali = isoToJalali(iso);
              const log = logsByJalaliDate.get(jalali);
              const inMonth = day.month.number === calendarMonth.month.number;
              const inactive = log?.site_status === "inactive";
              const colorClass = log
                ? WEATHER_CALENDAR_COLORS[log.weather_condition]
                : "bg-muted/30 text-muted-foreground";

              return (
                <button
                  key={iso}
                  type="button"
                  className={`flex min-h-[4.5rem] flex-col items-center justify-start rounded-md p-1 text-xs transition hover:ring-2 hover:ring-ring ${colorClass} ${!inMonth ? "opacity-40" : ""} ${inactive ? "opacity-50 grayscale" : ""}`}
                  onClick={() => {
                    if (log) {
                      setEditTarget(log);
                      setDrawerOpen(true);
                    } else if (inMonth) {
                      openCreate(iso);
                    }
                  }}
                  title={log ? log.weather_condition_label : inMonth ? "افزودن گزارش" : undefined}
                >
                  <span className="font-medium">{day.format("D")}</span>
                  {log ? (
                    <WeatherIcon condition={log.weather_condition} className="mt-1 size-4" />
                  ) : inMonth ? (
                    <Plus className="mt-1 size-3 opacity-40" />
                  ) : null}
                </button>
              );
            })}
          </div>
        </div>
      )}

      <WeatherLogDrawer
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); setEditTarget(null); }}
        initial={editTarget}
        presetDateIso={presetDateIso}
        loading={saveMutation.isPending}
        onSubmit={async (form) => {
          await saveMutation.mutateAsync({
            form: formToPayload(form),
            id: editTarget?.id,
          });
        }}
      />

      <Modal
        open={deleteTarget !== null}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
        title="حذف گزارش جوی"
        idBase="deleteWeather"
      >
        <p className="mb-4 text-sm text-muted-foreground">
          آیا از حذف گزارش جوی تاریخ {deleteTarget?.log_date} اطمینان دارید؟
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>لغو</Button>
          <Button
            variant="danger"
            loading={deleteMutation.isPending}
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
          >
            حذف
          </Button>
        </div>
      </Modal>
    </div>
  );
}
