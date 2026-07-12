/**
 * Offline queue sync service (Sprint 5).
 *
 * Daily reports sync via the batch endpoint; remaining child-only queue entries
 * sync individually after headers resolve.
 */
import { apiFetch } from "@/app/lib/api-client";
import { syncBatch, type SyncBatchResult } from "@/app/lib/api/daily-reports";
import {
  addConflict,
  clearSyncedItems,
  deletePendingPhoto,
  generateUUID,
  getOfflineReportsByProject,
  getPendingPhoto,
  getPendingQueue,
  type QueueItem,
  updateOfflineReport,
  updateQueueItem,
} from "@/app/lib/offlineDB";
import { confirmUpload, requestUploadUrl } from "@/app/lib/api/files";

export interface SyncResult {
  synced: number;
  failed: number;
  conflicts: number;
}

interface ConflictPayload {
  server_state?: unknown;
  fields?: string[];
}

const CHILD_RESOURCE_MAP: Record<string, string> = {
  activities: "activities",
  labor: "labor",
  equipment: "equipment",
  materials: "materials",
  "concrete-logs": "concrete_logs",
  "labor-camp": "labor_camp",
  incidents: "incidents",
};

async function parseBody(res: Response): Promise<Record<string, unknown>> {
  const raw = await res.text();
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function extractConflict(body: Record<string, unknown>): ConflictPayload {
  const error = body.error as Record<string, unknown> | undefined;
  const details = (error?.details ?? body) as Record<string, unknown>;
  const conflict = (details?.conflict ?? body.conflict) as ConflictPayload | undefined;
  return conflict ?? {};
}

function parseChildEndpoint(endpoint: string): { resource: string; rowId: string | null } | null {
  const match = endpoint.match(/\/daily-reports\/[^/]+\/([^/]+)(?:\/([^/]+)\/)?$/);
  if (!match) return null;
  return { resource: match[1], rowId: match[2] ?? null };
}

async function updateChildEndpoints(localReportId: string, serverReportId: string): Promise<void> {
  const pending = await getPendingQueue();
  for (const entry of pending) {
    if (entry.endpoint.includes(localReportId)) {
      await updateQueueItem(entry.queue_id, {
        endpoint: entry.endpoint.replace(localReportId, serverReportId),
        local_id: serverReportId,
        server_id: serverReportId,
      });
    }
  }
}

function groupProjects(items: QueueItem[]): string[] {
  return [...new Set(items.map((i) => i.project_id))];
}

async function resolvePendingPhotoRefs(
  projectId: string,
  payload: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const clone = structuredClone(payload);
  for (const sectionKey of Object.values(CHILD_RESOURCE_MAP)) {
    const rows = clone[sectionKey];
    if (!Array.isArray(rows)) continue;
    for (const row of rows) {
      const photoRef = (row as { photo_file?: string }).photo_file;
      if (!photoRef || !String(photoRef).startsWith("pending:")) continue;
      const photoId = String(photoRef).slice("pending:".length);
      const pending = await getPendingPhoto(photoId);
      if (!pending) continue;
      const { file_id, upload_url } = await requestUploadUrl(
        projectId,
        pending.filename,
        pending.content_type,
      );
      const put = await fetch(upload_url, {
        method: "PUT",
        body: pending.data,
        headers: { "Content-Type": pending.content_type },
      });
      if (!put.ok) throw new Error("photo upload failed");
      await confirmUpload(file_id, pending.data.byteLength);
      (row as { photo_file?: string }).photo_file = file_id;
      await deletePendingPhoto(photoId);
    }
  }
  return clone;
}

async function buildReportBatchPayload(
  projectId: string,
  localId: string,
  headerItems: QueueItem[],
  childItems: QueueItem[],
): Promise<Record<string, unknown>> {
  const offlineReports = await getOfflineReportsByProject(projectId);
  const offline = offlineReports.find((r) => r.local_id === localId);

  const headerItem = headerItems.find((i) => i.local_id === localId);
  const payload: Record<string, unknown> = {
    local_id: localId,
    ...(headerItem?.payload as Record<string, unknown>),
    ...(offline ?? {}),
  };

  for (const key of Object.values(CHILD_RESOURCE_MAP)) {
    if (Array.isArray(payload[key])) continue;
    const pendingKey = `_${key}` as keyof typeof payload;
    if (Array.isArray(payload[pendingKey])) {
      payload[key] = payload[pendingKey];
    }
  }

  for (const item of childItems.filter((i) => i.local_id === localId)) {
    const parsed = parseChildEndpoint(item.endpoint);
    if (!parsed) continue;
    const sectionKey = CHILD_RESOURCE_MAP[parsed.resource];
    if (!sectionKey) continue;
    const rows = (payload[sectionKey] as unknown[]) ?? [];
    if (item.method === "DELETE" && parsed.rowId) {
      payload[sectionKey] = rows.filter(
        (r) => String((r as { id?: string }).id) !== parsed.rowId,
      );
    } else if (item.method === "POST") {
      payload[sectionKey] = [...rows, item.payload];
    } else if (item.method === "PATCH" && parsed.rowId) {
      payload[sectionKey] = rows.map((r) =>
        String((r as { id?: string }).id) === parsed.rowId
          ? {
              ...(r as Record<string, unknown>),
              ...(item.payload as Record<string, unknown>),
            }
          : r,
      );
    }
  }

  delete payload._offline;
  delete payload._dirty;
  delete payload.updated_at;
  delete payload.status;
  delete payload.project_id;
  return payload;
}

async function syncProjectBatch(
  projectId: string,
  pending: QueueItem[],
): Promise<{ synced: number; failed: number; conflicts: number }> {
  let synced = 0;
  let failed = 0;
  let conflicts = 0;

  const projectPending = pending.filter((i) => i.project_id === projectId);
  const headerItems = projectPending.filter((i) => i.entity_type === "daily_report");
  const childItems = projectPending.filter((i) => i.entity_type !== "daily_report");

  const localIds = new Set<string>();
  for (const item of headerItems) localIds.add(item.local_id);
  for (const item of childItems) localIds.add(item.local_id);
  const offlineReports = await getOfflineReportsByProject(projectId);
  for (const report of offlineReports) {
    if (report._dirty) localIds.add(report.local_id);
  }

  if (localIds.size === 0) return { synced, failed, conflicts };

  const batchPayloads: Record<string, unknown>[] = [];
  const batchQueueIds: string[][] = [];

  for (const localId of localIds) {
    const relatedIds = projectPending
      .filter((i) => i.local_id === localId)
      .map((i) => i.queue_id);
    if (relatedIds.length === 0 && !offlineReports.some((r) => r.local_id === localId && r._dirty)) {
      continue;
    }
    batchPayloads.push(
      await resolvePendingPhotoRefs(
        projectId,
        await buildReportBatchPayload(projectId, localId, headerItems, childItems),
      ),
    );
    batchQueueIds.push(relatedIds.length ? relatedIds : []);
  }

  if (batchPayloads.length === 0) return { synced, failed, conflicts };

  for (const ids of batchQueueIds) {
    for (const id of ids) await updateQueueItem(id, { status: "syncing" });
  }

  let result: SyncBatchResult;
  try {
    result = await syncBatch(projectId, batchPayloads);
  } catch {
    for (const ids of batchQueueIds) {
      for (const id of ids) {
        await updateQueueItem(id, {
          status: "failed",
          error_message: "خطا در همگام‌سازی دسته‌ای",
        });
      }
    }
    return { synced: 0, failed: batchQueueIds.flat().length, conflicts: 0 };
  }

  for (let i = 0; i < result.results.length; i++) {
    const row = result.results[i];
    const localId = batchPayloads[i]?.local_id as string;
    const queueIds = batchQueueIds[i] ?? [];

    if (row.status === "created" || row.status === "merged") {
      for (const id of queueIds) {
        await updateQueueItem(id, { status: "synced", server_id: row.server_id });
      }
      if (row.server_id && localId) {
        await updateChildEndpoints(localId, row.server_id);
        await updateOfflineReport(localId, { _dirty: false, _offline: false });
      }
      synced += Math.max(queueIds.length, 1);
    } else if (row.status === "conflict") {
      for (const id of queueIds) {
        await addConflict({
          conflict_id: generateUUID(),
          queue_id: id,
          project_id: projectId,
          entity_type: "daily_report",
          local_payload: batchPayloads[i],
          server_payload: { server_id: row.server_id, reason: row.conflict_reason },
          conflict_fields: [],
          status: "unresolved",
          created_at: new Date().toISOString(),
        });
        await updateQueueItem(id, {
          status: "failed",
          error_message: row.conflict_reason ?? "تعارض داده",
        });
      }
      conflicts += Math.max(queueIds.length, 1);
    } else if (row.status === "error" || row.status === "skipped") {
      for (const id of queueIds) {
        await updateQueueItem(id, {
          status: "failed",
          error_message: row.conflict_reason ?? "خطا در همگام‌سازی",
        });
      }
      failed += Math.max(queueIds.length, 1);
    }
  }

  return { synced, failed, conflicts };
}

async function syncRemainingItems(pending: QueueItem[]): Promise<SyncResult> {
  let synced = 0;
  let failed = 0;
  let conflicts = 0;

  for (const entry of pending) {
    await updateQueueItem(entry.queue_id, { status: "syncing" });
    try {
      const res = await apiFetch(entry.endpoint, {
        method: entry.method,
        body: entry.method === "DELETE" ? undefined : JSON.stringify(entry.payload),
      });

      if (res.status === 409) {
        const body = await parseBody(res);
        const conflict = extractConflict(body);
        await addConflict({
          conflict_id: generateUUID(),
          queue_id: entry.queue_id,
          project_id: entry.project_id,
          entity_type: entry.entity_type,
          local_payload: entry.payload,
          server_payload: conflict.server_state ?? {},
          conflict_fields: conflict.fields ?? [],
          status: "unresolved",
          created_at: new Date().toISOString(),
        });
        await updateQueueItem(entry.queue_id, {
          status: "failed",
          error_message: "تعارض داده — نیاز به بررسی دستی",
        });
        conflicts++;
        continue;
      }

      if (!res.ok) throw new Error("sync failed");

      await updateQueueItem(entry.queue_id, { status: "synced" });
      synced++;
    } catch {
      await updateQueueItem(entry.queue_id, {
        status: "failed",
        error_message: "خطا در ارتباط با سرور",
      });
      failed++;
    }
  }

  return { synced, failed, conflicts };
}

export async function syncPendingQueue(): Promise<SyncResult> {
  const pending = await getPendingQueue();
  if (pending.length === 0) return { synced: 0, failed: 0, conflicts: 0 };

  let synced = 0;
  let failed = 0;
  let conflicts = 0;

  for (const projectId of groupProjects(pending)) {
    const batchResult = await syncProjectBatch(projectId, pending);
    synced += batchResult.synced;
    failed += batchResult.failed;
    conflicts += batchResult.conflicts;
  }

  const remaining = await getPendingQueue();
  if (remaining.length > 0) {
    const rest = await syncRemainingItems(remaining);
    synced += rest.synced;
    failed += rest.failed;
    conflicts += rest.conflicts;
  }

  await clearSyncedItems();
  return { synced, failed, conflicts };
}

export async function retryFailedQueueItem(queueId: string): Promise<void> {
  await updateQueueItem(queueId, { status: "pending", retry_count: 0, error_message: null });
  await syncPendingQueue();
}

export async function discardFailedQueueItem(queueId: string): Promise<void> {
  const { removeQueueItem } = await import("@/app/lib/offlineDB");
  await removeQueueItem(queueId);
}
