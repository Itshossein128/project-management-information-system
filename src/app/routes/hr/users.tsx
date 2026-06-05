import { useAuth } from "@/app/contexts/auth-context";
import { useCreateHrUser, useHrUsersQuery } from "@/app/hooks/queries";
import type { UserBusinessAssignment } from "@/app/lib/api-types";
import { splitAssignmentsForTablePreview } from "@/app/lib/assignment-preview";
import { PATHS } from "@/app/routeVars";
import { AllAssignmentsModal } from "@/components/assignments/all-assignments-modal";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/form";
import { DataTable, ExcelImportModal, useGridState } from "@/components/grid";
import { CreateHrUserModal } from "@/components/hr/create-hr-user-modal";
import { ROLES } from "@/config/roles";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { z } from "zod";

export interface HrUserRow {
  id: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  date_joined: string;
  is_active: boolean;
  roles: string[];
  assignments_preview?: UserBusinessAssignment[];
}

export function meta() {
  return [
    { title: "Users | Building Management" },
    { name: "description", content: "Directory of application users" },
  ];
}

function formatJoinedAt(iso: string, language: string) {
  try {
    return new Date(iso).toLocaleString(language, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default function HrUsersPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const canAccess = hasRole(ROLES.HR) || hasRole(ROLES.ADMIN);

  const [createOpen, setCreateOpen] = useState(false);
  const createUser = useCreateHrUser();

  const [importOpen, setImportOpen] = useState(false);
  const grid = useGridState({
    initialPageIndex: 0,
    initialPageSize: 20,
    searchDebounceMs: 350,
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  const ordering = grid.query.sorting[0]
    ? `${grid.query.sorting[0].desc ? "-" : ""}${grid.query.sorting[0].id}`
    : undefined;

  const usersQuery = useHrUsersQuery(
    {
      page: grid.query.pagination.pageIndex + 1,
      page_size: grid.query.pagination.pageSize,
      search: grid.debouncedSearch?.trim()
        ? grid.debouncedSearch.trim()
        : undefined,
      ordering,
    },
    isAuthenticated && canAccess,
  );
  const rows = (usersQuery.data?.results ?? []) as HrUserRow[];
  const count = usersQuery.data?.count ?? 0;
  const loading = usersQuery.isFetching;
  const loadError =
    usersQuery.error instanceof Error ? usersQuery.error.message : null;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalUserLabel, setModalUserLabel] = useState<string>("");
  const [modalAssignments, setModalAssignments] = useState<
    UserBusinessAssignment[]
  >([]);

  const columns = useMemo<ColumnDef<HrUserRow>[]>(
    () => [
      {
        id: "phone",
        header: t("hrUsers.columnPhone"),
        cell: ({ row }) => (
          <span id={`text-hrUserPhone-${row.index}`}>
            {row.original.phone_number}
          </span>
        ),
      },
      {
        id: "name",
        header: t("hrUsers.columnName"),
        cell: ({ row }) => (
          <span id={`text-hrUserName-${row.index}`}>
            {row.original.full_name}
          </span>
        ),
      },
      {
        id: "roles",
        header: t("hrUsers.columnRoles"),
        cell: ({ row }) => (
          <span id={`text-hrUserRoles-${row.index}`}>
            {row.original.roles.length ? row.original.roles.join(", ") : "—"}
          </span>
        ),
      },
      {
        id: "assignments",
        header: t("hrUsers.columnAssignments"),
        cell: ({ row }) => {
          const assignments = Array.isArray(row.original.assignments_preview)
            ? row.original.assignments_preview
            : [];
          const preview = splitAssignmentsForTablePreview(assignments, 2);
          return (
            <div
              id={`container-hrUserAssignments-${row.index}`}
              className='space-y-1'
            >
              {preview.lines.length ? (
                <>
                  {preview.lines.map((line, lineIndex) => (
                    <div
                      key={`${lineIndex}-${line}`}
                      id={`item-hrUserAssignmentLine-${row.index}-${lineIndex}`}
                      className='truncate text-sm'
                    >
                      <span
                        id={`text-hrUserAssignmentLine-${row.index}-${lineIndex}`}
                      >
                        {line}
                      </span>
                    </div>
                  ))}
                  {preview.overflowCount > 0 && (
                    <Button
                      id={`button-openAllAssignments-${row.index}`}
                      type='button'
                      variant='ghost'
                      size='sm'
                      className='h-auto px-0 text-xs text-muted-foreground hover:text-foreground'
                      onClick={() => {
                        setModalUserLabel(
                          row.original.full_name || row.original.phone_number,
                        );
                        setModalAssignments(assignments);
                        setModalOpen(true);
                      }}
                    >
                      {t("assignments.viewAll", {
                        count: preview.overflowCount,
                      })}
                    </Button>
                  )}
                </>
              ) : (
                <span
                  id={`text-hrUserAssignmentsEmpty-${row.index}`}
                  className='text-muted-foreground'
                >
                  —
                </span>
              )}
            </div>
          );
        },
      },
      {
        id: "joined",
        header: t("hrUsers.columnJoined"),
        cell: ({ row }) => (
          <span id={`text-hrUserJoined-${row.index}`}>
            {formatJoinedAt(row.original.date_joined, i18n.language)}
          </span>
        ),
      },
      {
        id: "status",
        header: t("hrUsers.columnStatus"),
        cell: ({ row }) => (
          <span
            id={`text-hrUserStatus-${row.index}`}
            className={
              row.original.is_active
                ? "text-success"
                : "text-muted-foreground"
            }
          >
            {row.original.is_active
              ? t("hrUsers.statusActive")
              : t("hrUsers.statusInactive")}
          </span>
        ),
      },
    ],
    [i18n.language, t],
  );

  const excelMapping = useMemo(
    () => ({
      phone_number: [
        "phone_number",
        "phone",
        "mobile",
        "شماره",
        "شماره موبایل",
      ],
      first_name: ["first_name", "first name", "نام"],
      last_name: ["last_name", "last name", "نام خانوادگی"],
      password: ["password", "رمز", "پسورد"],
    }),
    [],
  );

  const excelSchema = useMemo(
    () =>
      z.object({
        phone_number: z
          .string({ message: "Phone number is required." })
          .min(8, "Phone number is too short."),
        first_name: z.string({ message: "First name is required." }).min(1),
        last_name: z.string({ message: "Last name is required." }).min(1),
        password: z.string({ message: "Password is required." }).min(6),
      }),
    [],
  );

  if (isLoading || !isAuthenticated) {
    return null;
  }

  if (!canAccess) {
    return (
      <div className='mx-auto max-w-2xl p-4' id='container-hrUsersForbidden'>
        <div className='mb-4'>
          <Button
            id='button-forbiddenBackToHrHub'
            variant='ghost'
            size='sm'
            type='button'
            onClick={() => navigate(`/${PATHS.HR}`)}
          >
            {t("common.back")}
          </Button>
        </div>
        <h1
          className='mb-2 text-lg font-semibold'
          id='text-hrUsersForbiddenTitle'
        >
          {t("hrUsers.forbiddenTitle")}
        </h1>
        <p className='text-muted-foreground' id='text-hrUsersForbiddenBody'>
          {t("hrUsers.forbiddenBody")}
        </p>
      </div>
    );
  }

  return (
    <div className='page-main' id='container-hrUsersPage'>
      <AllAssignmentsModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        userLabel={modalUserLabel}
        assignments={modalAssignments}
      />
      <ExcelImportModal
        name='hrUsers'
        title={t("hrUsers.title")}
        open={importOpen}
        onClose={() => setImportOpen(false)}
        mapping={excelMapping}
        schema={excelSchema}
        onSubmitValidRows={async (validRows) => {
          // Minimal: create users one-by-one (until backend provides bulk endpoint).
          for (const row of validRows) {
            const payload = row as unknown as {
              phone_number: string;
              first_name: string;
              last_name: string;
              password: string;
            };
            await new Promise<void>((resolve, reject) => {
              createUser.mutate(
                {
                  phone_number: payload.phone_number,
                  first_name: payload.first_name,
                  last_name: payload.last_name,
                  password: payload.password,
                  password_confirm: payload.password,
                },
                {
                  onSuccess: () => resolve(),
                  onError: (e) => reject(e),
                },
              );
            });
          }
        }}
      />
      <CreateHrUserModal
        open={createOpen}
        onOpenChange={(open) => {
          if (createUser.isPending) return;
          setCreateOpen(open);
        }}
        submitting={createUser.isPending}
        submitError={
          createUser.error instanceof Error ? createUser.error.message : null
        }
        onSubmit={(payload) => {
          createUser.mutate(payload, {
            onSuccess: () => setCreateOpen(false),
          });
        }}
      />
      <div className='mb-4'>
        <Button
          id='button-backToHrHub'
          variant='ghost'
          size='sm'
          type='button'
          onClick={() => navigate(`/${PATHS.HR}`)}
        >
          {t("common.back")}
        </Button>
      </div>
      <h1 className='mb-1 text-xl font-semibold' id='text-hrUsersPageTitle'>
        {t("hrUsers.title")}
      </h1>
      <p className='mb-6 text-muted-foreground' id='text-hrUsersPageSubtitle'>
        {t("hrUsers.subtitle")}
      </p>

      <Card id='container-hrUsersCard'>
        <CardHeader className='flex flex-col gap-3 space-y-0 pb-2 sm:flex-row sm:items-center sm:justify-between'>
          <CardTitle
            className='text-base font-medium'
            id='text-hrUsersCardTitle'
          >
            {t("hrUsers.tableTitle", { count })}
          </CardTitle>
          <div
            id='container-hrUsersHeaderActions'
            className='flex w-full flex-wrap items-center gap-2 sm:w-auto sm:justify-end'
          >
            {loading && (
              <span
                className='text-muted-foreground text-sm'
                id='text-hrUsersLoading'
              >
                {t("common.loading")}
              </span>
            )}
            <Button
              id='button-importHrUsers'
              type='button'
              variant='outline'
              size='sm'
              onClick={() => setImportOpen(true)}
            >
              Import Excel
            </Button>
            <Button
              id='button-newHrUser'
              type='button'
              size='sm'
              onClick={() => setCreateOpen(true)}
            >
              {t("hrUsers.newUser")}
            </Button>
          </div>
        </CardHeader>
        <CardContent className='space-y-4'>
          {loadError && (
            <p className='text-destructive text-sm' id='text-hrUsersError'>
              {loadError}
            </p>
          )}

          <DataTable
            name='hrUsers'
            columns={columns}
            data={rows}
            emptyMessage={
              loadError ? t("hrUsers.loadError") : t("hrUsers.empty")
            }
            manual
            enableRowSelection
            sorting={grid.query.sorting}
            onSortingChange={(next) => grid.setSorting(next)}
            globalFilter={grid.query.search}
            onGlobalFilterChange={(value) => grid.setSearch(value)}
            pagination={grid.query.pagination}
            onPaginationChange={(next) => grid.setPagination(next)}
            totalCount={count}
            isLoading={loading}
          />

        </CardContent>
      </Card>
    </div>
  );
}
