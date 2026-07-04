import { Button } from "@/components/form";
import { DataTable, useGridState } from "@/components/grid";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import { apiJson } from "src/app/lib/api-client";
import { PATHS } from "src/app/routeVars";

import { useAssignmentsForBusinessQuery } from "@/app/hooks/queries";
import type { UserBusinessAssignment } from "@/app/lib/api-types";
import { AssignmentDetailModal } from "@/components/assignments/assignment-detail-modal";

interface BusinessDetail {
  id: number;
  name: string;
  slug: string;
}

export default function BusinessUsersPage() {
  const { t } = useTranslation();
  const { businessId } = useParams();
  // Variable holding navigate
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Variable holding businessIdNum
  const businessIdNum = businessId ? Number(businessId) : Number.NaN;

  // Variable holding grid
  const grid = useGridState({ initialPageIndex: 0, initialPageSize: 20 });
  // Variable holding ordering
  const ordering = grid.query.sorting[0]
    ? `${grid.query.sorting[0].desc ? "-" : ""}${grid.query.sorting[0].id}`
    : undefined;

  // Variable holding assignmentsQuery
  const assignmentsQuery = useAssignmentsForBusinessQuery(
    businessId ?? "",
    {
      page: grid.query.pagination.pageIndex + 1,
      page_size: grid.query.pagination.pageSize,
      search: grid.debouncedSearch?.trim()
        ? grid.debouncedSearch.trim()
        : undefined,
      ordering,
    },
    isAuthenticated && Boolean(businessId) && !Number.isNaN(businessIdNum),
  );
  // Variable holding assignments
  const assignments = assignmentsQuery.data?.results ?? [];
  // Variable holding count
  const count = assignmentsQuery.data?.count ?? 0;
  // Variable holding assignmentsLoading
  const assignmentsLoading = assignmentsQuery.isFetching;
  // Variable holding assignmentsError
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
    if (Number.isNaN(businessIdNum)) {
      setError("Invalid business");
      return;
    }
    apiJson<BusinessDetail>(`/${PATHS.BUSINESS}/${businessIdNum}/`)
      .then((b) => {
        setBusiness(b);
        setError(null);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, [isAuthenticated, businessId, businessIdNum]);

  // Variable holding columns
  const columns = useMemo<ColumnDef<UserBusinessAssignment>[]>(() => {
    return [
      {
        id: "user",
        header: t("assignmentDetail.user"),
        accessorFn: (a) =>
          typeof a.user === "object" && a.user
            ? a.user.full_name
            : String(a.user ?? ""),
        cell: ({ row }) => (
          <span id={`text-teamUser-${row.index}`}>
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
          <span id={`text-teamJobPosition-${row.index}`}>
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
          <span id={`text-teamAssignmentStatus-${row.index}`}>
            {row.original.status ?? "—"}
          </span>
        ),
      },
      {
        id: "actions",
        header: t("businessAssignments.viewDetails"),
        enableSorting: false,
        cell: ({ row }) => (
          <Button
            id={`button-openTeamAssignmentDetail-${row.index}`}
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
  }, [t]);

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className='page-shell' id='container-businessUsersPage'>
      <AssignmentDetailModal
        open={detailOpen}
        onOpenChange={setDetailOpen}
        assignment={detailAssignment}
      />
      <header className='page-route-header'>
        <div className='page-route-header-inner'>
          <div className='page-route-header-title'>
            <Button
              id='button-backToBusinessHub'
              variant='ghost'
              size='sm'
              type='button'
              onClick={() => navigate(`/${PATHS.BUSINESS}/${businessId ?? ""}`)}
            >
              {t("common.back")}
            </Button>
            <h1
              id='text-businessUsersTitle'
              className='min-w-0 truncate text-base font-semibold sm:text-lg'
            >
              {t("businessProject.teamPageTitle", {
                name: business?.name ?? "—",
              })}
            </h1>
          </div>
        </div>
      </header>

      <main className='page-main' id='container-businessUsersMain'>
        {error && (
          <p
            id='text-businessUsersError'
            className='mb-4 text-destructive text-sm'
          >
            {error}
          </p>
        )}
        {assignmentsError && (
          <p
            id='text-businessUsersAssignmentsError'
            className='mb-4 text-destructive text-sm'
          >
            {assignmentsError}
          </p>
        )}
        {business && (
          <section
            id='container-businessTeam'
            className='mb-4'
            aria-labelledby='text-teamHeading'
          >
            <div className='mb-4 flex flex-wrap items-center justify-between gap-2'>
              <h2 id='text-teamHeading' className='text-xl font-medium'>
                {t("businessProject.teamSectionTitle")}
              </h2>
              <Button
                id='button-openBusinessJobPositionsFromTeam'
                type='button'
                size='sm'
                variant='outline'
                onClick={() =>
                  navigate(
                    `/${PATHS.BUSINESS}/${businessId ?? ""}/job-positions`,
                  )
                }
              >
                {t("businessJobPositions.cardTitle")}
              </Button>
            </div>
            {assignmentsLoading && (
              <p
                id='text-teamAssignmentsLoading'
                className='mb-2 text-muted-foreground text-sm'
              >
                {t("common.loading")}
              </p>
            )}
            <DataTable
              name='businessMembers'
              columns={columns}
              data={assignments}
              emptyMessage={t("businessAssignments.empty")}
              manual
              enableRowSelection
              sorting={grid.query.sorting}
              onSortingChange={(next) => grid.setSorting(next)}
              globalFilter={grid.query.search}
              onGlobalFilterChange={(value) => grid.setSearch(value)}
              pagination={grid.query.pagination}
              onPaginationChange={(next) => grid.setPagination(next)}
              totalCount={count}
              isLoading={assignmentsLoading}
            />
          </section>
        )}
      </main>
    </div>
  );
}
