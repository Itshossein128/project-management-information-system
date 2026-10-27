/**
 * Feature 037 — US8: an unknown legacy queue item is kept and not replayed (T064).
 */
import { expect, test } from "@playwright/test";

test.describe("US8 — legacy upgrade (T064)", () => {
  test("keeps an ambiguous legacy payload out of the automatic queue", async ({ page }) => {
    await page.goto("/");
    const observed = await page.evaluate(async () => {
      const opened = await new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open("ipcas-offline-legacy-probe", 1);
        request.onupgradeneeded = () => {
          request.result.createObjectStore("offline_queue", { keyPath: "queue_id" });
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
      await new Promise<void>((resolve, reject) => {
        const tx = opened.transaction("offline_queue", "readwrite");
        tx.objectStore("offline_queue").put({
          queue_id: "ambiguous-legacy",
          payload: { notes: "do not guess" },
          status: "pending",
        });
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });
      opened.close();
      const module = await import("/src/app/lib/offlineDB.ts");
      const backup = {
        local_snapshots: [],
        offline_operations: [],
        legacy_quarantine: [{
          queue_id: "ambiguous-legacy",
          raw_record: { notes: "do not guess" },
          quarantine_reason: "unknown_owner",
          quarantined_at: new Date().toISOString(),
          project_id: "",
        }],
      };
      await module.restoreOfflineBackup(backup);
      const restored = await module.exportOfflineBackup();
      const pending = await module.getPendingOperations("someone-else");
      return {
        retained: restored.legacy_quarantine[0]?.raw_record,
        pending: pending.length,
      };
    });
    expect(observed.retained).toEqual({ notes: "do not guess" });
    expect(observed.pending).toBe(0);
  });
});
