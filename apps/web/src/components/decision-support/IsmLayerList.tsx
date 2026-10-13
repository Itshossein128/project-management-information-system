import { useTranslation } from "react-i18next";
import type { IsmRunResult } from "./ism-result-rules";

export function IsmMatrixTable({
  criteria,
  matrix,
  label,
}: {
  criteria: string[];
  matrix: unknown;
  label: string;
}) {
  const { t } = useTranslation();
  return (
    <div className="overflow-x-auto">
      <table aria-label={label} className="w-full border-collapse">
        <caption className="text-start font-medium">{label}</caption>
        <thead>
          <tr>
            <th />
            {criteria.map((name, i) => (
              <th scope="col" key={i} className="border border-border p-2">
                {name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {criteria.map((name, i) => (
            <tr key={i}>
              <th scope="row" className="border border-border p-2 text-start">
                {name}
              </th>
              {criteria.map((_, j) => {
                const row = Array.isArray(matrix) ? matrix[i] : undefined;
                const value = Array.isArray(row) ? row[j] : undefined;
                return (
                  <td key={j} className="border border-border p-2">
                    {value === null || value === undefined
                      ? t("decisionSupport.ismUnanswered")
                      : String(value)}
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
export function IsmLayerList({
  result,
  criteria,
  direct,
}: {
  result: IsmRunResult;
  criteria: string[];
  direct: unknown;
}) {
  const { t, i18n } = useTranslation();
  return (
    <div className="space-y-4">
      <ol className="space-y-2">
        {result.layers.map((layer) => (
          <li
            key={layer.level}
            data-ism-level={layer.level}
            className="rounded border border-border p-2"
          >
            <h3 className="font-medium">
              {t("decisionSupport.ismLayer", {
                level: layer.level.toLocaleString(i18n.language),
              })}
            </h3>
            <p>{layer.criteria.join(", ")}</p>
          </li>
        ))}
      </ol>
      <p>{t("decisionSupport.ismInterpretation")}</p>
      <p>{t("decisionSupport.ismNoRemoval")}</p>
      <div className="space-y-2">
        <h3 className="font-medium">{t("decisionSupport.ismGroups")}</h3>
        {result.mutual_groups.length ? (
          <ul>
            {result.mutual_groups.map((group, i) => (
              <li
                key={i}
                data-ism-group
                className="rounded border border-border p-2"
              >
                {t("decisionSupport.ismGroup", {
                  level: group.level.toLocaleString(i18n.language),
                })}
                : {group.criteria.join(", ")}
              </li>
            ))}
          </ul>
        ) : (
          <p>{t("decisionSupport.ismNoGroups")}</p>
        )}
      </div>
      <IsmMatrixTable
        criteria={criteria}
        matrix={direct}
        label={t("decisionSupport.ismDirect")}
      />
      <IsmMatrixTable
        criteria={criteria}
        matrix={result.reachability_matrix}
        label={t("decisionSupport.ismReachability")}
      />
    </div>
  );
}
