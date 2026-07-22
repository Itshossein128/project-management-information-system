import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router";
import Gantt from "frappe-gantt";
import "frappe-gantt/dist/frappe-gantt.css";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchActivity } from "@/app/lib/api/activities";
import { downloadGanttPdf, fetchGantt } from "@/app/lib/api/gantt";
import { ActivityDrawer } from "@/components/activities/activity-drawer";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function GanttContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const toast = useToast();
  const canView = has("view_activities");
  const containerRef = useRef<HTMLDivElement>(null);
  const ganttRef = useRef<Gantt | null>(null);

  const [viewMode, setViewMode] = useState<"Day" | "Week" | "Month" | "Year">("Week");
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [baselineId, setBaselineId] = useState("");
  const [selectedActivityId, setSelectedActivityId] = useState<string | null>(null);

  const { data, isLoading: loadingGantt } = useQuery({
    queryKey: ["gantt", projectId, baselineId],
    queryFn: () => fetchGantt(projectId, baselineId || undefined),
    enabled: canView,
  });

  const { data: selectedActivity } = useQuery({
    queryKey: ["activity", projectId, selectedActivityId],
    queryFn: () => fetchActivity(projectId, selectedActivityId!),
    enabled: Boolean(selectedActivityId),
  });

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
        custom_class: t.is_critical ? "bar-critical" : t.status === "completed" ? "bar-done" : "bar-normal",
      }));

    containerRef.current.innerHTML = "";
    ganttRef.current = new Gantt(containerRef.current, tasks, {
      view_mode: viewMode,
      language: "fa",
      readonly: true,
      bar_height: 24,
      padding: 18,
      on_click: (task) => {
        const row = taskByCode.get(task.id);
        if (row?.activity_id) setSelectedActivityId(row.activity_id);
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
  if (!project) return <NotFoundState title="پروژه یافت نشد" />;
  if (!canView)
    return (
      <AccessDenied description="برای مشاهده گانت به مجوز مشاهده فعالیت‌ها نیاز است." />
    );

  return (
    <div className="space-y-4">
      <PageHeader title="گانت" subtitle={project.project_name} />

      <div className="flex flex-wrap items-center gap-2">
        <select
          className="rounded border px-2 py-1.5 text-sm"
          value={baselineId}
          onChange={(e) => setBaselineId(e.target.value)}
        >
          <option value="">خط مبنای جاری</option>
          {(data?.baselines ?? []).map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}{b.is_current ? " (جاری)" : ""}
            </option>
          ))}
        </select>
        {(["Day", "Week", "Month", "Year"] as const).map((mode) => (
          <Button
            key={mode}
            variant={viewMode === mode ? "primary" : "secondary"}
            size="sm"
            onClick={() => setViewMode(mode)}
          >
            {mode === "Day" ? "روز" : mode === "Week" ? "هفته" : mode === "Month" ? "ماه" : "سال"}
          </Button>
        ))}
        <Button variant="secondary" size="sm" onClick={() => ganttRef.current?.scroll_current?.()}>
          امروز
        </Button>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={criticalOnly} onChange={(e) => setCriticalOnly(e.target.checked)} />
          فقط مسیر بحرانی
        </label>
        <Button variant="secondary" size="sm" onClick={() => void exportPdf()}>
          خروجی PDF
        </Button>
      </div>

      {data?.baseline_name ? (
        <p className="text-sm text-muted-foreground">خط مبنا: {data.baseline_name}</p>
      ) : null}

      <div className="overflow-x-auto rounded-lg border p-4 gantt-container" ref={containerRef} />

      <style>{`
        .bar-critical .bar { fill: #dc2626 !important; }
        .bar-done .bar { fill: #059669 !important; }
        .bar-normal .bar { fill: #2563eb !important; }
        .gantt-container .grid-row { direction: rtl; }
      `}</style>

      {selectedActivityId && selectedActivity ? (
        <ActivityDrawer
          projectId={projectId}
          isOpen
          activity={selectedActivity}
          onClose={() => setSelectedActivityId(null)}
          onSaved={() => setSelectedActivityId(null)}
          onError={(msg) => toast.error(msg)}
        />
      ) : null}
    </div>
  );
}

export default function ProjectScheduleGanttPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <GanttContent />
    </ProjectProvider>
  );
}
