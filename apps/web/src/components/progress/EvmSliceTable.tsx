import { useTranslation } from "react-i18next";
import type { EvmCbsRow, EvmIndex, EvmMeasure, EvmPhaseRow } from "@/app/lib/api/progress";
import { evmIndexValue, evmIsNotComputable, evmIsUnregistered, evmMeasureAmount } from "@/app/lib/api/progress";
import { formatFaAmount } from "@/app/lib/api/economic";

function fmtMeasure(m: EvmMeasure, t: (k: string) => string): string {
  if (evmIsUnregistered(m)) return t("progress.evm.unregistered");
  const amt = evmMeasureAmount(m);
  return amt == null ? t("progress.evm.notComputable") : formatFaAmount(amt);
}

function fmtIndex(i: EvmIndex, t: (k: string) => string, digits = 2): string {
  if (evmIsNotComputable(i)) return t("progress.evm.notComputable");
  const v = evmIndexValue(i);
  return v == null ? t("progress.evm.notComputable") : v.toFixed(digits);
}

export function EvmPhaseTable({ rows }: { rows: EvmPhaseRow[] }) {
  const { t } = useTranslation();
  if (!rows.length) {
    return <p className="text-sm text-muted-foreground">{t("progress.evm.noPhaseRows")}</p>;
  }
  return (
    <div className="overflow-x-auto" data-testid="evm-phase-table">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-start">
            <th className="p-2">{t("progress.evm.phase")}</th>
            <th className="p-2">BAC</th>
            <th className="p-2">PV</th>
            <th className="p-2">EV</th>
            <th className="p-2">AC</th>
            <th className="p-2">SPI</th>
            <th className="p-2">CPI</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.wbs_id} className="border-b border-border/60">
              <td className="p-2">
                {row.wbs_code} — {row.wbs_name}
              </td>
              <td className="p-2">{formatFaAmount(row.bac)}</td>
              <td className="p-2">{fmtMeasure(row.pv, t)}</td>
              <td className="p-2">{fmtMeasure(row.ev, t)}</td>
              <td className="p-2">{fmtMeasure(row.ac, t)}</td>
              <td className="p-2">{fmtIndex(row.spi, t)}</td>
              <td className="p-2">{fmtIndex(row.cpi, t)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function EvmCbsTable({ rows }: { rows: EvmCbsRow[] }) {
  const { t } = useTranslation();
  if (!rows.length) {
    return <p className="text-sm text-muted-foreground">{t("progress.evm.noCbsRows")}</p>;
  }
  return (
    <div className="overflow-x-auto" data-testid="evm-cbs-table">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-start">
            <th className="p-2">{t("progress.evm.cbs")}</th>
            <th className="p-2">BAC</th>
            <th className="p-2">PV</th>
            <th className="p-2">EV</th>
            <th className="p-2">AC</th>
            <th className="p-2">SPI</th>
            <th className="p-2">CPI</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.cbs_id} className="border-b border-border/60">
              <td className="p-2" style={{ paddingInlineStart: `${(row.depth || 1) * 0.5}rem` }}>
                {row.cbs_code} — {row.cbs_name}
              </td>
              <td className="p-2">{formatFaAmount(row.bac)}</td>
              <td className="p-2">{fmtMeasure(row.pv, t)}</td>
              <td className="p-2">{fmtMeasure(row.ev, t)}</td>
              <td className="p-2">{fmtMeasure(row.ac, t)}</td>
              <td className="p-2">{fmtIndex(row.spi, t)}</td>
              <td className="p-2">{fmtIndex(row.cpi, t)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
