import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  fetchForecast,
  fetchMonthlyCashFlow,
  formatFaAmount,
  monthIsoToKey,
  upsertForecast,
  type ForecastRow,
} from "@/app/lib/api/cashflow";
import { CashFlowChart, monthLabel } from "@/components/cashflow/CashFlowChart";
import { useToast } from "@/components/ui/toast";

function ForecastRowEditor({
  projectId,
  row,
}: {
  projectId: string;
  row: ForecastRow;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [inflow, setInflow] = useState(String(row.expected_inflow));
  const [outflow, setOutflow] = useState(String(row.expected_outflow));
  const [confidence, setConfidence] = useState(row.confidence_pct ?? 80);

  const save = useMutation({
    mutationFn: () =>
      upsertForecast(projectId, monthIsoToKey(row.month), {
        expected_inflow: Number(inflow),
        expected_outflow: Number(outflow),
        confidence_pct: confidence,
      }),
    onSuccess: () => {
      toast.success("ذخیره شد");
      qc.invalidateQueries({ queryKey: ["cash-forecast", projectId] });
      qc.invalidateQueries({ queryKey: ["cash-monthly", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const forecastNet = Number(inflow) - Number(outflow);
  const actualNet =
    row.actual_net != null ? row.actual_net : null;
  const deviation =
    actualNet != null ? actualNet - forecastNet : null;

  return (
    <tr className="border-t">
      <td className="px-3 py-2 font-medium">{monthLabel(row.month)}</td>
      <td className="px-3 py-2">
        <input
          type="number"
          className="w-28 rounded border px-2 py-1 text-sm"
          value={inflow}
          onChange={(e) => setInflow(e.target.value)}
          onBlur={() => save.mutate()}
        />
      </td>
      <td className="px-3 py-2">
        <input
          type="number"
          className="w-28 rounded border px-2 py-1 text-sm"
          value={outflow}
          onChange={(e) => setOutflow(e.target.value)}
          onBlur={() => save.mutate()}
        />
      </td>
      <td className="px-3 py-2">{formatFaAmount(forecastNet)}</td>
      <td className="px-3 py-2">
        {row.actual_inflow != null ? formatFaAmount(row.actual_inflow) : "—"}
      </td>
      <td className="px-3 py-2">
        {row.actual_outflow != null ? formatFaAmount(row.actual_outflow) : "—"}
      </td>
      <td className="px-3 py-2">
        {actualNet != null ? formatFaAmount(actualNet) : "—"}
      </td>
      <td
        className={`px-3 py-2 ${deviation != null && deviation >= 0 ? "text-emerald-600" : "text-red-600"}`}
      >
        {deviation != null ? formatFaAmount(deviation) : "—"}
      </td>
      <td className="px-3 py-2">
        <input
          type="range"
          min={0}
          max={100}
          value={confidence}
          onChange={(e) => setConfidence(Number(e.target.value))}
          onMouseUp={() => save.mutate()}
          onTouchEnd={() => save.mutate()}
          className="w-24"
        />
        <span className="ms-2 text-xs">{confidence}٪</span>
      </td>
    </tr>
  );
}

export function ForecastTab({ projectId }: { projectId: string }) {
  const todayIso = new Date().toISOString().slice(0, 10);

  const { data: forecastData, isLoading: forecastLoading } = useQuery({
    queryKey: ["cash-forecast", projectId],
    queryFn: () => fetchForecast(projectId),
  });

  const { data: monthlyData } = useQuery({
    queryKey: ["cash-monthly", projectId],
    queryFn: () => fetchMonthlyCashFlow(projectId),
  });

  const rows = useMemo(() => {
    const existing = forecastData?.results ?? [];
    if (existing.length >= 12) return existing.slice(0, 12);
    const result = [...existing];
    const now = new Date();
    for (let i = result.length; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
      result.push({
        month: d.toISOString().slice(0, 10),
        expected_inflow: 0,
        expected_outflow: 0,
        confidence_pct: 80,
        notes: "",
        actual_inflow: null,
        actual_outflow: null,
        actual_net: null,
      });
    }
    return result;
  }, [forecastData?.results]);

  const chartData = monthlyData?.results ?? [];

  return (
    <div className="space-y-6">
      {forecastLoading ? (
        <p className="text-muted-foreground">در حال بارگذاری...</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[1000px] text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-start">ماه</th>
                <th className="px-3 py-2 text-start">دریافت پیش‌بینی</th>
                <th className="px-3 py-2 text-start">پرداخت پیش‌بینی</th>
                <th className="px-3 py-2 text-start">خالص پیش‌بینی</th>
                <th className="px-3 py-2 text-start">دریافت واقعی</th>
                <th className="px-3 py-2 text-start">پرداخت واقعی</th>
                <th className="px-3 py-2 text-start">خالص واقعی</th>
                <th className="px-3 py-2 text-start">انحراف</th>
                <th className="px-3 py-2 text-start">اطمینان</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <ForecastRowEditor key={row.month} projectId={projectId} row={row} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {chartData.length > 0 && (
        <div className="rounded-lg border p-4">
          <h3 className="mb-4 font-medium">نمودار جریان نقدی</h3>
          <CashFlowChart data={chartData} todayIso={todayIso} />
        </div>
      )}
    </div>
  );
}
