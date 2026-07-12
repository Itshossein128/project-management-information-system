/**
 * Helpers that translate daily-report writes into IndexedDB offline-queue
 * entries when the network is unavailable (Sprint 4, Section 4).
 */
import { PATHS } from "@/app/routeVars";
import {
  addToQueue,
  type EntityType,
  generateUUID,
  getQueueByProject,
  getUnresolvedConflicts,
  isOfflineDBAvailable,
  type OfflineReport,
  type QueueMethod,
  saveOfflineReport,
} from "@/app/lib/offlineDB";
import type { ChildResource, HeaderPayload } from "@/app/lib/api/daily-reports";

export type RowSyncStatus = "synced" | "pending" | "failed" | "conflict";

const reportBase = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/daily-reports`;

const CHILD_ENTITY: Record<ChildResource, EntityType> = {
  activities: "daily_activity",
  labor: "daily_labor",
  equipment: "daily_equipment",
  materials: "daily_material",
  "concrete-logs": "daily_activity",
  "labor-camp": "daily_labor",
  incidents: "daily_activity",
};

export function isNetworkError(): boolean {
  return typeof navigator !== "undefined" && !navigator.onLine;
}

/** Queue a report header write and mirror it into offline_daily_reports. */
export async function queueReportHeader(
  projectId: string,
  reportRef: string | null,
  payload: HeaderPayload,
): Promise<string> {
  const localId = reportRef ?? generateUUID();
  const method: QueueMethod = reportRef ? "PATCH" : "POST";
  const endpoint = reportRef
    ? `${reportBase(projectId)}/${reportRef}/`
    : `${reportBase(projectId)}/`;

  await saveOfflineReport({
    ...payload,
    local_id: localId,
    project_id: projectId,
    status: "draft",
    updated_at: new Date().toISOString(),
    _offline: true,
    _dirty: true,
  } as OfflineReport);

  await addToQueue({
    queue_id: generateUUID(),
    entity_type: "daily_report",
    project_id: projectId,
    method,
    endpoint,
    payload: { ...payload, local_id: localId },
    created_at: new Date().toISOString(),
    status: "pending",
    retry_count: 0,
    error_message: null,
    local_id: localId,
    server_id: reportRef && !reportRef.includes("-") ? reportRef : null,
  });

  return localId;
}

function extractRowId(endpoint: string, resource: ChildResource): string | null {
  const marker = `/${resource}/`;
  const idx = endpoint.indexOf(marker);
  if (idx === -1) return null;
  const rest = endpoint.slice(idx + marker.length).replace(/\/+$/, "");
  return rest.length > 0 ? rest : null;
}

/**
 * Build a map of `rowId → sync status` for a report's child rows by inspecting
 * the offline queue and unresolved conflicts. Rows with no queue entry are
 * considered synced (they came from the server).
 */
export async function buildChildRowSyncMap(
  projectId: string,
  reportRef: string,
  resource: ChildResource,
): Promise<Map<string, RowSyncStatus>> {
  const map = new Map<string, RowSyncStatus>();
  if (!isOfflineDBAvailable()) return map;
  try {
    const queue = await getQueueByProject(projectId);
    const scoped = queue.filter(
      (q) => q.endpoint.includes(`/${reportRef}/`) && q.endpoint.includes(`/${resource}/`),
    );
    for (const q of scoped) {
      if (q.status === "synced") continue;
      const rowId = extractRowId(q.endpoint, resource);
      if (!rowId) continue;
      map.set(rowId, q.status === "failed" ? "failed" : "pending");
    }
    const conflicts = await getUnresolvedConflicts(projectId);
    for (const c of conflicts) {
      const q = scoped.find((x) => x.queue_id === c.queue_id);
      if (!q) continue;
      const rowId = extractRowId(q.endpoint, resource);
      if (rowId) map.set(rowId, "conflict");
    }
  } catch {
    /* db not ready */
  }
  return map;
}

/** Queue a child-row write against the report (server id or offline local id). */
export async function queueChildWrite(
  projectId: string,
  reportRef: string,
  resource: ChildResource,
  method: QueueMethod,
  payload: unknown,
  rowId?: string,
): Promise<void> {
  const suffix = rowId ? `${rowId}/` : "";
  const endpoint = `${reportBase(projectId)}/${reportRef}/${resource}/${suffix}`;
  await addToQueue({
    queue_id: generateUUID(),
    entity_type: CHILD_ENTITY[resource],
    project_id: projectId,
    method,
    endpoint,
    payload,
    created_at: new Date().toISOString(),
    status: "pending",
    retry_count: 0,
    error_message: null,
    local_id: reportRef,
    server_id: null,
  });
}
