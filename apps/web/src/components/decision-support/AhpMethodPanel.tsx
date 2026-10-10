import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  DecisionSupportRequestError,
  createDecisionRun,
  patchDecisionCase,
  type AhpRunResult,
  type DecisionRun,
} from "@/app/lib/api/decision-support";
import { CriteriaWeightTable } from "./CriteriaWeightTable";
import { RunActionBar } from "./RunActionBar";
import { SquareMatrixEditor } from "./SquareMatrixEditor";
import { ValidationIssueList } from "./ValidationIssueList";
import type { RankingIssue } from "./ranking-input-rules";
import { parseApiValidationIssues } from "./validation-issues";

type Props = {
  projectId: string;
  caseId: string;
  criteria: string[];
  matrix: (number | null)[][];
  onMatrixChange: (m: (number | null)[][]) => void;
  latestResult?: AhpRunResult | null;
};

export function AhpMethodPanel({
  projectId,
  caseId,
  criteria,
  matrix,
  onMatrixChange,
  latestResult = null,
}: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [issues, setIssues] = useState<RankingIssue[]>([]);
  const [result, setResult] = useState<AhpRunResult | null>(latestResult);

  // Sync result when parent selects a history run or clears on case change
  useEffect(() => {
    setResult(latestResult);
  }, [latestResult]);

  const collectLocalIssues = (): RankingIssue[] => {
    const n = criteria.length;
    const localIssues: RankingIssue[] = [];

    if (n < 1 || n > 10) {
      localIssues.push({
        code: "dimension_invalid",
        path: "criteria",
        message: t("decisionSupport.errors.dimension_invalid"),
      });
      return localIssues;
    }

    if (!matrix || matrix.length !== n) {
      localIssues.push({
        code: "dimension_invalid",
        path: "ahp_matrix",
        message: t("decisionSupport.errors.dimension_invalid"),
      });
      return localIssues;
    }

    for (let i = 0; i < n; i++) {
      const row = matrix[i];
      if (!row || row.length !== n) {
        localIssues.push({
          code: "dimension_invalid",
          path: `ahp_matrix.${i}`,
          message: t("decisionSupport.errors.length_mismatch"),
        });
        continue;
      }
      for (let j = 0; j < n; j++) {
        const val = row[j];
        const path = `ahp_matrix.${i}.${j}`;
        if (val === null || val === undefined) {
          localIssues.push({
            code: "cell_empty",
            path,
            message: t("decisionSupport.errors.cell_empty"),
          });
          continue;
        }
        if (typeof val !== "number" || isNaN(val)) {
          localIssues.push({
            code: "non_numeric",
            path,
            message: t("decisionSupport.errors.non_numeric"),
          });
          continue;
        }
        if (val <= 0) {
          localIssues.push({
            code: "cell_non_positive",
            path,
            message: t("decisionSupport.errors.cell_non_positive"),
          });
          continue;
        }
      }
    }

    if (localIssues.length === 0) {
      for (let i = 0; i < n; i++) {
        if (Math.abs((matrix[i]?.[i] ?? 0) - 1.0) > 1e-4) {
          localIssues.push({
            code: "ahp_diagonal_invalid",
            path: `ahp_matrix.${i}.${i}`,
            message: t("decisionSupport.errors.ahp_diagonal_invalid"),
          });
        }
        for (let j = i + 1; j < n; j++) {
          const val_ij = matrix[i]?.[j] ?? 0;
          const val_ji = matrix[j]?.[i] ?? 0;
          if (Math.abs(val_ij * val_ji - 1.0) >= 1e-4) {
            localIssues.push({
              code: "ahp_reciprocal_mismatch",
              path: `ahp_matrix.${j}.${i}`,
              message: t("decisionSupport.errors.ahp_reciprocal_mismatch"),
            });
          }
        }
      }
    }

    return localIssues;
  };

  const runMutation = useMutation({
    mutationFn: async () => {
      await patchDecisionCase(projectId, caseId, {
        ahp_matrix: matrix,
        criteria,
      });
      return createDecisionRun(projectId, caseId, "ahp");
    },
    onSuccess: (run: DecisionRun) => {
      setIssues([]);
      const res = run.result as unknown as AhpRunResult;
      setResult(res);
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
      <h2 className="text-sm font-medium">{t("decisionSupport.ahpPanelTitle")}</h2>
      <p className="text-xs text-muted-foreground">{t("decisionSupport.ahpPanelHint")}</p>

      <SquareMatrixEditor
        criteria={criteria}
        matrix={matrix}
        onChange={onMatrixChange}
        mode="pairwise"
      />

      <ValidationIssueList issues={issues} />

      <RunActionBar
        methodLabel="AHP"
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

      {result && (
        <CriteriaWeightTable
          weights={result.weights ?? []}
          cr={result.cr}
          ci={result.ci}
          lambdaMax={result.lambda_max}
          isConsistent={result.is_consistent}
        />
      )}
    </div>
  );
}
