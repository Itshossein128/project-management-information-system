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
import { CostPaymentsLedgerPanel } from "@/components/costs/CostPaymentsLedgerPanel";
import { CostPoolTab } from "@/components/costs/CostPoolTab";
import { RemainingAllocatablePanel } from "@/components/costs/RemainingAllocatablePanel";
import { VarianceTab } from "@/components/costs/VarianceTab";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useProductTour } from "@/components/tour/useProductTour";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { KPICard } from "@/components/progress/KPICard";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Tab = "budget" | "actual" | "variance" | "pools" | "cbs" | "payments";

const TABS: { id: Tab; label: string }[] = [
  { id: "budget", label: "بودجه" },
  { id: "actual", label: "هزینه‌های واقعی" },
  { id: "variance", label: "واریانس" },
  { id: "pools", label: "استخر هزینه" },
  { id: "cbs", label: "CBS / تعهد" },
  { id: "payments", label: "پرداخت / دفتر" },
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

  const { startTour } = useProductTour({
    tourId: "project-costs",
    steps: [
      {
        element: '[data-tour="costs-kpi-grid"]',
        popover: {
          title: t("tour.projectCosts.kpiTitle", {
            defaultValue: "شاخص‌های کلیدی بودجه و هزینه",
          }),
          description: t("tour.projectCosts.kpiDesc", {
            defaultValue:
              "خلاصه بودجه مصوب (BAC)، هزینه‌های واقعی، تعهدات و درصد مصرف بودجه پروژه را در یک نگاه بررسی کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="costs-tabs"]',
        popover: {
          title: t("tour.projectCosts.tabsTitle", {
            defaultValue: "تب‌های مدیریت مالی",
          }),
          description: t("tour.projectCosts.tabsDesc", {
            defaultValue:
              "بین بودجه، هزینه‌های واقعی، تحلیل واریانس، استخرهای هزینه، تعهدات CBS و دفتر کل پرداخت‌ها جابه‌جا شوید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="costs-versions-panel"]',
        popover: {
          title: t("tour.projectCosts.versionsTitle", {
            defaultValue: "نسخه‌های بودجه",
          }),
          description: t("tour.projectCosts.versionsDesc", {
            defaultValue:
              "نسخه‌های پیش‌نویس را ویرایش کرده یا نسخه کنترل (Baseline) مصوب پروژه را جهت مقایسه عملکرد انتخاب کنید.",
          }),
          side: "bottom",
        },
      },
      {
        element: '[data-tour="costs-budget-grid"]',
        popover: {
          title: t("tour.projectCosts.gridTitle", {
            defaultValue: "جدول ساختار شکست هزینه (CBS)",
          }),
          description: t("tour.projectCosts.gridDesc", {
            defaultValue:
              "سطوح مختلف بودجه پروژه را مشاهده کرده و ردیف‌های هزینه را بر اساس گروه‌های کاری مدیریت کنید.",
          }),
          side: "top",
        },
      },
      {
        element: '[data-tour="costs-change-requests"]',
        popover: {
          title: t("tour.projectCosts.changeRequestsTitle", {
            defaultValue: "درخواست‌های تغییر بودجه (BCR)",
          }),
          description: t("tour.projectCosts.changeRequestsDesc", {
            defaultValue:
              "در صورت نیاز به اصلاح بودجه مصوب، درخواست تغییر ثبت کرده و گردش‌کار تأیید آن را پیگیری نمایید.",
          }),
          side: "top",
        },
      },
    ],
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pages.costs.title")}
        subtitle={project.project_name}
        actions={<ProductTourButton onClick={startTour} />}
      />

      <div
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-5"
        data-testid="costs-kpi-grid"
        data-tour="costs-kpi-grid"
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
        <TabsList className="mb-4" data-testid="costs-tabs" data-tour="costs-tabs">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id} data-testid={`costs-tab-${t.id}`}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="budget" className="mt-0 space-y-8">
          <div data-tour="costs-versions-panel">
            <BudgetVersionsPanel
              projectId={projectId}
              canEdit={canEdit}
              canApprove={canApprove}
              selectedVersionId={activeVersionId}
              onSelectVersion={setSelectedVersionId}
            />
          </div>
          {activeVersionId && !gridLocked ? (
            <BudgetLineEditor
              projectId={projectId}
              versionId={activeVersionId}
              enabled={canEdit}
            />
          ) : null}
          <div data-tour="costs-budget-grid">
            <BudgetGrid
              projectId={projectId}
              canEdit={canEdit}
              versionId={activeVersionId}
              locked={gridLocked}
            />
          </div>
          <RemainingAllocatablePanel
            projectId={projectId}
            canEdit={canEdit}
            versionId={activeVersion?.is_control ? activeVersionId : null}
          />
          <div data-tour="costs-change-requests">
            <BudgetChangeRequestPanel
              projectId={projectId}
              canEdit={canEdit}
              canApprove={canApprove}
              controlLineId={gridLocked ? controlLineId : null}
            />
          </div>
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
        <ShadcnTabsContent value="payments" className="mt-0">
          <CostPaymentsLedgerPanel projectId={projectId} canEdit={canEdit} />
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
