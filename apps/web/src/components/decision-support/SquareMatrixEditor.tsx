import { useTranslation } from "react-i18next";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { createDefaultPairwiseMatrix, updatePairwiseCell } from "./square-matrix-rules";

type Props = {
  criteria: string[];
  matrix: (number | null)[][];
  onChange: (matrix: (number | null)[][]) => void;
  mode?: "pairwise" | "general";
};

function ensureSquareShape(
  matrix: (number | null)[][],
  n: number,
  mode: "pairwise" | "general",
): (number | null)[][] {
  if (n <= 0) return [];
  if (!matrix || matrix.length !== n || matrix.some((r) => !r || r.length !== n)) {
    return mode === "pairwise" ? createDefaultPairwiseMatrix(n) : [];
  }
  const next: (number | null)[][] = [];
  for (let i = 0; i < n; i++) {
    const row = [...(matrix[i] ?? [])];
    while (row.length < n) row.push(i === row.length && mode === "pairwise" ? 1.0 : null);
    if (mode === "pairwise") {
      row[i] = 1.0;
    }
    next.push(row.slice(0, n));
  }
  return next;
}

export function SquareMatrixEditor({
  criteria,
  matrix,
  onChange,
  mode = "pairwise",
}: Props) {
  const { t } = useTranslation();
  const n = criteria.length;
  const shaped = ensureSquareShape(matrix, n, mode);

  if (n === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("decisionSupport.matrixNeedsNames")}</p>
    );
  }

  return (
    <div className="space-y-2 overflow-x-auto">
      <div className="flex flex-col gap-1">
        <Label>{t("decisionSupport.pairwiseMatrix")}</Label>
        <p className="text-xs text-muted-foreground">
          {t("decisionSupport.pairwiseMatrixHint")}
        </p>
      </div>
      <table className="w-full min-w-[320px] border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-border px-2 py-1 text-start font-medium" />
            {criteria.map((c, j) => (
              <th key={`head-${j}`} className="border border-border px-2 py-1 text-start font-medium">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {criteria.map((rowCrit, i) => (
            <tr key={`row-${i}`}>
              <th className="border border-border px-2 py-1 text-start font-medium">{rowCrit}</th>
              {criteria.map((colCrit, j) => {
                const isDiagonal = i === j;
                const cellVal = shaped[i]?.[j];
                const displayVal = cellVal !== null && cellVal !== undefined
                  ? Number(cellVal.toFixed(4))
                  : "";

                return (
                  <td key={`cell-${i}-${j}`} className="border border-border p-1">
                    <Input
                      type="number"
                      step="any"
                      min={0.0001}
                      disabled={isDiagonal && mode === "pairwise"}
                      className={`h-8 ${isDiagonal ? "bg-muted font-semibold text-muted-foreground cursor-not-allowed" : ""}`}
                      value={isDiagonal ? 1 : displayVal}
                      onChange={(e) => {
                        const parsed = e.target.value === "" ? null : Number(e.target.value);
                        if (mode === "pairwise") {
                          const updated = updatePairwiseCell(shaped, i, j, parsed);
                          onChange(updated);
                        } else {
                          const next = shaped.map((r) => [...r]);
                          next[i]![j] = parsed;
                          onChange(next);
                        }
                      }}
                      aria-label={`${rowCrit} × ${colCrit}`}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.matrixEmptyHint")}</p>
    </div>
  );
}
