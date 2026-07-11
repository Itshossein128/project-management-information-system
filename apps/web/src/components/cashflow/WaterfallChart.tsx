import { useMemo } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import { formatBillions, type GapRow } from "@/app/lib/api/cashflow";
import { monthLabel } from "@/components/cashflow/CashFlowChart";

export function WaterfallChart({ data }: { data: GapRow[] }) {
  const chartData = useMemo(
    () =>
      data.map((row) => ({
        ...row,
        label: monthLabel(row.month),
      })),
    [data],
  );

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={formatBillions} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => formatBillions(Number(v ?? 0))} />
          <Bar dataKey="net" name="خالص">
            {chartData.map((entry) => (
              <Cell key={entry.month} fill={entry.net >= 0 ? "#22c55e" : "#ef4444"} />
            ))}
          </Bar>
          <Line
            type="monotone"
            dataKey="cumulative_balance"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="مانده تجمعی"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
