import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchScheduleStatus } from "@/app/lib/api/schedule";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import { AccessDenied, EmptyState, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ChangeRequestPanel } from "@/components/schedule/ChangeRequestPanel";
import { WbsEmptyBanner } from "@/components/wbs/wbs-empty-banner";

function DateCell({ value }: { value: string | null | undefined }) {
  return <>{value ? formatDisplayDate(value) : "—"}</>;
}

function ScheduleStatusContent() {
  const { t } = useTranslation();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_activities");
  const canEdit = has("edit_activities");

  const {
    data,
    isLoading: loadingStatus,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["schedule-status", projectId],
    queryFn: () => fetchScheduleStatus(projectId),
    enabled: canView && Boolean(projectId),
  });

  if (isLoading || loadingStatus) return <LoadingSkeleton rows={10} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) {
    return (
      <AccessDenied
        title={t("common.accessDenied")}
        description={t("pages.scheduleStatus.accessDeniedDescription")}
      />
    );
  }
  if (isError || !data) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }

  return (
    <div className="space-y-6">
      <Breadcrumb
        items={[
          { label: t("nav.sidebarProjects"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("pages.scheduleStatus.title") },
        ]}
      />
      <PageHeader
        title={t("pages.scheduleStatus.title")}
        subtitle={t("pages.scheduleStatus.subtitle")}
      />

      <WbsEmptyBanner projectId={projectId} />

      {!data.critical_path.valid ? (
        <div
          className="rounded-md border border-warning-500/40 bg-warning-500/10 px-3 py-2 text-sm text-warning-800 dark:text-warning-300"
          role="alert"
          data-testid="critical-path-not-valid"
        >
          {t("schedule.criticalPathNotValid")}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-4 text-sm">
        <div>
          <span className="text-muted-foreground">{t("pages.scheduleStatus.asOf")}: </span>
          <DateCell value={data.as_of} />
        </div>
        <div>
          <span className="text-muted-foreground">
            {t("pages.scheduleStatus.forecastProjectFinish")}:{" "}
          </span>
          <DateCell value={data.forecast_project_finish} />
        </div>
      </div>

      <section className="space-y-2">
        <h2 className="text-base font-medium">{t("pages.scheduleStatus.milestones")}</h2>
        {data.milestones.length === 0 ? (
          <EmptyState title={t("pages.scheduleStatus.emptyMilestones")} />
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="bg-muted/30">
                <tr>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colActivity")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colBaseline")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colPlanned")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colActual")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colForecast")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colDelayDays")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.milestones.map((m) => (
                  <tr key={m.activity_id} className="border-t">
                    <td className="px-3 py-2">
                      {m.activity_code} — {m.activity_name}
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={m.baseline_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={m.planned_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={m.actual_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={m.forecast_finish} />
                    </td>
                    <td className="px-3 py-2">
                      {m.delay_days != null ? m.delay_days : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-medium">{t("pages.scheduleStatus.delays")}</h2>
        <div
          className="flex flex-wrap gap-4 text-xs text-muted-foreground"
          data-testid="near-critical-legend"
          role="note"
        >
          <span>
            <span aria-hidden="true">★ </span>
            {t("pages.scheduleStatus.legendCritical")}
          </span>
          <span>
            <span aria-hidden="true">~ </span>
            {t("pages.scheduleStatus.legendNearCritical")}
          </span>
        </div>
        {data.delays.length === 0 ? (
          <EmptyState title={t("pages.scheduleStatus.emptyDelays")} />
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="bg-muted/30">
                <tr>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colActivity")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colBaseline")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colPlanned")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colActual")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colForecast")}
                  </th>
                  <th className="px-3 py-2 text-start">
                    {t("pages.scheduleStatus.colDelayDays")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.delays.map((d) => (
                  <tr key={d.activity_id} className="border-t">
                    <td className="px-3 py-2">
                      {d.activity_code}
                      {d.is_critical
                        ? ` ★ ${t("pages.scheduleStatus.markerCritical")}`
                        : d.is_near_critical
                          ? ` ~ ${t("pages.scheduleStatus.markerNearCritical")}`
                          : ""}
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={d.baseline_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={d.planned_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={d.actual_finish} />
                    </td>
                    <td className="px-3 py-2">
                      <DateCell value={d.forecast_finish} />
                    </td>
                    <td className="px-3 py-2">
                      {d.delay_days != null ? d.delay_days : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <ChangeRequestPanel projectId={projectId} canEdit={canEdit} />
    </div>
  );
}

export default function ProjectScheduleStatusPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <main className="page-main page-shell mx-auto max-w-[100vw] px-4 py-8">
        <ScheduleStatusContent />
      </main>
    </ProjectProvider>
  );
}
