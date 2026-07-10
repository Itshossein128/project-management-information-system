/**
 * IndexedDB wrapper for IPCAS offline support (Sprint 4, O-01).
 *
 * All access goes through `idb`. Every exported function is client-only:
 * IndexedDB does not exist during SSR, so callers must invoke these from
 * effects / event handlers that run in the browser. `getDB()` throws a clear
 * error if called on the server.
 */
import { type DBSchema, type IDBPDatabase, openDB } from "idb";

export const OFFLINE_DB_NAME = "ipcas-offline";
export const OFFLINE_DB_VERSION = 1;

export type EntityType =
  | "daily_report"
  | "daily_activity"
  | "daily_labor"
  | "daily_equipment"
  | "daily_material"
  | "weather_log";

export type QueueMethod = "POST" | "PATCH" | "DELETE";
export type QueueStatus = "pending" | "syncing" | "synced" | "failed";

export interface QueueItem {
  queue_id: string;
  entity_type: EntityType;
  project_id: string;
  method: QueueMethod;
  endpoint: string;
  payload: unknown;
  created_at: string;
  status: QueueStatus;
  retry_count: number;
  error_message: string | null;
  local_id: string;
  server_id: string | null;
}

export interface OfflineReport {
  local_id: string;
  project_id: string;
  report_date: string;
  status: string;
  updated_at: string;
  _offline?: boolean;
  _dirty?: boolean;
  [key: string]: unknown;
}

export interface CachedProject {
  project_id: string;
  [key: string]: unknown;
}

export interface CachedWBS {
  wbs_id: string;
  project_id: string;
  [key: string]: unknown;
}

export interface CachedActivity {
  activity_id: string;
  project_id: string;
  wbs_id: string;
  [key: string]: unknown;
}

export interface CachedManpowerTitle {
  id: string;
  category: "indirect" | "direct";
  [key: string]: unknown;
}

export interface CachedSubcontractor {
  id: string;
  project_id: string;
  [key: string]: unknown;
}

export type ConflictStatus =
  | "unresolved"
  | "resolved_local"
  | "resolved_server"
  | "resolved_merged";

export interface ConflictEntry {
  conflict_id: string;
  queue_id: string;
  project_id: string;
  entity_type: string;
  local_payload: unknown;
  server_payload: unknown;
  conflict_fields: string[];
  status: ConflictStatus;
  created_at: string;
}

export interface QueueStats {
  pending: number;
  syncing: number;
  failed: number;
  total: number;
}

interface IpcasDB extends DBSchema {
  offline_queue: {
    key: string;
    value: QueueItem;
    indexes: {
      entity_type: string;
      project_id: string;
      created_at: string;
      status: string;
    };
  };
  offline_daily_reports: {
    key: string;
    value: OfflineReport;
    indexes: { project_id: string; report_date: string; status: string };
  };
  cached_projects: { key: string; value: CachedProject };
  cached_wbs: {
    key: string;
    value: CachedWBS;
    indexes: { project_id: string };
  };
  cached_activities: {
    key: string;
    value: CachedActivity;
    indexes: { project_id: string; wbs_id: string };
  };
  cached_manpower_titles: {
    key: string;
    value: CachedManpowerTitle;
    indexes: { category: string };
  };
  cached_subcontractors: {
    key: string;
    value: CachedSubcontractor;
    indexes: { project_id: string };
  };
  conflict_log: {
    key: string;
    value: ConflictEntry;
    indexes: { project_id: string; status: string };
  };
}

let dbPromise: Promise<IDBPDatabase<IpcasDB>> | null = null;

