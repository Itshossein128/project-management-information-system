import { useAuth } from "@/app/contexts/auth-context";
import {
  useCreateJobPosition,
  useDeleteJobPosition,
  useJobPositionsForBusinessQuery,
  useUpdateJobPosition,
} from "@/app/hooks/queries";
import { apiJson } from "@/app/lib/api-client";
import type { BusinessJobPosition } from "@/app/lib/api-types";
import { PATHS } from "@/app/routeVars";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from "@/components/form";
import { DataTable, useGridState } from "@/components/grid";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router";

interface BusinessDetail {
  id: string;
  name: string;
  slug: string;
}

export default function BusinessJobPositionsPage() {
  const { t } = useTranslation();
  const { businessId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [businessError, setBusinessError] = useState<string | null>(null);

  const grid = useGridState({ initialPageIndex: 0, initialPageSize: 20 });
  const ordering = grid.query.sorting[0]
    ? `${grid.query.sorting[0].desc ? "-" : ""}${grid.query.sorting[0].id}`
    : undefined;

  const jobsQuery = useJobPositionsForBusinessQuery(
    businessId ?? "",
    {
      page: grid.query.pagination.pageIndex + 1,
      page_size: grid.query.pagination.pageSize,
      search: grid.debouncedSearch?.trim()
        ? grid.debouncedSearch.trim()
        : undefined,
      ordering,
    },
    isAuthenticated && Boolean(businessId),
  );

  const createJob = useCreateJobPosition(businessId ?? "");
  const updateJob = useUpdateJobPosition(businessId ?? "");
  const deleteJob = useDeleteJobPosition(businessId ?? "");

  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [slug, setSlug] = useState("");
  const [label, setLabel] = useState("");
  const [orderingInput, setOrderingInput] = useState("0");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId) return;
    apiJson<BusinessDetail>(`/${PATHS.API_PROJECTS}/${businessId}/`)
      .then((b) => {
        setBusiness(b);
        setBusinessError(null);
      })
      .catch((e) =>
        setBusinessError(
          e instanceof Error ? e.message : "Failed to load business",
        ),
      );
  }, [isAuthenticated, businessId]);

  if (isLoading || !isAuthenticated) return null;

  const jobs = jobsQuery.data?.results ?? [];
  const count = jobsQuery.data?.count ?? 0;
  const loadingJobs = jobsQuery.isFetching;
  const jobsError =
    jobsQuery.error instanceof Error ? jobsQuery.error.message : null;

  const resetForm = () => {
    setEditingId(null);
    setSlug("");
    setLabel("");
    setOrderingInput("0");
    setFormError(null);
  };

  const startEdit = (jp: BusinessJobPosition) => {

    setEditingId(jp.id);
    setSlug(jp.slug);
    setLabel(jp.label);
    setOrderingInput(String(jp.ordering ?? 0));
    setFormError(null);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const orderNum = Number.parseInt(orderingInput, 10);
    if (Number.isNaN(orderNum) || orderNum < 0) {
      setFormError("Ordering must be a non-negative integer.");
      return;
    }

    const slugTrim = slug.trim().toLowerCase().replace(/\s+/g, "-");
    if (!/^[a-z][a-z0-9-]*$/.test(slugTrim)) {
      setFormError(
        "Slug must start with a letter, then only lowercase letters, numbers, and dashes.",
      );
      return;
    }

    try {
      if (editingId === null) {
        await createJob.mutateAsync({
          slug: slugTrim,
          label: label.trim(),
          ordering: orderNum,
        });
      } else {
        await updateJob.mutateAsync({
          id: editingId,
          patch: { label: label.trim(), ordering: orderNum },
        });
      }
      setShowForm(false);
      resetForm();
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Request failed");
    }
  };

  const handleDelete = async (jp: BusinessJobPosition, index: number) => {
    if (!window.confirm(`Delete job position “${jp.label}” (${jp.slug})?`))
      return;
    try {
      await deleteJob.mutateAsync(jp.id);
    } catch {
      // ignore
    }
  };

  const columns = useMemo<ColumnDef<BusinessJobPosition>[]>(() => {
    return [
      {
        id: "slug",
        header: t("businessJobPositions.columnSlug"),
        accessorKey: "slug",
        cell: ({ row }) => (
          <span
            id={`text-jobPositionSlug-${row.index}`}
            className='font-mono text-muted-foreground'
          >
            {row.original.slug}
          </span>
        ),
      },
      {
        id: "label",
        header: t("businessJobPositions.columnLabel"),
        accessorKey: "label",
        cell: ({ row }) => (
          <span id={`text-jobPositionLabel-${row.index}`}>
            {row.original.label}
          </span>
        ),
      },
      {
        id: "ordering",
        header: t("businessJobPositions.columnOrdering"),
        accessorKey: "ordering",
        cell: ({ row }) => (
          <span id={`text-jobPositionOrdering-${row.index}`}>
            {row.original.ordering}
          </span>
        ),
      },
      {
        id: "actions",
        header: t("businessJobPositions.columnActions"),
        enableSorting: false,
        cell: ({ row }) => (
          <div
            id={`container-jobPositionActions-${row.index}`}
            className='flex flex-wrap gap-2'
          >
            <Button
              id={`button-editJobPosition-${row.index}`}
              type='button'
              size='sm'
              variant='outline'
              onClick={() => startEdit(row.original)}
            >
              {t("businessJobPositions.save")}
            </Button>
            <Button
              id={`button-deleteJobPosition-${row.index}`}
              type='button'
              size='sm'
              variant='outline'
              onClick={() => void handleDelete(row.original, row.index)}
            >
              {t("businessJobPositions.delete")}
            </Button>
          </div>
        ),
      },
    ];
  }, [t]);

  return (
    <div
      className='page-shell'
      id='container-businessJobPositionsPage'
    >
      <header className='page-route-header'>
        <div className='page-route-header-inner'>
          <div className='page-route-header-title'>
            <Button
              id='button-backToBusinessHubFromJobPositions'
              variant='ghost'
              size='sm'
              type='button'
              onClick={() => navigate(`/${PATHS.BUSINESS}/${businessId ?? ""}`)}
            >
              {t("common.back")}
            </Button>
            <h1
              id='text-businessJobPositionsTitle'
              className='min-w-0 truncate text-base font-semibold sm:text-lg'
            >
              {t("businessJobPositions.title", { name: business?.name ?? "—" })}
            </h1>
          </div>
          <div className='page-route-header-actions'>
            <Button
              id='button-toggleJobPositionForm'
              type='button'
              size='sm'
              variant={showForm ? "secondary" : "default"}
              onClick={() => {
                setShowForm((v) => !v);
                setFormError(null);
                if (showForm) resetForm();
              }}
            >
              {showForm
                ? t("businessJobPositions.closeForm")
                : t("businessJobPositions.add")}
            </Button>
          </div>
        </div>
      </header>

      <main className='page-main' id='container-businessJobPositionsMain'>
        <p
          id='text-businessJobPositionsSubtitle'
          className='mb-4 text-muted-foreground text-sm'
        >
          {t("businessJobPositions.subtitle")}
        </p>

        {businessError && (
          <p
            id='text-businessJobPositionsBusinessError'
            className='mb-4 text-destructive text-sm'
          >
            {businessError}
          </p>
        )}
        {jobsError && (
          <p
            id='text-businessJobPositionsLoadError'
            className='mb-4 text-destructive text-sm'
          >
            {jobsError}
          </p>
        )}

        {showForm && (
          <Card id='container-jobPositionForm' className='mb-4'>
            <CardHeader>
              <CardTitle id='text-jobPositionFormTitle' className='text-base'>
                {editingId === null
                  ? t("businessJobPositions.newTitle")
                  : t("businessJobPositions.editTitle")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form
                id='form-jobPosition'
                className='max-w-md space-y-4'
                onSubmit={handleSubmit}
              >
                {formError && (
                  <p
                    id='text-jobPositionFormError'
                    className='text-destructive text-sm'
                  >
                    {formError}
                  </p>
                )}
                <div>
                  <Label
                    id='text-jobPositionSlugInputLabel'
                    htmlFor='input-jobPositionSlug'
                  >
                    {t("businessJobPositions.slug")}
                  </Label>
                  <Input
                    id='input-jobPositionSlug'
                    name='jobPositionSlug'
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    disabled={editingId !== null}
                    required
                    placeholder='e.g. electrician'
                  />
                  <p
                    id='text-jobPositionSlugHelper'
                    className='mt-1 text-muted-foreground text-xs'
                  >
                    {t("businessJobPositions.slugHelper")}
                  </p>
                </div>
                <div>
                  <Label
                    id='text-jobPositionLabelInputLabel'
                    htmlFor='input-jobPositionLabel'
                  >
                    {t("businessJobPositions.label")}
                  </Label>
                  <Input
                    id='input-jobPositionLabel'
                    name='jobPositionLabel'
                    value={label}
                    onChange={(e) => setLabel(e.target.value)}
                    required
                    placeholder='e.g. Electrician'
                  />
                </div>
                <div>
                  <Label
                    id='text-jobPositionOrderingInputLabel'
                    htmlFor='input-jobPositionOrdering'
                  >
                    {t("businessJobPositions.ordering")}
                  </Label>
                  <Input
                    id='input-jobPositionOrdering'
                    name='jobPositionOrdering'
                    type='number'
                    min={0}
                    value={orderingInput}
                    onChange={(e) => setOrderingInput(e.target.value)}
                    required
                  />
                </div>
                <div
                  id='container-jobPositionFormActions'
                  className='flex gap-2'
                >
                  <Button
                    id='button-submitJobPosition'
                    type='submit'
                    disabled={createJob.isPending || updateJob.isPending}
                  >
                    {editingId === null
                      ? t("businessJobPositions.create")
                      : t("businessJobPositions.save")}
                  </Button>
                  <Button
                    id='button-cancelJobPosition'
                    type='button'
                    variant='outline'
                    onClick={() => {
                      setShowForm(false);
                      resetForm();
                    }}
                  >
                    {t("businessJobPositions.cancel")}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <div
          className='mb-2 flex flex-wrap items-center justify-between gap-2'
          id='container-businessJobPositionsHeaderRow'
        >
          <h2
            id='text-businessJobPositionsTableTitle'
            className='text-xl font-medium'
          >
            {t("businessJobPositions.tableTitle")}
          </h2>
          {loadingJobs && (
            <span
              id='text-businessJobPositionsLoading'
              className='text-muted-foreground text-sm'
            >
              {t("common.loading")}
            </span>
          )}
        </div>

        <DataTable
          name='businessJobPositions'
          columns={columns}
          data={jobs}
          emptyMessage={t("businessJobPositions.empty")}
          manual
          enableRowSelection
          sorting={grid.query.sorting}
          onSortingChange={(next) => grid.setSorting(next)}
          globalFilter={grid.query.search}
          onGlobalFilterChange={(value) => grid.setSearch(value)}
          pagination={grid.query.pagination}
          onPaginationChange={(next) => grid.setPagination(next)}
          totalCount={count}
          isLoading={loadingJobs}
        />
      </main>
    </div>
  );
}
