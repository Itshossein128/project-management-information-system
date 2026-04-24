import { useAuth } from "@/app/contexts/auth-context";
import { PATHS } from "@/app/routeVars";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/form";
import { ROLES } from "@/config/roles";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";

/**
 * HR hub: card navigation to app-level HR and business-admin screens.
 * The sidebar only links here; this page is the in-app HR menu.
 */
export default function HrHubPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const canHr = hasRole(ROLES.HR) || hasRole(ROLES.ADMIN);
  const canBusinessSetup = hasRole(ROLES.BUSINESS_SETUP);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return (
    <main className='mx-auto p-4' id='container-hrHub'>
      <h1 className='mb-1 text-xl font-semibold' id='text-hrHubTitle'>
        {t("hrHub.title")}
      </h1>
      <p className='mb-6 text-muted-foreground' id='text-hrHubSubtitle'>
        {t("hrHub.subtitle")}
      </p>

      <div
        className='grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'
        id='grid-hrHubCards'
      >
        {canHr && (
          <>
            <Link id='link-hrHubUsers' to={`/${PATHS.USERS}`}>
              <Card className='h-full transition-colors hover:bg-muted/50'>
                <CardHeader>
                  <CardTitle
                    className='text-base'
                    id='text-hrHubCardUsersTitle'
                  >
                    {t("hrHub.cardUsersTitle")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p
                    className='text-muted-foreground text-sm'
                    id='text-hrHubCardUsersDescription'
                  >
                    {t("hrHub.cardUsersDescription")}
                  </p>
                </CardContent>
              </Card>
            </Link>
            <Link
              id='link-hrHubJobPositions'
              to={`/${PATHS.HR}/${PATHS.HR_JOB_POSITIONS}`}
            >
              <Card className='h-full transition-colors hover:bg-muted/50'>
                <CardHeader>
                  <CardTitle
                    className='text-base'
                    id='text-hrHubCardJobPositionsTitle'
                  >
                    {t("hrHub.cardJobPositionsTitle")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p
                    className='text-muted-foreground text-sm'
                    id='text-hrHubCardJobPositionsDescription'
                  >
                    {t("hrHub.cardJobPositionsDescription")}
                  </p>
                </CardContent>
              </Card>
            </Link>
          </>
        )}

        {canBusinessSetup && (
          <>
            <Link id='link-hrHubBusinesses' to={`/${PATHS.BUSINESS}`}>
              <Card className='h-full transition-colors hover:bg-muted/50'>
                <CardHeader>
                  <CardTitle
                    className='text-base'
                    id='text-hrHubCardBusinessesTitle'
                  >
                    {t("hrHub.cardBusinessesTitle")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p
                    className='text-muted-foreground text-sm'
                    id='text-hrHubCardBusinessesDescription'
                  >
                    {t("hrHub.cardBusinessesDescription")}
                  </p>
                </CardContent>
              </Card>
            </Link>
          </>
        )}
      </div>

      {!canHr && !canBusinessSetup && (
        <p
          className='mt-6 text-muted-foreground text-sm'
          id='text-hrHubNoCards'
        >
          {t("hrHub.noModules")}
        </p>
      )}
    </main>
  );
}
