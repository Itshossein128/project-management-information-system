import { useQuery } from "@tanstack/react-query";
import { fetchFinancingCost, formatFaAmount } from "@/app/lib/api/economic";
import { LoadingSkeleton } from "@/components/layout/page-header";

export function FinancingCostPanel({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["financing", projectId],
    queryFn: () => fetchFinancingCost(projectId),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;

  return (
    <div className="rounded-lg border p-4">
      <h3 className="mb-3 font-semibold">هزینه تأمین مالی (تأخیر پرداخت IPC)</h3>
      <p className="mb-2 text-3xl font-bold">{data?.avg_payment_delay_days?.toFixed(0) ?? 0} روز</p>
      <p className="mb-2 text-sm text-muted-foreground">میانگین تأخیر پرداخت</p>
      <p className="mb-4 text-lg font-semibold">
        کل هزینه تأمین مالی: {formatFaAmount(data?.total_financing_cost ?? 0)}
      </p>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b">
            {["IPC", "تأخیر", "هزینه"].map((h) => (
              <th key={h} className="py-1 text-start">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(data?.details ?? []).map((d) => (
            <tr key={d.ipc_number} className="border-b">
              <td className="py-1">IPC {d.ipc_number}</td>
              <td className="py-1">{d.delay_days} روز</td>
              <td className="py-1">{formatFaAmount(d.financing_cost)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
