import { Button } from "@/components/form";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import { PATHS } from "@/app/routeVars";
import { useEffect } from "react";

/**
 * Placeholder for job positions; extend when the API exists.
 */
export default function HrJobPositionsPage() {
  const { t } = useTranslation();
  // Variable holding navigate
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return (
    <div className="page-main max-w-2xl" id="container-hrJobPositions">
      <div className="mb-4">
        <Button
          id="button-backToHrHub"
          variant="ghost"
          size="sm"
          type="button"
          onClick={() => navigate(`/${PATHS.HR}`)}
        >
          {t("common.back")}
        </Button>
      </div>
      <h1
        className="mb-2 text-xl font-semibold"
        id="text-hrJobPositionsTitle"
      >
        {t("hrJobPositions.title")}
      </h1>
      <p className="text-muted-foreground" id="text-hrJobPositionsBody">
        {t("hrJobPositions.placeholder")}
      </p>
    </div>
  );
}
