import { useQuery } from "@tanstack/react-query";
import {
  fetchGapAnalysis,
  fetchReceivables,
  formatFaAmount,
} from "@/app/lib/api/cashflow";
import { monthLabel } from "@/components/cashflow/CashFlowChart";
import { WaterfallChart } from "@/components/cashflow/WaterfallChart";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

export function GapAnalysisTab({ projectId }: { projectId: string }) {
  const {
    data: gapData,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["cash-gap", projectId],
    queryFn: () => fetchGapAnalysis(projectId),
  });

  const { data: receivables } = useQuery({
    queryKey: ["cash-receivables", projectId],
    queryFn: () => fetchReceivables(projectId),
  });

  const gaps = gapData?.results ?? [];

  return (
    <div className="space-y-6">
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : gaps.length === 0 ? (
        <div className="rounded-lg border border-success-200 bg-success-50 p-8 text-center text-success-800">
          در بازه پیش‌بینی شده کمبود نقدینگی وجود ندارد
        </div>
      ) : (
        <>
          <div className="rounded-lg border border-warning-200 bg-warning-50 p-4 text-warning-900">
            ⚠ {gaps.length} ماه با کمبود نقدینگی پیش‌بینی شده شناسایی شد
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {gaps.map((g) => (
              <div
                key={g.month}
                className={`rounded-lg border p-4 ${
                  g.is_cumulative_negative
                    ? "border-danger-300 bg-danger-50"
                    : "border-warning-300 bg-warning-50"
                }`}
              >
                <h4 className="font-medium">{monthLabel(g.month)}</h4>
                <dl className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <dt>دریافت پیش‌بینی</dt>
                    <dd>{formatFaAmount(g.expected_inflow)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>پرداخت پیش‌بینی</dt>
                    <dd>{formatFaAmount(g.expected_outflow)}</dd>
                  </div>
                  <div className="flex justify-between font-medium text-danger-700">
                    <dt>کمبود</dt>
                    <dd>{formatFaAmount(g.gap_amount)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>مانده تجمعی</dt>
                    <dd>{formatFaAmount(g.cumulative_balance)}</dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>
          <div className="rounded-lg border p-4">
            <h3 className="mb-4 font-medium">نمودار آبشاری</h3>
            <WaterfallChart data={gaps} />
          </div>
        </>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-medium">مطالبات (کارفرما)</h3>
          {receivables?.receivables ? (
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt>کل IPC تأییدشده پرداخت‌نشده</dt>
                <dd>{formatFaAmount(receivables.receivables.total_approved_unpaid)}</dd>
              </div>
              <div className="flex justify-between text-danger-600">
                <dt>معوق</dt>
                <dd>{formatFaAmount(receivables.receivables.overdue)}</dd>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-muted-foreground">
              {receivables?.note ?? "پس از راه‌اندازی ماژول قراردادها فعال می‌شود"}
            </p>
          )}
        </div>
        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-medium">بدهی‌ها (پیمانکاران)</h3>
          {receivables?.payables ? (
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt>کل IPC پیمانکاران پرداخت‌نشده</dt>
                <dd>{formatFaAmount(receivables.payables.total_approved_unpaid)}</dd>
              </div>
              <div className="flex justify-between text-danger-600">
                <dt>معوق</dt>
                <dd>{formatFaAmount(receivables.payables.overdue)}</dd>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-muted-foreground">
              {receivables?.note ?? "پس از راه‌اندازی ماژول قراردادها فعال می‌شود"}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
