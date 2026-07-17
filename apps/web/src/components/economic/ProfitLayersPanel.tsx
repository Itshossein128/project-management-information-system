import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatFaAmount, profitColor, type EconomicSnapshot } from "@/app/lib/api/economic";

export function ProfitLayersPanel({ snapshot }: { snapshot: EconomicSnapshot }) {
  const profitBars = [
    { name: "حسابداری", value: snapshot.accounting_profit },
    { name: "واقعی", value: snapshot.real_profit },
    { name: "اقتصادی", value: snapshot.economic_profit },
  ];

  return (
    <div className="space-y-6" data-testid="economic-overview">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          {
            title: "سود حسابداری",
            value: snapshot.accounting_profit,
            formula: "درآمد − هزینه واقعی",
            sub: `${formatFaAmount(snapshot.revenue_to_date)} − ${formatFaAmount(snapshot.actual_cost)}`,
          },
          {
            title: "سود واقعی",
            value: snapshot.real_profit,
            formula: "درآمد − هزینه تعدیل‌شده با تورم",
            sub: `تفاوت: ${formatFaAmount(snapshot.real_profit - snapshot.accounting_profit)}`,
          },
          {
            title: "سود اقتصادی",
            value: snapshot.economic_profit,
            formula: "درآمد − هزینه − تأمین مالی",
            sub: `${formatFaAmount(snapshot.financing_cost)} هزینه تأخیر`,
          },
          {
            title: "سرمایه در گردش",
            value: snapshot.working_capital,
            formula: "حداکثر هزینه تجمعی − پرداخت",
            sub: "نیاز نقدینگی فعلی",
          },
        ].map((card) => (
          <div key={card.title} className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">{card.title}</p>
            <p className={`text-2xl font-bold ${profitColor(card.value)}`}>{formatFaAmount(card.value)}</p>
            <p className="mt-1 text-xs text-muted-foreground">{card.formula}</p>
            <p className="text-xs text-amber-700">{card.sub}</p>
          </div>
        ))}
      </div>

      <div className="h-72 rounded-lg border p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={profitBars}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v) => formatFaAmount(v)} />
            <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
            <Bar dataKey="value">
              {profitBars.map((entry) => (
                <Cell key={entry.name} fill={entry.value >= 0 ? "#059669" : "#dc2626"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
