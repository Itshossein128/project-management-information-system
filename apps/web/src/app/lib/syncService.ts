/**
 * Offline queue sync service (Sprint 4, O-02/O-03).
 *
 * Processes the IndexedDB `offline_queue` when connectivity is restored.
 * Daily-report headers sync before their child rows so the children can be
 * remapped onto the server-assigned report id.
 */
import { apiFetch } from "@/app/lib/api-client";
import {
  addConflict,
  clearSyncedItems,
  generateUUID,
  getPendingQueue,
  type QueueItem,
  updateQueueItem,
} from "@/app/lib/offlineDB";

export interface SyncResult {
  synced: number;
  failed: number;
  conflicts: number;
}

interface ConflictPayload {
  server_state?: unknown;
  fields?: string[];
}

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
  // Our backend error shape: { error: { code, message, details } }.
  const error = body.error as Record<string, unknown> | undefined;
  const details = (error?.details ?? body) as Record<string, unknown>;
  const conflict = (details?.conflict ?? body.conflict) as ConflictPayload | undefined;
  return conflict ?? {};
}

/**
 * After a `daily_report` POST resolves, rewrite any queued child endpoints
 * that still reference the client-side local id.
 */
async function updateChildEndpoints(
  localReportId: string,
  serverReportId: string,
): Promise<void> {
  const pending = await getPendingQueue();
  for (const entry of pending) {
    if (entry.endpoint.includes(localReportId)) {
      await updateQueueItem(entry.queue_id, {
        endpoint: entry.endpoint.replace(localReportId, serverReportId),
      });
    }
  }
}

export async function syncPendingQueue(): Promise<SyncResult> {
  const pending = await getPendingQueue();
  if (pending.length === 0) return { synced: 0, failed: 0, conflicts: 0 };

  const ordered: QueueItem[] = [
    ...pending.filter((e) => e.entity_type === "daily_report"),
    ...pending.filter((e) => e.entity_type !== "daily_report"),
  ];

  let synced = 0;
  let failed = 0;
  let conflicts = 0;

  for (const entry of ordered) {
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

      if (!res.ok) {
        throw Object.assign(new Error("sync request failed"), {
          status: res.status,
          body: await parseBody(res),
        });
      }

      const body = await parseBody(res);
      if (entry.entity_type === "daily_report" && entry.method === "POST") {
        const serverId = String((body.report_id ?? body.id ?? "") as string);
        await updateQueueItem(entry.queue_id, { status: "synced", server_id: serverId });
        if (serverId) await updateChildEndpoints(entry.local_id, serverId);
      } else {
        await updateQueueItem(entry.queue_id, { status: "synced" });
      }
      synced++;
    } catch (err) {
      const status = (err as { status?: number })?.status;
      const body = (err as { body?: Record<string, unknown> })?.body;
      const serverMessage =
        (body?.error as { message?: string } | undefined)?.message ??
        "خطا در ارتباط با سرور";
      const retryCount = entry.retry_count + 1;
      if (status && status >= 400 && status < 500) {
        // Non-retryable client error.
        await updateQueueItem(entry.queue_id, {
          status: "failed",
          retry_count: retryCount,
          error_message: serverMessage,
        });
      } else if (retryCount >= 3) {
        await updateQueueItem(entry.queue_id, {
          status: "failed",
          retry_count: retryCount,
          error_message: serverMessage,
        });
      } else {
        await updateQueueItem(entry.queue_id, {
          status: "pending",
          retry_count: retryCount,
        });
      }
      failed++;
    }
  }

  await clearSyncedItems();
  return { synced, failed, conflicts };
}
