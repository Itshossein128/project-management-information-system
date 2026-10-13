import { useTranslation } from "react-i18next";
import { Button } from "@/components/form/Button";
import {
  createIsmMatrix,
  editIsmCell,
  selectIsmValue,
} from "./ism-input-rules";
import type { ValidationIssue } from "./validation-issues";

type Props = {
  criteria: string[];
  matrix: unknown;
  onChange: (value: unknown) => void;
  idPrefix: string;
  issues?: ValidationIssue[];
};
export function BinaryRelationEditor({
  criteria,
  matrix,
  onChange,
  idPrefix,
  issues = [],
}: Props) {
  const { t } = useTranslation();
  const shape =
    Array.isArray(matrix) &&
    matrix.length === criteria.length &&
    matrix.every((row) => Array.isArray(row) && row.length === criteria.length);
  return (
    <div className="space-y-2">
      <p>{t("decisionSupport.ismDirection")}</p>
      {!shape && (
        <div role="alert">
          <p>{t("decisionSupport.ismInvalidDraft")}</p>
          <pre>{JSON.stringify(matrix)}</pre>
          <Button
            type="button"
            onClick={() => onChange(createIsmMatrix(criteria.length))}
          >
            {t("decisionSupport.ismReset")}
          </Button>
        </div>
      )}
      <div className="overflow-x-auto">
        <table
          aria-label={t("decisionSupport.ismDirect")}
          className="w-full border-collapse"
        >
          <thead>
            <tr>
              <th scope="col">{t("decisionSupport.ismAxes")}</th>
              {criteria.map((name, j) => (
                <th scope="col" className="border border-border p-2" key={j}>
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {criteria.map((from, i) => (
              <tr key={i}>
                <th scope="row" className="border border-border p-2 text-start">
                  {from}
                </th>
                {criteria.map((to, j) => {
                  const row = Array.isArray(matrix) ? matrix[i] : undefined;
                  const value = Array.isArray(row) ? row[j] : undefined;
                  const invalid =
                    value !== null &&
                    value !== undefined &&
                    value !== 0 &&
                    value !== 1;
                  const hasIssue = issues.some(
                    (issue) => issue.path === `ism_matrix.${i}.${j}`,
                  );
                  return (
                    <td className="border border-border p-2" key={j}>
                      <select
                        id={`${idPrefix}-${i}-${j}`}
                        data-ism-cell={`${i}-${j}`}
                        aria-label={t("decisionSupport.ismCell", { from, to })}
                        aria-invalid={invalid || hasIssue}
                        disabled={!shape}
                        className="min-w-28 rounded border border-border bg-background p-2 focus-visible:outline-2 focus-visible:outline-primary"
                        value={
                          invalid
                            ? "invalid"
                            : value === null || value === undefined
                              ? ""
                              : String(value)
                        }
                        onChange={(event) =>
                          onChange(
                            editIsmCell(
                              matrix,
                              i,
                              j,
                              selectIsmValue(event.target.value),
                            ),
                          )
                        }
                      >
                        {invalid && (
                          <option value="invalid" disabled>
                            {t("decisionSupport.ismInvalidValue")}:{" "}
                            {JSON.stringify(value)}
                          </option>
                        )}
                        <option value="">
                          {t("decisionSupport.ismUnanswered")}
                        </option>
                        <option value="0">{t("decisionSupport.ismNo")}</option>
                        <option value="1">{t("decisionSupport.ismYes")}</option>
                      </select>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
