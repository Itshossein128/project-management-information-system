import { useDecisionExecution } from "./useDecisionExecution";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, useId, useRef } from "react";
import { useTranslation } from "react-i18next";
import {
  DecisionSupportRequestError,
  isAhpRunResult,
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
import { parseApiRequestIssues } from "./validation-issues";

type Props = {
  disabled?: boolean;
  beginOperation: () => (() => void) | null;
  onHistoryRecovered: (caseId: string) => void;
  projectId: string;
  caseId: string;
  criteria: string[];
  matrix: (number | null)[][];
  onMatrixChange: (m: (number | null)[][]) => void;
  latestResult?: AhpRunResult | null;
  savedCriteria: string[];
  onSavedCriteria: (criteria: string[]) => void;
  onResult: (result: AhpRunResult) => void;
};

export function AhpMethodPanel({
  disabled = false,
  beginOperation,
  onHistoryRecovered,
  projectId,
  caseId,
  criteria,
  matrix,
  onMatrixChange,
  latestResult = null,
  savedCriteria,
  onSavedCriteria,
  onResult,
}: Props) {
  const { t } = useTranslation();
  const cellPrefix = useId();
  const active = useRef(true);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
    };
  }, []);
  const focusIssue = (issue: RankingIssue) => {
    const match = /^ahp_matrix\.(\d+)\.(\d+)$/.exec(issue.path);
    if (match)
      document
        .getElementById(cellPrefix + "-" + match[1] + "-" + match[2])
        ?.focus();
  };
  const showIssues = (next: RankingIssue[]) => {
    setIssues(next);
    requestAnimationFrame(() => {
      if (next[0]) focusIssue(next[0]);
    });
  };
  const [issues, setIssues] = useState<RankingIssue[]>([]);
  const [result, setResult] = useState<AhpRunResult | null>(latestResult);

  // Sync the current execution result; historical inspection is separate.
  useEffect(() => {
    setResult(latestResult);
  }, [latestResult]);

  useEffect(() => {
    setResult(null);
  }, [criteria, matrix]);

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

    const seen = new Set<string>();
    criteria.forEach((name, index) => {
      const text = typeof name === "string" ? name.trim() : "";
      const code =
        typeof name !== "string"
          ? "invalid_type"
          : !text
            ? "name_empty"
            : seen.has(text)
              ? "name_duplicate"
              : null;
      if (code)
        localIssues.push({
          code,
          path: "criteria." + index,
          message: t("decisionSupport.errors." + code),
        });
      seen.add(text);
    });
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
        if (typeof val !== "number") {
          localIssues.push({
            code: "non_numeric",
            path,
            message: t("decisionSupport.errors.non_numeric"),
          });
          continue;
        }
        if (!Number.isFinite(val)) {
          localIssues.push({
            code: "non_finite",
            path,
            message: t("decisionSupport.errors.non_finite"),
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
        if (matrix[i]?.[i] !== 1) {
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

  const {
    mutation: runMutation,
    recovery,
    clearRecovery,
  } = useDecisionExecution({
    projectId,
    caseId,
    method: "ahp",
    onHistoryRecovered,
    onSaved: (saved) => onSavedCriteria(saved.criteria),
    onSuccess: (run) => {
      setIssues([]);
      if (isAhpRunResult(run.result)) {
        setResult(run.result);
        onResult(run.result);
      }
    },
    onError: (err) => {
      setResult(null);
      showIssues(
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
        {t("decisionSupport.ahpPanelTitle")}
      </h2>
      <p className="text-xs text-muted-foreground">
        {t("decisionSupport.ahpPanelHint")}
      </p>

      <SquareMatrixEditor
        criteria={criteria}
        matrix={matrix}
        onChange={onMatrixChange}
        mode="pairwise"
        idPrefix={cellPrefix}
        issues={issues}
      />

      <ValidationIssueList
        criterionNames={criteria}
        issues={issues}
        onFocusIssue={focusIssue}
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
        methodLabel="AHP"
        pending={runMutation.isPending}
        onValidate={() => showIssues(collectLocalIssues())}
        onRun={() => {
          setResult(null);
          const local = collectLocalIssues();
          if (local.length) {
            showIssues(local);
            return;
          }
          const release = beginOperation();
          if (!release) return;
          const payload = structuredClone({
            ahp_matrix: matrix,
            ...(JSON.stringify(criteria.map((name) => name.trim())) !==
            JSON.stringify(savedCriteria)
              ? { criteria: criteria.map((name) => name.trim()) }
              : {}),
          });
          clearRecovery();
          runMutation.mutate({ payload, release });
        }}
      />

      {result && (
        <section aria-label={t("decisionSupport.currentAhpResult")}>
          <CriteriaWeightTable
            weights={result.weights ?? []}
            cr={result.cr}
            ci={result.ci}
            lambdaMax={result.lambda_max}
            isConsistent={result.is_consistent}
          />
        </section>
      )}
    </fieldset>
  );
}
