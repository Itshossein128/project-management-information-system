/**
 * Business admin list at `/businesses`. Edit inline; Add opens `/businesses/create`.
 * Requires `business-setup` Django group (layout guard).
 */
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
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import { ROLES } from "@/config/roles";

export interface BusinessItem {
  id: number;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

interface BusinessesListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: BusinessItem[];
}

export default function BusinessSetup() {
  const navigate = useNavigate();
  const { hasRole, isLoading } = useAuth();
  const [businesses, setBusinesses] = useState<BusinessItem[]>([]);
  const [count, setCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const grid = useGridState({ initialPageIndex: 0, initialPageSize: 20 });
  const ordering = grid.query.sorting[0]
    ? `${grid.query.sorting[0].desc ? "-" : ""}${grid.query.sorting[0].id}`
    : undefined;

  const loadBusinesses = useCallback(() => {
    apiJson<BusinessesListResponse>(
      `/${PATHS.API_PROJECTS}/?${new URLSearchParams({
        page: String(grid.query.pagination.pageIndex + 1),
        page_size: String(grid.query.pagination.pageSize),
        ...(grid.debouncedSearch?.trim()
          ? { search: grid.debouncedSearch.trim() }
          : {}),
        ...(ordering ? { ordering } : {}),
      }).toString()}`,
    )
      .then((data) => {
        setBusinesses(data.results);
        setCount(data.count ?? data.results.length);
        setError(null);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, [
    grid.debouncedSearch,
    grid.query.pagination.pageIndex,
    grid.query.pagination.pageSize,
    ordering,
  ]);

  useEffect(() => {
    if (!hasRole(ROLES.BUSINESS_SETUP)) return;
    loadBusinesses();
  }, [hasRole, loadBusinesses]);

  const handleSubmitEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    setFormError(null);
    const payload = {
      name: name.trim(),
      slug: slug.trim().toLowerCase().replace(/\s+/g, "_"),
    };
    if (!payload.slug || !/^[a-z][a-z0-9_]*$/.test(payload.slug)) {
      setFormError(
        "Slug must start with a letter, then only lowercase letters, numbers, underscores.",
      );
      return;
    }
    try {
      await apiJson(`/${PATHS.API_PROJECTS}/${editingId}/`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      loadBusinesses();
      setEditingId(null);
      setName("");
      setSlug("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Request failed";
      setFormError(typeof msg === "string" ? msg : "Request failed");
      if (
        err &&
        typeof err === "object" &&
        "errors" in err &&
        typeof (err as { errors: unknown }).errors === "object"
      ) {
        const errors = (err as { errors: Record<string, string[]> }).errors;
        const first = Object.values(errors).flat()[0];
        if (first) setFormError(first);
      }
    }
  };

  const startEdit = useCallback((b: BusinessItem) => {
    setEditingId(b.id);
    setName(b.name);
    setSlug(b.slug);
    setFormError(null);
  }, []);

  const goToCreate = useCallback(() => {
    navigate(`/${PATHS.BUSINESS}/${PATHS.BUSINESS_CREATE}`);
  }, [navigate]);

  const columns = useMemo<ColumnDef<BusinessItem>[]>(() => {
    return [
      {
        accessorKey: "name",
        header: "Name",
        cell: ({ row }) => (
          <span id={`text-businessName-${row.index}`}>{row.original.name}</span>
        ),
      },
      {
        accessorKey: "slug",
        header: "Slug",
        cell: ({ row }) => (
          <span id={`text-businessSlug-${row.index}`} className="font-mono text-muted-foreground">
            {row.original.slug}
          </span>
        ),
      },
      {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => (
          <div
            id={`container-businessActions-${row.index}`}
            className="flex flex-wrap gap-2"
          >
            <Link
              id={`button-businessSchema-${row.index}`}
              to={`/${PATHS.BUSINESS}/${row.original.id}/${PATHS.BUSINESS_ADMIN_SETUP}`}
            >
              <Button variant="outline" size="sm" type="button">
                Tables & fields
              </Button>
            </Link>
            <Button
              id={`button-businessEdit-${row.index}`}
              variant="outline"
              size="sm"
              type="button"
              onClick={() => startEdit(row.original)}
            >
              Edit
            </Button>
          </div>
        ),
      },
    ];
  }, [startEdit]);

  if (isLoading || !hasRole(ROLES.BUSINESS_SETUP)) return null;

  return (
    <div className="page-shell-padded">
      <div className="page-main mx-auto max-w-5xl !p-0">
        <h1
          id="text-pageTitle-businessSetup"
          className="text-lg font-semibold sm:text-xl"
        >
          Business setup
        </h1>
        <p
          id="text-pageDescription-businessSetup"
          className="mt-2 text-muted-foreground text-sm"
        >
          Create and edit businesses. Each business can have its own tables and
          fields.
        </p>

        {error && (
          <p id="text-businessSetupError" className="mt-4 text-destructive text-sm">
            {error}
          </p>
        )}

        <div
          id="container-businessSetupToolbar"
          className="mt-6 flex justify-end"
        >
          <Button id="button-addBusiness" type="button" onClick={goToCreate}>
            Add business
          </Button>
        </div>

        {editingId !== null && (
          <Card id="container-businessForm" className="mt-4">
            <CardHeader>
              <CardTitle className="text-base">Edit business</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                id="form-businessSetup"
                onSubmit={handleSubmitEdit}
                className="space-y-4"
              >
                {formError && (
                  <p id="text-businessFormError" className="text-destructive text-sm">
                    {formError}
                  </p>
                )}
                <div>
                  <Label id="text-businessNameInputLabel" htmlFor="input-businessName">
                    Name
                  </Label>
                  <Input
                    id="input-businessName"
                    name="businessName"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="e.g. Main Warehouse"
                  />
                </div>
                <div>
                  <Label id="text-businessSlugInputLabel" htmlFor="input-businessSlug">
                    Slug
                  </Label>
                  <Input
                    id="input-businessSlug"
                    name="businessSlug"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    required
                    placeholder="e.g. main_warehouse"
                    disabled
                  />
                  <p
                    id="text-businessSlugHelper"
                    className="mt-1 text-muted-foreground text-xs"
                  >
                    Slug cannot be changed after create.
                  </p>
                </div>
                <div id="container-businessFormActions" className="flex gap-2">
                  <Button id="button-submitBusinessForm" type="submit">
                    Save
                  </Button>
                  <Button
                    id="button-cancelBusinessForm"
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setEditingId(null);
                      setName("");
                      setSlug("");
                      setFormError(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <div id="container-businessesGrid" className="mt-6">
          <DataTable
            name="businesses"
            columns={columns}
            data={businesses}
            emptyMessage={
              error
                ? "Could not load businesses."
                : "No businesses yet. Add one with the button above."
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
          />
        </div>
      </div>
    </div>
  );
}
