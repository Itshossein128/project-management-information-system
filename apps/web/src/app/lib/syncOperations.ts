import type { SyncV2Operation, SyncV2Request, SyncV2Response } from "@/app/lib/api/unit-reports";
import type { OfflineOperation } from "@/app/lib/offlineDB";

export const SYNC_OPERATIONS_V2_PATH = "/v1/projects/{project_id}/daily-reports/sync-operations/v2/";

const TARGET_KIND: Record<string, string> = {
  header: "header",
  activities: "activity",
  activity: "activity",
  labor: "labor",
  materials: "material",
  material: "material",
  machinery: "machinery",
  "general-activities": "general_activity",
  issues: "issue",
  visits: "visit",
  "hse-incidents": "hse",
};

export function operationToV2(operation: OfflineOperation, reportDate: string): SyncV2Operation {
  const kind = TARGET_KIND[operation.target_type] ?? operation.target_type;
  const action = operation.operation_kind === "header_update" ? "update" : operation.operation_kind;
  return {
    operation_id: operation.operation_id,
    local_report_id: operation.local_report_id,
    scope: {
      kind: "unit",
      unit: operation.unit,
      report_date: reportDate,
      report_id: null,
    },
    action,
    target: {
      kind,
      client_id: operation.client_id ?? null,
      server_id: operation.target_server_id ?? null,
    },
    base_revision: operation.base_target_revision ?? null,
    depends_on: operation.predecessor_ids,
    supersedes_operation_id: operation.supersedes_operation_id ?? null,
    payload: (operation.payload ?? {}) as Record<string, unknown>,
  };
}

export function buildSyncRequest(operations: SyncV2Operation[]): SyncV2Request {
  return { contract_version: 2, operations };
}

export interface AckDecision {
  acknowledged: string[];
  retained: string[];
  mappings: Array<{ operationId: string; clientId: string | null; serverId: string | null }>;
}

function isSuccessItem(value: unknown): value is SyncV2Response["results"][number] {
  if (!value || typeof value !== "object") return false;
  const item = value as { operation_id?: unknown; outcome?: unknown };
  return typeof item.operation_id === "string" && item.outcome === "success";
}

/**
 * Acknowledge an operation only when its own result is a unique success and
 * `synced_ids` lists that same operation id. Order is irrelevant.
 */
export function reconcileOperationAcks(
  requestedIds: string[],
  response: SyncV2Response | null | undefined,
): AckDecision {
  const acknowledged: string[] = [];
  const retained: string[] = [];
  const mappings: AckDecision["mappings"] = [];
  const results = Array.isArray(response?.results) ? response.results : [];
  const synced = new Set(Array.isArray(response?.synced_ids) ? response.synced_ids : []);
  const requested = new Set(requestedIds);

  const grouped = new Map<string, SyncV2Response["results"]>();
  for (const item of results) {
    if (!item || typeof item.operation_id !== "string" || !requested.has(item.operation_id)) {
      continue;
    }
    const list = grouped.get(item.operation_id) ?? [];
    list.push(item);
    grouped.set(item.operation_id, list);
  }

  for (const operationId of requestedIds) {
    const matches = grouped.get(operationId) ?? [];
    const item = matches.length === 1 ? matches[0] : undefined;
    const consistent = isSuccessItem(item) && synced.has(operationId);
    if (!consistent) {
      retained.push(operationId);
      continue;
    }
    acknowledged.push(operationId);
    mappings.push({
      operationId,
      clientId: item.target?.client_id ?? null,
      serverId: item.target?.server_id ?? null,
    });
  }
  return { acknowledged, retained, mappings };
}
