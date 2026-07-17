import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchEconomicHistory, formatFaAmount } from "@/app/lib/api/economic";
import { LoadingSkeleton } from "@/components/layout/page-header";

export function EconomicHistoryChart({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["economic-history", projectId],
    queryFn: () => fetchEconomicHistory(projectId),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;

  const points = (data?.results ?? []).map((s) => ({
    date: s.snapshot_date,
    accounting: s.accounting_profit,
    real: s.real_profit,
    economic: s.economic_profit,
    working_capital: s.working_capital,
  }));

  if (points.length === 0) {
    return (
      <p className="rounded-lg border border-dashed py-12 text-center text-muted-foreground">
        تاریخچه‌ای ثبت نشده است
      </p>
    );
  }

  return (
    <div className="rounded-lg border p-4">
      <h3 className="mb-3 font-semibold">روند سود و سرمایه در گردش</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={(v) => formatFaAmount(v)} />
            <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
            <Legend />
            <Line type="monotone" dataKey="accounting" stroke="#3b82f6" name="حسابداری" />
            <Line type="monotone" dataKey="real" stroke="#059669" name="واقعی" />
            <Line type="monotone" dataKey="economic" stroke="#7c3aed" name="اقتصادی" />
            <Line type="monotone" dataKey="working_capital" stroke="#dc2626" name="سرمایه در گردش" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
