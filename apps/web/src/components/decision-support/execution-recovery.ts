import type { QueryClient } from "@tanstack/react-query";
// @ts-expect-error Native Node recovery tests require an explicit source extension.
import { isHistoryPage } from "./execution-record-rules.ts";
export type Recovery = "checking" | "refreshed" | "failed" | null;
/** One bounded authoritative read; no retry or execution. Timeout includes invalidation. */
export async function recoverExecutionHistory({
  qc,
  projectId,
  caseId,
  read,
  onRecovered,
  setState,
  timeoutMs = 10_000,
}: {
  qc: QueryClient;
  projectId: string;
  caseId: string;
  read: (signal: AbortSignal) => Promise<unknown>;
  onRecovered: () => void;
  setState: (state: Recovery) => void;
  timeoutMs?: number;
}): Promise<void> {
  setState("checking");
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let settled = false;
  const timeout = new Promise<never>((_, reject) => {
    timer = setTimeout(() => {
      settled = true;
      controller.abort();
      reject(new Error("History recovery timed out"));
    }, timeoutMs);
  });
  try {
    const work = async () => {
      await qc.invalidateQueries({
        queryKey: ["decision-runs", projectId, caseId],
        refetchType: "none",
      });
      // fetchQuery deduplicates in-flight work. An earlier GET can predate the
      // commit, so cancel that captured first-page promise before forcing a read.
      await qc.cancelQueries({
        queryKey: ["decision-runs", projectId, caseId, "", 1],
        exact: true,
      });
      if (settled) throw new Error("Expired recovery");
      return qc.fetchQuery({
        queryKey: ["decision-runs", projectId, caseId, "", 1],
        staleTime: 0,
        retry: false,
        queryFn: async () => {
          const value = await read(controller.signal);
          if (settled || !isHistoryPage(value))
            throw new Error("Unconfirmed history");
          return value;
        },
      });
    };
    await Promise.race([work(), timeout]);
    if (!settled) {
      onRecovered();
      setState("refreshed");
    }
  } catch {
    setState("failed");
  } finally {
    settled = true;
    if (timer !== undefined) clearTimeout(timer);
  }
}
