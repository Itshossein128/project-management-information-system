import { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Settings } from "lucide-react";
import { Link, useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { fetchMembers } from "@/app/lib/api/members";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import { warmProjectCache } from "@/app/lib/offlineCache";
import { isOfflineDBAvailable } from "@/app/lib/offlineDB";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import {
  Badge,
  projectStatusBadge,
  projectStatusLabels,
} from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";

function OverviewContent() {
  const { t } = useTranslation();
  const { projectId, project, isLoading } = useProject();
  const isOnline = useOnlineStatus();
  const toast = useToast();
  const warmedRef = useRef(false);
  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  useEffect(() => {
    if (!projectId || !isOnline || warmedRef.current) return;
    if (!isOfflineDBAvailable()) return;
    warmedRef.current = true;
    void warmProjectCache(projectId).then(() => {
      toast.success("💾 پروژه برای استفاده آفلاین ذخیره شد");
    });
  }, [projectId, isOnline, toast]);

  const MODULES = [
    {
      key: "wbs",
      title: t("projectOverview.moduleWbs"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_WBS}`,
    },
    {
      key: "weather",
      title: t("projectOverview.moduleWeather"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_WEATHER}`,
    },
    {
      key: "schedule",
      title: t("projectOverview.moduleSchedule"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/schedule/${PATHS.PROJECT_GANTT}`,
    },
    {
      key: "reports",
      title: t("projectOverview.moduleReports"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_DAILY_REPORTS}`,
    },
    {
      key: "costs",
      title: t("projectOverview.moduleCosts"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_COSTS}`,
    },
    {
      key: "contracts",
      title: t("projectOverview.moduleContracts"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_CONTRACTS}`,
    },
    {
      key: "documents",
      title: t("projectOverview.moduleDocuments"),
      href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_DOCUMENTS}`,
    },
  ];

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <EmptyState title={t("project.notFound")} />;

  return (
    <>
      <Breadcrumb
        items={[
          { label: t("project.title"), href: `/${PATHS.PROJECT}` },
          { label: project.project_name },
        ]}
      />
      <PageHeader
        title={project.project_name}
        subtitle={project.project_code}
        actions={
          <>
            <Badge
              variant={projectStatusBadge[project.status] ?? "neutral"}
              label={projectStatusLabels[project.status] ?? project.status}
            />
            <Link
              to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`}
            >
              <Button variant='secondary' size='sm'>
                <Settings className='size-4' />
                {t("project.settings")}
              </Button>
            </Link>
          </>
        }
      />

      <div className='mb-8 grid gap-4 rounded-lg border border-border p-4 sm:grid-cols-2'>
        <div>
          <span className='text-muted-foreground'>
            {t("project.employer")}:{" "}
          </span>
          {project.employer}
        </div>
        <div>
          <span className='text-muted-foreground'>
            {t("project.contractor")}:{" "}
          </span>
          {project.contractor || "—"}
        </div>
        <div>
          <span className='text-muted-foreground'>
            {t("project.startDate")}:{" "}
          </span>
          {formatDisplayDate(project.start_date)}
        </div>
        <div>
          <span className='text-muted-foreground'>{t("project.finish")}: </span>
          {formatDisplayDate(project.planned_finish_date)}
        </div>
        <div>
          <span className='text-muted-foreground'>{t("project.amount")}: </span>
          {project.contract_amount ?? "—"}
        </div>
      </div>

      <h2 className='mb-3 text-lg font-semibold'>{t("project.modules")}</h2>
      <div className='mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
        {MODULES.map((mod) => (
          <Link
            key={mod.key}
            to={mod.href(projectId)}
            className='flex items-center justify-between rounded-lg border border-border p-4 hover:bg-muted/40'
          >
            <span>{mod.title}</span>
            <ArrowLeft className='size-4' />
          </Link>
        ))}
      </div>

      <h2 className='mb-3 text-lg font-semibold'>
        {t("project.activeMembers")}
      </h2>
      {members.filter((m) => m.status === "active").length === 0 ? (
        <EmptyState title={t("projectMembers.empty")} className="py-8" />
      ) : (
        <ul className='space-y-2'>
          {members
            .filter((m) => m.status === "active")
            .slice(0, 6)
            .map((m) => (
              <li
                key={m.user_id ?? m.invited_email}
                className='flex justify-between rounded border border-border px-3 py-2 text-sm'
              >
                <span>{m.full_name}</span>
                <span className='text-muted-foreground'>{m.roles[0] ?? "—"}</span>
              </li>
            ))}
        </ul>
      )}
    </>
  );
}

export default function ProjectOverviewPage() {
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <OverviewContent />
      </ProjectProvider>
    </main>
  );
}
