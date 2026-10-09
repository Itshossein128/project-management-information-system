import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  fetchProjection,
  fetchSuggestedNeed,
  formatFaAmount,
} from "@/app/lib/api/cashflow";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

export function ProjectionPanel({
  projectId,
  fromMonth,
  toMonth,
}: {
  projectId: string;
  fromMonth: string;
  toMonth: string;
}) {
  const { t } = useTranslation();
  const projection = useQuery({
    queryKey: ["cash-projection", projectId, fromMonth, toMonth],
    queryFn: () => fetchProjection(projectId, fromMonth, toMonth),
  });
  const need = useQuery({
    queryKey: ["cash-suggested-need", projectId, fromMonth, toMonth],
    queryFn: () => fetchSuggestedNeed(projectId, fromMonth, toMonth),
  });

  if (projection.isLoading) return <LoadingSkeleton rows={4} />;
  if (projection.isError) {
    return <QueryErrorState onRetry={() => void projection.refetch()} />;
  }

  const months = projection.data?.months ?? [];

  return (
    <div className="space-y-4" data-testid="cash-projection-panel">
      <div>
        <h3 className="mb-2 font-medium">{t("pages.cashFlow.projectionTitle")}</h3>
        <p className="mb-3 text-sm text-muted-foreground">
          {t("pages.cashFlow.projectionHint")}
        </p>
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 text-start">
              <tr>
                <th className="p-2 text-start">{t("pages.cashFlow.month")}</th>
                <th className="p-2 text-start">{t("pages.cashFlow.projectedInflow")}</th>
                <th className="p-2 text-start">{t("pages.cashFlow.projectedOutflow")}</th>
                <th className="p-2 text-start">{t("pages.cashFlow.netNeed")}</th>
              </tr>
            </thead>
            <tbody>
              {months.map((m) => (
                <tr key={m.month} className="border-t">
                  <td className="p-2">{m.month.slice(0, 7)}</td>
                  <td className="p-2">
                    {m.inflow_status === "unregistered"
                      ? t("pages.cashFlow.noScheduledReceipts")
                      : formatFaAmount(m.projected_inflow)}
                  </td>
                  <td className="p-2">{formatFaAmount(m.projected_outflow)}</td>
                  <td className="p-2">{formatFaAmount(m.net_need)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-lg border p-4" data-testid="cash-net-need-card">
        <h3 className="mb-2 font-medium">{t("pages.cashFlow.suggestedNeedTitle")}</h3>
        {need.isLoading ? (
          <LoadingSkeleton rows={2} />
        ) : need.data ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div className="flex justify-between gap-4">
              <dt>{t("pages.cashFlow.dueCommitments")}</dt>
              <dd>{formatFaAmount(need.data.due_commitments)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>{t("pages.cashFlow.essentialCosts")}</dt>
              <dd>{formatFaAmount(need.data.essential_costs)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>{t("pages.cashFlow.certainReceipts")}</dt>
              <dd>{formatFaAmount(need.data.certain_planned_receipts)}</dd>
            </div>
            <div className="flex justify-between gap-4 font-medium">
              <dt>{t("pages.cashFlow.suggestedNetNeed")}</dt>
              <dd>{formatFaAmount(need.data.suggested_net_need)}</dd>
            </div>
          </dl>
        ) : null}
      </div>
    </div>
  );
}
