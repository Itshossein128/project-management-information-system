import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  fetchBudgetVersions,
  fetchBudgets,
  fetchCostSummary,
  formatFaAmount,
} from "@/app/lib/api/costs";
import { PATHS } from "@/app/routeVars";
import { ActualCostsTab } from "@/components/costs/ActualCostsTab";
import { BudgetChangeRequestPanel } from "@/components/costs/BudgetChangeRequestPanel";
import { BudgetGrid } from "@/components/costs/BudgetGrid";
import { BudgetLineEditor } from "@/components/costs/BudgetLineEditor";
import { BudgetVersionsPanel } from "@/components/costs/BudgetVersionsPanel";
import { CBSCommitmentTab } from "@/components/costs/CBSCommitmentTab";
import { CostPoolTab } from "@/components/costs/CostPoolTab";
import { RemainingAllocatablePanel } from "@/components/costs/RemainingAllocatablePanel";
import { VarianceTab } from "@/components/costs/VarianceTab";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { KPICard } from "@/components/progress/KPICard";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Tab = "budget" | "actual" | "variance" | "pools" | "cbs";

const TABS: { id: Tab; label: string }[] = [
  { id: "budget", label: "بودجه" },
  { id: "actual", label: "هزینه‌های واقعی" },
  { id: "variance", label: "واریانس" },
  { id: "pools", label: "استخر هزینه" },
  { id: "cbs", label: "CBS / تعهد" },
];

function CostsContent() {
  const { t, i18n } = useTranslation();

  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_costs");
  const canEdit = has("edit_costs");
  const canApprove = has("approve_costs") || has("edit_costs");
  const [tab, setTab] = useState<Tab>("budget");
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);

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

  const { data: versions = [] } = useQuery({
    queryKey: ["budget-versions", projectId],
    queryFn: () => fetchBudgetVersions(projectId),
    enabled: canView && Boolean(projectId) && tab === "budget",
  });

  const activeVersionId = useMemo(() => {
    if (selectedVersionId) return selectedVersionId;
    const control = versions.find((v) => v.is_control);
    if (control) return control.id;
    const draft = versions.find((v) => v.status === "draft");
    return draft?.id ?? versions[0]?.id ?? null;
  }, [selectedVersionId, versions]);

  const activeVersion = versions.find((v) => v.id === activeVersionId) ?? null;
  const gridLocked = Boolean(
    activeVersion && activeVersion.status !== "draft",
  );

  const { data: activeBudgets } = useQuery({
    queryKey: ["budgets", projectId, activeVersionId ?? "none", "cr-line"],
    queryFn: () =>
      fetchBudgets(projectId, activeVersionId ? { version_id: activeVersionId } : {}),
    enabled: Boolean(activeVersionId) && tab === "budget",
  });
  const controlLineId = activeBudgets?.results?.[0]?.id ?? null;

  if (projectLoading || summaryLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("pages.costs.accessDeniedDescription", {
          defaultValue: "نقش شما مجوز مشاهده هزینه‌ها را ندارد.",
        })}
      />
    );
  }
  if (summaryError) {
    return <QueryErrorState onRetry={() => void refetchSummary()} />;
  }

  const consumption = summary?.budget_consumption_pct;

  return (
    <div className="space-y-6">
      <PageHeader title={t("pages.costs.title")} subtitle={project.project_name} />

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

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir={i18n.dir()}>
        <TabsList className="mb-4" data-testid="costs-tabs">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id} data-testid={`costs-tab-${t.id}`}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="budget" className="mt-0 space-y-8">
          <BudgetVersionsPanel
            projectId={projectId}
            canEdit={canEdit}
            canApprove={canApprove}
            selectedVersionId={activeVersionId}
            onSelectVersion={setSelectedVersionId}
          />
          {activeVersionId && !gridLocked ? (
            <BudgetLineEditor
              projectId={projectId}
              versionId={activeVersionId}
              enabled={canEdit}
            />
          ) : null}
          <BudgetGrid
            projectId={projectId}
            canEdit={canEdit}
            versionId={activeVersionId}
            locked={gridLocked}
          />
          <RemainingAllocatablePanel
            projectId={projectId}
            canEdit={canEdit}
            versionId={activeVersion?.is_control ? activeVersionId : null}
          />
          <BudgetChangeRequestPanel
            projectId={projectId}
            canEdit={canEdit}
            canApprove={canApprove}
            controlLineId={gridLocked ? controlLineId : null}
          />
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
        <ShadcnTabsContent value="cbs" className="mt-0">
          <CBSCommitmentTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>
      </Tabs>
    </div>
  );
}

export default function ProjectCostsPage() {
  const { t, i18n } = useTranslation();
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
