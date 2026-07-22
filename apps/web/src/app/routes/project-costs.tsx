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
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { KPICard } from "@/components/progress/KPICard";
import { Button } from "@/components/ui/sprint-button";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

  const {
    data: summary,
    isLoading: summaryLoading,
    isError: summaryError,
    refetch: refetchSummary,
  } = useQuery({
    queryKey: ["cost-summary", projectId],
    queryFn: () => fetchCostSummary(projectId),
    enabled: canView && Boolean(projectId),
  });

  if (projectLoading || summaryLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <EmptyState title="پروژه یافت نشد" />;
  if (!canView) {
    return (
      <EmptyState
        title="دسترسی ندارید"
        description="نقش شما مجوز مشاهده هزینه‌ها را ندارد."
      />
    );
  }
  if (summaryError) {
    return <QueryErrorState onRetry={() => void refetchSummary()} />;
  }

  const consumption = summary?.budget_consumption_pct;

  return (
    <div className="space-y-6">
      <PageHeader title="کنترل هزینه" subtitle={project.project_name} />

      <div
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-5"
        data-testid="costs-kpi-grid"
      >
        <KPICard
          title="بودجه کل (BAC)"
          value={summary ? formatFaAmount(summary.total_budget) : "—"}
        />
        <KPICard
          title="هزینه واقعی"
          value={summary ? formatFaAmount(summary.total_actual) : "—"}
        />
        <KPICard
          title="تعهدات"
          value={summary ? formatFaAmount(summary.total_committed) : "—"}
          subtitle="قراردادهای فعال"
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

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir="rtl">
        <TabsList className="mb-4" data-testid="costs-tabs">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id} data-testid={`costs-tab-${t.id}`}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="budget" className="mt-0">
          <BudgetGrid projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>
        <ShadcnTabsContent value="actual" className="mt-0">
          <ActualCostsTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>
        <ShadcnTabsContent value="variance" className="mt-0">
          <VarianceTab projectId={projectId} />
        </ShadcnTabsContent>
        <ShadcnTabsContent value="pools" className="mt-0">
          <CostPoolTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>
      </Tabs>
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
