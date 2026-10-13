import { useTranslation } from "react-i18next";
import { object } from "./execution-record-rules";
export function RankingSnapshotTable({
  snapshot,
  criteria,
  alternatives,
}: {
  snapshot: Record<string, unknown>;
  criteria: string[];
  alternatives: string[];
}) {
  const { t } = useTranslation();
  const unavailable = t("decisionSupport.historyResultUnavailable");
  const cell = (v: unknown) =>
    typeof v === "number" && Number.isFinite(v)
      ? v
      : typeof v === "string"
        ? v
        : unavailable;
  const at = (v: unknown, i: number, j?: number): unknown =>
    Array.isArray(v)
      ? j === undefined
        ? v[i]
        : Array.isArray(v[i])
          ? v[i][j]
          : undefined
      : undefined;
  if (!criteria.length || !alternatives.length) return <p>{unavailable}</p>;
  return (
    <div className="overflow-x-auto" tabIndex={0}>
      <table
        aria-label={t("decisionSupport.frozenRankingInputs")}
        className="w-full border-collapse text-sm"
      >
        <thead>
          <tr>
            <th scope="col">{t("decisionSupport.colOption")}</th>
            {criteria.map((name, i) => (
              <th scope="col" key={i}>
                {name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(["types", "weights", "weights_normalized"] as const).map((key) => (
            <tr key={key}>
              <th scope="row">
                {t(
                  "decisionSupport." + (key === "weights" ? "rawWeight" : key),
                )}
              </th>
              {criteria.map((_, i) => (
                <td key={i}>{cell(at(snapshot[key], i))}</td>
              ))}
            </tr>
          ))}
          {alternatives.map((name, i) => (
            <tr key={i}>
              <th scope="row">{name}</th>
              {criteria.map((_, j) => (
                <td key={j}>{cell(at(snapshot.performance_matrix, i, j))}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
