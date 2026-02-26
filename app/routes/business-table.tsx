import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { Button } from "~/components/form";
import { Input } from "~/components/form";
import { Label } from "~/components/form";
import { apiFetch, apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";

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
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRow, setNewRow] = useState<Record<string, string>>({});
  const pageSize = 20;
  const canEdit = hasRole("manager") || hasRole("business-setup");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId || !tableSlug) return;
    apiJson<TableSchema>(
      `/${PATHS.BUSINESS}/${businessId}/tables/by_slug/${tableSlug}/`
    )
      .then(setSchema)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load schema"));
  }, [isAuthenticated, businessId, tableSlug]);

  useEffect(() => {
    if (!isAuthenticated || !businessId || !tableSlug) return;
    apiJson<RowResponse>(
      `/${PATHS.BUSINESS}/${businessId}/tables/${tableSlug}/rows/?page=${page}&page_size=${pageSize}`
    )
      .then((r) => {
        setRows(r.results);
        setTotal(r.total);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load rows"));
  }, [isAuthenticated, businessId, tableSlug, page]);

  const handleDelete = async (rowId: string) => {
    if (!businessId || !tableSlug || !confirm("Delete this row?")) return;
    const res = await apiFetch(
      `/${PATHS.BUSINESS}/${businessId}/tables/${tableSlug}/rows/${rowId}/`,
      { method: "DELETE" }
    );
    if (res.ok) {
      setRows((prev) => prev.filter((r) => String(r.id) !== rowId));
      setTotal((t) => Math.max(0, t - 1));
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
      else if (f.field_type === "boolean") payload[f.slug] = v === "true" || v === "1";
      else payload[f.slug] = v;
    }
    try {
      const created = await apiJson<Record<string, unknown>>(
        `/${PATHS.BUSINESS}/${businessId}/tables/${tableSlug}/rows/`,
        { method: "POST", body: JSON.stringify(payload) }
      );
      setRows((prev) => [created, ...prev]);
      setTotal((t) => t + 1);
      setNewRow({});
      setShowAddForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add row");
    }
  };

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className="min-h-svh bg-muted/30">
      <header className="border-b bg-background px-4 py-3">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Button variant="ghost" size="sm" onClick={() => navigate(`/${PATHS.BUSINESS}/${businessId}`)}>
            Back
          </Button>
          <h1 className="text-lg font-semibold">{schema?.name ?? tableSlug}</h1>
        </div>
      </header>

      <main className="mx-auto max-w-6xl p-4">
        {error && <p className="mb-4 text-destructive text-sm">{error}</p>}
        {schema && (
          <>
            {showAddForm && schema && (
              <form
                className="mb-4 rounded-md border bg-muted/30 p-4"
                onSubmit={handleAddSubmit}
              >
                <h3 className="mb-3 text-sm font-medium">New row</h3>
                <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {schema.fields.map((f) => (
                    <div key={f.id}>
                      <Label htmlFor={f.slug}>{f.name}{f.required ? " *" : ""}</Label>
                      <Input
                        id={f.slug}
                        value={newRow[f.slug] ?? ""}
                        onChange={(e) =>
                          setNewRow((prev) => ({ ...prev, [f.slug]: e.target.value }))
                        }
                        required={f.required}
                        type={f.field_type === "number" ? "number" : "text"}
                      />
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex gap-2">
                  <Button type="submit" size="sm">Save</Button>
                  <Button type="button" variant="outline" size="sm" onClick={() => { setShowAddForm(false); setNewRow({}); }}>
                    Cancel
                  </Button>
                </div>
              </form>
            )}
            <div className="mb-4 flex items-center justify-between">
              <p className="text-muted-foreground text-sm">
                {total} row{total !== 1 ? "s" : ""}
              </p>
              {canEdit && (
                <Button size="sm" onClick={() => setShowAddForm(true)}>
                  Add row
                </Button>
              )}
            </div>
            <div className="overflow-x-auto rounded-md border bg-background">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    {schema.fields.map((f) => (
                      <th key={f.id} className="px-4 py-2 text-left font-medium">
                        {f.name}
                      </th>
                    ))}
                    {canEdit && <th className="w-24 px-4 py-2" />}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={String(row.id)} className="border-b last:border-0">
                      {schema.fields.map((f) => (
                        <td key={f.id} className="px-4 py-2">
                          {row[f.slug] != null ? String(row[f.slug]) : "—"}
                        </td>
                      ))}
                      {canEdit && (
                        <td className="px-4 py-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive"
                            onClick={() => handleDelete(String(row.id))}
                          >
                            Delete
                          </Button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {total > pageSize && (
              <div className="mt-4 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <span className="flex items-center px-2 text-muted-foreground text-sm">
                  Page {page} of {Math.ceil(total / pageSize)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= Math.ceil(total / pageSize)}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
