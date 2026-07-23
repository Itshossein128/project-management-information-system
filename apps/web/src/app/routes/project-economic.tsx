import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchEconomicSnapshot } from "@/app/lib/api/economic";
import { PATHS } from "@/app/routeVars";
import { EconomicHistoryChart } from "@/components/economic/EconomicHistoryChart";
import { EvmForecastPanel } from "@/components/economic/EvmForecastPanel";
import { FinancingCostPanel } from "@/components/economic/FinancingCostPanel";
import { InflationDetailTable } from "@/components/economic/InflationDetailTable";
import { MonteCarloPanel } from "@/components/economic/MonteCarloPanel";
import { ProfitLayersPanel } from "@/components/economic/ProfitLayersPanel";
import { SensitivityTornadoChart } from "@/components/economic/SensitivityTornadoChart";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";

type Tab = "overview" | "inflation" | "financing" | "forecast" | "simulation" | "sensitivity" | "history";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "خلاصه سود" },
  { id: "inflation", label: "تورم" },
  { id: "financing", label: "تأمین مالی" },
  { id: "forecast", label: "پیش‌بینی EVM" },
  { id: "simulation", label: "مونت‌کارلو" },
  { id: "sensitivity", label: "حساسیت" },
  { id: "history", label: "تاریخچه" },
];

function EconomicContent() {
  const { t, i18n } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard");
  const canEdit = has("edit_cashflow");
  const [tab, setTab] = useState<Tab>("overview");
  const [asOf, setAsOf] = useState("");

  const {
    data: snapshot,
    isLoading: loadingSnap,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["economic-snapshot", projectId, asOf],
    queryFn: () => fetchEconomicSnapshot(projectId, asOf || undefined),
    enabled: canView,
  });

  if (isLoading || loadingSnap) return <LoadingSkeleton rows={12} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <EmptyState
        title={t("common.accessDenied")}
        description="برای مشاهده تحلیل اقتصادی به مجوز داشبورد نیاز است."
      />
    );
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }
  if (!snapshot) {
    return (
      <EmptyState
        title="داده‌ای برای تحلیل موجود نیست"
        description="پس از ثبت هزینه و پیشرفت، خلاصه اقتصادی اینجا نمایش داده می‌شود."
      />
    );
  }

  return (
    <div className="space-y-6" data-testid="economic-page">
      <PageHeader title={t("pages.economic.title")} subtitle={project.project_name} />

      <div className="flex flex-wrap items-end gap-3">
        <JalaliDatePicker
          name="economic_as_of"
          label="تاریخ مبنا (اختیاری)"
          value={asOf}
          onChange={setAsOf}
        />
      </div>

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir={i18n.dir()}>
        <TabsList className="mb-4">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="overview" className="mt-0">
          <ProfitLayersPanel snapshot={snapshot} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="inflation" className="mt-0">
          <InflationDetailTable projectId={projectId} canEdit={canEdit} asOf={asOf || undefined} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="financing" className="mt-0">
          <FinancingCostPanel projectId={projectId} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="forecast" className="mt-0">
          <EvmForecastPanel projectId={projectId} asOf={asOf || undefined} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="simulation" className="mt-0">
          <MonteCarloPanel projectId={projectId} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="sensitivity" className="mt-0">
          <SensitivityTornadoChart projectId={projectId} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="history" className="mt-0">
          <EconomicHistoryChart projectId={projectId} />
        </ShadcnTabsContent>
      </Tabs>
    </div>
  );
}

export default function ProjectEconomicPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <main className="page-main page-shell mx-auto  px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تحلیل اقتصادی" },
          ]}
        />
        <EconomicContent />
      </main>
    </ProjectProvider>
  );
}
