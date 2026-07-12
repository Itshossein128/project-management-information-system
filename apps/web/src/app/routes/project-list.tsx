import { useQuery } from "@tanstack/react-query";
import { FolderKanban } from "lucide-react";
import { Link, useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import { fetchProjects, type ProjectListItem } from "@/app/lib/api/projects";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import {
  Badge,
  projectStatusBadge,
  projectStatusLabels,
} from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";

function formatAmount(value: string | null) {
  if (!value) return "—";
  return Number(value).toLocaleString("fa-IR");
}

export default function ProjectListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  const projects = data?.results ?? [];

  const columns = [
    { key: "project_code", label: t("project.code") },
    { key: "project_name", label: t("project.name") },
    { key: "employer", label: t("project.employer") },
    {
      key: "status",
      label: t("project.status"),
      render: (row: ProjectListItem) => (
        <Badge
          variant={projectStatusBadge[row.status] ?? "neutral"}
          label={projectStatusLabels[row.status] ?? row.status}
        />
      ),
    },
    {
      key: "start_date",
      label: t("project.startDate"),
      render: (row: ProjectListItem) => formatDisplayDate(row.start_date),
    },
    {
      key: "planned_finish_date",
      label: t("project.plannedFinish"),
      render: (row: ProjectListItem) =>
        formatDisplayDate(row.planned_finish_date),
    },
    {
      key: "contract_amount",
      label: t("project.contractAmount"),
      render: (row: ProjectListItem) => formatAmount(row.contract_amount),
    },
    {
      key: "actions",
      label: "",
      render: (row: ProjectListItem) => (
        <Button
          variant='ghost'
          size='sm'
          onClick={(e) => {
            e.stopPropagation();
            navigate(
              `/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_OVERVIEW}`,
            );
          }}
        >
          {t("project.view")}
        </Button>
      ),
    },
  ];

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <Breadcrumb items={[{ label: t("project.title") }]} />
      <PageHeader
        title={t("project.title")}
        subtitle={t("project.subtitle")}
        actions={
          <Link to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}>
            <Button variant='primary'>{t("project.create")}</Button>
          </Link>
        }
      />

      {!isLoading && projects.length === 0 ? (
        <div className='flex flex-col items-center gap-4 py-20 text-center text-muted-foreground'>
          <FolderKanban className='size-12 opacity-40' />
          <p>{t("project.empty")}</p>
          <Link to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}>
            <Button variant='primary'>{t("project.create")}</Button>
          </Link>
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={projects}
          loading={isLoading}
          rowKey={(row) => row.project_id}
          onRowClick={(row) =>
            navigate(
              `/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_OVERVIEW}`,
            )
          }
        />
      )}
    </main>
  );
}
