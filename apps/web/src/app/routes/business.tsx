import { useAssignmentsForBusinessQuery } from "@/app/hooks/queries";
import type { UserBusinessAssignment } from "@/app/lib/api-types";
import { AssignmentDetailModal } from "@/components/assignments/assignment-detail-modal";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/form";
import { DataTable, useGridState } from "@/components/grid";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import { apiJson } from "src/app/lib/api-client";
import { PATHS } from "src/app/routeVars";

interface BusinessDetail {
  id: number;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

interface TableItem {
  id: number;
  name: string;
  slug: string;
  ordering: number;
  created_at: string;
  updated_at: string;
}

interface TablesListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TableItem[];
}

export interface BusinessMembershipRow {
  id: number;
  user: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  business_role: string;
  created_at: string;
  updated_at: string;
}

/**
 * Project hub at `/businesses/:id` — card navigation to `users` and table routes.
 * Sidebar stays global; use in-page back links and these cards to move through the project.
 */
export default function BusinessPage() {
  const { t } = useTranslation();
  const { businessId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [tables, setTables] = useState<TableItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const businessIdNum = businessId ? Number(businessId) : Number.NaN;

  const assignmentsGrid = useGridState({
    initialPageIndex: 0,
    initialPageSize: 20,
  });
  const ordering = assignmentsGrid.query.sorting[0]
    ? `${assignmentsGrid.query.sorting[0].desc ? "-" : ""}${assignmentsGrid.query.sorting[0].id}`
    : undefined;

  const assignmentsQuery = useAssignmentsForBusinessQuery(
    businessId ?? "",
    {
      page: assignmentsGrid.query.pagination.pageIndex + 1,
      page_size: assignmentsGrid.query.pagination.pageSize,
      search: assignmentsGrid.debouncedSearch?.trim()
        ? assignmentsGrid.debouncedSearch.trim()
        : undefined,
      ordering,
    },
    isAuthenticated && Boolean(businessId) && !Number.isNaN(businessIdNum),
  );
  const assignments = assignmentsQuery.data?.results ?? [];
  const assignmentsCount = assignmentsQuery.data?.count ?? 0;
  const assignmentsLoading = assignmentsQuery.isFetching;
  const assignmentsError =
    assignmentsQuery.error instanceof Error
      ? assignmentsQuery.error.message
      : null;

  const [detailOpen, setDetailOpen] = useState(false);
  const [detailAssignment, setDetailAssignment] =
    useState<UserBusinessAssignment | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId) return;
    const id = Number(businessId);
    if (Number.isNaN(id)) {
      setError("Invalid business");
      return;
    }
    Promise.all([
      apiJson<BusinessDetail>(`/${PATHS.BUSINESS}/${id}/`),
      apiJson<TablesListResponse>(`/${PATHS.BUSINESS}/${id}/tables/`),
    ])
      .then(([b, tListData]) => {
        setBusiness(b);
        setTables(tListData.results);
        setError(null);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, [isAuthenticated, businessId]);

  if (isLoading || !isAuthenticated) return null;

  const assignmentColumns: ColumnDef<UserBusinessAssignment>[] = [
    {
      id: "user",
      header: t("assignmentDetail.user"),
      accessorFn: (a) =>
        typeof a.user === "object" && a.user
          ? a.user.full_name
          : String(a.user ?? ""),
      cell: ({ row }) => (
        <span id={`text-assignmentUser-${row.index}`}>
          {typeof row.original.user === "object" && row.original.user
            ? row.original.user.full_name
            : "—"}
        </span>
      ),
    },
    {
      id: "job",
      header: t("assignmentDetail.jobPosition"),
      accessorFn: (a) =>
        typeof a.job_position === "object" && a.job_position
          ? a.job_position.label
          : String(a.job_position ?? ""),
      cell: ({ row }) => (
        <span id={`text-assignmentJob-${row.index}`}>
          {typeof row.original.job_position === "object" &&
          row.original.job_position
            ? row.original.job_position.label
            : "—"}
        </span>
      ),
    },
    {
      id: "status",
      header: t("assignmentDetail.status"),
      accessorKey: "status",
      cell: ({ row }) => (
        <span id={`text-assignmentStatus-${row.index}`}>
          {row.original.status ?? "—"}
        </span>
      ),
    },
    {
      id: "wage",
      header: t("assignmentDetail.wage"),
      accessorKey: "wage",
      cell: ({ row }) => (
        <span id={`text-assignmentWage-${row.index}`}>
          {row.original.wage ?? "—"}
        </span>
      ),
    },
    {
      id: "actions",
      header: t("common.submit"),
      enableSorting: false,
      cell: ({ row }) => (
        <Button
          id={`button-openAssignmentDetail-${row.index}`}
          type='button'
          variant='outline'
          size='sm'
          onClick={() => {
            setDetailAssignment(row.original);
            setDetailOpen(true);
          }}
        >
          {t("businessAssignments.viewDetails")}
        </Button>
      ),
    },
  ];

  return (
    <div className='page-shell' id='container-businessHub'>
      <AssignmentDetailModal
        open={detailOpen}
        onOpenChange={setDetailOpen}
        assignment={detailAssignment}
      />
      <header className='page-route-header'>
        <div className='page-route-header-inner'>
          <div className='page-route-header-title'>
            <Button
              id='button-backFromBusinessToHome'
              variant='ghost'
              size='sm'
              type='button'
              onClick={() => navigate(`/${PATHS.HOME}`)}
            >
              {t("common.back")}
            </Button>
            <h1
              id='text-businessTitle'
              className='min-w-0 truncate text-base font-semibold sm:text-lg'
            >
              {business?.name ?? "Business"}
            </h1>
          </div>
        </div>
      </header>

      <main className='page-main' id='container-businessHubMain'>
        <p
          className='mb-4 text-muted-foreground text-sm'
          id='text-businessHubHint'
        >
          {t("businessProject.hubHint")}
        </p>
        {error && (
          <p id='text-businessError' className='mb-4 text-destructive text-sm'>
            {error}
          </p>
        )}
        {business && (
          <>
            <div
              className='mb-6 grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
              id='grid-businessProjectCards'
            >
              <Link
                id='link-businessProjectUsers'
                to={`/${PATHS.BUSINESS}/${businessId}/users`}
              >
                <Card className='card-interactive h-full'>
                  <CardHeader>
                    <CardTitle
                      className='text-base'
                      id='text-businessProjectUsersTitle'
                    >
                      {t("businessProject.cardUsersTitle")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p
                      className='text-muted-foreground text-sm'
                      id='text-businessProjectUsersDescription'
                    >
                      {t("businessProject.cardUsersDescription")}
                    </p>
                  </CardContent>
                </Card>
              </Link>
              <Link
                id='link-businessProjectJobPositions'
                to={`/${PATHS.BUSINESS}/${businessId}/job-positions`}
              >
                <Card className='card-interactive h-full'>
                  <CardHeader>
                    <CardTitle
                      className='text-base'
                      id='text-businessProjectJobPositionsTitle'
                    >
                      {t("businessJobPositions.cardTitle")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p
                      className='text-muted-foreground text-sm'
                      id='text-businessProjectJobPositionsDescription'
                    >
                      {t("businessJobPositions.cardDescription")}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            </div>

            <section id='container-businessAssignments' className='mb-8'>
              <div className='mb-3 flex flex-wrap items-center justify-between gap-2'>
                <h2
                  id='text-businessAssignmentsTitle'
                  className='text-xl font-medium'
                >
                  {t("businessAssignments.title")}
                </h2>
                {assignmentsLoading && (
                  <span
                    id='text-businessAssignmentsLoading'
                    className='text-muted-foreground text-sm'
                  >
                    {t("common.loading")}
                  </span>
                )}
              </div>
              {assignmentsError && (
                <p
                  id='text-businessAssignmentsError'
                  className='mb-2 text-destructive text-sm'
                >
                  {assignmentsError}
                </p>
              )}
              <DataTable
                name='businessAssignments'
                columns={assignmentColumns}
                data={assignments}
                emptyMessage={t("businessAssignments.empty")}
                manual
                enableRowSelection
                globalFilter={assignmentsGrid.query.search}
                onGlobalFilterChange={(value) =>
                  assignmentsGrid.setSearch(value)
                }
                sorting={assignmentsGrid.query.sorting}
                onSortingChange={(next) => assignmentsGrid.setSorting(next)}
                pagination={assignmentsGrid.query.pagination}
                onPaginationChange={(next) =>
                  assignmentsGrid.setPagination(next)
                }
                totalCount={assignmentsCount}
                isLoading={assignmentsLoading}
              />
            </section>

            <h2 id='text-tablesHeading' className='mb-4 text-xl font-medium'>
              {t("businessProject.tablesHeading")}
            </h2>
            <div
              className='grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
              id='grid-businessTables'
            >
              {tables.map((table, index) => (
                <Card key={table.id} id={`container-tableCard-${table.id}`}>
                  <CardHeader>
                    <CardTitle
                      className='text-base'
                      id={`text-tableName-${index}`}
                    >
                      {table.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p
                      className='mb-3 text-muted-foreground text-sm'
                      id={`text-tableSlug-${index}`}
                    >
                      {t("home.businessSlugLabel", { slug: table.slug })}
                    </p>
                    <Link
                      id={`link-tableRows-${table.id}`}
                      to={`/${PATHS.BUSINESS}/${businessId}/tables/${table.slug}`}
                    >
                      <Button variant='outline' size='sm' type='button'>
                        {t("businessProject.viewRows")}
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
            {tables.length === 0 && (
              <p className='text-muted-foreground text-sm' id='text-noTables'>
                {t("businessProject.noTables")}
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
