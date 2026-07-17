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
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
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
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard");
  const canEdit = has("edit_costs");
  const [tab, setTab] = useState<Tab>("overview");
  const [asOf, setAsOf] = useState("");

  const { data: snapshot, isLoading: loadingSnap } = useQuery({
    queryKey: ["economic-snapshot", projectId, asOf],
    queryFn: () => fetchEconomicSnapshot(projectId, asOf || undefined),
    enabled: canView,
  });

  if (isLoading || loadingSnap) return <LoadingSkeleton rows={12} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) return <p className="p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;
  if (!snapshot) return null;

  return (
    <div className="space-y-6" data-testid="economic-page">
      <PageHeader title="تحلیل اقتصادی" subtitle={project.project_name} />

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm">
          تاریخ مبنا (اختیاری)
          <input
            type="date"
            className="mt-1 block rounded-md border px-2 py-1.5 text-sm"
            value={asOf}
            onChange={(e) => setAsOf(e.target.value)}
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <Button
            key={t.id}
            variant={tab === t.id ? "primary" : "secondary"}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </Button>
        ))}
      </div>

      {tab === "overview" && <ProfitLayersPanel snapshot={snapshot} />}
      {tab === "inflation" && (
        <InflationDetailTable projectId={projectId} canEdit={canEdit} asOf={asOf || undefined} />
      )}
      {tab === "financing" && <FinancingCostPanel projectId={projectId} />}
      {tab === "forecast" && <EvmForecastPanel projectId={projectId} asOf={asOf || undefined} />}
      {tab === "simulation" && <MonteCarloPanel projectId={projectId} />}
      {tab === "sensitivity" && <SensitivityTornadoChart projectId={projectId} />}
      {tab === "history" && <EconomicHistoryChart projectId={projectId} />}
    </div>
  );
}

export default function ProjectEconomicPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
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
