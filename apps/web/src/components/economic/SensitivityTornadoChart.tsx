import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fetchSensitivity, formatFaAmount } from "@/app/lib/api/economic";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { chartColor } from "@/design/tokens";

export function SensitivityTornadoChart({ projectId }: { projectId: string }) {
  const impactColor = chartColor("warning");
  const { data, isLoading } = useQuery({
    queryKey: ["economic-sensitivity", projectId],
    queryFn: () => fetchSensitivity(projectId),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;

  const rows = (data?.sensitivity ?? []).map((r) => ({
    name: r.variable,
    impact: Math.abs(r.impact),
    low: r.low_profit,
    high: r.high_profit,
  }));

  if (rows.length === 0) {
    return (
      <p className="rounded-lg border border-dashed py-12 text-center text-muted-foreground">
        ابتدا یک شبیه‌سازی مونت‌کارلو اجرا کنید
      </p>
    );
  }

  return (
    <div className="rounded-lg border p-4" data-testid="sensitivity-tornado">
      <h3 className="mb-3 font-semibold">نمودار حساسیت (تورنادو)</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} layout="vertical" margin={{ left: 80 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={(v) => formatFaAmount(v)} />
            <YAxis type="category" dataKey="name" width={100} />
            <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
            <Bar dataKey="impact" fill={impactColor} name="تأثیر" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <table className="mt-4 w-full text-sm">
        <thead>
          <tr className="border-b">
            {["متغیر", "سود پایین", "سود بالا", "تأثیر"].map((h) => (
              <th key={h} className="py-1 text-start">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.name} className="border-b">
              <td className="py-1">{r.name}</td>
              <td className="py-1">{formatFaAmount(r.low)}</td>
              <td className="py-1">{formatFaAmount(r.high)}</td>
              <td className="py-1">{formatFaAmount(r.impact)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
