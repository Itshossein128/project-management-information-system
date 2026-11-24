import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Download, ExternalLink } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigation, useParams, useSearchParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  activityLogScalarFilters,
  fetchActivityLog,
  fetchActivityLogFilters,
  type ActivityLogSelection,
} from "@/app/lib/api/reports";
import { fetchActivityLogExcel } from "@/app/lib/api/daily-reports";
import { formatDisplayDate, isPersianLanguage, jalaliToIso } from "@/app/lib/jalali-utils";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";

const defaultPageSize = 50;
const selectClass = "min-h-9 rounded-md border border-input bg-background px-3 py-2";
const statuses = ["draft", "submitted", "under_review", "approved", "rejected"] as const;
const columns = [
  "date", "day", "discipline", "parcel", "shift", "activityCode", "description", "zone", "block",
  "floor", "contractor", "headcount", "quantity", "unit", "location", "status", "report",
] as const;
const textFilters = ["q", "location", "headcount", "quantity", "report_id", "activity_id"] as const;

function projectDateBounds() {
  const today = new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Tehran" }).format(new Date());
  const currentMonth = `${today.slice(0, 7)}-01`;
  const lastDay = new Date(Date.parse(currentMonth) - 86_400_000).toISOString().slice(0, 10);
  return {
    current: { from: currentMonth, to: today },
    previous: { from: `${lastDay.slice(0, 7)}-01`, to: lastDay },
  };
}

