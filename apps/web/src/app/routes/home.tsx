import { Card, CardHeader, CardTitle } from "@/components/form";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ChevronLeft } from "lucide-react";
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
  id: string;
  project_id?: string;
  name: string;
  project_name?: string;
  slug: string;
  project_code?: string;
  created_at?: string;
  updated_at?: string;
}

function projectIdOf(b: BusinessItem): string {
  return b.project_id ?? b.id;
}

function projectNameOf(b: BusinessItem): string {
  return b.project_name ?? b.name;
}

function projectCodeOf(b: BusinessItem): string {
  return b.project_code ?? b.slug;
}

function monogramOf(name: string): string {
  const trimmed = name.trim();
  return trimmed ? Array.from(trimmed)[0].toUpperCase() : "؟";
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
    apiJson<BusinessesListResponse>(`/${PATHS.API_PROJECTS}/`)
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
    <main className='page-main' id='container-homeBusinessPicker'>
      <div className='mb-6'>
        <h1 className='text-page-title' id='text-homePageTitle'>
          {t("home.chooseBusinessTitle")}
        </h1>
        <p className='mt-1 max-w-2xl text-sm text-muted-foreground'>
          {t("home.chooseBusinessSubtitle")}
        </p>
      </div>

      {businessesError && (
        <p
          className='mb-4 text-destructive text-sm'
          id='text-homeBusinessesError'
        >
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
                key={projectIdOf(b)}
                id={`link-homeBusiness-${index}`}
                className='group block'
                to={`/${PATHS.BUSINESS}/${projectIdOf(b)}/${PATHS.PROJECT_OVERVIEW}`}
              >
                <Card className='card-interactive h-full'>
                  <CardHeader className='flex flex-row items-center gap-3 space-y-0'>
                    <div
                      aria-hidden='true'
                      className='flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-secondary text-base font-semibold text-secondary-foreground'
                    >
                      {monogramOf(projectNameOf(b))}
                    </div>
                    <div className='min-w-0 flex-1'>
                      <CardTitle
                        className='truncate text-base'
                        id={`text-homeBusinessName-${index}`}
                      >
                        {projectNameOf(b)}
                      </CardTitle>
                      <Badge
                        className='mt-1'
                        label={t("home.businessSlugLabel", {
                          slug: projectCodeOf(b),
                        })}
                      />
                    </div>
                    <ChevronLeft
                      aria-hidden='true'
                      id={`text-homeBusinessSlug-${index}`}
                      className='h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-200 group-hover:-translate-x-0.5 ltr:rotate-180 ltr:group-hover:translate-x-0.5'
                    />
                  </CardHeader>
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
