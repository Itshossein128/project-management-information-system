import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchActivityLog, fetchActivityLogFilters } from "@/app/lib/api/reports";
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
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");

  const [dateRange, setDateRange] = useState({ from: monthStartIso(), to: todayIso() });
  const [zone, setZone] = useState("");
  const [block, setBlock] = useState("");
  const [subcontractor, setSubcontractor] = useState("");
  const [page, setPage] = useState(1);

  const { data: filters } = useQuery({
    queryKey: ["activity-log-filters", projectId],
    queryFn: () => fetchActivityLogFilters(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data, isLoading } = useQuery({
    queryKey: ["activity-log", projectId, dateRange, zone, block, subcontractor, page],
    queryFn: () =>
      fetchActivityLog(projectId, {
        date_from: dateRange.from,
        date_to: dateRange.to,
        zone: zone || undefined,
        block: block || undefined,
        subcontractor: subcontractor || undefined,
        page,
        page_size: 50,
      }),
    enabled: canView && Boolean(projectId),
  });

  if (projectLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title="پروژه یافت نشد" />;

  if (!canView) {
    return (
      <AccessDenied description="نقش شما مجوز مشاهده گزارش‌ها را ندارد." />
    );
  }

  const rows = data?.results ?? [];
  const totalPages = data ? Math.ceil(data.count / 50) : 1;

  return (
    <div className="space-y-6">
      <PageHeader title="بانک فعالیت‌ها" subtitle={project.project_name} />

      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-[260px] flex-1">
          <JalaliDateRangePicker
            name="activity_log_range"
            label="بازه تاریخ"
            value={dateRange}
            onChange={(v) => {
              setDateRange(v);
              setPage(1);
            }}
          />
        </div>
        <label className="flex flex-col gap-1 text-sm">
          <span>زون</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={zone}
            onChange={(e) => {
              setZone(e.target.value);
              setPage(1);
            }}
          >
            <option value="">همه</option>
            {(filters?.zones ?? []).map((z) => (
              <option key={z} value={z}>
                {z}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>بلوک</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={block}
            onChange={(e) => {
              setBlock(e.target.value);
              setPage(1);
            }}
          >
            <option value="">همه</option>
            {(filters?.blocks ?? []).map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>پیمانکار</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={subcontractor}
            onChange={(e) => {
              setSubcontractor(e.target.value);
              setPage(1);
            }}
          >
            <option value="">همه</option>
            {(filters?.subcontractors ?? []).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {[
                    "تاریخ",
                    "فعالیت",
                    "شرح",
                    "زون",
                    "بلوک",
                    "طبقه",
                    "پیمانکار",
                    "نفر",
                    "مقدار",
                    "گزارش",
                  ].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="px-3 py-6 text-center text-muted-foreground">
                      فعالیتی یافت نشد
                    </td>
                  </tr>
                ) : (
                  rows.map((r) => (
                    <tr key={r.id} className="border-t border-border">
                      <td className="px-3 py-2 whitespace-nowrap">{r.report_date}</td>
                      <td className="px-3 py-2">
                        {r.activity_code ? (
                          <span title={r.activity_name ?? ""}>
                            {r.activity_code}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="px-3 py-2 max-w-[180px] truncate" title={r.activity_description}>
                        {r.activity_description || "—"}
                      </td>
                      <td className="px-3 py-2">{r.zone || "—"}</td>
                      <td className="px-3 py-2">{r.block || "—"}</td>
                      <td className="px-3 py-2">{r.floor || "—"}</td>
                      <td className="px-3 py-2">{r.subcontractor || "—"}</td>
                      <td className="px-3 py-2">{r.headcount ?? "—"}</td>
                      <td className="px-3 py-2">
                        {r.quantity != null ? `${r.quantity} ${r.unit || ""}` : "—"}
                      </td>
                      <td className="px-3 py-2">
                        <Link
                          to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${r.report_id}/view`}
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          <ExternalLink className="size-3.5" />
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
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                قبلی
              </Button>
              <span className="text-sm text-muted-foreground">
                صفحه {page} از {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
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
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
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