function ActivityLogContent() {
  const { t, i18n } = useTranslation();
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigation = useNavigation();
  const pendingFilters = useRef<{ origin: string; next: URLSearchParams } | null>(null);
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");
  const [exportingExcel, setExportingExcel] = useState(false);
  const bounds = projectDateBounds();
  const needsDefaultDates = !searchParams.has("date_from") && !searchParams.has("date_to");
  const from = needsDefaultDates ? bounds.current.from : searchParams.get("date_from") ?? "";
  const to = needsDefaultDates ? bounds.current.to : searchParams.get("date_to") ?? "";
  const pageParam = Number(searchParams.get("page"));
  const page = Number.isSafeInteger(pageParam) && pageParam > 0 ? pageParam : 1;
  const sizeParam = Number(searchParams.get("page_size"));
  const pageSize = Number.isSafeInteger(sizeParam) && sizeParam > 0 && sizeParam <= 500 ? sizeParam : defaultPageSize;

  useEffect(() => {
    if (!needsDefaultDates) return;
    const next = new URLSearchParams(searchParams);
    next.set("date_from", from);
    next.set("date_to", to);
    setSearchParams(next, { replace: true });
  }, [from, needsDefaultDates, searchParams, setSearchParams, to]);

  const selection = useMemo<ActivityLogSelection>(() => ({
    ...Object.fromEntries(activityLogScalarFilters.map((filter) => [filter, searchParams.get(filter) || undefined])),
    date_from: from || undefined,
    date_to: to || undefined,
    discipline: (searchParams.get("source_discipline") || searchParams.get("discipline") || "")
      .split(",").map((value) => value.trim()).filter(Boolean),
    parcel: (searchParams.get("parcel") || "").split(",").map((value) => value.trim()).filter(Boolean),
    approved_only: searchParams.get("approved_only") === "false" ? false : undefined,
  }), [from, searchParams, to]);
  const approvedOnly = selection.approved_only !== false;

  function updateFilters(updates: Record<string, string>) {
    const origin = window.location.search;
    const previous = pendingFilters.current?.origin === origin
      ? pendingFilters.current.next
      : new URLSearchParams(origin);
    const next = new URLSearchParams(previous);
    if (!("page" in updates)) next.delete("page");
    if ("discipline" in updates) next.delete("source_discipline");
    for (const [key, value] of Object.entries(updates)) {
      if (value || key === "date_from" || key === "date_to") next.set(key, value);
      else next.delete(key);
    }
    if (next.toString() === previous.toString()) return;
    pendingFilters.current = { origin, next };
    setSearchParams(next);
  }

  useEffect(() => {
    if (navigation.state === "idle") pendingFilters.current = null;
  }, [navigation.state, searchParams]);

  const optionsQuery = useQuery({
    queryKey: ["activity-log-filters", projectId, approvedOnly],
    queryFn: () => fetchActivityLogFilters(projectId, approvedOnly),
    enabled: canView && Boolean(projectId),
  });

  const listQuery = useQuery({
    queryKey: ["activity-log", projectId, selection, page, pageSize],
    queryFn: () => fetchActivityLog(projectId, { ...selection, page, page_size: pageSize }),
    enabled: canView && Boolean(projectId),
    staleTime: 0,
    refetchOnWindowFocus: true,
    // An approval in another session must become visible while the log is open.
    refetchInterval: (query) => query.state.status === "error" ? false : 450,
  });

  const options = optionsQuery.data;
  const loading = listQuery.isPending || navigation.state !== "idle";
  const rows = listQuery.isError ? [] : listQuery.data?.results ?? [];
  const totalPages = Math.max(1, Math.ceil((listQuery.data?.count ?? 0) / pageSize));
  const aggregates = listQuery.data?.aggregates;
  const formatNumber = (value: number) => value.toLocaleString(i18n.language, { maximumFractionDigits: 4 });
  const formatDecimal = (value: string) => {
    const decimal = value.includes(".") ? value.replace(/0+$/, "").replace(/\.$/, "") : value;
    return isPersianLanguage(i18n.language) ? decimal.replace(".", "٫").replace(/[0-9]/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]) : decimal;
  };
  const label = (key: string) => t(`reportFilters.${key}`);
  const statusLabel = (status: string) => t(`reportFilters.statuses.${status}`, { defaultValue: status });

  const handleExportExcel = async () => {
    setExportingExcel(true);
    try {
      const blob = await fetchActivityLogExcel(projectId, selection);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "activity-database.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : label("downloadFailed"));
    } finally {
      setExportingExcel(false);
    }
  };

  if (projectLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) {
    return <AccessDenied title={t("common.accessDenied")} description={t("pages.activityLog.accessDeniedDescription")} />;
  }

  const optionFilters = [
    { key: "zone", values: options?.zones },
    { key: "block", values: options?.blocks },
    { key: "floor", values: options?.floors },
    { key: "shift", values: options?.shifts },
    { key: "unit", values: options?.units },
    { key: "status", values: statuses },
  ] as const;
  const contractorValue = selection.contractor_id ?? (selection.subcontractor ? `legacy:${selection.subcontractor}` : "");

  return (
    <div className="space-y-6">
      <PageHeader title={t("pages.activityLog.title")} subtitle={project.project_name} />
      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card p-4">
        <div className="min-w-[15rem]">
          <JalaliDateRangePicker
            name="activity_log_range"
            label={label("dateRange")}
            value={{ from, to }}
            onChange={(range) => updateFilters({ date_from: range.from, date_to: range.to })}
          />
        </div>
        <Button variant="secondary" onClick={() => updateFilters({
          date_from: bounds.previous.from, date_to: bounds.previous.to,
        })}>
          {label("lastMonth")}
        </Button>
        {(["discipline", "parcel"] as const).map((field) => {
          const available = field === "discipline" ? options?.disciplines : options?.parcels;
          const selected = selection[field] as string[];
          // The API accepts case-insensitive values in older shared links.
          const values = [...new Map([...(available ?? []), ...selected].map((value) => [value.toLowerCase(), value])).values()];
          return (
            <label key={field} className="flex flex-col gap-1 text-sm">
              {label(field)}
              <select
                className={selectClass}
                aria-label={label(field)}
                multiple
                size={3}
                value={selected}
                onChange={(event) => updateFilters({
                  [field]: Array.from(event.target.selectedOptions, (option) => option.value).join(","),
                })}
              >
                {values.map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>
          );
        })}
        <label className="flex flex-col gap-1 text-sm">
          {label("contractor")}
          <select
            className={selectClass}
            aria-label={label("contractor")}
            value={contractorValue}
            onChange={(event) => {
              const value = event.target.value;
              const legacy = value.startsWith("legacy:");
              updateFilters({ contractor_id: legacy ? "" : value, subcontractor: legacy ? value.slice(7) : "" });
            }}
          >
            <option value="">{label("all")}</option>
            {(options?.contractors ?? []).map(({ id, name }) => <option key={id} value={id}>{name}</option>)}
            {selection.contractor_id && !options?.contractors?.some(({ id }) => id === selection.contractor_id) && (
              <option value={selection.contractor_id}>{label("unavailable")}</option>
            )}
            {[...new Set([...(options?.subcontractors ?? []), selection.subcontractor].filter(Boolean))].map((name) => (
              <option key={name} value={`legacy:${name}`}>{name}</option>
            ))}
          </select>
        </label>
        {optionFilters.map(({ key, values }) => {
          const selected = selection[key] ?? "";
          const choices = new Set([...(values ?? []), ...(selected ? [selected] : [])]);
          return (
            <label key={key} className="flex flex-col gap-1 text-sm">
              {label(key)}
              <select className={selectClass} aria-label={label(key)} value={selected} onChange={(event) => updateFilters({ [key]: event.target.value })}>
                <option value="">{label("all")}</option>
                {[...choices].map((value) => (
                  <option key={value} value={value}>
                    {key === "status" ? statusLabel(value) : key === "shift" ? t(`reportFilters.shifts.${value}`, { defaultValue: value }) : value}
                  </option>
                ))}
              </select>
            </label>
          );
        })}
        <label className="flex flex-col gap-1 text-sm">
          {label("policy")}
          <select className={selectClass} aria-label={label("policy")} value={approvedOnly ? "approved" : "preview"} onChange={(event) =>
            updateFilters({ approved_only: event.target.value === "preview" ? "false" : "" })
          }>
            <option value="approved">{label("official")}</option>
            <option value="preview">{label("preview")}</option>
          </select>
        </label>
        {textFilters.map((field) => (
          <label key={field} className="flex flex-col gap-1 text-sm">
            {label(field === "report_id" ? "reportReference" : field === "activity_id" ? "activityReference" : field)}
            <input
              key={selection[field] ?? ""}
              className={selectClass}
              type={field === "headcount" || field === "quantity" ? "number" : "text"}
              step={field === "quantity" ? "any" : undefined}
              defaultValue={selection[field] ?? ""}
              onBlur={(event) => {
                const value = event.target.value.trim();
                if (value !== (selection[field] ?? "")) updateFilters({ [field]: value });
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") event.currentTarget.blur();
              }}
            />
          </label>
        ))}
        {optionsQuery.isError && <QueryErrorState onRetry={() => void optionsQuery.refetch()} />}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-card p-4">
        <div className="flex flex-wrap items-center gap-4" data-testid="activity-log-totals">
          {!loading && listQuery.data && aggregates && !listQuery.isError && (
            <>
              <span data-testid="activity-result-count" data-count={listQuery.data.count}>
                {label("resultCount")} <strong>{formatNumber(listQuery.data.count)}</strong>
              </span>
              <span data-testid="activity-headcount-sum" data-count={aggregates.headcount_sum}>
                {label("headcountSum")} <strong>{formatNumber(aggregates.headcount_sum)}</strong>
              </span>
              {aggregates.quantity_by_unit.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <span>{label("quantityTotals")}</span>
                  {aggregates.quantity_by_unit.map(({ unit, total, measured_count, unknown_count }) => (
                    <span key={unit} data-unit={unit} data-total={total ?? undefined} className="rounded-md bg-muted px-2 py-1 text-sm">
                      <strong>{total === null ? label("unknown") : formatDecimal(total)}</strong> {unit}
                      <span className="ms-1 text-muted-foreground">
                        ({t("reportFilters.quantityCoverage", { measured: formatNumber(measured_count), unknown: formatNumber(unknown_count) })})
                      </span>
                    </span>
                  ))}
                </div>
              )}
              {aggregates.unknown_quantity_without_unit_count > 0 && (
                <span>{t("reportFilters.unknownUnit", { count: formatNumber(aggregates.unknown_quantity_without_unit_count) })}</span>
              )}
            </>
          )}
        </div>
        <Button variant="secondary" size="sm" disabled={exportingExcel || listQuery.isError || loading} onClick={handleExportExcel}>
          <Download aria-hidden="true" className="size-4" />
          {label("file1")}
        </Button>
      </div>

      {loading ? (
        <div role="status" aria-label={t("common.loading")}><LoadingSkeleton rows={8} /></div>
      ) : listQuery.isError ? (
        <QueryErrorState onRetry={() => void listQuery.refetch()} message={listQuery.error.message} error={listQuery.error} />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>{columns.map((field) => <th key={field} scope="col" className="px-3 py-2 text-start">{label(field)}</th>)}</tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr><td colSpan={columns.length} className="px-3 py-6 text-center text-muted-foreground">{label("empty")}</td></tr>
                ) : rows.map((row) => {
                  const isoDate = jalaliToIso(row.report_date);
                  const day = isoDate ? new Date(isoDate).toLocaleDateString(i18n.language, {
                    weekday: "long", timeZone: "UTC",
                  }) : row.day_name;
                  const details = { activityCode: row.activity_name, description: row.activity_description, location: row.location };
                  const cells = [
                    isPersianLanguage(i18n.language) ? formatDisplayDate(row.report_date) : isoDate,
                    day, row.source_discipline, row.parcel,
                    t(`reportFilters.shifts.${row.shift}`, { defaultValue: row.shift }),
                    row.activity_code, row.activity_description, row.zone, row.block, row.floor,
                    row.subcontractor, row.headcount == null ? null : formatNumber(row.headcount),
                    row.quantity == null ? label("unknown") : formatNumber(row.quantity),
                    row.unit, row.location, statusLabel(row.report_status),
                  ];
                  return (
                    <tr key={row.id} data-testid="activity-log-row" data-row-id={row.id} className="border-t border-border">
                      {cells.map((value, index) => {
                        const column = columns[index];
                        const title = column in details ? details[column as keyof typeof details] ?? undefined : undefined;
                        return <td key={column} data-field={column} title={title} className="px-3 py-2">{value || "—"}</td>;
                      })}
                      <td className="px-3 py-2">
                        <Link
                          to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${row.report_id}/view`}
                          title={row.report_id}
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          <ExternalLink aria-hidden="true" className="size-3.5" />
                          {t("common.view")}
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => updateFilters({ page: String(page - 1) })}>
                {label("previousPage")}
              </Button>
              <span className="text-sm text-muted-foreground">{t("reportFilters.pages", { page, total: totalPages })}</span>
              <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => updateFilters({ page: String(page + 1) })}>
                {label("nextPage")}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function ProjectActivityLogPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[
          { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
          { label: t("pages.activityLog.title") },
        ]} />
        <ActivityLogContent />
      </ProjectProvider>
    </main>
  );
}
