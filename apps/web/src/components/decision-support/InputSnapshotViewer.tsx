import { useTranslation } from "react-i18next";
import type {
  DecisionRun,
  TopsisRankingRow,
} from "@/app/lib/api/decision-support";
import { classifyHistory, object } from "./execution-record-rules";
import { IsmLayerList, IsmMatrixTable } from "./IsmLayerList";
import { CriteriaWeightTable } from "./CriteriaWeightTable";
import { RankingSnapshotTable } from "./RankingSnapshotTable";
import { RankingResultTable } from "./RankingResultTable";
import { CriteriaMetricsTable } from "./CriteriaMetricsTable";
export function InputSnapshotViewer({ run }: { run: DecisionRun | null }) {
  const { t, i18n } = useTranslation();
  if (!run) return null;
  const h = classifyHistory(run),
    s = h.snapshot;
  const unavailable = <p>{t("decisionSupport.historyResultUnavailable")}</p>;
  return (
    <section
      data-history-detail={run.id}
      aria-label={t("decisionSupport.historicalRun")}
      className="space-y-3 rounded-md border border-border p-3 text-sm"
    >
      <h3 className="font-medium">{t("decisionSupport.historicalRun")}</h3>
      <p>{t("decisionSupport.historyReadOnly")}</p>
      <dl className="flex flex-wrap gap-4">
        {[
          ["historyRunId", run.id],
          ["historyMethod", run.method.toUpperCase()],
          ["historyActor", run.extracted_by_name || run.extracted_by],
          [
            "historyTime",
            new Date(run.extracted_at).toLocaleString(i18n.language),
          ],
        ].map(([key, value]) => (
          <div key={key}>
            <dt>{t("decisionSupport." + key)}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <h4>{t("decisionSupport.snapshotTitle")}</h4>
      {(run.method === "saw" || run.method === "topsis") && (
        <RankingSnapshotTable
          snapshot={s}
          criteria={h.criteria}
          alternatives={h.alternatives}
        />
      )}
      {run.method === "saw" &&
        (h.ranking ? (
          <RankingResultTable method="saw" ranking={h.ranking} />
        ) : (
          unavailable
        ))}
      {run.method === "topsis" &&
        (h.ranking ? (
          <RankingResultTable
            method="topsis"
            ranking={h.ranking as TopsisRankingRow[]}
            extraColumns={(["d_best", "d_worst", "closeness"] as const).map(
              (key) => ({
                key,
                header: t(
                  "decisionSupport." +
                    {
                      d_best: "colDBest",
                      d_worst: "colDWorst",
                      closeness: "colCloseness",
                    }[key],
                ),
                render: (row) =>
                  typeof row[key] === "number" && Number.isFinite(row[key])
                    ? Number(row[key].toFixed(4))
                    : t("decisionSupport.historyResultUnavailable"),
              }),
            )}
          />
        ) : (
          unavailable
        ))}
      {run.method === "ahp" && (
        <>
          <IsmMatrixTable
            criteria={h.criteria}
            matrix={s.ahp_matrix}
            label={t("decisionSupport.frozenMatrix")}
          />
          {h.ahp ? (
            <CriteriaWeightTable
              weights={h.ahp.weights}
              cr={h.ahp.cr}
              ci={h.ahp.ci}
              lambdaMax={h.ahp.lambda_max}
              isConsistent={h.ahp.is_consistent}
            />
          ) : (
            unavailable
          )}
        </>
      )}
      {run.method === "ism" &&
        (h.ism ? (
          <IsmLayerList
            result={h.ism}
            criteria={h.criteria}
            direct={s.ism_matrix}
          />
        ) : (
          <>
            <IsmMatrixTable
              criteria={h.criteria}
              matrix={s.ism_matrix}
              label={t("decisionSupport.ismDirect")}
            />
            {unavailable}
          </>
        ))}
      {run.method === "dematel" && (
        <>
          <IsmMatrixTable
            criteria={h.criteria}
            matrix={s.dematel_matrix}
            label={t("decisionSupport.frozenMatrix")}
          />
          {h.dematel ? (
            <>
              <CriteriaMetricsTable result={h.dematel} />
              <IsmMatrixTable
                criteria={h.criteria}
                matrix={h.dematel.normalized_matrix}
                label={t("decisionSupport.dematelNormalized")}
              />
              <IsmMatrixTable
                criteria={h.criteria}
                matrix={h.dematel.total_relation_matrix}
                label={t("decisionSupport.dematelTotal")}
              />
              <pre>{JSON.stringify(h.dematel.numerical_policy, null, 2)}</pre>
            </>
          ) : (
            unavailable
          )}
        </>
      )}
      {!object(run.input_snapshot) && unavailable}
      <details>
        <summary>{t("decisionSupport.snapshotDetails")}</summary>
        <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words text-xs text-muted-foreground">
          {JSON.stringify(run.input_snapshot, null, 2)}
        </pre>
      </details>
    </section>
  );
}
