/**
 * Helpers that translate daily-report writes into IndexedDB offline-queue
 * entries when the network is unavailable (Sprint 4, Section 4).
 */
import { PATHS } from "@/app/routeVars";
import {
  addToQueue,
  type EntityType,
  generateUUID,
  getOfflineReport,
  getQueueByProject,
  getUnresolvedConflicts,
  isOfflineDBAvailable,
  type OfflineReport,
  type QueueMethod,
  saveOfflineReport,
  updateOfflineReport,
} from "@/app/lib/offlineDB";
import type { ChildResource, HeaderPayload } from "@/app/lib/api/daily-reports";

export type RowSyncStatus = "synced" | "pending" | "failed" | "conflict";

export interface LaborBatchMeta {
  report_date?: string;
  shift?: string;
  weather_condition?: string | null;
  site_status?: string;
  general_notes?: string;
  temp_min?: number | string | null;
  temp_max?: number | string | null;
  /** Server-side labor rows used to seed IndexedDB on first offline save. */
  existing_labor?: unknown[];
}

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
    server_id: reportRef ?? null,
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

function mergeLaborByCategory(existing: unknown[] | undefined, incoming: unknown[]): unknown[] {
  const prev = Array.isArray(existing) ? existing : [];
  const categories = new Set(
    incoming
      .map((row) => (row as { labor_category?: string }).labor_category)
      .filter((c): c is string => Boolean(c)),
  );
  const kept = prev.filter(
    (row) => !categories.has(String((row as { labor_category?: string }).labor_category ?? "")),
  );
  return [...kept, ...incoming];
}

/** Queue labor batch for offline sync via sync-batch payload. */
export async function queueLaborBatch(
  projectId: string,
  reportRef: string,
  rows: unknown[],
  meta: LaborBatchMeta = {},
): Promise<void> {
  const existing = await getOfflineReport(reportRef);
  const reportDate =
    (typeof existing?.report_date === "string" && existing.report_date) ||
    meta.report_date ||
    "";
  if (!reportDate) {
    throw new Error("تاریخ گزارش برای ذخیره آفلاین نیروی انسانی مشخص نیست");
  }

  const mergedLabor = mergeLaborByCategory(
    (existing?.labor as unknown[] | undefined) ?? meta.existing_labor,
    rows,
  );

  const base: OfflineReport = {
    ...(existing ?? {}),
    local_id: reportRef,
    project_id: projectId,
    report_date: reportDate,
    status: (existing?.status as string | undefined) ?? "draft",
    updated_at: new Date().toISOString(),
    shift: meta.shift ?? (existing?.shift as string | undefined) ?? "full",
    weather_condition: meta.weather_condition ?? existing?.weather_condition ?? null,
    site_status: meta.site_status ?? existing?.site_status ?? "active",
    general_notes: meta.general_notes ?? existing?.general_notes ?? "",
    temp_min: meta.temp_min ?? existing?.temp_min ?? null,
    temp_max: meta.temp_max ?? existing?.temp_max ?? null,
    labor: mergedLabor,
    _dirty: true,
    _offline: true,
  };

  await saveOfflineReport(base);

  const queue = await getQueueByProject(projectId);
  const headerEntry = queue.find(
    (q) => q.entity_type === "daily_report" && q.local_id === reportRef && q.status === "pending",
  );
  const headerPayload = {
    local_id: reportRef,
    report_date: reportDate,
    shift: base.shift,
    weather_condition: base.weather_condition,
    site_status: base.site_status,
    general_notes: base.general_notes,
    temp_min: base.temp_min,
    temp_max: base.temp_max,
    labor: mergedLabor,
  };

  if (!headerEntry) {
    const hasServerId = Boolean(reportRef && reportRef.length > 20);
    await addToQueue({
      queue_id: generateUUID(),
      entity_type: "daily_report",
      project_id: projectId,
      method: hasServerId ? "PATCH" : "POST",
      endpoint: hasServerId
        ? `${reportBase(projectId)}/${reportRef}/`
        : `${reportBase(projectId)}/`,
      payload: headerPayload,
      created_at: new Date().toISOString(),
      status: "pending",
      retry_count: 0,
      error_message: null,
      local_id: reportRef,
      server_id: hasServerId ? reportRef : null,
    });
  } else {
    await updateOfflineReport(reportRef, { labor: mergedLabor, _dirty: true });
  }
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
