import { useDecisionExecution } from "./useDecisionExecution";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import {
  DecisionSupportRequestError,
  createDecisionRun,
  patchDecisionCase,
  type CriterionType,
  type DecisionRun,
  type TopsisRankingRow,
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
import { parseApiRequestIssues } from "./validation-issues";
import { WeightVectorEditor } from "./WeightVectorEditor";

type Props = {
  disabled?: boolean;
  beginOperation: () => (() => void) | null;
  onHistoryRecovered: (caseId: string) => void;
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
  latestRanking?: TopsisRankingRow[];
};

export function TopsisMethodPanel({
  disabled = false,
  beginOperation,
  onHistoryRecovered,
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
  const active = useRef(true);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
    };
  }, []);
  const [issues, setIssues] = useState<RankingIssue[]>([]);
  const [ranking, setRanking] = useState<TopsisRankingRow[]>(latestRanking);

  // Sync table when parent selects a history run (or clears ranking on case change)
  useEffect(() => {
    setRanking(latestRanking);
  }, [latestRanking]);

  useEffect(() => {
    setRanking([]);
  }, [JSON.stringify([criteria, alternatives, weights, types, matrix])]);

  const collectLocalIssues = (): RankingIssue[] => {
    const n = criteria.length;
    const m = alternatives.length;
    return [
      ...validateWeightVector(weights, n),
      ...validateCriterionTypes(types, n),
      ...validateRectangularMatrix(matrix, m, n, types),
    ];
  };

  const {
    mutation: runMutation,
    recovery,
    clearRecovery,
  } = useDecisionExecution({
    projectId,
    caseId,
    method: "topsis",
    onHistoryRecovered,
    onSuccess: (run) => {
      setIssues([]);
      setRanking(run.result.ranking as TopsisRankingRow[]);
    },
    onError: (err) => {
      setRanking([]);
      setIssues(
        parseApiRequestIssues(
          err instanceof DecisionSupportRequestError ? err.payload : null,
        ),
      );
    },
  });

  return (
    <fieldset
      disabled={disabled || runMutation.isPending}
      className="min-w-0 space-y-4 rounded-md border border-border p-4"
    >
      <h2 className="text-sm font-medium">
        {t("decisionSupport.topsisPanelTitle")}
      </h2>
      <p className="text-xs text-muted-foreground">
        {t("decisionSupport.topsisPanelHint")}
      </p>

      <WeightVectorEditor
        criteria={criteria}
        weights={weights}
        onChange={onWeightsChange}
      />
      <CriterionTypeToggle
        criteria={criteria}
        types={types}
        onChange={onTypesChange}
      />
      <RectangularMatrixEditor
        criteria={criteria}
        alternatives={alternatives}
        matrix={matrix}
        onChange={onMatrixChange}
      />

      <ValidationIssueList
        criterionNames={criteria}
        alternativeNames={alternatives}
        issues={issues}
      />

      {recovery && (
        <p role="status" data-execution-recovery={recovery}>
          {t(
            `decisionSupport.${recovery === "checking" ? "executionRecoveryChecking" : recovery === "failed" ? "executionRecoveryFailed" : "executionRecoveryRefreshed"}`,
          )}
        </p>
      )}
      <RunActionBar
        disabled={disabled}
        methodLabel="TOPSIS"
        pending={runMutation.isPending}
        onValidate={() => setIssues(collectLocalIssues())}
        onRun={() => {
          setRanking([]);
          const local = collectLocalIssues();
          if (local.length) {
            setIssues(local);
            return;
          }
          const release = beginOperation();
          if (!release) return;
          const payload = structuredClone({
            weights,
            types,
            performance_matrix: matrix,
            criteria,
            alternatives,
          });
          clearRecovery();
          runMutation.mutate({ payload, release });
        }}
      />

      <RankingResultTable
        method="topsis"
        ranking={ranking}
        extraColumns={[
          { key: "d_best", header: t("decisionSupport.colDBest") },
          { key: "d_worst", header: t("decisionSupport.colDWorst") },
          { key: "closeness", header: t("decisionSupport.colCloseness") },
        ]}
      />
    </fieldset>
  );
}
