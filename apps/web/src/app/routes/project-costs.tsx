import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchCostSummary, formatFaAmount } from "@/app/lib/api/costs";
import { PATHS } from "@/app/routeVars";
import { ActualCostsTab } from "@/components/costs/ActualCostsTab";
import { BudgetGrid } from "@/components/costs/BudgetGrid";
import { CostPoolTab } from "@/components/costs/CostPoolTab";
import { VarianceTab } from "@/components/costs/VarianceTab";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { KPICard } from "@/components/progress/KPICard";
import { Button } from "@/components/ui/sprint-button";

type Tab = "budget" | "actual" | "variance" | "pools";

const TABS: { id: Tab; label: string }[] = [
  { id: "budget", label: "بودجه" },
  { id: "actual", label: "هزینه‌های واقعی" },
  { id: "variance", label: "واریانس" },
  { id: "pools", label: "استخر هزینه" },
];

function CostsContent() {
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_costs");
  const canEdit = has("edit_costs");
  const [tab, setTab] = useState<Tab>("budget");

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["cost-summary", projectId],
    queryFn: () => fetchCostSummary(projectId),
    enabled: canView && Boolean(projectId),
  });

  if (projectLoading || summaryLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  if (!canView) {
    return (
      <p className="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
        دسترسی به این بخش ندارید — نقش شما مجوز مشاهده هزینه‌ها را ندارد.
      </p>
    );
  }

  const consumption = summary?.budget_consumption_pct;

  return (
    <div className="space-y-6">
      <PageHeader title="کنترل هزینه" subtitle={project.project_name} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KPICard
          title="بودجه کل (BAC)"
          value={summary ? formatFaAmount(summary.total_budget) : "—"}
        />
        <KPICard
          title="هزینه واقعی"
          value={summary ? formatFaAmount(summary.total_actual) : "—"}
        />
        <KPICard
          title="درصد مصرف بودجه"
          value={consumption != null ? `${consumption.toFixed(1)}٪` : "—"}
          trend={
            consumption != null && consumption > 100
              ? { label: "بیش از بودجه", positive: false }
              : consumption != null && consumption > 85
                ? { label: "نزدیک به سقف", positive: false }
                : null
          }
        />
        <KPICard
          title="واریانس"
          value={
            summary
              ? formatFaAmount(summary.total_budget - summary.total_actual)
              : "—"
          }
          subtitle="بودجه منهای واقعی"
        />
      </div>

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {TABS.map((t) => (
          <Button
            key={t.id}
            size="sm"
            variant={tab === t.id ? "primary" : "secondary"}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </Button>
        ))}
      </div>

      {tab === "budget" ? <BudgetGrid projectId={projectId} canEdit={canEdit} /> : null}
      {tab === "actual" ? <ActualCostsTab projectId={projectId} canEdit={canEdit} /> : null}
      {tab === "variance" ? <VarianceTab projectId={projectId} /> : null}
      {tab === "pools" ? <CostPoolTab projectId={projectId} canEdit={canEdit} /> : null}
    </div>
  );
}

export default function ProjectCostsPage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "کنترل هزینه" },
          ]}
        />
        <CostsContent />
      </ProjectProvider>
    </main>
  );
}
