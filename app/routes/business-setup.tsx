/**
 * Business setup: list businesses, create/edit business (name, slug).
 * Only users with the "business-setup" permission can access this route.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/form";
import { Button } from "~/components/form";
import { Input } from "~/components/form";
import { Label } from "~/components/form";
import { apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";

interface BusinessItem {
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
  const { hasRole, isLoading } = useAuth();
  const [businesses, setBusinesses] = useState<BusinessItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const loadBusinesses = () => {
    apiJson<BusinessesListResponse>(`/${PATHS.BUSINESS}/`)
      .then((data) => setBusinesses(data.results))
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  };

  useEffect(() => {
    if (!hasRole("business-setup")) return;
    loadBusinesses();
  }, [hasRole]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    const duplicate =
      !editingId && businesses.some((b) => b.slug === payload.slug);
    if (duplicate) {
      setFormError("A business with this slug already exists.");
      return;
    }
    try {
      if (editingId) {
        await apiJson(`/${PATHS.BUSINESS}/${editingId}/`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiJson(`/${PATHS.BUSINESS}/`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      loadBusinesses();
      setShowForm(false);
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

  const startEdit = (b: BusinessItem) => {
    setEditingId(b.id);
    setName(b.name);
    setSlug(b.slug);
    setShowForm(true);
    setFormError(null);
  };

  const startCreate = () => {
    setEditingId(null);
    setName("");
    setSlug("");
    setShowForm(true);
    setFormError(null);
  };

  if (isLoading || !hasRole("business-setup")) return null;

  return (
    <div className='min-h-svh bg-muted/30 p-4'>
      <div className='mx-auto max-w-4xl'>
        <h1 className='text-xl font-semibold'>Business setup</h1>
        <p className='mt-2 text-muted-foreground text-sm'>
          Create and edit businesses. Each business can have its own tables and
          fields.
        </p>

        {error && <p className='mt-4 text-destructive text-sm'>{error}</p>}

        <div className='mt-6 flex justify-end'>
          <Button onClick={startCreate}>Add business</Button>
        </div>

        {showForm && (
          <Card className='mt-4'>
            <CardHeader>
              <CardTitle className='text-base'>
                {editingId ? "Edit business" : "New business"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className='space-y-4'>
                {formError && (
                  <p className='text-destructive text-sm'>{formError}</p>
                )}
                <div>
                  <Label htmlFor='bs-name'>Name</Label>
                  <Input
                    id='bs-name'
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder='e.g. Main Warehouse'
                  />
                </div>
                <div>
                  <Label htmlFor='bs-slug'>Slug</Label>
                  <Input
                    id='bs-slug'
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    required
                    placeholder='e.g. main_warehouse'
                    disabled={!!editingId}
                  />
                  <p className='mt-1 text-muted-foreground text-xs'>
                    Lowercase letters, numbers, underscores only. Cannot change
                    after create.
                  </p>
                </div>
                <div className='flex gap-2'>
                  <Button type='submit'>{editingId ? "Save" : "Create"}</Button>
                  <Button
                    type='button'
                    variant='outline'
                    onClick={() => {
                      setShowForm(false);
                      setEditingId(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <div className='mt-6 space-y-3'>
          {businesses.length > 0
            ? businesses.map((b) => (
                <Card key={b.id}>
                  <CardContent className='flex items-center justify-between py-4'>
                    <div>
                      <p className='font-medium'>{b.name}</p>
                      <p className='text-muted-foreground text-sm'>
                        Slug: {b.slug}
                      </p>
                    </div>
                    <div className='flex gap-2'>
                      <Link to={`/${PATHS.BUSINESS_SETUP}/businesses/${b.id}`}>
                        <Button variant='outline' size='sm'>
                          Tables & fields
                        </Button>
                      </Link>
                      <Button
                        variant='outline'
                        size='sm'
                        onClick={() => startEdit(b)}
                      >
                        Edit
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            : !error && (
                <p className='mt-4 text-muted-foreground text-sm'>
                  No businesses yet. Add one above.
                </p>
              )}
        </div>
      </div>
    </div>
  );
}
