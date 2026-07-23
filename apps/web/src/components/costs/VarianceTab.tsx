import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  costCategoryLabel,
  fetchVariance,
  formatFaAmount,
  type VarianceRow,
} from "@/app/lib/api/costs";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";

type GroupBy = "wbs" | "category" | "activity";

function rowLabel(row: VarianceRow, groupBy: GroupBy): string {
  if (groupBy === "category") return costCategoryLabel(row.cost_category ?? "");
  if (groupBy === "activity") {
    return row.activity_code
      ? `${row.activity_code} — ${row.activity_name ?? ""}`
      : (row.activity_name ?? "تخصیص‌نیافته");
  }
  return row.wbs_code ? `${row.wbs_code} — ${row.wbs_name ?? ""}` : (row.wbs_name ?? "تخصیص‌نیافته");
}

function varianceColor(row: VarianceRow): string {
  if (row.budget === 0 && row.actual > 0) return "bg-danger-50 dark:bg-danger-950/30";
  if (row.consumption_pct == null) return "";
  if (row.consumption_pct > 100) return "bg-danger-50 dark:bg-danger-950/30";
  if (row.consumption_pct > 85) return "bg-warning-50 dark:bg-warning-950/30";
  return "";
}

export function VarianceTab({ projectId }: { projectId: string }) {
  const [groupBy, setGroupBy] = useState<GroupBy>("wbs");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["cost-variance", projectId, groupBy],
    queryFn: () => fetchVariance(projectId, { group_by: groupBy }),
  });

  const rows = data?.results ?? [];

  const chartData = useMemo(
    () =>
      rows.slice(0, 20).map((r) => ({
        name: rowLabel(r, groupBy).slice(0, 24),
        budget: r.budget,
        actual: r.actual,
      })),
    [rows, groupBy],
  );

  const groupLabels: Record<GroupBy, string> = {
    wbs: "WBS",
    category: "دسته هزینه",
    activity: "فعالیت",
  };

  return (
    <div className="space-y-6" data-testid="variance-tab">
      <div className="flex flex-wrap gap-2">
        {(["wbs", "category", "activity"] as GroupBy[]).map((g) => (
          <Button
            key={g}
            size="sm"
            variant={groupBy === g ? "primary" : "secondary"}
            data-testid={`variance-group-${g}`}
            onClick={() => setGroupBy(g)}
          >
            {groupLabels[g]}
          </Button>
        ))}
        {data?.as_of ? (
          <span className="self-center text-sm text-muted-foreground">تا {data.as_of}</span>
        ) : null}
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : rows.length === 0 ? (
        <EmptyState
          title="داده‌ای یافت نشد"
          description="پس از ثبت بودجه و هزینه‌های واقعی، واریانس اینجا نمایش داده می‌شود."
        />
      ) : (
        <>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={60} />
                <YAxis tickFormatter={(v) => formatFaAmount(v)} tick={{ fontSize: 10 }} width={80} />
                <Tooltip
                  formatter={(value, name) => [
                    formatFaAmount(Number(value ?? 0)),
                    name === "budget" ? "بودجه" : "واقعی",
                  ]}
                />
                <Legend formatter={(v) => (v === "budget" ? "بودجه" : "واقعی")} />
                <Bar dataKey="budget" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="actual" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-3 py-2 text-start">عنوان</th>
                  <th className="px-3 py-2 text-start">بودجه</th>
                  <th className="px-3 py-2 text-start">واقعی</th>
                  <th className="px-3 py-2 text-start">واریانس</th>
                  <th className="px-3 py-2 text-start">درصد مصرف</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} className={`border-t border-border ${varianceColor(r)}`}>
                    <td className="px-3 py-2">{rowLabel(r, groupBy)}</td>
                    <td className="px-3 py-2">{formatFaAmount(r.budget)}</td>
                    <td className="px-3 py-2">{formatFaAmount(r.actual)}</td>
                    <td
                      className={`px-3 py-2 font-medium ${
                        r.variance < 0 ? "text-danger-600" : "text-success-600"
                      }`}
                    >
                      {formatFaAmount(r.variance)}
                    </td>
                    <td className="px-3 py-2">
                      {r.consumption_pct != null ? `${r.consumption_pct.toFixed(1)}٪` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
