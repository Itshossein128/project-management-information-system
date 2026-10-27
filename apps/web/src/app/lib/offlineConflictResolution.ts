import type { LocalReportSnapshot, OfflineOperation } from "./offlineDB";

export function reconcileServerChoice(
  snapshot: Pick<LocalReportSnapshot, "local_report_id" | "overlay_rows">,
  operations: Array<Pick<OfflineOperation, "operation_id" | "local_report_id" | "client_id" | "status">>,
  selectedOperationIds: string[],
) {
  const selected = new Set(selectedOperationIds);
  const removedClients = new Set(
    operations.filter((operation) => selected.has(operation.operation_id)).map((operation) => operation.client_id),
  );
  const overlayRows: Record<string, unknown[]> = {};
  for (const [section, rows] of Object.entries(snapshot.overlay_rows ?? {})) {
    overlayRows[section] = (rows as Array<{ client_id?: string }>).filter((row) => !removedClients.has(row.client_id));
  }
  return {
    snapshot: { ...snapshot, overlay_rows: overlayRows },
    operations: operations.filter((operation) => !selected.has(operation.operation_id)),
  };
}

/** Keep the local source while any selected destination operation lacks a receipt. */
export function retainUntilReceipts(operationIds: string[], acknowledgedIds: string[]): boolean {
  const done = new Set(acknowledgedIds);
  return operationIds.some((operationId) => !done.has(operationId));
}
