import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { ForecastTab } from "@/components/cashflow/ForecastTab";
import { GapAnalysisTab } from "@/components/cashflow/GapAnalysisTab";
import { TransactionsTab } from "@/components/cashflow/TransactionsTab";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Tab = "transactions" | "forecast" | "gap";

const TABS: { id: Tab; label: string }[] = [
  { id: "transactions", label: "تراکنش‌ها" },
  { id: "forecast", label: "پیش‌بینی جریان نقدی" },
  { id: "gap", label: "تحلیل کمبود نقدینگی" },
];

function CashFlowContent() {
  const { t, i18n } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_cashflow");
  const canEdit = has("edit_cashflow");
  const [tab, setTab] = useState<Tab>("transactions");

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  if (!canView) {
    return (
      <p className="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
        دسترسی به این بخش ندارید — نقش شما مجوز مشاهده جریان نقدی را ندارد.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title={t("pages.cashFlow.title")} subtitle={project.project_name} />

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir={i18n.dir()}>
        <TabsList className="mb-4">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="transactions" className="mt-0">
          <TransactionsTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="forecast" className="mt-0">
          <ForecastTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="gap" className="mt-0">
          <GapAnalysisTab projectId={projectId} />
        </ShadcnTabsContent>
      </Tabs>
    </div>
  );
}

export default function ProjectCashFlowPage() {
  const { t, i18n } = useTranslation();
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
