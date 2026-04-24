import { Card, CardContent, CardHeader, CardTitle } from "@/components/form";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";
import type { Route } from "./+types/home";

/**
 * Business picker at `/home`. The sidebar is fixed (Home + HR); business setup
 * and HR tools are reached from the HR hub (`/hr`) and in-project navigation
 * uses cards under each business (`/businesses/:id/...`).
 */
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

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Home | Building Management" },
    { name: "description", content: "Dashboard home" },
  ];
}

export default function Home() {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [businesses, setBusinesses] = useState<BusinessItem[]>([]);
  const [businessesError, setBusinessesError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated) return;
    apiJson<BusinessesListResponse>(`/${PATHS.BUSINESS}/`)
      .then((data) => setBusinesses(data.results))
      .catch((e) =>
        setBusinessesError(
          e instanceof Error ? e.message : "Failed to load businesses",
        ),
      );
  }, [isAuthenticated]);

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return (
    <main className='mx-auto p-4' id='container-homeBusinessPicker'>
      <h1 className='mb-6 text-xl font-medium' id='text-homePageTitle'>
        {t("home.chooseBusinessTitle")}
      </h1>

      {businessesError && (
        <p className='mb-4 text-destructive text-sm' id='text-homeBusinessesError'>
          {businessesError}
        </p>
      )}
      <div
        className='grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
        id='grid-homeBusinesses'
      >
        {businesses.length > 0
          ? businesses.map((b, index) => (
              <Link
                key={b.id}
                id={`link-homeBusiness-${index}`}
                to={`/${PATHS.BUSINESS}/${b.id}`}
              >
                <Card className='transition-colors hover:bg-muted/50'>
                  <CardHeader>
                    <CardTitle
                      className='text-base'
                      id={`text-homeBusinessName-${index}`}
                    >
                      {b.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p
                      className='text-muted-foreground text-sm'
                      id={`text-homeBusinessSlug-${index}`}
                    >
                      {t("home.businessSlugLabel", { slug: b.slug })}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))
          : !businessesError && (
              <p
                className='mt-4 text-muted-foreground text-sm'
                id='text-homeNoBusinesses'
              >
                {t("home.noBusinesses")}
              </p>
            )}
      </div>
    </main>
  );
}
