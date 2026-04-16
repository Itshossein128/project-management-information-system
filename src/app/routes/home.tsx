import { Card, CardContent, CardHeader, CardTitle } from "@/components/form";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { useAuth } from "~/contexts/auth-context";
import { apiJson } from "~/lib/api-client";
import { PATHS } from "~/routeVars";
import type { Route } from "./+types/home";

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
  const { user, logout, hasRole, isAuthenticated, isLoading } = useAuth();
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

  const displayName =
    user?.full_name ||
    `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim() ||
    user?.phone_number ||
    "User";

  return (
    <div className='min-h-svh bg-muted/30'>
      <main className='mx-auto  p-4'>
        <h2 className='mb-4 text-xl font-medium'>
          {t("home.pageDescription")}
        </h2>
        <p className='mb-6 text-muted-foreground'>
          {t("home.welcome", { name: user?.first_name || displayName })}
        </p>

        {businessesError && (
          <p className='mb-4 text-destructive text-sm'>{businessesError}</p>
        )}
        <h3 className='mb-3 text-sm font-medium text-muted-foreground'>
          Businesses
        </h3>
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
          {businesses.length > 0
            ? businesses.map((b) => (
                <Link key={b.id} to={`/${PATHS.BUSINESS}/${b.id}`}>
                  <Card className='transition-colors hover:bg-muted/50'>
                    <CardHeader>
                      <CardTitle className='text-base'>{b.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className='text-muted-foreground text-sm'>
                        Slug: {b.slug}
                      </p>
                    </CardContent>
                  </Card>
                </Link>
              ))
            : !businessesError && (
                <p className='mt-4 text-muted-foreground text-sm'>
                  No businesses yet.
                </p>
              )}
        </div>

        {hasRole("visitor") && (
          <Card className='mt-6'>
            <CardHeader>
              <CardTitle className='text-base'>
                {t("home.visitorSection")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className='text-muted-foreground text-sm'>
                {t("home.visitorDescription")}
              </p>
            </CardContent>
          </Card>
        )}
        {hasRole("manager") && (
          <Card className='mt-6'>
            <CardHeader>
              <CardTitle className='text-base'>
                {t("home.managerSection")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className='text-muted-foreground text-sm'>
                {t("home.managerDescription")}
              </p>
            </CardContent>
          </Card>
        )}
        {hasRole("commentor") && (
          <Card className='mt-6'>
            <CardHeader>
              <CardTitle className='text-base'>
                {t("home.commentorSection")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className='text-muted-foreground text-sm'>
                {t("home.commentorDescription")}
              </p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
