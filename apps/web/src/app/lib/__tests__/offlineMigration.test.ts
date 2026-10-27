import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { chromium } from "@playwright/test";

// Run against an isolated Vite server; Chromium uses its own temporary profile.
const origin = process.env.OFFLINE_TEST_ORIGIN ?? "http://127.0.0.1:5197";
let browser: Awaited<ReturnType<typeof chromium.launch>>;
let result: { pendingIds: string[]; preservedPayload: unknown; version: number };

before(async () => {
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(origin, { waitUntil: "domcontentloaded" });
  result = await page.evaluate(async () => {
    const db = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("ipcas-offline", 3);
      request.onupgradeneeded = () => {
        const queue = request.result.createObjectStore("offline_queue", { keyPath: "queue_id" });
        queue.createIndex("status", "status");
        queue.createIndex("project_id", "project_id");
        queue.createIndex("entity_type", "entity_type");
        queue.createIndex("created_at", "created_at");
      };
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
    const payload = { description: "legacy work", quantity: 7 };
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction("offline_queue", "readwrite");
      tx.objectStore("offline_queue").put({ queue_id: "legacy-unknown", project_id: "project-a", entity_type: "daily_activity", method: "POST", endpoint: "/activities/", payload, created_at: "2026-01-01", status: "pending", local_id: "legacy-report", server_id: null, retry_count: 0, error_message: null });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
    db.close();
    // Vite serves the current production module, without changing source files.
    const module = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
    const pending = await module.getPendingQueue();
    const current = await module.initDB();
    const raw = await current.get("offline_queue", "legacy-unknown");
    return { pendingIds: pending.map((entry: { queue_id: string }) => entry.queue_id), preservedPayload: raw?.payload, version: current.version };
  });
  await context.close();
});
after(async () => { await browser?.close(); });

describe("legacy offline queue upgrade", () => {
  it("retains the complete legacy payload", () => {
    assert.deepEqual(result.preservedPayload, { description: "legacy work", quantity: 7 });
  });
  it("does not make an unknown-owner legacy operation eligible for automatic replay", () => {
    assert.equal(result.pendingIds.includes("legacy-unknown"), false);
  });
});

it("recovers from an aborted upgrade without losing the old queue", async () => {
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto(origin, { waitUntil: "domcontentloaded" });
    const observed = await page.evaluate(async () => {
      const oldDb = await new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open("ipcas-offline", 2);
        request.onupgradeneeded = () => {
          const queue = request.result.createObjectStore("offline_queue", { keyPath: "queue_id" });
          queue.createIndex("status", "status");
          queue.createIndex("project_id", "project_id");
          queue.createIndex("entity_type", "entity_type");
          queue.createIndex("created_at", "created_at");
        };
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
      });
      await new Promise<void>((resolve, reject) => {
        const tx = oldDb.transaction("offline_queue", "readwrite");
        tx.objectStore("offline_queue").put({ queue_id: "recoverable", status: "pending", payload: { notes: "preserve this" } });
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });
      oldDb.close();
      const original = indexedDB.open.bind(indexedDB);
      let abortNext = true;
      indexedDB.open = ((name: string, version?: number) => {
        const request = original(name, version);
        if (abortNext && name === "ipcas-offline") {
          abortNext = false;
          request.addEventListener("upgradeneeded", () => request.transaction?.abort());
        }
        return request;
      }) as typeof indexedDB.open;
      const module = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
      let failureReported = false;
      try { await module.initDB(); } catch { failureReported = true; }
      indexedDB.open = original;
      const existing = await new Promise<IDBDatabase>((resolve, reject) => {
        const request = original("ipcas-offline", 2);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
      });
      const preservedAfterAbort = await new Promise<unknown>((resolve, reject) => {
        const request = existing.transaction("offline_queue").objectStore("offline_queue").get("recoverable");
        request.onsuccess = () => resolve(request.result?.payload);
        request.onerror = () => reject(request.error);
      });
      existing.close();
      let retried = false;
      let preserved: unknown = null;
      try {
        const recovered = await module.initDB();
        preserved = (await recovered.get("offline_queue", "recoverable"))?.payload;
        retried = true;
      } catch { /* the assertion below reports the failure */ }
      return { failureReported, retried, preserved, preservedAfterAbort };
    });
    assert.equal(observed.failureReported, true);
    assert.deepEqual(observed.preservedAfterAbort, { notes: "preserve this" });
    assert.equal(observed.retried, true, "the failed upgrade must not poison all later recovery attempts");
    assert.deepEqual(observed.preserved, { notes: "preserve this" });
  } finally {
    await context.close();
  }
});

