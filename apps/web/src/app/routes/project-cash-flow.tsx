import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { ForecastTab } from "@/components/cashflow/ForecastTab";
import { GapAnalysisTab } from "@/components/cashflow/GapAnalysisTab";
import { TransactionsTab } from "@/components/cashflow/TransactionsTab";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Button } from "@/components/ui/sprint-button";

type Tab = "transactions" | "forecast" | "gap";

const TABS: { id: Tab; label: string }[] = [
  { id: "transactions", label: "تراکنش‌ها" },
  { id: "forecast", label: "پیش‌بینی جریان نقدی" },
  { id: "gap", label: "تحلیل کمبود نقدینگی" },
];

function CashFlowContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_cashflow");
  const canEdit = has("edit_cashflow");
  const [tab, setTab] = useState<Tab>("transactions");

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title="پروژه یافت نشد" />;

  if (!canView) {
    return (
      <AccessDenied description="نقش شما مجوز مشاهده جریان نقدی را ندارد." />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="جریان نقدی" subtitle={project.project_name} />

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

      {tab === "transactions" && (
        <TransactionsTab projectId={projectId} canEdit={canEdit} />
      )}
      {tab === "forecast" && <ForecastTab projectId={projectId} />}
      {tab === "gap" && <GapAnalysisTab projectId={projectId} />}
    </div>
  );
}

export default function ProjectCashFlowPage() {
  const { projectId } = useParams();

  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "جریان نقدی" },
          ]}
        />
        <CashFlowContent />
      </main>
    </ProjectProvider>
  );
}
