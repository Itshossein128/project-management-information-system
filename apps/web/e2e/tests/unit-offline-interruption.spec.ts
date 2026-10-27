/**
 * Feature 037 — US8: an abandoned syncing operation is recoverable (T062).
 */
import { expect, test, chromium } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("US8 — interrupted sync (T062)", () => {
  test.setTimeout(180_000);

  test("reopens the same profile and does not leave the operation syncing forever", async () => {
    const profileDir = mkdtempSync(join(tmpdir(), "velora-us8-"));
    const context = await chromium.launchPersistentContext(profileDir, { baseURL: "http://127.0.0.1:5173" });
    const page = context.pages()[0] ?? (await context.newPage());
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop() ?? "";
    const date = "2026-10-27";
    await page.goto(`${projectBase}/electrical?date=${date}`);
    const actorId = await page.evaluate(() => {
      const raw = localStorage.getItem("auth_user");
      const parsed = raw ? (JSON.parse(raw) as { id?: string | number }) : {};
      return parsed.id == null ? "" : String(parsed.id);
    });
    await page.evaluate(async ({ actorId, projectId, date }) => {
      const module = await import("/src/app/lib/offlineDB.ts");
      const localReportId = crypto.randomUUID();
      await module.saveLocalSnapshot({
        local_report_id: localReportId,
        actor_id: actorId,
        project_id: projectId,
        unit: "electrical",
        report_date: date,
        status: "draft",
        base_header: {},
        base_rows: {},
        overlay_header: { notes: "recover me" },
        overlay_rows: {},
        tombstones: {},
        field_errors: {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      await module.saveOperation({
        operation_id: crypto.randomUUID(),
        local_report_id: localReportId,
        actor_id: actorId,
        project_id: projectId,
        unit: "electrical",
        operation_kind: "create_report",
        target_type: "header",
        payload: { form_code: "RECOVER" },
        predecessor_ids: [],
        created_at: new Date().toISOString(),
        status: "syncing",
      });
    }, { actorId, projectId, date });
    await context.close();

    const reopened = await chromium.launchPersistentContext(profileDir, { baseURL: "http://127.0.0.1:5173" });
    const page2 = reopened.pages()[0] ?? (await reopened.newPage());
    await page2.goto(`${projectBase}/electrical?date=${date}`);
    await expect.poll(async () => page2.evaluate(async () => {
      const module = await import("/src/app/lib/offlineDB.ts");
      const db = await module.initDB();
      const ops = await db.getAll("offline_operations");
      return ops.filter((item: { status: string }) => item.status === "syncing").length;
    })).toBe(0);
    const notes = await page2.evaluate(async () => {
      const module = await import("/src/app/lib/offlineDB.ts");
      const db = await module.initDB();
      const snapshots = await db.getAll("local_snapshots");
      return snapshots[0]?.overlay_header?.notes ?? "";
    });
    expect(notes).toBe("recover me");
    await reopened.close();
  });
});
