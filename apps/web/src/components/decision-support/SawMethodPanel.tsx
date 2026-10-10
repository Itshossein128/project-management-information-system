import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  DecisionSupportRequestError,
  createDecisionRun,
  patchDecisionCase,
  type CriterionType,
  type DecisionRun,
  type SawRankingRow,
} from "@/app/lib/api/decision-support";
import { CriterionTypeToggle } from "./CriterionTypeToggle";
import { RankingResultTable } from "./RankingResultTable";
import { RectangularMatrixEditor } from "./RectangularMatrixEditor";
import { RunActionBar } from "./RunActionBar";
import { ValidationIssueList } from "./ValidationIssueList";
import {
  validateCriterionTypes,
  validateRectangularMatrix,
  validateWeightVector,
  type RankingIssue,
} from "./ranking-input-rules";
import { parseApiValidationIssues } from "./validation-issues";
import { WeightVectorEditor } from "./WeightVectorEditor";

type Props = {
  projectId: string;
  caseId: string;
  criteria: string[];
  alternatives: string[];
  weights: number[];
  types: CriterionType[];
  matrix: (number | null)[][];
  onWeightsChange: (w: number[]) => void;
  onTypesChange: (t: CriterionType[]) => void;
  onMatrixChange: (m: (number | null)[][]) => void;
  latestRanking?: SawRankingRow[];
};

export function SawMethodPanel({
  projectId,
  caseId,
  criteria,
  alternatives,
  weights,
  types,
  matrix,
  onWeightsChange,
  onTypesChange,
  onMatrixChange,
  latestRanking = [],
}: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [issues, setIssues] = useState<RankingIssue[]>([]);
  const [ranking, setRanking] = useState<SawRankingRow[]>(latestRanking);

  // Sync table when parent selects a history run (or clears ranking on case change)
  useEffect(() => {
    setRanking(latestRanking);
  }, [latestRanking]);

  const collectLocalIssues = (): RankingIssue[] => {
    const n = criteria.length;
    const m = alternatives.length;
    return [
      ...validateWeightVector(weights, n),
      ...validateCriterionTypes(types, n),
      ...validateRectangularMatrix(matrix, m, n, types),
    ];
  };

  const runMutation = useMutation({
    mutationFn: async () => {
      await patchDecisionCase(projectId, caseId, {
        weights,
        types,
        performance_matrix: matrix,
        criteria,
        alternatives,
      });
      return createDecisionRun(projectId, caseId, "saw");
    },
    onSuccess: (run: DecisionRun) => {
      setIssues([]);
      const rows = run.result?.ranking ?? [];
      setRanking(rows);
      void qc.invalidateQueries({ queryKey: ["decision-runs", projectId, caseId] });
    },
    onError: (err: unknown) => {
      if (err instanceof DecisionSupportRequestError) {
        setIssues(parseApiValidationIssues(err.payload));
      } else {
        setIssues([{ code: "error", path: "", message: String(err) }]);
      }
    },
  });

  return (
    <div className="space-y-4 rounded-md border border-border p-4">
      <h2 className="text-sm font-medium">{t("decisionSupport.sawPanelTitle")}</h2>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.sawPanelHint")}</p>

      <WeightVectorEditor criteria={criteria} weights={weights} onChange={onWeightsChange} />
      <CriterionTypeToggle criteria={criteria} types={types} onChange={onTypesChange} />
      <RectangularMatrixEditor
        criteria={criteria}
        alternatives={alternatives}
        matrix={matrix}
        onChange={onMatrixChange}
      />

      <ValidationIssueList issues={issues} />

      <RunActionBar
        methodLabel="SAW"
        pending={runMutation.isPending}
        onValidate={() => setIssues(collectLocalIssues())}
        onRun={() => {
          const local = collectLocalIssues();
          if (local.length) {
            setIssues(local);
            return;
          }
          runMutation.mutate();
        }}
      />

      <RankingResultTable method="saw" ranking={ranking} />
    </div>
  );
}
