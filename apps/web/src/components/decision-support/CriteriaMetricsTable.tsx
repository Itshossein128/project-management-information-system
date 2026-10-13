import { useTranslation } from "react-i18next";
import type { DematelResult } from "./execution-record-rules";
export function CriteriaMetricsTable({ result }: { result: DematelResult }) {
  const { t } = useTranslation();
  return (
    <div className="overflow-x-auto" tabIndex={0}>
      <table
        aria-label={t("decisionSupport.dematelIndicators")}
        className="w-full text-sm"
      >
        <thead>
          <tr>
            {["criterion", "d", "r", "prominence", "relation", "role"].map(
              (k) => (
                <th scope="col" key={k}>
                  {t("decisionSupport.dematel." + k)}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {result.criteria_results.map((row) => (
            <tr key={row.criterion}>
              <th scope="row">{row.criterion}</th>
              <td>{row.d}</td>
              <td>{row.r}</td>
              <td>{row.prominence}</td>
              <td>{row.relation}</td>
              <td>{t("decisionSupport.dematel." + row.role)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
