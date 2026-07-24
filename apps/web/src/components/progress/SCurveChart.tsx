import { useMemo } from "react";
import {
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
import type { SCurvePoint } from "@/app/lib/api/progress";
import { chartColor } from "@/design/tokens";

export function SCurveChart({
  data,
  todayIso,
}: {
  data: SCurvePoint[];
  todayIso: string;
}) {
  const chartData = useMemo(
    () =>
      data.map((row) => ({
        ...row,
        label: isoToJalali(row.date) || row.date,
      })),
    [data],
  );

  const todayLabel = isoToJalali(todayIso) || todayIso;
  const colors = useMemo(
    () => ({
      today: chartColor("danger"),
      planned: chartColor("info"),
      actual: chartColor("success"),
    }),
    [],
  );

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}٪`} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name) => [
              `${Number(value ?? 0).toFixed(1)}٪`,
              name === "planned_progress" ? "برنامه" : "واقعی",
            ]}
            labelFormatter={(label) => `تاریخ: ${label}`}
          />
          <Legend
            formatter={(value) =>
              value === "planned_progress" ? "برنامه‌ریزی شده" : "واقعی"
            }
          />
          <ReferenceLine x={todayLabel} stroke={colors.today} strokeDasharray="4 4" label="امروز" />
          <Line
            type="monotone"
            dataKey="planned_progress"
            stroke={colors.planned}
            strokeWidth={2}
            dot={false}
            name="planned_progress"
          />
          <Line
            type="monotone"
            dataKey="actual_progress"
            stroke={colors.actual}
            strokeWidth={2}
            dot={false}
            name="actual_progress"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
