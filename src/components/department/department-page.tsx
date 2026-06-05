import { useDepartmentActivityRecordsQuery } from "@/app/hooks/queries";
import type { DepartmentActivityRecord, DepartmentSlug } from "@/app/lib/api-types";
import { apiBlob, apiUploadFile } from "@/app/lib/api-client";
import { Button, Input, JalaliDateRangePicker, type DateRangeValue } from "@/components/form";
import { DataTable, useGridState } from "@/components/grid";
import { DepartmentActivityRecordModal } from "@/components/department/department-activity-record-modal";
import { findDepartmentBySlug } from "@/config/business-departments.config";
import type { ColumnDef } from "@tanstack/react-table";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { apiJson } from "~/lib/api-client";
import { queryKeys } from "~/lib/react-query-keys";
import { PATHS } from "~/routeVars";

const DEPARTMENT_ACTIVITY_RECORDS_PATH = "department-activity-records";

interface BusinessDetail {
  id: number;
  name: string;
  slug: string;
}

export interface DepartmentPageProps {
  /** Route slug segment, e.g. `PATHS.BUSINESS_DEPT.BUILDINGS`. */
  slug: string;
}

export function DepartmentPage({ slug }: DepartmentPageProps) {
  const { t } = useTranslation();
  const { businessId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const businessIdNum = businessId ? Number(businessId) : Number.NaN;

  const dept = findDepartmentBySlug(slug);
  const department = slug as DepartmentSlug;

  const grid = useGridState({ initialPageIndex: 0, initialPageSize: 20 });

  const [dateRange, setDateRange] = useState<DateRangeValue>({ from: "", to: "" });
  const [locationFilter, setLocationFilter] = useState("");
  const [activityFilter, setActivityFilter] = useState("");
  const [contractorFilter, setContractorFilter] = useState("");
  const [unitFilter, setUnitFilter] = useState("");

  const ordering = grid.query.sorting[0]
    ? `${grid.query.sorting[0].desc ? "-" : ""}${grid.query.sorting[0].id}`
    : undefined;

  const activityQuery = useDepartmentActivityRecordsQuery(
    businessId ?? "",
    {
      department,
      page: grid.query.pagination.pageIndex + 1,
      page_size: grid.query.pagination.pageSize,
      search: grid.debouncedSearch?.trim() ? grid.debouncedSearch.trim() : undefined,
      ordering,
      date_from: dateRange.from || undefined,
      date_to: dateRange.to || undefined,
      location: locationFilter.trim() ? locationFilter.trim() : undefined,
      activity_description: activityFilter.trim() ? activityFilter.trim() : undefined,
      contractor: contractorFilter.trim() ? contractorFilter.trim() : undefined,
      unit: unitFilter.trim() ? unitFilter.trim() : undefined,
    },
    isAuthenticated && Boolean(businessId) && !Number.isNaN(businessIdNum),
  );

  const rows = activityQuery.data?.results ?? [];
  const count = activityQuery.data?.count ?? 0;
  const listError =
    activityQuery.error instanceof Error ? activityQuery.error.message : null;

  const [createOpen, setCreateOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [reporting, setReporting] = useState<"daily" | "weekly" | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const importInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const activityExportParams = useMemo(() => {
    const sp = new URLSearchParams();
    sp.set("department", department);
    if (dateRange.from) sp.set("date_from", dateRange.from);
    if (dateRange.to) sp.set("date_to", dateRange.to);
    if (locationFilter.trim()) sp.set("location", locationFilter.trim());
    if (activityFilter.trim()) sp.set("activity_description", activityFilter.trim());
    if (contractorFilter.trim()) sp.set("contractor", contractorFilter.trim());
    if (unitFilter.trim()) sp.set("unit", unitFilter.trim());
    if (grid.debouncedSearch?.trim()) sp.set("search", grid.debouncedSearch.trim());
    if (ordering) sp.set("ordering", ordering);
    return sp;
  }, [
    department,
    dateRange.from,
    dateRange.to,
    locationFilter,
    activityFilter,
    contractorFilter,
    unitFilter,
    grid.debouncedSearch,
    ordering,
  ]);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const handleExportExcel = async () => {
    if (!businessId) return;
    setExporting(true);
    setActionMessage(null);
    try {
      const blob = await apiBlob(
        `/${PATHS.BUSINESS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/export/?${activityExportParams.toString()}`,
      );
      downloadBlob(blob, `${department}_activity_export.xlsx`);
    } catch (e) {
      setActionMessage(
        e instanceof Error ? e.message : t("businessDepartment.activityLog.exportFailed"),
      );
    } finally {
      setExporting(false);
    }
  };

  const handleImportExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !businessId) return;
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      setActionMessage(t("businessDepartment.activityLog.importFailed"));
      return;
    }
    setImporting(true);
    setActionMessage(null);
    try {
      const result = await apiUploadFile<{
        created: number;
        errors: { row: number; errors: Record<string, string> }[];
      }>(
        `/${PATHS.BUSINESS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/import/?department=${department}`,
        file,
      );
      if (result.errors.length > 0) {
        setActionMessage(
          t("businessDepartment.activityLog.importPartial", {
            created: result.created,
            errorCount: result.errors.length,
          }),
        );
      } else {
        setActionMessage(
          t("businessDepartment.activityLog.importSuccess", {
            count: result.created,
          }),
        );
      }
      if (result.created > 0) {
        grid.resetPage();
        void queryClient.invalidateQueries({
          queryKey: queryKeys.departmentActivityRecords(businessId, department),
        });
      }
    } catch (err) {
      setActionMessage(
        err instanceof Error
          ? err.message
          : t("businessDepartment.activityLog.importFailed"),
      );
    } finally {
      setImporting(false);
    }
  };

  const handleDownloadReport = async (period: "daily" | "weekly") => {
    if (!businessId) return;
    setReporting(period);
    setActionMessage(null);
    try {
      const blob = await apiBlob(
        `/${PATHS.BUSINESS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/reports/${period}/?department=${department}`,
      );
      downloadBlob(blob, `${department}_${period}_report.pdf`);
    } catch (e) {
      setActionMessage(
        e instanceof Error ? e.message : t("businessDepartment.activityLog.reportFailed"),
      );
    } finally {
      setReporting(null);
    }
  };

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId) return;
    if (Number.isNaN(businessIdNum)) {
      setError("Invalid business");
      return;
    }
    apiJson<BusinessDetail>(`/${PATHS.BUSINESS}/${businessIdNum}/`)
      .then((b) => {
        setBusiness(b);
        setError(null);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, [isAuthenticated, businessId, businessIdNum]);

  if (isLoading || !isAuthenticated) return null;

  const deptTitle = dept?.labelI18nKey
    ? t(dept.labelI18nKey)
    : slug;

  const columns = useMemo<ColumnDef<DepartmentActivityRecord>[]>(() => {
    return [
      {
        id: "date",
        header: t("businessDepartment.activityLog.columns.date"),
        accessorKey: "date",
        cell: ({ row }) => (
          <span id={`text-departmentActivityDate-${row.index}`}>
            {row.original.date || "—"}
          </span>
        ),
      },
      {
        id: "location",
        header: t("businessDepartment.activityLog.columns.location"),
        accessorKey: "location",
        cell: ({ row }) => (
          <span id={`text-departmentActivityLocation-${row.index}`}>
            {row.original.location || "—"}
          </span>
        ),
      },
      {
        id: "activity_description",
        header: t("businessDepartment.activityLog.columns.activityDescription"),
        accessorKey: "activity_description",
        enableSorting: false,
        cell: ({ row }) => (
          <span id={`text-departmentActivityActivityDescription-${row.index}`}>
            {row.original.activity_description || "—"}
          </span>
        ),
      },
      {
        id: "contractor",
        header: t("businessDepartment.activityLog.columns.contractor"),
        accessorKey: "contractor",
        cell: ({ row }) => (
          <span id={`text-departmentActivityContractor-${row.index}`}>
            {row.original.contractor || "—"}
          </span>
        ),
      },
      {
        id: "unit",
        header: t("businessDepartment.activityLog.columns.unit"),
        accessorKey: "unit",
        cell: ({ row }) => (
          <span id={`text-departmentActivityUnit-${row.index}`}>
            {row.original.unit || "—"}
          </span>
        ),
      },
      {
        id: "description",
        header: t("businessDepartment.activityLog.columns.description"),
        accessorKey: "description",
        enableSorting: false,
        cell: ({ row }) => (
          <span id={`text-departmentActivityDescription-${row.index}`}>
            {row.original.description?.trim() ? row.original.description : "—"}
          </span>
        ),
      },
    ];
  }, [t]);

  return (
    <div className="page-shell" id="container-businessDepartment">
      <DepartmentActivityRecordModal
        open={createOpen}
        onOpenChange={setCreateOpen}
        businessId={businessId ?? ""}
        department={department}
      />
      <header className="page-route-header">
        <div className="page-route-header-inner">
          <div className="page-route-header-title">
            <Button
              id="button-backFromDepartmentToBusiness"
              variant="ghost"
              size="sm"
              type="button"
              onClick={() =>
                navigate(
                  `/${PATHS.BUSINESS}/${businessId ?? ""}`.replace(/\/+$/, ""),
                )
              }
            >
              {t("businessDepartment.back")}
            </Button>
            <h1
              id="text-departmentTitle"
              className="min-w-0 truncate text-base font-semibold sm:text-lg"
            >
              {deptTitle}
            </h1>
            {business && (
              <span
                id="text-departmentBusinessName"
                className="hidden text-muted-foreground text-sm sm:inline"
              >
                {business.name}
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="page-main" id="container-businessDepartmentMain">
        {error && (
          <p
            id="text-departmentError"
            className="mb-4 text-destructive text-sm"
          >
            {error}
          </p>
        )}
        {listError ? (
          <p
            id="text-departmentActivityListError"
            className="mb-4 text-destructive text-sm"
          >
            {listError}
          </p>
        ) : null}
        {actionMessage ? (
          <p
            id="text-departmentActivityActionMessage"
            className="mb-4 text-muted-foreground text-sm"
          >
            {actionMessage}
          </p>
        ) : null}

        <section
          id="container-departmentActivityLog"
          className="space-y-3"
          aria-labelledby="text-departmentActivityLogTitle"
        >
          <div
            id="container-departmentActivityLogHeader"
            className="flex flex-wrap items-center justify-between gap-2"
          >
            <h2 id="text-departmentActivityLogTitle" className="text-xl font-medium">
              {t("businessDepartment.activityLog.title")}
            </h2>
            {activityQuery.isFetching ? (
              <span
                id="text-departmentActivityLogLoading"
                className="text-muted-foreground text-sm"
              >
                {t("common.loading")}
              </span>
            ) : null}
          </div>

          <DataTable
            name="departmentActivityRecords"
            columns={columns}
            data={rows}
            emptyMessage={t("businessDepartment.activityLog.empty")}
            manual
            sorting={grid.query.sorting}
            onSortingChange={(next) => grid.setSorting(next)}
            globalFilter={grid.query.search}
            onGlobalFilterChange={(value) => grid.setSearch(value)}
            pagination={grid.query.pagination}
            onPaginationChange={(next) => grid.setPagination(next)}
            totalCount={count}
            isLoading={activityQuery.isFetching}
            searchPlaceholder={t("businessDepartment.activityLog.searchPlaceholder")}
            toolbarLeftSlot={
              <div
                id="container-departmentActivityFilters"
                className="flex flex-col gap-2 sm:flex-row sm:items-center"
              >
                <div
                  id="container-departmentActivityDateRange"
                  className="w-full sm:min-w-[220px] sm:w-auto"
                >
                  <JalaliDateRangePicker
                    name="departmentActivityDateRange"
                    id="input-departmentActivityDateRange"
                    value={dateRange}
                    onChange={(next) => {
                      setDateRange(next);
                      grid.resetPage();
                    }}
                    placeholder={t("businessDepartment.activityLog.filters.dateRange")}
                  />
                </div>

                <Input
                  id="input-departmentActivityFilterLocation"
                  name="departmentActivityFilterLocation"
                  value={locationFilter}
                  onChange={(e) => {
                    setLocationFilter(e.target.value);
                    grid.resetPage();
                  }}
                  placeholder={t("businessDepartment.activityLog.filters.location")}
                />
                <Input
                  id="input-departmentActivityFilterActivityDescription"
                  name="departmentActivityFilterActivityDescription"
                  value={activityFilter}
                  onChange={(e) => {
                    setActivityFilter(e.target.value);
                    grid.resetPage();
                  }}
                  placeholder={t("businessDepartment.activityLog.filters.activityDescription")}
                />
                <Input
                  id="input-departmentActivityFilterContractor"
                  name="departmentActivityFilterContractor"
                  value={contractorFilter}
                  onChange={(e) => {
                    setContractorFilter(e.target.value);
                    grid.resetPage();
                  }}
                  placeholder={t("businessDepartment.activityLog.filters.contractor")}
                />
                <Input
                  id="input-departmentActivityFilterUnit"
                  name="departmentActivityFilterUnit"
                  value={unitFilter}
                  onChange={(e) => {
                    setUnitFilter(e.target.value);
                    grid.resetPage();
                  }}
                  placeholder={t("businessDepartment.activityLog.filters.unit")}
                />
              </div>
            }
            toolbarRightSlot={
              <div
                id="container-departmentActivityActions"
                className="flex flex-wrap items-center justify-end gap-2"
              >
                <Button
                  id="button-exportDepartmentActivityExcel"
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={exporting}
                  onClick={() => void handleExportExcel()}
                >
                  {exporting
                    ? t("businessDepartment.activityLog.exporting")
                    : t("businessDepartment.activityLog.exportExcel")}
                </Button>
                <input
                  ref={importInputRef}
                  id="input-departmentActivityImportExcel"
                  name="departmentActivityImportExcel"
                  type="file"
                  accept=".xlsx"
                  className="hidden"
                  onChange={(e) => void handleImportExcel(e)}
                />
                <Button
                  id="button-importDepartmentActivityExcel"
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={importing}
                  onClick={() => importInputRef.current?.click()}
                >
                  {importing
                    ? t("businessDepartment.activityLog.importing")
                    : t("businessDepartment.activityLog.importExcel")}
                </Button>
                <Button
                  id="button-departmentActivityDailyReport"
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={reporting !== null}
                  onClick={() => void handleDownloadReport("daily")}
                >
                  {reporting === "daily"
                    ? t("businessDepartment.activityLog.generatingReport")
                    : t("businessDepartment.activityLog.dailyReport")}
                </Button>
                <Button
                  id="button-departmentActivityWeeklyReport"
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={reporting !== null}
                  onClick={() => void handleDownloadReport("weekly")}
                >
                  {reporting === "weekly"
                    ? t("businessDepartment.activityLog.generatingReport")
                    : t("businessDepartment.activityLog.weeklyReport")}
                </Button>
                <Button
                  id="button-openDepartmentActivityCreateModal"
                  type="button"
                  size="sm"
                  onClick={() => setCreateOpen(true)}
                >
                  {t("businessDepartment.activityLog.add")}
                </Button>
              </div>
            }
          />
        </section>
      </main>
    </div>
  );
}
