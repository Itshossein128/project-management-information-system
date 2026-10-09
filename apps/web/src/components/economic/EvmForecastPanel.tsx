import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { fetchCashFlowReal, fetchEconomicForecast, fetchWorkingCapital, formatFaAmount } from "@/app/lib/api/economic";
import {
  evmIndexValue,
  evmIsNotComputable,
  fetchProgressKpis,
} from "@/app/lib/api/progress";
import { KPICard } from "@/components/progress/KPICard";
import { LoadingSkeleton } from "@/components/layout/page-header";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { chartColor } from "@/design/tokens";

export function EvmForecastPanel({ projectId, asOf }: { projectId: string; asOf?: string }) {
  const { t } = useTranslation();
  const notComputable = t("progress.evm.notComputable");
  const colors = {
    workingCapital: chartColor("danger"),
    nominalOutflow: chartColor("accent"),
    realOutflow: chartColor("danger"),
    inflow: chartColor("success"),
    netReal: chartColor("info"),
  };
  const { data: forecast, isLoading: fLoading } = useQuery({
    queryKey: ["economic-forecast", projectId, asOf],
    queryFn: () => fetchEconomicForecast(projectId, asOf),
  });

  const { data: kpis } = useQuery({
    queryKey: ["progress-kpis", projectId],
    queryFn: () => fetchProgressKpis(projectId),
  });

  const { data: wc, isLoading: wcLoading } = useQuery({
    queryKey: ["working-capital", projectId],
    queryFn: () => fetchWorkingCapital(projectId),
  });

  const { data: cashFlowReal, isLoading: cfLoading } = useQuery({
    queryKey: ["cash-flow-real", projectId, asOf],
    queryFn: () => fetchCashFlowReal(projectId, asOf),
  });

  if (fLoading || wcLoading || cfLoading) return <LoadingSkeleton rows={8} />;

  const spi =
    forecast?.spi ??
    evmIndexValue(kpis?.spi, kpis?.spi_legacy) ??
    null;
  const cpi =
    forecast?.cpi ??
    evmIndexValue(kpis?.cpi, kpis?.cpi_legacy) ??
    null;
  const eacNominal =
    forecast?.eac_nominal ??
    evmIndexValue(kpis?.eac, kpis?.eac_legacy) ??
    null;
  const etc =
    forecast?.etc_to_complete ??
    evmIndexValue(kpis?.etc, kpis?.etc_legacy) ??
    null;
  const vac =
    forecast?.vac ??
    evmIndexValue(kpis?.vac, kpis?.vac_legacy) ??
    null;

  const spiNotComputable = spi == null || evmIsNotComputable(kpis?.spi);
  const cpiNotComputable = cpi == null || evmIsNotComputable(kpis?.cpi);
  const eacNotComputable = eacNominal == null || evmIsNotComputable(kpis?.eac);
  const etcNotComputable = etc == null || evmIsNotComputable(kpis?.etc);
  const vacNotComputable = vac == null || evmIsNotComputable(kpis?.vac);

  return (
    <div className="space-y-6" data-testid="economic-forecast">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KPICard title="BAC" value={formatFaAmount(Number(forecast?.bac ?? kpis?.bac ?? 0))} />
        <KPICard
          title="SPI"
          value={spiNotComputable || spi == null ? notComputable : spi.toFixed(2)}
        />
        <KPICard
          title="CPI"
          value={cpiNotComputable || cpi == null ? notComputable : cpi.toFixed(2)}
        />
        <KPICard
          title="EAC (اسمی)"
          value={
            eacNotComputable || eacNominal == null
              ? notComputable
              : formatFaAmount(eacNominal)
          }
        />
        <KPICard
          title="EAC (تعدیل تورم)"
          value={
            forecast?.eac_inflation_adjusted != null
              ? formatFaAmount(forecast.eac_inflation_adjusted)
              : "—"
          }
        />
        <KPICard
          title="ETC"
          value={etcNotComputable || etc == null ? notComputable : formatFaAmount(etc)}
        />
        <KPICard
          title="VAC"
          value={vacNotComputable || vac == null ? notComputable : formatFaAmount(vac)}
        />
        <KPICard
          title="ضریب تورم"
          value={
            forecast?.inflation_factor != null
              ? forecast.inflation_factor.toFixed(2)
              : "—"
          }
        />
      </div>

      {wc && wc.points.length > 0 ? (
        <div className="rounded-lg border p-4">
          <h3 className="mb-2 font-semibold">
            منحنی سرمایه در گردش (اوج: {formatFaAmount(wc.peak_working_capital)})
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={wc.points}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => formatFaAmount(v)} />
                <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
                <Line type="monotone" dataKey="working_capital" stroke={colors.workingCapital} name="سرمایه در گردش" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : null}

      {cashFlowReal && cashFlowReal.points.length > 0 ? (
        <div className="rounded-lg border p-4" data-testid="cash-flow-real-chart">
          <h3 className="mb-2 font-semibold">جریان نقدی واقعی (اسمی در برابر تعدیل‌شده)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={cashFlowReal.points}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => formatFaAmount(v)} />
                <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
                <Legend />
                <Bar dataKey="nominal_outflow" fill={colors.nominalOutflow} name="خروجی اسمی" />
                <Bar dataKey="real_outflow" fill={colors.realOutflow} name="خروجی واقعی" />
                <Bar dataKey="inflow" fill={colors.inflow} name="ورودی" />
                <Line type="monotone" dataKey="net_real" stroke={colors.netReal} name="خالص واقعی" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : null}
    </div>
  );
}
