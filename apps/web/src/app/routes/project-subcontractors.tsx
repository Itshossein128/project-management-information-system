import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  fetchSubcontractors,
  formatFaAmount,
  STATUS_LABELS,
} from "@/app/lib/api/subcontractors";
import { PATHS } from "@/app/routeVars";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";

function SubcontractorsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");

  const { data, isLoading: loading } = useQuery({
    queryKey: ["subcontractors", projectId],
    queryFn: () => fetchSubcontractors(projectId),
    enabled: canView,
  });

  if (isLoading || loading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) {
    return <p className="rounded-lg border p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;
  }

  const rows = data?.results ?? [];
  const atRisk = rows.filter((r) => r.risk_flag).length;
  const active = rows.filter((r) => r.status === "active").length;
  const suspended = rows.filter((r) => r.status === "suspended").length;

  return (
    <div className="space-y-6">
      <PageHeader title="پیمانکاران فرعی" subtitle={project.project_name} />

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">کل</p><p className="text-xl font-semibold">{rows.length}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">فعال</p><p className="text-xl font-semibold text-emerald-600">{active}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">در خطر</p><p className="text-xl font-semibold text-red-600">{atRisk}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">تعلیق‌شده</p><p className="text-xl font-semibold text-amber-600">{suspended}</p></div>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["نام شرکت", "حوزه", "وضعیت", "آخرین نمره", "طلب معوق", "هشدارها", "ریسک"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="px-3 py-2 font-medium">{r.company_name}</td>
                <td className="px-3 py-2">{r.discipline || "—"}</td>
                <td className="px-3 py-2">{STATUS_LABELS[r.status] ?? r.status}</td>
                <td className={`px-3 py-2 ${r.latest_score != null && r.latest_score < 6 ? "text-red-600" : r.latest_score != null && r.latest_score >= 8 ? "text-emerald-600" : "text-amber-600"}`}>
                  {r.latest_score?.toFixed(1) ?? "—"}
                </td>
                <td className="px-3 py-2">{formatFaAmount(r.financial_summary.outstanding)}</td>
                <td className="px-3 py-2">{r.warning_count}</td>
                <td className="px-3 py-2">
                  {r.risk_flag ? (
                    <span title={r.risk_reasons.join("\n")} className="rounded bg-red-100 px-2 py-0.5 text-red-800">در خطر</span>
                  ) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ProjectSubcontractorsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb items={[{ label: "پروژه‌ها", href: `/${PATHS.PROJECT}` }, { label: "پیمانکاران فرعی" }]} />
        <SubcontractorsContent />
      </main>
    </ProjectProvider>
  );
}
