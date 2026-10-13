import { useDecisionExecution } from "./useDecisionExecution";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useId, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createDecisionRun,
  listDecisionRuns,
  patchDecisionCase,
  DecisionSupportRequestError,
  isIsmRunResult,
  isIsmRunResponse,
  isIsmSavedCase,
  type DecisionRun,
  type DecisionCase,
} from "@/app/lib/api/decision-support";
import { BinaryRelationEditor } from "./BinaryRelationEditor";
import { IsmLayerList } from "./IsmLayerList";
import { RunActionBar } from "./RunActionBar";
import { ValidationIssueList } from "./ValidationIssueList";
import {
  parseApiRequestIssues,
  type ValidationIssue,
} from "./validation-issues";
import { validateIsmDraft } from "./ism-input-rules";

type Props = {
  projectId: string;
  caseId: string;
  criteria: string[];
  matrix: unknown;
  onMatrixChange: (value: unknown) => void;
  savedCriteria: string[];
  onSavedCase: (value: DecisionCase) => void;
  onHistoryRecovered: (caseId: string) => void;
  disabled: boolean;
  beginOperation: () => null | (() => void);
};
export function IsmMethodPanel({
  projectId,
  caseId,
  criteria,
  matrix,
  onMatrixChange,
  savedCriteria,
  onSavedCase,
  onHistoryRecovered,
  disabled,
  beginOperation,
}: Props) {
  const { t } = useTranslation();
  const prefix = useId();
  const active = useRef(true);
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [run, setRun] = useState<DecisionRun | null>(null);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
    };
  }, []);
  useEffect(() => {
    setRun(null);
    setIssues([]);
  }, [criteria, matrix]);
  const focus = (issue: ValidationIssue) => {
    const match = /^ism_matrix\.(\d+)\.(\d+)$/.exec(issue.path);
    if (match)
      document.getElementById(`${prefix}-${match[1]}-${match[2]}`)?.focus();
  };
  const show = (next: ValidationIssue[]) => {
    setIssues(next);
    requestAnimationFrame(() => {
      if (active.current && next[0]) focus(next[0]);
    });
  };
  const { mutation, recovery, clearRecovery } = useDecisionExecution({
    projectId,
    caseId,
    method: "ism",
    onHistoryRecovered,
    onSaved: onSavedCase,
    onSuccess: (value) => {
      setRun(value);
      setIssues([]);
    },
    onError: (error) => {
      setRun(null);
      show(
        parseApiRequestIssues(
          error instanceof DecisionSupportRequestError ? error.payload : null,
        ),
      );
    },
  });
  const execute = () => {
    setRun(null);
    const local = validateIsmDraft(criteria, matrix);
    if (local.length) {
      show(local);
      return;
    }
    const release = beginOperation();
    if (!release) return;
    const names = criteria.map((name) => name.trim());
    const payload = structuredClone({
      ism_matrix: matrix,
      ...(JSON.stringify(names) !== JSON.stringify(savedCriteria)
        ? { criteria: names }
        : {}),
    });
    clearRecovery();
    mutation.mutate({ payload, release });
  };
  const names =
    run && Array.isArray(run.input_snapshot.criteria)
      ? (run.input_snapshot.criteria as string[])
      : [];
  return (
    <fieldset
      disabled={disabled || mutation.isPending}
      data-ism-panel
      className="min-w-0 space-y-4 rounded border border-border p-4"
    >
      <h2 className="font-medium">{t("decisionSupport.ismPanelTitle")}</h2>
      <p>{t("decisionSupport.ismPanelHint")}</p>
      <BinaryRelationEditor
        criteria={criteria}
        matrix={matrix}
        onChange={onMatrixChange}
        idPrefix={prefix}
        issues={issues}
      />
      <ValidationIssueList
        criterionNames={criteria}
        issues={issues}
        onFocusIssue={focus}
      />
      {recovery && (
        <p role="status" data-ism-recovery={recovery}>
          {t(
            `decisionSupport.${recovery === "checking" ? "ismRecoveryChecking" : recovery === "failed" ? "ismRecoveryFailed" : "ismRecoveryRefreshed"}`,
          )}
        </p>
      )}
      <RunActionBar
        methodLabel="ISM"
        disabled={disabled}
        pending={mutation.isPending}
        onValidate={() => show(validateIsmDraft(criteria, matrix))}
        onRun={execute}
      />
      {run && isIsmRunResult(run.result, names) && (
        <section
          data-ism-result={run.id}
          aria-label={t("decisionSupport.ismCurrent")}
        >
          <h2 className="font-medium">
            {t("decisionSupport.resultTitle", { method: "ISM" })}
          </h2>
          <IsmLayerList
            result={run.result}
            criteria={names}
            direct={run.input_snapshot.ism_matrix}
          />
        </section>
      )}
    </fieldset>
  );
}
