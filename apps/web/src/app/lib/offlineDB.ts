/**
 * IndexedDB wrapper for Velora offline support (Sprint 4, O-01).
 *
 * All access goes through `idb`. Every exported function is client-only:
 * IndexedDB does not exist during SSR, so callers must invoke these from
 * effects / event handlers that run in the browser. `getDB()` throws a clear
 * error if called on the server.
 */
import { type DBSchema, type IDBPDatabase, openDB } from "idb";

// Keep the historical IndexedDB name so existing offline caches stay readable.
export const OFFLINE_DB_NAME = "ipcas-offline";
export const OFFLINE_DB_VERSION = 4;

export function normalizeWeatherValue(val: unknown): string {
  if (val === "sunny") return "clear";
  if (val === "partly_cloudy" || val === "foggy") return "cloudy";
  return typeof val === "string" ? val : "";
}

export function normalizePayloadWeather<T>(payload: T): T {
  if (!payload || typeof payload !== "object") return payload;
  const clone = { ...(payload as Record<string, unknown>) };
  if ("weather_condition" in clone && clone.weather_condition) {
    clone.weather_condition = normalizeWeatherValue(clone.weather_condition);
  }
  if ("weather" in clone && clone.weather) {
    clone.weather = normalizeWeatherValue(clone.weather);
  }
  return clone as T;
}

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
  actor_id?: string;
  unit?: string;
  canonical_unit?: string;
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
  conflict_reason?: string | null;
  status: ConflictStatus;
  created_at: string;
}

export interface QueueStats {
  pending: number;
  syncing: number;
  failed: number;
  total: number;
}

export interface PendingPhoto {
  photo_id: string;
  project_id: string;
  filename: string;
  content_type: string;
  data: ArrayBuffer;
}

export type OperationKind = "create_report" | "create" | "update" | "delete" | "header_update";
export type OperationStatus = "pending" | "syncing" | "synced" | "failed" | "conflict";

export interface LocalReportSnapshot {
  local_report_id: string;
  actor_id: string;
  project_id: string;
  unit: string;
  report_date: string;
  status: string;
  server_report_id?: string | null;
  server_version?: number | null;
  base_revision?: string | null;
  base_header: Record<string, unknown>;
  base_rows: Record<string, unknown[]>;
  overlay_header: Record<string, unknown>;
  overlay_rows: Record<string, unknown[]>;
  tombstones: Record<string, string[]>;
  field_errors: Record<string, Record<string, string>>;
  cached_config?: unknown;
  created_at: string;
  updated_at: string;
}

export interface OfflineOperation {
  operation_id: string;
  local_report_id: string;
  client_id?: string;
  actor_id: string;
  project_id: string;
  unit: string;
  operation_kind: OperationKind;
  target_type: string;
  target_server_id?: string | null;
  base_target_revision?: string | null;
  payload: unknown;
  predecessor_ids: string[];
  supersedes_operation_id?: string | null;
  created_at: string;
  status: OperationStatus;
  error_code?: string | null;
  error_message?: string | null;
  result?: unknown;
}

export interface OfflineClaim {
  claim_id: string;
  scope: string;
  actor_id: string;
  project_id: string;
  owner_tab: string;
  fencing_token: number;
  acquired_at: string;
  expires_at: string;
}

export interface OfflineConflict {
  conflict_id: string;
  source_operation_ids: string[];
  local_report_id: string;
  actor_id: string;
  project_id: string;
  unit: string;
  reason_code: string;
  local_snapshot: unknown;
  server_snapshot: unknown;
  status: "unresolved" | "resolved_server" | "resolved_correction";
  destination_transfer_id?: string | null;
  created_at: string;
}

export interface LegacyQuarantine {
  queue_id: string;
  raw_record: unknown;
  quarantine_reason: string;
  quarantined_at: string;
  project_id: string;
}

