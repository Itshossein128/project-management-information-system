import { useTranslation } from "react-i18next";
import type { CriterionType } from "@/app/lib/api/decision-support";
import { Label } from "@/components/form/Label";

type Props = {
  criteria: string[];
  types: CriterionType[];
  onChange: (types: CriterionType[]) => void;
};

export function CriterionTypeToggle({ criteria, types, onChange }: Props) {
  const { t } = useTranslation();

  return (
    <div className="space-y-2">
      <Label>{t("decisionSupport.criterionTypes")}</Label>
      <div className="grid gap-2 sm:grid-cols-2">
        {criteria.map((name, j) => (
          <div key={`${name}-${j}`} className="flex items-center gap-2">
            <span className="w-28 truncate text-xs text-muted-foreground">{name}</span>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-background px-2 text-sm"
              value={types[j] ?? "benefit"}
              onChange={(e) => {
                const next = [...types] as CriterionType[];
                while (next.length < criteria.length) next.push("benefit");
                next[j] = e.target.value === "cost" ? "cost" : "benefit";
                onChange(next.slice(0, criteria.length));
              }}
              aria-label={`${t("decisionSupport.criterionTypes")} ${name}`}
            >
              <option value="benefit">{t("decisionSupport.typeBenefit")}</option>
              <option value="cost">{t("decisionSupport.typeCost")}</option>
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
