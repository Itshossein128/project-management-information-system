import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { fetchKpiDrill } from "@/app/lib/api/dashboards";
import { Drawer } from "@/components/ui/drawer";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { formatDisplayDate } from "@/app/lib/jalali-utils";

export function FigureDrillDrawer({
  projectId,
  figureKey,
  figureLabel,
  asOf,
  isOpen,
  onClose,
  approvedOnly = true,
}: {
  projectId: string;
  figureKey: string | null;
  figureLabel?: string;
  asOf?: string;
  isOpen: boolean;
  onClose: () => void;
  approvedOnly?: boolean;
}) {
  const { t } = useTranslation();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["kpi-drill", projectId, figureKey, asOf, approvedOnly],
    queryFn: () =>
      fetchKpiDrill(projectId, {
        figure_key: figureKey!,
        as_of: asOf,
        approved_only: approvedOnly ? "true" : "false",
      }),
    enabled: isOpen && Boolean(projectId && figureKey),
  });

  const title =
    figureLabel ||
    (figureKey ? t(`dashboard.figures.${figureKey.replace(/\./g, "_")}`, figureKey) : "");

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title={t("dashboard.drillTitle", { figure: title })}>
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : !data?.results?.length ? (
        <p className="text-sm text-muted-foreground">{t("dashboard.drillEmpty")}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-start text-muted-foreground">
                <th className="py-2 pe-2 font-medium">{t("dashboard.drillColumnItem")}</th>
                <th className="py-2 pe-2 font-medium">{t("dashboard.drillColumnAmount")}</th>
                <th className="py-2 pe-2 font-medium">{t("dashboard.drillColumnStatus")}</th>
                <th className="py-2 font-medium">{t("dashboard.drillColumnSource")}</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((row) => (
                <tr key={row.id} className="border-b border-border/60">
                  <td className="py-2 pe-2 align-top">{row.display}</td>
                  <td className="py-2 pe-2 align-top tabular-nums">
                    {row.amount == null ? "—" : Number(row.amount).toLocaleString("fa-IR")}
                  </td>
                  <td className="py-2 pe-2 align-top">
                    {row.approval_status || (row.approved ? t("dashboard.approved") : "—")}
                  </td>
                  <td className="py-2 align-top">
                    {row.source_path ? (
                      <Link className="text-primary underline" to={row.source_path}>
                        {t("dashboard.viewSource")}
                      </Link>
                    ) : (
                      "—"
                    )}
                    {row.last_updated_at ? (
                      <p className="mt-1 text-xs text-muted-foreground">
                        {formatDisplayDate(row.last_updated_at.slice(0, 10))}
                      </p>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Drawer>
  );
}
