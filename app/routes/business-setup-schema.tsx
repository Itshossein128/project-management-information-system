/**
 * Business setup schema: tables and fields for one business.
 * List tables, add/edit table; per table list fields, add/edit field.
 */
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/form";
import { Button } from "~/components/form";
import { Input } from "~/components/form";
import { Label } from "~/components/form";
import { apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";

const FIELD_TYPES = [
  { value: "string", label: "String" },
  { value: "number", label: "Number" },
  { value: "date", label: "Date" },
  { value: "boolean", label: "Boolean" },
  { value: "reference", label: "Reference" },
] as const;

interface BusinessDetail {
  id: number;
  name: string;
  slug: string;
}

interface TableItem {
  id: number;
  name: string;
  slug: string;
  ordering: number;
}

interface PaginatedResults<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface FieldItem {
  id: number;
  table: number;
  name: string;
  slug: string;
  field_type: string;
  required: boolean;
  ordering: number;
  target_table: number | null;
}

export default function BusinessSetupSchema() {
  const { businessId } = useParams();
  const { hasRole, isLoading } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [tables, setTables] = useState<TableItem[]>([]);
  const [fieldsByTable, setFieldsByTable] = useState<Record<number, FieldItem[]>>({});
  const [error, setError] = useState<string | null>(null);

  const [tableForm, setTableForm] = useState<{ name: string; slug: string } | null>(null);
  const [editingTableId, setEditingTableId] = useState<number | null>(null);
  const [fieldFormTableId, setFieldFormTableId] = useState<number | null>(null);
  const [fieldForm, setFieldForm] = useState<{ name: string; slug: string; field_type: string; required: boolean } | null>(null);
  const [editingFieldId, setEditingFieldId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const id = Number(businessId);
  const validId = !Number.isNaN(id);

  const loadBusiness = () => {
    if (!validId) return;
    apiJson<BusinessDetail>(`/${PATHS.BUSINESS}/${id}/`)
      .then(setBusiness)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  };

  const loadTables = () => {
    if (!validId) return;
    apiJson<PaginatedResults<TableItem>>(`/${PATHS.BUSINESS}/${id}/tables/`)
      .then((data) => setTables(data.results))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load tables"));
  };

  const loadFields = (tableId: number) => {
    if (!validId) return;
    apiJson<PaginatedResults<FieldItem>>(
      `/${PATHS.BUSINESS}/${id}/tables/${tableId}/fields/`,
    )
      .then((data) =>
        setFieldsByTable((prev) => ({ ...prev, [tableId]: data.results })),
      )
      .catch(() => {});
  };

  useEffect(() => {
    if (!hasRole("business-setup")) return;
    loadBusiness();
    loadTables();
  }, [hasRole, validId]);

  useEffect(() => {
    tables.forEach((t) => loadFields(t.id));
  }, [tables.length, validId]);

  const slugFromName = (s: string) =>
    s
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "_")
      .replace(/[^a-z0-9_]/g, "");

  const validateSlug = (slug: string) => /^[a-z][a-z0-9_]*$/.test(slug);

  const saveTable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tableForm || !validId) return;
    setFormError(null);
    const slug = tableForm.slug.trim() || slugFromName(tableForm.name);
    if (!validateSlug(slug)) {
      setFormError("Slug: lowercase letter first, then letters, numbers, underscores.");
      return;
    }
    const duplicateTable = tables.some(
      (t) => t.slug === slug && t.id !== (editingTableId ?? 0)
    );
    if (duplicateTable) {
      setFormError("A table with this slug already exists in this business.");
      return;
    }
    try {
      if (editingTableId) {
        await apiJson(`/${PATHS.BUSINESS}/${id}/tables/${editingTableId}/`, {
          method: "PATCH",
          body: JSON.stringify({ name: tableForm.name.trim(), slug, ordering: 0 }),
        });
      } else {
        await apiJson(`/${PATHS.BUSINESS}/${id}/tables/`, {
          method: "POST",
          body: JSON.stringify({ name: tableForm.name.trim(), slug, ordering: 0 }),
        });
      }
      loadTables();
      setTableForm(null);
      setEditingTableId(null);
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Request failed");
    }
  };

  const saveField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fieldForm || !fieldFormTableId || !validId) return;
    setFormError(null);
    const slug = fieldForm.slug.trim() || slugFromName(fieldForm.name);
    if (!validateSlug(slug)) {
      setFormError("Slug: lowercase letter first, then letters, numbers, underscores.");
      return;
    }
    const existingFields = fieldsByTable[fieldFormTableId] ?? [];
    const duplicateField = existingFields.some(
      (f) => f.slug === slug && (editingFieldId ? f.id !== editingFieldId : true)
    );
    if (duplicateField) {
      setFormError("A field with this slug already exists in this table.");
      return;
    }
    try {
      const payload = {
        name: fieldForm.name.trim(),
        slug,
        field_type: fieldForm.field_type,
        required: fieldForm.required,
        ordering: 0,
      };
      if (editingFieldId) {
        await apiJson(
          `/${PATHS.BUSINESS}/${id}/tables/${fieldFormTableId}/fields/${editingFieldId}/`,
          { method: "PATCH", body: JSON.stringify(payload) }
        );
      } else {
        await apiJson(
          `/${PATHS.BUSINESS}/${id}/tables/${fieldFormTableId}/fields/`,
          { method: "POST", body: JSON.stringify(payload) }
        );
      }
      loadFields(fieldFormTableId);
      setFieldForm(null);
      setFieldFormTableId(null);
      setEditingFieldId(null);
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Request failed");
    }
  };

  const deleteTable = async (tableId: number) => {
    if (!validId || !confirm("Delete this table and all its fields?")) return;
    try {
      await apiJson(`/${PATHS.BUSINESS}/${id}/tables/${tableId}/`, { method: "DELETE" });
      loadTables();
    } catch {}
  };

  const deleteField = async (tableId: number, fieldId: number) => {
    if (!validId || !confirm("Delete this field?")) return;
    try {
      await apiJson(`/${PATHS.BUSINESS}/${id}/tables/${tableId}/fields/${fieldId}/`, {
        method: "DELETE",
      });
      loadFields(tableId);
    } catch {}
  };

  if (isLoading || !hasRole("business-setup")) return null;
  if (!validId) return <p className="p-4 text-destructive">Invalid business.</p>;

  return (
    <div className="min-h-svh bg-muted/30 p-4">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center gap-3">
          <Link to={`/${PATHS.BUSINESS_SETUP}`} className="text-muted-foreground hover:underline">
            Business setup
          </Link>
          <span className="text-muted-foreground">/</span>
          <h1 className="text-xl font-semibold">{business?.name ?? "Schema"}</h1>
        </div>
        {error && <p className="mt-2 text-destructive text-sm">{error}</p>}

        <section className="mt-6">
          <h2 className="text-lg font-medium">Tables</h2>
          <Button
            className="mt-2"
            size="sm"
            variant="outline"
            onClick={() => {
              setTableForm({ name: "", slug: "" });
              setEditingTableId(null);
              setFormError(null);
            }}
          >
            Add table
          </Button>

          {tableForm && (
            <Card className="mt-3">
              <CardContent className="pt-4">
                <form onSubmit={saveTable} className="space-y-3">
                  {formError && <p className="text-destructive text-sm">{formError}</p>}
                  <div>
                    <Label>Name</Label>
                    <Input
                      value={tableForm.name}
                      onChange={(e) =>
                        setTableForm((p) => p && { ...p, name: e.target.value, slug: p.slug || slugFromName(e.target.value) })
                      }
                      placeholder="e.g. Inventory"
                    />
                  </div>
                  <div>
                    <Label>Slug</Label>
                    <Input
                      value={tableForm.slug}
                      onChange={(e) => setTableForm((p) => p && { ...p, slug: e.target.value })}
                      placeholder="e.g. inventory"
                      disabled={!!editingTableId}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit">{editingTableId ? "Save" : "Create"}</Button>
                    <Button type="button" variant="outline" onClick={() => setTableForm(null)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          <div className="mt-4 space-y-4">
            {tables.map((t) => (
              <Card key={t.id}>
                <CardHeader className="flex flex-row items-center justify-between py-3">
                  <CardTitle className="text-base">{t.name}</CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setTableForm({ name: t.name, slug: t.slug });
                        setEditingTableId(t.id);
                        setFormError(null);
                      }}
                    >
                      Edit
                    </Button>
                    <Button variant="ghost" size="sm" className="text-destructive" onClick={() => deleteTable(t.id)}>
                      Delete
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-muted-foreground text-sm">Slug: {t.slug}</p>
                  <h3 className="mt-3 text-sm font-medium">Fields</h3>
                  <Button
                    className="mt-2"
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setFieldFormTableId(t.id);
                      setFieldForm({ name: "", slug: "", field_type: "string", required: false });
                      setEditingFieldId(null);
                      setFormError(null);
                    }}
                  >
                    Add field
                  </Button>
                  {fieldFormTableId === t.id && fieldForm && (
                    <Card className="mt-3 border-dashed">
                      <CardContent className="pt-4">
                        <form onSubmit={saveField} className="space-y-3">
                          {formError && <p className="text-destructive text-sm">{formError}</p>}
                          <div className="grid gap-2 sm:grid-cols-2">
                            <div>
                              <Label>Name</Label>
                              <Input
                                value={fieldForm.name}
                                onChange={(e) =>
                                  setFieldForm((p) =>
                                    p ? { ...p, name: e.target.value, slug: p.slug || slugFromName(e.target.value) } : p
                                  )
                                }
                                placeholder="e.g. Quantity"
                              />
                            </div>
                            <div>
                              <Label>Slug</Label>
                              <Input
                                value={fieldForm.slug}
                                onChange={(e) => setFieldForm((p) => p && { ...p, slug: e.target.value })}
                                placeholder="e.g. quantity"
                                disabled={!!editingFieldId}
                              />
                            </div>
                            <div>
                              <Label>Type</Label>
                              <select
                                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={fieldForm.field_type}
                                onChange={(e) =>
                                  setFieldForm((p) => p && { ...p, field_type: e.target.value })
                                }
                              >
                                {FIELD_TYPES.map((opt) => (
                                  <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                  </option>
                                ))}
                              </select>
                            </div>
                            <div className="flex items-center gap-2">
                              <input
                                type="checkbox"
                                id="field-required"
                                checked={fieldForm.required}
                                onChange={(e) =>
                                  setFieldForm((p) => p && { ...p, required: e.target.checked })
                                }
                              />
                              <Label htmlFor="field-required">Required</Label>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button type="submit">{editingFieldId ? "Save" : "Create"}</Button>
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => {
                                setFieldForm(null);
                                setFieldFormTableId(null);
                                setEditingFieldId(null);
                              }}
                            >
                              Cancel
                            </Button>
                          </div>
                        </form>
                      </CardContent>
                    </Card>
                  )}
                  <ul className="mt-3 space-y-1 text-sm">
                    {(fieldsByTable[t.id] ?? []).map((f) => (
                      <li key={f.id} className="flex items-center justify-between rounded py-1">
                        <span>
                          {f.name} ({f.slug}) — {f.field_type}
                          {f.required ? " *" : ""}
                        </span>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setFieldFormTableId(t.id);
                              setFieldForm({
                                name: f.name,
                                slug: f.slug,
                                field_type: f.field_type,
                                required: f.required,
                              });
                              setEditingFieldId(f.id);
                              setFormError(null);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive"
                            onClick={() => deleteField(t.id, f.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
