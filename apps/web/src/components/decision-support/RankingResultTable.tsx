import { useTranslation } from "react-i18next";
import type { SawRankingRow } from "@/app/lib/api/decision-support";

type Props = {
  method: "saw";
  ranking: SawRankingRow[];
};

export function RankingResultTable({ method, ranking }: Props) {
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
          </tr>
        </thead>
        <tbody>
          {ranking.map((row) => (
            <tr key={`${row.rank}-${row.option}`}>
              <td className="border border-border px-2 py-1">{row.rank}</td>
              <td className="border border-border px-2 py-1">{row.option}</td>
              <td className="border border-border px-2 py-1">{row.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
