import { useId } from "react";
import { useTranslation } from "react-i18next";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { localizeIssueMessage, type ValidationIssue } from "./validation-issues";
import { updatePairwiseCell } from "./square-matrix-rules";

type Props = {
  criteria: string[];
  matrix: (number | null)[][];
  onChange: (matrix: (number | null)[][]) => void;
  mode?: "pairwise" | "general";
  idPrefix?: string;
  issues?: ValidationIssue[];
};
const presets = [1, 2, 3, 4, 5, 6, 7, 8, 9, ...[2, 3, 4, 5, 6, 7, 8, 9].map(n => 1 / n)];

export function SquareMatrixEditor({ criteria, matrix, onChange, mode = "pairwise", idPrefix, issues = [] }: Props) {
  const { t } = useTranslation();
  const generatedId = useId();
  const id = idPrefix ?? generatedId;
  if (!criteria.length) return <p className="text-sm text-muted-foreground">{t("decisionSupport.matrixNeedsNames")}</p>;
  // Display the owned draft exactly, including malformed saved values.
  const change = (i: number, j: number, value: number | null) => {
    const next = criteria.map((_, row) => criteria.map((__, col) => matrix[row]?.[col] ?? null));
    if (mode === "pairwise") onChange(updatePairwiseCell(next, i, j, value));
    else { next[i]![j] = value; onChange(next); }
  };
  return (
    <div className="w-full max-w-full space-y-2 overflow-x-auto">
      <Label>{t("decisionSupport.pairwiseMatrix")}</Label>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.pairwiseMatrixHint")}</p>
      <table className="w-full border-collapse text-sm" style={{ minWidth: Math.max(320, criteria.length * 140) }}>
        <thead><tr>
          <th className="border border-border" />
          {criteria.map((name, j) => <th scope="col" key={j} className="border border-border px-2 py-1 text-start">{name}</th>)}
        </tr></thead>
        <tbody>{criteria.map((name, i) => <tr key={i}>
          <th scope="row" className="border border-border px-2 py-1 text-start">{name}</th>
          {criteria.map((other, j) => {
            const diagonal = i === j && mode === "pairwise";
            const value = matrix[i]?.[j];
            const pair = name + " × " + other;
            const cellIssue = issues.find(issue => issue.path === "ahp_matrix." + i + "." + j);
            const errorId = id + "-error-" + i + "-" + j;
            const advisory = typeof value === "number" && Number.isFinite(value) && value > 0 && (value < 1/9 || value > 9);
            return <td key={j} className="border border-border p-1">
              <Input id={id + "-" + i + "-" + j} type="number" step="any" readOnly={diagonal}
                className={diagonal ? "h-8 bg-muted font-semibold" : "h-8"} value={value ?? ""} aria-label={pair} aria-invalid={!!cellIssue} aria-describedby={cellIssue ? errorId : undefined}
                onChange={event => change(i, j, event.target.value === "" ? null : Number(event.target.value))} />
              {!diagonal && mode === "pairwise" && <select className="mt-1 w-full rounded border border-border bg-background text-xs"
                aria-label={t("decisionSupport.pairwisePreset") + " " + pair} value=""
                onChange={event => { if (event.target.value) change(i, j, Number(event.target.value)); }}>
                <option value="">{t("decisionSupport.pairwisePreset")}</option>
                {presets.map((preset, k) => <option key={k} value={preset}>{k < 9 ? String(preset) : "1/" + (k - 7)}</option>)}
              </select>}
              {cellIssue && <p id={errorId} className="text-xs text-destructive">{localizeIssueMessage(cellIssue, t)}</p>}
              {advisory && <p className="text-xs text-amber-700">{t("decisionSupport.scaleAdvisory")}</p>}
            </td>;
          })}
        </tr>)}</tbody>
      </table>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.matrixEmptyHint")}</p>
    </div>
  );
}
