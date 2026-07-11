import { useMemo } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { isoToJalali } from "@/app/lib/jalali-utils";
import { formatBillions, type MonthlyCashFlowRow } from "@/app/lib/api/cashflow";

const JALALI_MONTHS = [
  "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
  "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
];

export function monthLabel(iso: string) {
  const jalali = isoToJalali(iso.slice(0, 10));
  if (!jalali) return iso.slice(0, 7);
  const parts = jalali.split("/");
  const m = Number(parts[1]);
  return JALALI_MONTHS[m - 1] ?? jalali.slice(0, 7);
}

export function CashFlowChart({
  data,
  todayIso,
}: {
  data: MonthlyCashFlowRow[];
  todayIso: string;
}) {
  const chartData = useMemo(
    () =>
      data.map((row) => ({
        ...row,
        label: monthLabel(row.month),
      })),
    [data],
  );

  const todayLabel = monthLabel(todayIso);

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} />
          <YAxis yAxisId="left" tickFormatter={formatBillions} tick={{ fontSize: 11 }} />
          <YAxis yAxisId="right" orientation="left" tickFormatter={formatBillions} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name) => [
              formatBillions(Number(value ?? 0)),
              name === "inflow" ? "دریافت" : name === "outflow" ? "پرداخت" : "مانده تجمعی",
            ]}
          />
          <Legend
            formatter={(value) =>
              value === "inflow" ? "دریافت" : value === "outflow" ? "پرداخت" : "مانده تجمعی"
            }
          />
          <ReferenceLine x={todayLabel} stroke="#ef4444" strokeDasharray="4 4" label="امروز" />
          <Bar yAxisId="left" dataKey="inflow" fill="#22c55e" name="inflow" />
          <Bar yAxisId="left" dataKey="outflow" fill="#ef4444" name="outflow" />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cumulative_balance"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="cumulative_balance"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