interface VeloraDB extends DBSchema {
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
  pending_photos: {
    key: string;
    value: PendingPhoto;
  };
  local_snapshots: {
    key: string;
    value: LocalReportSnapshot;
    indexes: {
      actor_id: string;
      project_id: string;
    };
  };
  offline_operations: {
    key: string;
    value: OfflineOperation;
    indexes: {
      status: string;
      local_report_id: string;
      actor_id: string;
      project_id: string;
      created_at: string;
    };
  };
  offline_claims: {
    key: string;
    value: OfflineClaim;
  };
  offline_conflicts: {
    key: string;
    value: OfflineConflict;
    indexes: { project_id: string; local_report_id: string };
  };
  legacy_quarantine: {
    key: string;
    value: LegacyQuarantine;
    indexes: { project_id: string; quarantined_at: string };
  };
}

let dbPromise: Promise<IDBPDatabase<VeloraDB>> | null = null;

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

export function isEligibleForReplay(item: QueueItem): boolean {
  if (item.status !== "pending") return false;
  // An item must have a proven actor/owner and proven unit scope to be eligible for automatic replay.
  // Legacy queue records that lack proven actor or canonical unit are quarantined from automatic replay.
  const hasProvenActor = Boolean(item.actor_id || (item as any).actor || (item as any).user_id);
  const hasProvenUnit = Boolean(item.unit || item.canonical_unit || (item as any).discipline);
  if (!hasProvenActor || !hasProvenUnit) {
    return false;
  }
  return true;
}

export function initDB(): Promise<IDBPDatabase<VeloraDB>> {
  if (!isOfflineDBAvailable()) {
    return Promise.reject(new Error("IndexedDB is not available in this environment"));
  }
  if (!dbPromise) {
    dbPromise = openDB<VeloraDB>(OFFLINE_DB_NAME, OFFLINE_DB_VERSION, {
      upgrade(db, oldVersion, _newVersion, transaction) {
        if (oldVersion < 1) {
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
        }
        if (oldVersion < 2 && !db.objectStoreNames.contains("pending_photos")) {
          db.createObjectStore("pending_photos", { keyPath: "photo_id" });
        }
        if (oldVersion < 3 && transaction) {
          if (db.objectStoreNames.contains("offline_daily_reports")) {
            const reportStore = transaction.objectStore("offline_daily_reports");
            reportStore.openCursor().then(function iter(cursor: any) {
              if (!cursor) return;
              const rep = cursor.value;
              let changed = false;
              if (
                rep.weather_condition &&
                ["sunny", "partly_cloudy", "foggy"].includes(rep.weather_condition as string)
              ) {
                rep.weather_condition = normalizeWeatherValue(rep.weather_condition);
                changed = true;
              }
              if (changed) {
                cursor.update(rep);
              }
              cursor.continue().then(iter);
            });
          }

          if (db.objectStoreNames.contains("offline_queue")) {
            const queueStore = transaction.objectStore("offline_queue");
            queueStore.openCursor().then(function iter(cursor: any) {
              if (!cursor) return;
              const item = cursor.value;
              if (item.payload && typeof item.payload === "object") {
                const norm = normalizePayloadWeather(item.payload);
                if (JSON.stringify(norm) !== JSON.stringify(item.payload)) {
                  item.payload = norm;
                  cursor.update(item);
                }
              }
              cursor.continue().then(iter);
            });
          }
        }
        if (oldVersion < 4) {
          if (!db.objectStoreNames.contains("local_snapshots")) {
            const snapshots = db.createObjectStore("local_snapshots", { keyPath: "local_report_id" });
            snapshots.createIndex("actor_id", "actor_id");
            snapshots.createIndex("project_id", "project_id");
          }
          if (!db.objectStoreNames.contains("offline_operations")) {
            const ops = db.createObjectStore("offline_operations", { keyPath: "operation_id" });
            ops.createIndex("status", "status");
            ops.createIndex("local_report_id", "local_report_id");
            ops.createIndex("actor_id", "actor_id");
            ops.createIndex("project_id", "project_id");
            ops.createIndex("created_at", "created_at");
          }
          if (!db.objectStoreNames.contains("offline_claims")) {
            db.createObjectStore("offline_claims", { keyPath: "claim_id" });
          }
          if (!db.objectStoreNames.contains("offline_conflicts")) {
            const conflicts = db.createObjectStore("offline_conflicts", { keyPath: "conflict_id" });
            conflicts.createIndex("project_id", "project_id");
            conflicts.createIndex("local_report_id", "local_report_id");
          }
          if (!db.objectStoreNames.contains("legacy_quarantine")) {
            const quarantine = db.createObjectStore("legacy_quarantine", { keyPath: "queue_id" });
            quarantine.createIndex("project_id", "project_id");
            quarantine.createIndex("quarantined_at", "quarantined_at");
          }
        }
      },
    }).catch((err) => {
      dbPromise = null;
      throw err;
    });
  }
  return dbPromise;
}

