import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import {
  patchDecisionCase,
  createDecisionRun,
  listDecisionRuns,
  isSavedCase,
  isCompletedRun,
  DecisionSupportRequestError,
  type DecisionCase,
  type DecisionRun,
  type DecisionMethod,
} from "@/app/lib/api/decision-support";
import { recoverExecutionHistory, type Recovery } from "./execution-recovery";
export function useDecisionExecution({
  projectId,
  caseId,
  method,
  onSaved,
  onSuccess,
  onError,
  onHistoryRecovered,
}: {
  projectId: string;
  caseId: string;
  method: DecisionMethod;
  onSaved?: (value: DecisionCase) => void;
  onSuccess: (value: DecisionRun) => void;
  onError: (error: unknown) => void;
  onHistoryRecovered: (caseId: string) => void;
}) {
  const qc = useQueryClient();
  const active = useRef(true);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
    };
  }, []);
  const key = ["decision-execution-recovery", projectId, caseId];
  const { data: recovery } = useQuery<Recovery>({
    queryKey: key,
    queryFn: () => null,
    initialData: null,
    enabled: false,
  });
  const setRecovery = (state: Recovery) => qc.setQueryData(key, state);
  const mutation = useMutation({
    retry: false,
    mutationFn: async ({
      payload,
      release,
    }: {
      payload: Partial<DecisionCase>;
      release: () => void;
    }) => {
      let postStarted = false;
      try {
        const saved = await patchDecisionCase(projectId, caseId, payload);
        if (!isSavedCase(saved, caseId))
          throw new DecisionSupportRequestError(
            "Invalid saved case response",
            null,
          );
        if (active.current) onSaved?.(saved);
        postStarted = true;
        const run = await createDecisionRun(projectId, caseId, method);
        if (!isCompletedRun(run, method))
          throw new DecisionSupportRequestError(
            "Unconfirmed execution response",
            null,
          );
        return run;
      } catch (error) {
        if (postStarted)
          await recoverExecutionHistory({
            qc,
            projectId,
            caseId,
            read: (signal) =>
              listDecisionRuns(projectId, caseId, {
                page: 1,
                pageSize: 10,
                signal,
              }),
            onRecovered: () => onHistoryRecovered(caseId),
            setState: setRecovery,
          });
        throw error;
      } finally {
        release();
      }
    },
    onSuccess: (run) => {
      void qc.invalidateQueries({
        queryKey: ["decision-runs", projectId, caseId],
      });
      void qc.invalidateQueries({ queryKey: ["decision-cases", projectId] });
      if (active.current) onSuccess(run);
    },
    onError: (error) => {
      if (active.current) onError(error);
    },
  });
  return { mutation, recovery, clearRecovery: () => setRecovery(null) };
}
