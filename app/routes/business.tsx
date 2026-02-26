import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { useAuth } from "~/contexts/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/form";
import { Button } from "~/components/form";
import { apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";

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

export default function BusinessPage() {
  const { t } = useTranslation();
  const { businessId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [tables, setTables] = useState<TableItem[]>([]);
  const [error, setError] = useState<string | null>(null);

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
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [isAuthenticated, businessId]);

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className="min-h-svh bg-muted/30">
      <header className="border-b bg-background px-4 py-3">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => navigate(`/${PATHS.HOME}`)}>
              {t("common.back")}
            </Button>
            <h1 className="text-lg font-semibold">{business?.name ?? "Business"}</h1>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl p-4">
        {error && <p className="mb-4 text-destructive text-sm">{error}</p>}
        {business && (
          <>
            <h2 className="mb-4 text-xl font-medium">Tables</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {tables.map((table) => (
                <Card key={table.id}>
                  <CardHeader>
                    <CardTitle className="text-base">{table.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-3 text-muted-foreground text-sm">Slug: {table.slug}</p>
                    <Link to={`/${PATHS.BUSINESS}/${businessId}/tables/${table.slug}`}>
                      <Button variant="outline" size="sm">
                        View rows
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
            {tables.length === 0 && (
              <p className="text-muted-foreground text-sm">No tables defined for this business.</p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
