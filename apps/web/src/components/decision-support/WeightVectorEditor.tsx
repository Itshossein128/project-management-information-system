import { useTranslation } from "react-i18next";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { previewNormalizedWeights } from "./ranking-input-rules";

type Props = {
  criteria: string[];
  weights: number[];
  onChange: (weights: number[]) => void;
};

export function WeightVectorEditor({ criteria, weights, onChange }: Props) {
  const { t } = useTranslation();
  const n = criteria.length;
  const preview = previewNormalizedWeights(weights.length === n ? weights : []);

  return (
    <div className="space-y-2">
      <Label>{t("decisionSupport.weights")}</Label>
      <div className="grid gap-2 sm:grid-cols-2">
        {criteria.map((name, j) => (
          <div key={`${name}-${j}`} className="flex items-center gap-2">
            <span className="w-28 truncate text-xs text-muted-foreground">{name}</span>
            <Input
              type="number"
              min={0}
              step="any"
              value={weights[j] ?? ""}
              onChange={(e) => {
                const next = [...weights];
                while (next.length < n) next.push(0);
                next[j] = e.target.value === "" ? 0 : Number(e.target.value);
                onChange(next.slice(0, n));
              }}
              aria-label={`${t("decisionSupport.weights")} ${name}`}
            />
          </div>
        ))}
      </div>
      {preview ? (
        <p className="text-xs text-muted-foreground">
          {t("decisionSupport.weightsNormalizedPreview")}:{" "}
          {preview.map((w) => w.toFixed(3)).join(", ")}
        </p>
      ) : null}
    </div>
  );
}