export function generateUUID(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID.
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function isOfflineDBAvailable(): boolean {
  return typeof window !== "undefined" && typeof indexedDB !== "undefined";
}

export function initDB(): Promise<IDBPDatabase<IpcasDB>> {
  if (!isOfflineDBAvailable()) {
    return Promise.reject(new Error("IndexedDB is not available in this environment"));
  }
  if (!dbPromise) {
    dbPromise = openDB<IpcasDB>(OFFLINE_DB_NAME, OFFLINE_DB_VERSION, {
      upgrade(db) {
        const queue = db.createObjectStore("offline_queue", { keyPath: "queue_id" });
        queue.createIndex("entity_type", "entity_type");
        queue.createIndex("project_id", "project_id");
        queue.createIndex("created_at", "created_at");
        queue.createIndex("status", "status");

        const reports = db.createObjectStore("offline_daily_reports", {
          keyPath: "local_id",
        });
        reports.createIndex("project_id", "project_id");
        reports.createIndex("report_date", "report_date");
        reports.createIndex("status", "status");

        db.createObjectStore("cached_projects", { keyPath: "project_id" });

        const wbs = db.createObjectStore("cached_wbs", { keyPath: "wbs_id" });
        wbs.createIndex("project_id", "project_id");

        const activities = db.createObjectStore("cached_activities", {
          keyPath: "activity_id",
        });
        activities.createIndex("project_id", "project_id");
        activities.createIndex("wbs_id", "wbs_id");

        const titles = db.createObjectStore("cached_manpower_titles", {
          keyPath: "id",
        });
        titles.createIndex("category", "category");

        const subs = db.createObjectStore("cached_subcontractors", { keyPath: "id" });
        subs.createIndex("project_id", "project_id");

        const conflicts = db.createObjectStore("conflict_log", {
          keyPath: "conflict_id",
        });
        conflicts.createIndex("project_id", "project_id");
        conflicts.createIndex("status", "status");
      },
    });
  }
  return dbPromise;
}

function getDB(): Promise<IDBPDatabase<IpcasDB>> {
  return initDB();
}

// ---------------------------------------------------------------------------
// offline_queue
// ---------------------------------------------------------------------------

export async function addToQueue(entry: QueueItem): Promise<void> {
  const db = await getDB();
  await db.put("offline_queue", entry);
}

export async function getPendingQueue(): Promise<QueueItem[]> {
  const db = await getDB();
  const all = await db.getAllFromIndex("offline_queue", "status", "pending");
  return all.sort((a, b) => a.created_at.localeCompare(b.created_at));
}

export async function getQueueByProject(projectId: string): Promise<QueueItem[]> {
  const db = await getDB();
  return db.getAllFromIndex("offline_queue", "project_id", projectId);
}

export async function getQueueItem(queueId: string): Promise<QueueItem | undefined> {
  const db = await getDB();
  return db.get("offline_queue", queueId);
}

export async function updateQueueItem(
  queueId: string,
  updates: Partial<QueueItem>,
): Promise<void> {
  const db = await getDB();
  const existing = await db.get("offline_queue", queueId);
  if (!existing) return;
  await db.put("offline_queue", { ...existing, ...updates });
}

export async function clearSyncedItems(): Promise<void> {
  const db = await getDB();
  const tx = db.transaction("offline_queue", "readwrite");
  const all = await tx.store.getAll();
  await Promise.all(
    all.filter((item) => item.status === "synced").map((item) => tx.store.delete(item.queue_id)),
  );
  await tx.done;
}

export async function getQueueStats(): Promise<QueueStats> {
  const db = await getDB();
  const all = await db.getAll("offline_queue");
  return {
    pending: all.filter((i) => i.status === "pending").length,
    syncing: all.filter((i) => i.status === "syncing").length,
    failed: all.filter((i) => i.status === "failed").length,
    total: all.length,
  };
}

// ---------------------------------------------------------------------------
// offline_daily_reports
// ---------------------------------------------------------------------------

export async function saveOfflineReport(report: OfflineReport): Promise<void> {
  const db = await getDB();
  await db.put("offline_daily_reports", report);
}

export async function getOfflineReport(localId: string): Promise<OfflineReport | undefined> {
  const db = await getDB();
  return db.get("offline_daily_reports", localId);
}

export async function getOfflineReportsByProject(projectId: string): Promise<OfflineReport[]> {
  const db = await getDB();
  return db.getAllFromIndex("offline_daily_reports", "project_id", projectId);
}

export async function updateOfflineReport(
  localId: string,
  updates: Partial<OfflineReport>,
): Promise<void> {
  const db = await getDB();
  const existing = await db.get("offline_daily_reports", localId);
  if (!existing) return;
  await db.put("offline_daily_reports", { ...existing, ...updates });
}

export async function deleteOfflineReport(localId: string): Promise<void> {
  const db = await getDB();
  await db.delete("offline_daily_reports", localId);
}

// ---------------------------------------------------------------------------
// cached reference data
// ---------------------------------------------------------------------------

export async function cacheProject(project: CachedProject): Promise<void> {
  const db = await getDB();
  await db.put("cached_projects", project);
}

export async function getCachedProject(projectId: string): Promise<CachedProject | undefined> {
  const db = await getDB();
  return db.get("cached_projects", projectId);
}

export async function cacheWBS(nodes: CachedWBS[]): Promise<void> {
  const db = await getDB();
  const tx = db.transaction("cached_wbs", "readwrite");
  await Promise.all(nodes.map((node) => tx.store.put(node)));
  await tx.done;
}

export async function getCachedWBS(projectId: string): Promise<CachedWBS[]> {
  const db = await getDB();
  return db.getAllFromIndex("cached_wbs", "project_id", projectId);
}

export async function cacheActivities(activities: CachedActivity[]): Promise<void> {
  const db = await getDB();
  const tx = db.transaction("cached_activities", "readwrite");
  await Promise.all(activities.map((a) => tx.store.put(a)));
  await tx.done;
}

export async function getCachedActivities(projectId: string): Promise<CachedActivity[]> {
  const db = await getDB();
  return db.getAllFromIndex("cached_activities", "project_id", projectId);
}

export async function cacheManpowerTitles(titles: CachedManpowerTitle[]): Promise<void> {
  const db = await getDB();
  const tx = db.transaction("cached_manpower_titles", "readwrite");
  await Promise.all(titles.map((title) => tx.store.put(title)));
  await tx.done;
}

export async function getCachedManpowerTitles(
  category?: "indirect" | "direct",
): Promise<CachedManpowerTitle[]> {
  const db = await getDB();
  if (category) {
    return db.getAllFromIndex("cached_manpower_titles", "category", category);
  }
  return db.getAll("cached_manpower_titles");
}

export async function cacheSubcontractors(
  projectId: string,
  subs: (Partial<CachedSubcontractor> & { id: string })[],
): Promise<void> {
  const db = await getDB();
  const tx = db.transaction("cached_subcontractors", "readwrite");
  await Promise.all(subs.map((sub) => tx.store.put({ ...sub, project_id: projectId })));
  await tx.done;
}

export async function getCachedSubcontractors(
  projectId: string,
): Promise<CachedSubcontractor[]> {
  const db = await getDB();
  return db.getAllFromIndex("cached_subcontractors", "project_id", projectId);
}

// ---------------------------------------------------------------------------
// conflict_log
// ---------------------------------------------------------------------------

export async function addConflict(conflict: ConflictEntry): Promise<void> {
  const db = await getDB();
  await db.put("conflict_log", conflict);
}

export async function getUnresolvedConflicts(projectId: string): Promise<ConflictEntry[]> {
  const db = await getDB();
  const all = await db.getAllFromIndex("conflict_log", "project_id", projectId);
  return all.filter((c) => c.status === "unresolved");
}

export async function getConflict(conflictId: string): Promise<ConflictEntry | undefined> {
  const db = await getDB();
  return db.get("conflict_log", conflictId);
}

export async function countUnresolvedConflicts(): Promise<number> {
  const db = await getDB();
  return db.countFromIndex("conflict_log", "status", "unresolved");
}

export async function resolveConflict(
  conflictId: string,
  resolution: Exclude<ConflictStatus, "unresolved">,
): Promise<void> {
  const db = await getDB();
  const existing = await db.get("conflict_log", conflictId);
  if (!existing) return;
  await db.put("conflict_log", { ...existing, status: resolution });
}

export async function removeQueueItem(queueId: string): Promise<void> {
  const db = await getDB();
  await db.delete("offline_queue", queueId);
}

export async function getConflictQueueEndpoint(
  queueId: string,
): Promise<{ endpoint: string; method: QueueMethod } | null> {
  const item = await getQueueItem(queueId);
  if (!item) return null;
  return { endpoint: item.endpoint, method: item.method };
}