export async function closeDB(): Promise<void> {
  if (dbPromise) {
    try {
      const db = await dbPromise;
      db.close();
    } catch {
      // ignore
    } finally {
      dbPromise = null;
    }
  }
}

function getDB(): Promise<IDBPDatabase<VeloraDB>> {
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
  return all.filter(isEligibleForReplay).sort((a, b) => a.created_at.localeCompare(b.created_at));
}

export async function getQuarantinedLegacyQueue(): Promise<QueueItem[]> {
  const db = await getDB();
  const all = await db.getAll("offline_queue");
  return all.filter((item) => item.status === "pending" && !isEligibleForReplay(item));
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

export async function getFailedQueue(): Promise<QueueItem[]> {
  const db = await getDB();
  const all = await db.getAll("offline_queue");
  return all.filter((i) => i.status === "failed");
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

export async function savePendingPhoto(photo: PendingPhoto): Promise<void> {
  const db = await getDB();
  await db.put("pending_photos", photo);
}

export async function getPendingPhoto(photoId: string): Promise<PendingPhoto | undefined> {
  const db = await getDB();
  return db.get("pending_photos", photoId);
}

export async function deletePendingPhoto(photoId: string): Promise<void> {
  const db = await getDB();
  await db.delete("pending_photos", photoId);
}

export async function listPendingPhotos(projectId: string): Promise<PendingPhoto[]> {
  const db = await getDB();
  const all = await db.getAll("pending_photos");
  return all.filter((p) => p.project_id === projectId);
}

export async function getConflictQueueEndpoint(
  queueId: string,
): Promise<{ endpoint: string; method: QueueMethod } | null> {
  const item = await getQueueItem(queueId);
  if (!item) return null;
  return { endpoint: item.endpoint, method: item.method };
}

// ---------------------------------------------------------------------------
// local_snapshots & offline_operations (v2 specialty unit sync)
// ---------------------------------------------------------------------------

export async function saveSnapshotAndOperation(
  snapshot: LocalReportSnapshot,
  operation?: OfflineOperation,
): Promise<void> {
  const db = await getDB();
  const tx = db.transaction(
    operation ? ["local_snapshots", "offline_operations"] : ["local_snapshots"],
    "readwrite",
  );
  await tx.objectStore("local_snapshots").put(snapshot);
  if (operation) {
    await tx.objectStore("offline_operations").put(operation);
  }
  await tx.done;
}

export async function getLocalSnapshot(localReportId: string): Promise<LocalReportSnapshot | undefined> {
  const db = await getDB();
  return db.get("local_snapshots", localReportId);
}

export async function findLocalSnapshot(
  projectId: string,
  unit: string,
  reportDate: string,
  actorId?: string,
): Promise<LocalReportSnapshot | undefined> {
  const db = await getDB();
  try {
    const all = await db.getAllFromIndex("local_snapshots", "project_id", projectId);
    const match = all.find(
      (s) =>
        s.unit === unit &&
        s.report_date === reportDate &&
        (!actorId || s.actor_id === actorId),
    );
    if (match) return match;
  } catch {
    // Index fallback
  }
  const allSnapshots = await db.getAll("local_snapshots");
  return allSnapshots.find(
    (s) =>
      String(s.project_id) === String(projectId) &&
      s.unit === unit &&
      s.report_date === reportDate &&
      (!actorId || s.actor_id === actorId),
  );
}

export async function getLocalSnapshotsByProject(
  projectId: string,
  actorId?: string,
): Promise<LocalReportSnapshot[]> {
  const db = await getDB();
  const all = await db.getAllFromIndex("local_snapshots", "project_id", projectId);
  if (actorId) {
    return all.filter((s) => s.actor_id === actorId);
  }
  return all;
}

export async function saveLocalSnapshot(snapshot: LocalReportSnapshot): Promise<void> {
  const db = await getDB();
  await db.put("local_snapshots", snapshot);
}

export async function deleteLocalSnapshot(localReportId: string): Promise<void> {
  const db = await getDB();
  await db.delete("local_snapshots", localReportId);
}

export async function saveOperation(operation: OfflineOperation): Promise<void> {
  const db = await getDB();
  await db.put("offline_operations", operation);
}

export async function getOperation(operationId: string): Promise<OfflineOperation | undefined> {
  const db = await getDB();
  return db.get("offline_operations", operationId);
}

export async function getPendingOperations(
  actorId?: string,
  projectId?: string,
): Promise<OfflineOperation[]> {
  const db = await getDB();
  let ops = await db.getAllFromIndex("offline_operations", "status", "pending");
  if (actorId) {
    ops = ops.filter((o) => o.actor_id === actorId);
  }
  if (projectId) {
    ops = ops.filter((o) => o.project_id === projectId);
  }
  return ops.sort((a, b) => a.created_at.localeCompare(b.created_at));
}

export async function getOperationsForReport(localReportId: string): Promise<OfflineOperation[]> {
  const db = await getDB();
  const ops = await db.getAllFromIndex("offline_operations", "local_report_id", localReportId);
  return ops.sort((a, b) => a.created_at.localeCompare(b.created_at));
}

export async function updateOperation(
  operationId: string,
  updates: Partial<OfflineOperation>,
): Promise<void> {
  const db = await getDB();
  const existing = await db.get("offline_operations", operationId);
  if (!existing) return;
  await db.put("offline_operations", { ...existing, ...updates });
}

export async function quarantineLegacyRecord(quarantine: LegacyQuarantine): Promise<void> {
  const db = await getDB();
  await db.put("legacy_quarantine", quarantine);
}

export async function getQuarantinedRecords(projectId?: string): Promise<LegacyQuarantine[]> {
  const db = await getDB();
  if (projectId) {
    return db.getAllFromIndex("legacy_quarantine", "project_id", projectId);
  }
  return db.getAll("legacy_quarantine");
}

export interface OfflineBackup {
  local_snapshots: LocalReportSnapshot[];
  offline_operations: OfflineOperation[];
  legacy_quarantine: LegacyQuarantine[];
}

/** Copy the durable stores. This does not delete them and cannot downgrade IndexedDB. */
export async function exportOfflineBackup(): Promise<OfflineBackup> {
  const db = await getDB();
  return {
    local_snapshots: await db.getAll("local_snapshots"),
    offline_operations: await db.getAll("offline_operations"),
    legacy_quarantine: await db.getAll("legacy_quarantine"),
  };
}

export async function restoreOfflineBackup(backup: OfflineBackup): Promise<void> {
  const db = await getDB();
  const tx = db.transaction(["local_snapshots", "offline_operations", "legacy_quarantine"], "readwrite");
  for (const snapshot of backup.local_snapshots) await tx.objectStore("local_snapshots").put(snapshot);
  for (const operation of backup.offline_operations) await tx.objectStore("offline_operations").put(operation);
  for (const record of backup.legacy_quarantine) await tx.objectStore("legacy_quarantine").put(record);
  await tx.done;
}

