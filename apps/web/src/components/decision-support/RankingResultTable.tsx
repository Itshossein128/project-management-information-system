import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { SawRankingRow, TopsisRankingRow } from "@/app/lib/api/decision-support";

export type ExtraColumn<T> = {
  key: keyof T;
  header: string;
  render?: (row: T) => ReactNode;
};

type Props =
  | {
      method: "saw";
      ranking: SawRankingRow[];
      extraColumns?: never;
    }
  | {
      method: "topsis";
      ranking: TopsisRankingRow[];
      extraColumns?: ExtraColumn<TopsisRankingRow>[];
    };

export function RankingResultTable({ method, ranking, extraColumns }: Props) {
  const { t } = useTranslation();

  if (!ranking.length) {
    return <p className="text-sm text-muted-foreground">{t("decisionSupport.resultEmpty")}</p>;
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">
        {t("decisionSupport.resultTitle", { method: method.toUpperCase() })}
      </h3>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colRank")}</th>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colOption")}</th>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colScore")}</th>
            {extraColumns?.map((col) => (
              <th key={String(col.key)} className="border border-border px-2 py-1 text-start">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ranking.map((row) => (
            <tr key={`${row.rank}-${row.option}`}>
              <td className="border border-border px-2 py-1">{row.rank}</td>
              <td className="border border-border px-2 py-1">{row.option}</td>
              <td className="border border-border px-2 py-1">{row.score}</td>
              {extraColumns?.map((col) => {
                const val = (row as TopsisRankingRow)[col.key];
                return (
                  <td key={String(col.key)} className="border border-border px-2 py-1">
                    {col.render
                      ? col.render(row as TopsisRankingRow)
                      : typeof val === "number"
                        ? Number.isInteger(val)
                          ? val
                          : Number(val.toFixed(4))
                        : String(val ?? "")}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
