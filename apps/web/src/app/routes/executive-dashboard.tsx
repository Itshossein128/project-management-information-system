import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  fetchPortfolioDashboard,
  figureTitleKey,
  type DashboardFigure,
} from "@/app/lib/api/dashboards";
import { PATHS } from "@/app/routeVars";
import { DashboardFigureGrid } from "@/components/dashboard/DashboardFigureGrid";
import { FigureDrillDrawer } from "@/components/dashboard/FigureDrillDrawer";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

export default function ExecutiveDashboardPage() {
  const { t } = useTranslation();
  const [drill, setDrill] = useState<{ projectId: string; figure: DashboardFigure } | null>(
    null,
  );

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["portfolio-dashboard"],
    queryFn: () => fetchPortfolioDashboard(),
  });

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
          { label: t("dashboard.executiveTitle") },
        ]}
      />
      <PageHeader
        title={t("dashboard.executiveTitle")}
        subtitle={t("dashboard.executiveSubtitle", {
          pack: data?.pack_id ?? "—",
          asOf: data?.as_of ?? "—",
        })}
      />

      {isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : isLoading ? (
        <LoadingSkeleton rows={12} />
      ) : (
        <div className="space-y-10" data-testid="executive-portfolio-dashboard">
          {data?.projects.map((row) => (
            <section
              key={row.project_id}
              className="rounded-xl border border-border bg-card p-4 shadow-sm"
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold">{row.project_name}</h2>
                <Link
                  className="text-sm text-primary underline"
                  to={`/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_DASHBOARD}`}
                >
                  {t("dashboard.openProjectDashboard")}
                </Link>
              </div>
              <DashboardFigureGrid
                figures={row.figures}
                onFigureClick={(figure) =>
                  setDrill({ projectId: row.project_id, figure })
                }
              />
            </section>
          ))}
          {!data?.projects.length ? (
            <p className="text-sm text-muted-foreground">{t("dashboard.portfolioEmpty")}</p>
          ) : null}
        </div>
      )}

      <FigureDrillDrawer
        projectId={drill?.projectId ?? ""}
        figureKey={drill?.figure.figure_key ?? null}
        figureLabel={
          drill
            ? t(figureTitleKey(drill.figure.figure_key), drill.figure.figure_key)
            : undefined
        }
        asOf={data?.as_of}
        isOpen={Boolean(drill)}
        onClose={() => setDrill(null)}
      />
    </main>
  );
}
