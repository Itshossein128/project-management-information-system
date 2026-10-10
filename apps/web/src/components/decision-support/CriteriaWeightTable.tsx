import { useTranslation } from "react-i18next";
import type { AhpWeightRow } from "@/app/lib/api/decision-support";
import { formatWeightDecimal, formatWeightPercent } from "./criteria-weight-rules";

type Props = {
  weights: AhpWeightRow[];
  cr?: number;
  ci?: number;
  lambdaMax?: number;
  isConsistent?: boolean;
};

export function CriteriaWeightTable({
  weights,
  cr,
  ci,
  lambdaMax,
  isConsistent = true,
}: Props) {
  const { t } = useTranslation();

  if (!weights.length) {
    return <p className="text-sm text-muted-foreground">{t("decisionSupport.resultEmpty")}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-medium">
          {t("decisionSupport.resultTitle", { method: "AHP" })}
        </h3>
        {cr !== undefined && (
          <div className="flex items-center gap-2 text-xs">
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ${
                isConsistent
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-400"
                  : "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-400"
              }`}
            >
              {isConsistent
                ? t("decisionSupport.crBadgeConsistent")
                : t("decisionSupport.crBadgeInconsistent")}
            </span>
            <span className="text-muted-foreground">
              {t("decisionSupport.crLabel")}: {cr.toFixed(4)}
            </span>
          </div>
        )}
      </div>

      {!isConsistent && cr !== undefined && (
        <div
          role="alert"
          className="rounded-md border border-amber-500/50 bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-200"
        >
          <p className="font-medium">
            {t("decisionSupport.crInconsistent", { cr: cr.toFixed(4) })}
          </p>
        </div>
      )}

      {isConsistent && cr !== undefined && (
        <div
          role="status"
          className="rounded-md border border-emerald-500/30 bg-emerald-50/50 p-2.5 text-xs text-emerald-800 dark:bg-emerald-950/20 dark:text-emerald-300"
        >
          <p>{t("decisionSupport.crConsistent", { cr: cr.toFixed(4) })}</p>
        </div>
      )}

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colRank")}</th>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colCriterion")}</th>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colWeight")}</th>
            <th className="border border-border px-2 py-1 text-start">{t("decisionSupport.colPercent")}</th>
          </tr>
        </thead>
        <tbody>
          {weights.map((row) => (
            <tr key={`${row.rank}-${row.criterion}`}>
              <td className="border border-border px-2 py-1 font-medium">{row.rank}</td>
              <td className="border border-border px-2 py-1">{row.criterion}</td>
              <td className="border border-border px-2 py-1 font-mono">{formatWeightDecimal(row.weight)}</td>
              <td className="border border-border px-2 py-1">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 flex-1 max-w-[120px] rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${Math.min(100, Math.max(0, row.weight * 100))}%` }}
                    />
                  </div>
                  <span className="font-mono text-xs">{formatWeightPercent(row.weight)}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {(ci !== undefined || lambdaMax !== undefined) && (
        <div className="flex flex-wrap gap-4 text-xs text-muted-foreground pt-1">
          {ci !== undefined && (
            <span>
              {t("decisionSupport.ciLabel")}: <strong className="font-mono">{ci.toFixed(4)}</strong>
            </span>
          )}
          {lambdaMax !== undefined && (
            <span>
              {t("decisionSupport.lambdaMaxLabel")}: <strong className="font-mono">{lambdaMax.toFixed(4)}</strong>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
