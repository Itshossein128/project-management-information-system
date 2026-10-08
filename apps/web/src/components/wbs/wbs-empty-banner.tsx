import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";

/** Soft warning when schedule/progress entry has no WBS packages (T035). */
export function WbsEmptyBanner({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const { data: nodes = [], isLoading, isError } = useQuery({
    queryKey: ["wbs-flat", projectId, "empty-banner"],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: Boolean(projectId),
  });

  if (isLoading || isError || nodes.length > 0) return null;

  return (
    <p
      className="rounded-md border border-warning-200 bg-warning-50 px-3 py-2 text-sm text-warning-900 dark:border-warning-800 dark:bg-warning-950/40 dark:text-warning-100"
      data-testid="wbs-empty-entry-warning"
    >
      {t("wbs.emptyWarning")}{" "}
      <Link
        className="underline"
        to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_WBS}`}
      >
        {t("wbs.goToWbs")}
      </Link>
    </p>
  );
}
