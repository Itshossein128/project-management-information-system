import { Button, Input, Label } from "@/components/form";
import { GridPagination } from "@/components/grid";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import {
  apiBlob,
  apiFetch,
  apiJson,
  apiUploadFile,
} from "src/app/lib/api-client";
import { PATHS } from "src/app/routeVars";
import { ROLES } from "@/config/roles";

interface FieldDef {
  id: number;
  name: string;
  slug: string;
  field_type: string;
  required: boolean;
  ordering: number;
}

interface TableSchema {
  id: number;
  name: string;
  slug: string;
  ordering: number;
  fields: FieldDef[];
}

interface RowResponse {
  results: Record<string, unknown>[];
  count: number;
  total: number;
  page: number;
  page_size: number;
}

export default function BusinessTablePage() {
  const { businessId, tableSlug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const [schema, setSchema] = useState<TableSchema | null>(null);
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [rowsLoading, setRowsLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRow, setNewRow] = useState<Record<string, string>>({});
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const importInputRef = useRef<HTMLInputElement>(null);
  const pageSize = 20;
  const REQUEST_TIMEOUT_MS = 20_000;
  const canEdit =
    hasRole(ROLES.MANAGER) || hasRole(ROLES.BUSINESS_SETUP);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId || !tableSlug) return;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    setSchemaLoading(true);
    setError(null);
    apiJson<TableSchema>(
      `/${PATHS.API_PROJECTS}/${businessId}/tables/by_slug/${tableSlug}/`,
      { signal: controller.signal },
    )
      .then((s) => {
        if (!controller.signal.aborted) {
          setSchema(s);
          setError(null);
        }
      })
      .catch((e) => {
        if (controller.signal.aborted) return;
        const msg = e instanceof Error ? e.message : "Failed to load schema";
        setError(
          /abort|timeout/i.test(msg)
            ? "Request timed out. Check the backend and try again."
            : msg,
        );
      })
      .finally(() => {
        clearTimeout(timeoutId);
        if (!controller.signal.aborted) setSchemaLoading(false);
      });
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [isAuthenticated, businessId, tableSlug]);

  useEffect(() => {
    if (!isAuthenticated || !businessId || !tableSlug) return;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    setRowsLoading(true);
    setError(null);
    apiJson<RowResponse>(
      `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/?page=${page}&page_size=${pageSize}`,
      { signal: controller.signal },
    )
      .then((r) => {
        if (!controller.signal.aborted) {
          setRows(r.results);
          setTotal(r.total);
          setError(null);
        }
      })
      .catch((e) => {
        if (controller.signal.aborted) return;
        const msg = e instanceof Error ? e.message : "Failed to load rows";
        setError(
          /abort|timeout/i.test(msg)
            ? "Request timed out. Check the backend and try again."
            : msg,
        );
      })
      .finally(() => {
        clearTimeout(timeoutId);
        if (!controller.signal.aborted) setRowsLoading(false);
      });
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [isAuthenticated, businessId, tableSlug, page, pageSize]);

  const handleDelete = async (rowId: string) => {
    if (!businessId || !tableSlug || !confirm("Delete this row?")) return;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const res = await apiFetch(
        `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/${rowId}/`,
        { method: "DELETE", signal: controller.signal },
      );
      if (res.ok) {
        setRows((prev) => prev.filter((r) => String(r.id) !== rowId));
        setTotal((t) => Math.max(0, t - 1));
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Delete failed";
      if (!/abort|timeout/i.test(msg)) setError(msg);
    } finally {
      clearTimeout(timeoutId);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!businessId || !tableSlug || !schema) return;
    const payload: Record<string, unknown> = {};
    for (const f of schema.fields) {
      const v = newRow[f.slug];
      if (v === undefined || v === "") {
        if (f.required) return;
        continue;
      }
      if (f.field_type === "number") payload[f.slug] = Number(v);
      else if (f.field_type === "boolean")
        payload[f.slug] = v === "true" || v === "1";
      else payload[f.slug] = v;
    }
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const created = await apiJson<Record<string, unknown>>(
        `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/`,
        {
          method: "POST",
          body: JSON.stringify(payload),
          signal: controller.signal,
        },
      );
      setRows((prev) => [created, ...prev]);
      setTotal((t) => t + 1);
      setNewRow({});
      setShowAddForm(false);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to add row";
      setError(
        /abort|timeout/i.test(msg) ? "Request timed out. Try again." : msg,
      );
    } finally {
      clearTimeout(timeoutId);
    }
  };

  const handleExportExcel = async () => {
    if (!businessId || !tableSlug) return;
    setExporting(true);
    setError(null);
    try {
      const blob = await apiBlob(
        `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/export/`,
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${tableSlug}_export.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

  const handleImportExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !businessId || !tableSlug) return;
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      setError("Please select an .xlsx file.");
      return;
    }
    setImporting(true);
    setError(null);
    try {
      const result = await apiUploadFile<{
        created: number;
        errors: { row: number; errors: Record<string, string> }[];
      }>(
        `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/import/`,
        file,
      );
      const msg =
        result.errors.length > 0
          ? `Created ${result.created} row(s). Errors on ${result.errors.length} row(s): ${result.errors.map((x) => `row ${x.row}`).join(", ")}`
          : `Imported ${result.created} row(s).`;
      setError(null);
      if (result.created > 0) {
        setPage(1);
        const r = await apiJson<RowResponse>(
          `/${PATHS.API_PROJECTS}/${businessId}/tables/${tableSlug}/rows/?page=1&page_size=${pageSize}`,
        );
        setRows(r.results);
        setTotal(r.total);
      }
      alert(msg);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
    }
  };

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className='page-shell'>
      <header className='page-route-header'>
        <div className='page-route-header-inner'>
          <div className='page-route-header-title'>
            <Button
              variant='ghost'
              size='sm'
              onClick={() => navigate(`/${PATHS.BUSINESS}/${businessId}`)}
            >
              Back
            </Button>
            <h1 className='min-w-0 truncate text-base font-semibold sm:text-lg'>
              {schema?.name ?? tableSlug}
            </h1>
          </div>
        </div>
      </header>

      <main className='page-main'>
        {error && <p className='mb-4 text-destructive text-sm'>{error}</p>}
        {(schemaLoading || rowsLoading) && !schema && (
          <p className='text-muted-foreground text-sm'>Loading table…</p>
        )}
        {schema && (
          <>
            {showAddForm && schema && (
              <form
                className='mb-4 rounded-md border bg-muted/30 p-4'
                onSubmit={handleAddSubmit}
              >
                <h3 className='mb-3 text-sm font-medium'>New row</h3>
                <div className='grid gap-2 sm:grid-cols-2 lg:grid-cols-3'>
                  {schema.fields.map((f) => (
                    <div key={f.id}>
                      <Label htmlFor={f.slug}>
                        {f.name}
                        {f.required ? " *" : ""}
                      </Label>
                      <Input
                        id={f.slug}
                        value={newRow[f.slug] ?? ""}
                        onChange={(e) =>
                          setNewRow((prev) => ({
                            ...prev,
                            [f.slug]: e.target.value,
                          }))
                        }
                        required={f.required}
                        type={f.field_type === "number" ? "number" : "text"}
                      />
                    </div>
                  ))}
                </div>
                <div className='mt-3 flex gap-2'>
                  <Button type='submit' size='sm'>
                    Save
                  </Button>
                  <Button
                    type='button'
                    variant='outline'
                    size='sm'
                    onClick={() => {
                      setShowAddForm(false);
                      setNewRow({});
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}
            <div className='mb-4 flex flex-wrap items-center justify-between gap-2'>
              <p className='text-muted-foreground text-sm'>
                {total} row{total !== 1 ? "s" : ""}
              </p>
              <div className='flex flex-wrap gap-2'>
                <Button
                  size='sm'
                  variant='outline'
                  disabled={exporting}
                  onClick={handleExportExcel}
                >
                  {exporting ? "Exporting…" : "Export to Excel"}
                </Button>
                {canEdit && (
                  <>
                    <input
                      ref={importInputRef}
                      type='file'
                      accept='.xlsx'
                      className='hidden'
                      onChange={handleImportExcel}
                    />
                    <Button
                      size='sm'
                      variant='outline'
                      disabled={importing}
                      onClick={() => importInputRef.current?.click()}
                    >
                      {importing ? "Importing…" : "Import from Excel"}
                    </Button>
                    <Button size='sm' onClick={() => setShowAddForm(true)}>
                      Add row
                    </Button>
                  </>
                )}
              </div>
            </div>
            <div className='overflow-x-auto rounded-md border bg-background'>
              <table className='w-full text-sm'>
                <thead>
                  <tr className='border-b bg-muted/50'>
                    {schema.fields.map((f) => (
                      <th
                        key={f.id}
                        className='px-4 py-2 text-left font-medium'
                      >
                        {f.name}
                      </th>
                    ))}
                    {canEdit && <th className='w-24 px-4 py-2' />}
                  </tr>
                </thead>
                <tbody>
                  {rowsLoading && rows.length === 0 ? (
                    <tr>
                      <td
                        colSpan={schema.fields.length + (canEdit ? 1 : 0)}
                        className='px-4 py-8 text-center text-muted-foreground text-sm'
                      >
                        Loading rows…
                      </td>
                    </tr>
                  ) : (
                    rows.map((row) => (
                      <tr
                        key={String(row.id)}
                        className='border-b last:border-0'
                      >
                        {schema.fields.map((f) => (
                          <td key={f.id} className='px-4 py-2'>
                            {row[f.slug] != null ? String(row[f.slug]) : "—"}
                          </td>
                        ))}
                        {canEdit && (
                          <td className='px-4 py-2'>
                            <Button
                              variant='ghost'
                              size='sm'
                              className='text-destructive'
                              onClick={() => handleDelete(String(row.id))}
                            >
                              Delete
                            </Button>
                          </td>
                        )}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <GridPagination
              name="businessTableRows"
              pageIndex={page - 1}
              pageSize={pageSize}
              totalCount={total}
              isLoading={rowsLoading}
              className="mt-4 rounded-xl border border-border bg-card"
              onPageIndexChange={(nextIndex) => setPage(nextIndex + 1)}
            />
          </>
        )}
      </main>
    </div>
  );
}
