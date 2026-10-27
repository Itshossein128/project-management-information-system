import type { LocalReportSnapshot, OfflineOperation } from "./offlineDB";

export interface StoredFieldError {
  actor_id: string;
  project_id: string;
  unit: string;
  local_report_id: string;
  section: string;
  client_id: string;
  operation_id: string;
  field: string;
  code: string;
  message: string;
}

export function recordFieldError(
  snapshot: LocalReportSnapshot,
  error: StoredFieldError,
): LocalReportSnapshot {
  const next = structuredClone(snapshot);
  const current = next.field_errors[error.client_id] ?? {};
  next.field_errors = {
    ...next.field_errors,
    [error.client_id]: { ...current, [error.field]: error.code },
  };
  return next;
}

export function buildSupersedingRetry(
  failed: OfflineOperation,
  correctedPayload: unknown,
  operationId: string,
  createdAt: string,
): OfflineOperation {
  return {
    ...failed,
    operation_id: operationId,
    payload: structuredClone(correctedPayload),
    supersedes_operation_id: failed.operation_id,
    predecessor_ids: [failed.operation_id],
    status: "pending",
    error_code: null,
    error_message: null,
    created_at: createdAt,
  };
}

/** Only a new pending correction is sent. Synced and the failed original stay put. */
export function operationsForRetry(operations: OfflineOperation[], retry: OfflineOperation): string[] {
  return operations
    .filter((operation) => operation.status === "pending" && operation.operation_id === retry.operation_id)
    .map((operation) => operation.operation_id);
}
