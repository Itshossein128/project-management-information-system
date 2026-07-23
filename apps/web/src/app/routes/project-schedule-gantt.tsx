import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router";
import Gantt from "frappe-gantt";
import "frappe-gantt/dist/frappe-gantt.css";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchActivity } from "@/app/lib/api/activities";
import { downloadGanttPdf, fetchGantt, type GanttTask } from "@/app/lib/api/gantt";
import { PATHS } from "@/app/routeVars";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { Checkbox, Select } from "@/components/form";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";

function daysBetween(start: string | null, end: string | null): number | null {
  if (!start || !end) return null;
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return Math.round(ms / (1000 * 60 * 60 * 24));
}

function BaselineComparisonTable({ tasks }: { tasks: GanttTask[] }) {
  const { t } = useTranslation();

  const rows = tasks.filter((t) => t.baseline_start || t.baseline_end);
  if (rows.length === 0) return null;

  return (
    <div className="overflow-x-auto rounded-lg border" data-testid="gantt-baseline-compare">
      <h3 className="border-b bg-muted/50 px-4 py-2 text-sm font-medium">مقایسه برنامه جاری با خط مبنا</h3>
      <table className="w-full min-w-[800px] text-sm">
        <thead className="bg-muted/30">
          <tr>
            {["فعالیت", "شروع برنامه", "پایان برنامه", "شروع مبنا", "پایان مبنا", "انحراف (روز)"].map((h) => (
              <th key={h} className="px-3 py-2 text-start">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((t) => {
            const plannedDays = daysBetween(t.start, t.end);
            const baselineDays = daysBetween(t.baseline_start, t.baseline_end);
            const variance =
              plannedDays != null && baselineDays != null ? plannedDays - baselineDays : null;
            return (
              <tr key={t.id} className="border-t">
                <td className="px-3 py-2">{t.wbs_code ? `${t.wbs_code} — ` : ""}{t.name}</td>
                <td className="px-3 py-2">{t.start ? formatDisplayDate(t.start) : "—"}</td>
                <td className="px-3 py-2">{t.end ? formatDisplayDate(t.end) : "—"}</td>
                <td className="px-3 py-2">{t.baseline_start ? formatDisplayDate(t.baseline_start) : "—"}</td>
                <td className="px-3 py-2">{t.baseline_end ? formatDisplayDate(t.baseline_end) : "—"}</td>
                <td
                  className={`px-3 py-2 ${variance != null && variance > 0 ? "text-danger-600" : variance != null && variance < 0 ? "text-success-600" : ""}`}
                >
                  {variance != null ? `${variance > 0 ? "+" : ""}${variance}` : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function GanttContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_activities");
  const containerRef = useRef<HTMLDivElement>(null);
  const ganttRef = useRef<Gantt | null>(null);

  const [viewMode, setViewMode] = useState<"Day" | "Week" | "Month" | "Year">("Week");
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [showBaselineCompare, setShowBaselineCompare] = useState(true);
  const [baselineId, setBaselineId] = useState("");
  const [selectedTask, setSelectedTask] = useState<GanttTask | null>(null);

  const {
    data,
    isLoading: loadingGantt,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["gantt", projectId, baselineId],
    queryFn: () => fetchGantt(projectId, baselineId || undefined),
    enabled: canView,
  });

  const { data: selectedActivity } = useQuery({
    queryKey: ["activity", projectId, selectedTask?.activity_id],
    queryFn: () => fetchActivity(projectId, selectedTask!.activity_id),
    enabled: Boolean(selectedTask?.activity_id),
  });

  const chartTasks =
    data?.tasks
      ?.filter((t) => t.start && t.end)
      .filter((t) => !criticalOnly || t.is_critical) ?? [];

  useEffect(() => {
    if (!data?.tasks?.length || !containerRef.current) return;
    const taskByCode = new Map(data.tasks.map((t) => [t.id, t]));
    const tasks = data.tasks
      .filter((t) => t.start && t.end)
      .filter((t) => !criticalOnly || t.is_critical)
      .map((t) => ({
        id: t.id,
        name: `${t.wbs_code ? `${t.wbs_code} — ` : ""}${t.name}`,
        start: t.start!,
        end: t.end!,
        progress: t.progress,
        dependencies: t.dependencies || undefined,
        custom_class:
          t.is_critical
            ? "bar-critical"
            : t.status === "completed"
              ? "bar-done"
              : "bar-normal",
      }));

    if (tasks.length === 0) return;

    containerRef.current.innerHTML = "";
    ganttRef.current = new Gantt(containerRef.current, tasks, {
      view_mode: viewMode,
      language: "fa",
      readonly: true,
      bar_height: 24,
      padding: 18,
      on_click: (task) => {
        const row = taskByCode.get(task.id);
        if (row) setSelectedTask(row);
      },
    });
  }, [data, viewMode, criticalOnly]);

  const exportPdf = async () => {
    const blob = await downloadGanttPdf(projectId, baselineId || undefined);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "gantt.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading || loadingGantt) return <LoadingSkeleton rows={12} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <EmptyState
        title={t("common.accessDenied")}
        description="برای مشاهده گانت به مجوز فعالیت‌ها نیاز است."
      />
    );
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }

  return (
    <div className="space-y-4">
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: "گانت" },
        ]}
      />
      <PageHeader title={t("pages.gantt.title")} subtitle={project.project_name} />

      <div className="flex flex-wrap items-end gap-3">
        <Select
          name="gantt_baseline"
          label="خط مبنا"
          value={baselineId || "current"}
          onChange={(e) =>
            setBaselineId(e.target.value === "current" ? "" : e.target.value)
          }
          options={[
            { value: "current", label: "خط مبنای جاری" },
            ...(data?.baselines ?? []).map((b) => ({
              value: b.id,
              label: `${b.name}${b.is_current ? " (جاری)" : ""}`,
            })),
          ]}
          fieldClassName="min-w-[12rem]"
        />
        {(["Day", "Week", "Month", "Year"] as const).map((mode) => (
          <Button
            key={mode}
            variant={viewMode === mode ? "primary" : "secondary"}
            size="sm"
            onClick={() => setViewMode(mode)}
          >
            {mode === "Day"
              ? "روز"
              : mode === "Week"
                ? "هفته"
                : mode === "Month"
                  ? "ماه"
                  : "سال"}
          </Button>
        ))}
        <Button
          variant="secondary"
          size="sm"
          onClick={() => ganttRef.current?.scroll_current?.()}
        >
          امروز
        </Button>
        <Checkbox
          name="critical_only"
          label="فقط مسیر بحرانی"
          checked={criticalOnly}
          onChange={(e) =>
            setCriticalOnly(
              Boolean((e.target as unknown as { value: boolean }).value),
            )
          }
          fieldClassName="pb-2"
        />
        <Checkbox
          name="show_baseline_compare"
          label="جدول مقایسه مبنا"
          checked={showBaselineCompare}
          onChange={(e) =>
            setShowBaselineCompare(
              Boolean((e.target as unknown as { value: boolean }).value),
            )
          }
          fieldClassName="pb-2"
        />
        <Button variant="secondary" size="sm" onClick={() => void exportPdf()}>
          خروجی PDF
        </Button>
      </div>

      {data?.baseline_name ? (
        <p className="text-sm text-muted-foreground">خط مبنا: {data.baseline_name}</p>
      ) : null}

      {chartTasks.length === 0 ? (
        <EmptyState
          title="فعالیتی برای نمایش در گانت نیست"
          description="فعالیت‌ها باید تاریخ شروع و پایان برنامه‌ای داشته باشند."
        />
      ) : (
        <div
          className="gantt-container overflow-x-auto rounded-lg border p-4"
          ref={containerRef}
        />
      )}

      {showBaselineCompare && chartTasks.length > 0 ? (
        <BaselineComparisonTable tasks={chartTasks} />
      ) : null}

      <style>{`
        .bar-critical .bar { fill: var(--palette-danger-600) !important; }
        .bar-done .bar { fill: var(--palette-success-600) !important; }
        .bar-normal .bar { fill: var(--palette-info-600) !important; }
        .gantt-container .grid-row { direction: rtl; }
      `}</style>

      {selectedTask ? (
        <Drawer
          isOpen
          onClose={() => setSelectedTask(null)}
          title={selectedTask.name}
        >
          <dl className="grid gap-2 text-sm">
            <div><dt className="text-muted-foreground">کد WBS</dt><dd>{selectedTask.wbs_code || "—"}</dd></div>
            <div><dt className="text-muted-foreground">شروع برنامه</dt><dd>{selectedTask.start ? formatDisplayDate(selectedTask.start) : "—"}</dd></div>
            <div><dt className="text-muted-foreground">پایان برنامه</dt><dd>{selectedTask.end ? formatDisplayDate(selectedTask.end) : "—"}</dd></div>
            <div><dt className="text-muted-foreground">شروع مبنا</dt><dd>{selectedTask.baseline_start ? formatDisplayDate(selectedTask.baseline_start) : "—"}</dd></div>
            <div><dt className="text-muted-foreground">پایان مبنا</dt><dd>{selectedTask.baseline_end ? formatDisplayDate(selectedTask.baseline_end) : "—"}</dd></div>
            <div><dt className="text-muted-foreground">پیشرفت</dt><dd>{selectedTask.progress}٪</dd></div>
            <div><dt className="text-muted-foreground">مسئول</dt><dd>{selectedTask.responsible || "—"}</dd></div>
            {selectedActivity ? (
              <div><dt className="text-muted-foreground">وضعیت</dt><dd>{selectedActivity.status}</dd></div>
            ) : null}
          </dl>
          <p className="mt-4 text-xs text-muted-foreground">نمایش فقط‌خواندنی — برای ویرایش به صفحه فعالیت‌ها بروید.</p>
        </Drawer>
      ) : null}
    </div>
  );
}

export default function ProjectScheduleGanttPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <main className="page-main page-shell mx-auto max-w-[100vw] px-4 py-8">
        <GanttContent />
      </main>
    </ProjectProvider>
  );
}
