import { useQuery } from "@tanstack/react-query";
import { FolderKanban } from "lucide-react";
import { Link, useNavigate } from "react-router";
import { fetchProjects, type ProjectListItem } from "@/app/lib/api/projects";
import { PATHS } from "@/app/routeVars";
import { Badge, projectStatusBadge, projectStatusLabels } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";

function formatAmount(value: string | null) {
  if (!value) return "—";
  return Number(value).toLocaleString("fa-IR");
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return value;
}

export default function ProjectListPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  const projects = data?.results ?? [];

  const columns = [
    { key: "project_code", label: "کد پروژه" },
    { key: "project_name", label: "نام پروژه" },
    { key: "employer", label: "کارفرما" },
    {
      key: "status",
      label: "وضعیت",
      render: (row: ProjectListItem) => (
        <Badge
          variant={projectStatusBadge[row.status] ?? "neutral"}
          label={projectStatusLabels[row.status] ?? row.status}
        />
      ),
    },
    {
      key: "start_date",
      label: "تاریخ شروع",
      render: (row: ProjectListItem) => formatDate(row.start_date),
    },
    {
      key: "planned_finish_date",
      label: "پایان برنامه‌ای",
      render: (row: ProjectListItem) => formatDate(row.planned_finish_date),
    },
    {
      key: "contract_amount",
      label: "مبلغ قرارداد",
      render: (row: ProjectListItem) => formatAmount(row.contract_amount),
    },
    {
      key: "actions",
      label: "",
      render: (row: ProjectListItem) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_OVERVIEW}`);
          }}
        >
          مشاهده
        </Button>
      ),
    },
  ];

  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-8">
      <Breadcrumb items={[{ label: "پروژه‌ها" }]} />
      <PageHeader
        title="پروژه‌ها"
        subtitle="لیست پروژه‌هایی که عضو آن‌ها هستید"
        actions={
          <Link to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}>
            <Button variant="primary">ایجاد پروژه جدید</Button>
          </Link>
        }
      />

      {!isLoading && projects.length === 0 ? (
        <div className="flex flex-col items-center gap-4 py-20 text-center text-muted-foreground">
          <FolderKanban className="size-12 opacity-40" />
          <p>هنوز پروژه‌ای ایجاد نشده است</p>
          <Link to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}>
            <Button variant="primary">ایجاد پروژه جدید</Button>
          </Link>
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={projects}
          loading={isLoading}
          rowKey={(row) => row.project_id}
          onRowClick={(row) =>
            navigate(`/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_OVERVIEW}`)
          }
        />
      )}
    </main>
  );
}
