import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import {
  downloadReportExportByUrl,
  exportProjectReport,
  fetchProjectReportCatalog,
  runProjectReport,
  type ReportCatalogEntry,
} from "@/app/lib/api/standard-reports";
function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function monthStartIso() {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10);
}

function StandardReportsContent() {
  const { t } = useTranslation();
  const toast = useToast();
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard") || has("view_reports");

  const [selectedType, setSelectedType] = useState<string>("");
  const [dateRange, setDateRange] = useState({ from: monthStartIso(), to: todayIso() });
  const [approvedOnly, setApprovedOnly] = useState(true);
  const [previewJson, setPreviewJson] = useState<string>("");

  const { data: catalog, isLoading: catalogLoading, isError, refetch } = useQuery({
    queryKey: ["report-catalog", projectId],
    queryFn: () => fetchProjectReportCatalog(projectId),
    enabled: canView && Boolean(projectId),
  });

  const entries = catalog?.results ?? [];

  useEffect(() => {
    if (entries.length && !selectedType) {
      setSelectedType(entries[0].report_type);
    }
  }, [entries, selectedType]);

  const activeEntry: ReportCatalogEntry | undefined = useMemo(
    () => entries.find((e) => e.report_type === selectedType) ?? entries[0],
    [entries, selectedType],
  );

  const filters = useMemo(() => {
    const f: Record<string, string | boolean> = { approved_only: approvedOnly };
    if (activeEntry?.supported_filters.includes("date_from")) {
      f.date_from = dateRange.from;
    }
    if (activeEntry?.supported_filters.includes("date_to")) {
      f.date_to = dateRange.to;
    }
    return f;
  }, [activeEntry, approvedOnly, dateRange.from, dateRange.to]);

  const runMutation = useMutation({
    mutationFn: () => runProjectReport(projectId, activeEntry!.report_type, filters),
    onSuccess: (body) => {
      setPreviewJson(JSON.stringify(body, null, 2));
    },
    onError: (err: unknown) => {
      toast.error(resolveApiMessage(err, t));
    },
  });

  const exportMutation = useMutation({
    mutationFn: () =>
      exportProjectReport(projectId, activeEntry!.report_type, {
        filters,
        format: "json",
      }),
    onSuccess: async (meta) => {
      toast.success(t("reports.exportSuccess"));
      try {
        const payload = await downloadReportExportByUrl(meta.download_url);
        const blob = new Blob([JSON.stringify(payload, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${meta.report_type}-${meta.id}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err: unknown) {
        toast.error(resolveApiMessage(err, t));
      }
    },
    onError: (err: unknown) => {
      toast.error(resolveApiMessage(err, t));
    },
  });

  if (projectLoading) {
    return <LoadingSkeleton rows={8} />;
  }

  if (!project) {
    return <NotFoundState />;
  }

  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("reports.accessDeniedDescription")}
      />
    );
  }

  const reportType = activeEntry?.report_type ?? selectedType;

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("reports.title") },
        ]}
      />
      <PageHeader title={t("reports.title")} subtitle={t("reports.subtitle")} />

      {isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : catalogLoading ? (
        <LoadingSkeleton rows={8} />
      ) : (
        <div className="space-y-6" data-testid="standard-reports-page">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted-foreground">{t("reports.catalogLabel")}</span>
              <select
                className="rounded-md border border-border bg-background px-3 py-2"
                value={reportType}
                onChange={(e) => setSelectedType(e.target.value)}
                data-testid="report-type-select"
              >
                {entries.map((entry) => (
                  <option key={entry.report_type} value={entry.report_type}>
                    {entry.title}
                  </option>
                ))}
              </select>
            </label>

            {activeEntry?.supported_filters.some((f) => f.startsWith("date_")) ? (
              <JalaliDateRangePicker
                name="report_date_range"
                label={t("reports.dateRange")}
                value={dateRange}
                onChange={setDateRange}
              />
            ) : null}

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={approvedOnly}
                onChange={(e) => setApprovedOnly(e.target.checked)}
              />
              {t("reports.approvedOnly")}
            </label>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              variant="secondary"
              disabled={!reportType || runMutation.isPending}
              onClick={() => runMutation.mutate()}
              data-testid="run-report-btn"
            >
              {t("reports.runPreview")}
            </Button>
            <Button
              variant="primary"
              disabled={!reportType || exportMutation.isPending}
              onClick={() => exportMutation.mutate()}
              data-testid="export-report-btn"
            >
              <Download className="me-2 size-4" aria-hidden />
              {t("reports.export")}
            </Button>
          </div>

          {previewJson ? (
            <pre
              className="max-h-[480px] overflow-auto rounded-lg border border-border bg-muted/30 p-4 text-xs"
              data-testid="report-preview-json"
            >
              {previewJson}
            </pre>
          ) : (
            <p className="text-sm text-muted-foreground">{t("reports.previewHint")}</p>
          )}
        </div>
      )}
    </main>
  );
}

function resolveApiMessage(err: unknown, t: (key: string) => string): string {
  if (err instanceof Error) {
    if (err.message.includes("sod_self_approve")) {
      return t("errors.sod_self_approve");
    }
    return err.message;
  }
  return t("reports.runFailed");
}

export default function ProjectStandardReportsPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <StandardReportsContent />
    </ProjectProvider>
  );
}
