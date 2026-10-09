import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import {
  fetchReceivablesReport,
  formatFaAmount,
} from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

export function ReceivablesPanel({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["ipc-receivables", projectId],
    queryFn: () => fetchReceivablesReport(projectId, { near_due_days: 7 }),
  });

  if (isLoading) return <LoadingSkeleton rows={4} />;
  if (isError) return <QueryErrorState onRetry={() => void refetch()} />;
  if (!data) return null;

  const { summary, items } = data;

  return (
    <div className="space-y-4 rounded-lg border p-4">
      <div>
        <h3 className="text-base font-semibold">{t("pages.contracts.receivablesTitle")}</h3>
        <p className="text-sm text-muted-foreground">
          {t("pages.contracts.receivablesHint")}
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded border p-3">
          <p className="text-sm text-muted-foreground">{t("pages.contracts.overdue")}</p>
          <p className="font-semibold text-danger-600">
            {summary.overdue_count} — {formatFaAmount(Number(summary.overdue_remaining))}
          </p>
        </div>
        <div className="rounded border p-3">
          <p className="text-sm text-muted-foreground">{t("pages.contracts.nearDue")}</p>
          <p className="font-semibold">
            {summary.near_due_count} — {formatFaAmount(Number(summary.near_due_remaining))}
          </p>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">{t("pages.contracts.noOpenReceivables")}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-2 py-1.5 text-start">{t("pages.contracts.ipc")}</th>
                <th className="px-2 py-1.5 text-start">{t("pages.contracts.contract")}</th>
                <th className="px-2 py-1.5 text-start">{t("pages.contracts.remaining")}</th>
                <th className="px-2 py-1.5 text-start">{t("pages.contracts.dueDate")}</th>
                <th className="px-2 py-1.5 text-start">{t("pages.contracts.band")}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.ipc_id} className="border-t">
                  <td className="px-2 py-1.5">
                    <Link
                      className="text-primary underline"
                      to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_IPCS}/${row.ipc_id}`}
                    >
                      {row.ipc_number}
                    </Link>
                  </td>
                  <td className="px-2 py-1.5">{row.contract_number}</td>
                  <td className="px-2 py-1.5">
                    {formatFaAmount(Number(row.remaining_receivable))}
                  </td>
                  <td className="px-2 py-1.5">{row.planned_payment_date}</td>
                  <td className="px-2 py-1.5">
                    {row.band === "overdue"
                      ? t("pages.contracts.overdue")
                      : t("pages.contracts.nearDue")}
                    {row.days_overdue != null
                      ? ` (${row.days_overdue}d)`
                      : row.days_until_due != null
                        ? ` (${row.days_until_due}d)`
                        : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