it("retains and quarantines a legacy project activity without a provable unit or owner", async () => {
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto(origin, { waitUntil: "domcontentloaded" });
    const observed = await page.evaluate(async () => {
      const raw = {
        queue_id: "legacy-project-activity", project_id: "project-a",
        local_id: "legacy-report", entity_type: "daily_activity",
        method: "POST", endpoint: "/v1/projects/project-a/daily-reports/legacy-report/activities/",
        payload: { activity_description: "keep full local work", quantity: 7, notes: "حفظ شود" },
        created_at: "2026-01-01T00:00:00Z", status: "pending", server_id: null,
        retry_count: 0, error_message: null,
      };
      const old = await new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open("ipcas-offline", 2);
        request.onupgradeneeded = () => {
          const queue = request.result.createObjectStore("offline_queue", { keyPath: "queue_id" });
          for (const name of ["status", "project_id", "entity_type", "created_at"]) queue.createIndex(name, name);
        };
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
      });
      await new Promise<void>((resolve, reject) => {
        const tx = old.transaction("offline_queue", "readwrite");
        tx.objectStore("offline_queue").put(raw);
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });
      old.close();
      const module = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
      const db = await module.initDB();
      const retained = await db.get("offline_queue", raw.queue_id);
      const pending = await module.getPendingQueue();
      return { raw, retained, pendingIds: pending.map((item: { queue_id: string }) => item.queue_id) };
    });
    assert.deepEqual(observed.retained, observed.raw, "upgrade retains the original raw record");
    assert.equal(observed.pendingIds.includes(observed.raw.queue_id), false, "a project activity with no proven actor or unit cannot be replayed as a unit report");
  } finally { await context.close(); }
});

it("reports a failed local write and preserves a previously stored legacy record", async () => {
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto(origin, { waitUntil: "domcontentloaded" });
    const observed = await page.evaluate(async () => {
      const module = await import(/* @vite-ignore */ "/src/app/lib/offlineDB.ts");
      const db = await module.initDB();
      const previous = { queue_id: "prior", project_id: "project-a", entity_type: "daily_activity", method: "POST", endpoint: "/activities/", payload: { notes: "retain me" }, created_at: "2026-01-01", status: "pending", local_id: "legacy", server_id: null, retry_count: 0, error_message: null };
      await db.put("offline_queue", previous);
      const original = IDBDatabase.prototype.transaction;
      let injected = false;
      IDBDatabase.prototype.transaction = function (...args: Parameters<IDBDatabase["transaction"]>) {
        const tx = original.apply(this, args);
        if (!injected && args[0] === "offline_queue" && args[1] === "readwrite") {
          injected = true;
          queueMicrotask(() => tx.abort());
        }
        return tx;
      };
      let rejected = false;
      try { await module.addToQueue({ ...previous, queue_id: "failed-write", payload: { notes: "new input" } }); }
      catch { rejected = true; }
      finally { IDBDatabase.prototype.transaction = original; }
      return { injected, rejected, previous: await db.get("offline_queue", "prior"), failed: await db.get("offline_queue", "failed-write") };
    });
    assert.equal(observed.injected, true);
    assert.equal(observed.rejected, true, "a storage transaction failure must not be reported as success");
    assert.deepEqual(observed.previous?.payload, { notes: "retain me" });
    assert.equal(observed.failed, undefined, "an aborted write must not partially commit");
  } finally { await context.close(); }
});
