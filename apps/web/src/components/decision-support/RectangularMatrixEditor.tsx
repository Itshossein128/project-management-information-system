import { useTranslation } from "react-i18next";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";

type Props = {
  criteria: string[];
  alternatives: string[];
  matrix: (number | null)[][];
  onChange: (matrix: (number | null)[][]) => void;
};

function ensureShape(
  matrix: (number | null)[][],
  m: number,
  n: number,
): (number | null)[][] {
  const next: (number | null)[][] = [];
  for (let i = 0; i < m; i++) {
    const row = [...(matrix[i] ?? [])];
    while (row.length < n) row.push(null);
    next.push(row.slice(0, n));
  }
  return next;
}

export function RectangularMatrixEditor({
  criteria,
  alternatives,
  matrix,
  onChange,
}: Props) {
  const { t } = useTranslation();
  const m = alternatives.length;
  const n = criteria.length;
  const shaped = ensureShape(matrix, m, n);

  if (m === 0 || n === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("decisionSupport.matrixNeedsNames")}</p>
    );
  }

  return (
    <div className="space-y-2 overflow-x-auto">
      <Label>{t("decisionSupport.performanceMatrix")}</Label>
      <table className="w-full min-w-[320px] border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-border px-2 py-1 text-start font-medium" />
            {criteria.map((c, j) => (
              <th key={`c-${j}`} className="border border-border px-2 py-1 text-start font-medium">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {alternatives.map((alt, i) => (
            <tr key={`a-${i}`}>
              <th className="border border-border px-2 py-1 text-start font-medium">{alt}</th>
              {criteria.map((_, j) => (
                <td key={`c-${i}-${j}`} className="border border-border p-1">
                  <Input
                    type="number"
                    min={0}
                    step="any"
                    className="h-8"
                    value={shaped[i]?.[j] ?? ""}
                    onChange={(e) => {
                      const next = ensureShape(shaped, m, n);
                      next[i]![j] =
                        e.target.value === "" ? null : Number(e.target.value);
                      onChange(next);
                    }}
                    aria-label={`${alt} × ${criteria[j]}`}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.matrixEmptyHint")}</p>
    </div>
  );
}
