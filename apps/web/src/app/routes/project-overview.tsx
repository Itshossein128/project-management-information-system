import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Lock, Settings } from "lucide-react";
import { Link, useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import { fetchMembers } from "@/app/lib/api/members";
import { PATHS } from "@/app/routeVars";
import { Badge, projectStatusBadge, projectStatusLabels } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";

const MODULES = [
  { key: "wbs", title: "ساختار شکست کار (WBS)", href: (id: string) => `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_WBS}`, enabled: true },
  { key: "schedule", title: "زمان‌بندی", enabled: false },
  { key: "reports", title: "گزارش روزانه", enabled: false },
  { key: "costs", title: "هزینه‌ها", enabled: false },
  { key: "contracts", title: "قراردادها", enabled: false },
  { key: "documents", title: "اسناد", enabled: false },
];

function OverviewContent() {
  const { projectId, project, isLoading } = useProject();
  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  return (
    <>
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
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
            <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SETTINGS}/${PATHS.PROJECT_MEMBERS}`}>
              <Button variant="secondary" size="sm">
                <Settings className="size-4" />
                تنظیمات
              </Button>
            </Link>
          </>
        }
      />

      <div className="mb-8 grid gap-4 rounded-lg border border-border p-4 sm:grid-cols-2">
        <div><span className="text-muted-foreground">کارفرما: </span>{project.employer}</div>
        <div><span className="text-muted-foreground">پیمانکار: </span>{project.contractor || "—"}</div>
        <div><span className="text-muted-foreground">شروع: </span>{project.start_date ?? "—"}</div>
        <div><span className="text-muted-foreground">پایان: </span>{project.planned_finish_date ?? "—"}</div>
        <div><span className="text-muted-foreground">مبلغ: </span>{project.contract_amount ?? "—"}</div>
      </div>

      <h2 className="mb-3 text-lg font-semibold">ماژول‌ها</h2>
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MODULES.map((mod) =>
          mod.enabled && mod.href ? (
            <Link
              key={mod.key}
              to={mod.href(projectId)}
              className="flex items-center justify-between rounded-lg border border-border p-4 hover:bg-muted/40"
            >
              <span>{mod.title}</span>
              <ArrowLeft className="size-4" />
            </Link>
          ) : (
            <div
              key={mod.key}
              className="flex items-center justify-between rounded-lg border border-dashed border-border p-4 text-muted-foreground"
              title="در اسپرینت‌های بعدی"
            >
              <span>{mod.title}</span>
              <Lock className="size-4" />
            </div>
          ),
        )}
      </div>

      <h2 className="mb-3 text-lg font-semibold">اعضای فعال</h2>
      <ul className="space-y-2">
        {members.filter((m) => m.status === "active").slice(0, 6).map((m) => (
          <li key={m.user_id ?? m.invited_email} className="flex justify-between rounded border border-border px-3 py-2 text-sm">
            <span>{m.full_name}</span>
            <span className="text-muted-foreground">{m.roles[0] ?? "—"}</span>
          </li>
        ))}
      </ul>
    </>
  );
}

export default function ProjectOverviewPage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-5xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <OverviewContent />
      </ProjectProvider>
    </main>
  );
}
