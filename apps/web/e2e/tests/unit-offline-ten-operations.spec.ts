/**
 * Feature 037 — US3: ten independent offline operations sync on reconnect (T034).
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createActivityViaApi, createProjectViaApi, createRootWbs } from "../helpers/project";

const API_BASE = "http://127.0.0.1:8000/api";

test.describe("US3 — ten operations (T034)", () => {
  test.setTimeout(180_000);

  test("reconnect sends ten activity, labor, and material operations once", async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop() ?? "";
    const wbsId = await createRootWbs(page, projectBase);
    const activityId = await createActivityViaApi(page, projectBase, {
      code: "A-10",
      name: "Ten ops",
      wbsId,
    });
    const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
    const stakeholder = await page.request.post(`${API_BASE}/v1/projects/${projectId}/stakeholders/`, {
      headers: { Authorization: `Bearer ${access}`, "Content-Type": "application/json" },
      data: { name: "Ten Ops Crew", role: "contractor" },
    });
    expect(stakeholder.ok()).toBeTruthy();
    const contractorId = ((await stakeholder.json()) as { id: string }).id;
    const date = "2026-10-27";
    await page.goto(`${projectBase}/buildings?date=${date}`);
    await expect(page.locator("body")).toBeVisible();

    // Load the test helper while Vite is reachable before disconnecting.
    await page.evaluate(async () => { await import("/src/app/lib/offlineDB.ts"); });

    // Queue the operations while disconnected; reconnect must trigger sync
    // without reloading the page or requiring a manual sync action.
    await page.context().setOffline(true);

    const actorId = await page.evaluate(() => {
      const direct = localStorage.getItem("auth_user_id");
      if (direct) return direct;
      const raw = localStorage.getItem("auth_user");
      if (!raw) return "";
      const parsed = JSON.parse(raw) as { id?: string | number };
      return parsed.id == null ? "" : String(parsed.id);
    });
    await page.evaluate(
      async ({ actorId, projectId, date, activityId, contractorId }) => {
        const module = await import("/src/app/lib/offlineDB.ts");
        const localReportId = crypto.randomUUID();
        const headerId = crypto.randomUUID();
        const now = new Date().toISOString();
        await module.saveLocalSnapshot({
          local_report_id: localReportId,
          actor_id: actorId,
          project_id: projectId,
          unit: "buildings",
          report_date: date,
          status: "draft",
          base_header: {},
          base_rows: {},
          overlay_header: { form_code: "TEN" },
          overlay_rows: {},
          tombstones: {},
          field_errors: {},
          created_at: now,
          updated_at: now,
        });
        const header = {
          operation_id: headerId,
          local_report_id: localReportId,
          actor_id: actorId,
          project_id: projectId,
          unit: "buildings",
          operation_kind: "create_report",
          target_type: "header",
          payload: { form_code: "TEN" },
          predecessor_ids: [],
          created_at: now,
          status: "pending",
        };
        await module.saveOperation(header);
        const rows = [
          ["activities", { row_number: 1, shift: "shift_1", activity_ref: activityId, activity_description: "activity-1", contractor_ref: contractorId, crew_name: "A" }],
          ["activities", { row_number: 2, shift: "shift_1", activity_ref: activityId, activity_description: "activity-2", contractor_ref: contractorId, crew_name: "A" }],
          ["activities", { row_number: 3, shift: "shift_1", activity_ref: activityId, activity_description: "activity-3", contractor_ref: contractorId, crew_name: "A" }],
          ["labor", { labor_category: "direct", job_title: "Mason", present_count: 1 }],
          ["labor", { labor_category: "direct", job_title: "Mason", present_count: 2 }],
          ["labor", { labor_category: "direct", job_title: "Mason", present_count: 3 }],
          ["materials", { transaction_type: "consumption", material_description: "material-1", quantity: "1", unit: "kg", consumption_location: "Yard" }],
          ["materials", { transaction_type: "consumption", material_description: "material-2", quantity: "2", unit: "kg", consumption_location: "Yard" }],
          ["materials", { transaction_type: "consumption", material_description: "material-3", quantity: "3", unit: "kg", consumption_location: "Yard" }],
          ["materials", { transaction_type: "consumption", material_description: "material-4", quantity: "4", unit: "kg", consumption_location: "Yard" }],
        ] as const;
        for (const [targetType, payload] of rows) {
          await module.saveOperation({
            operation_id: crypto.randomUUID(),
            local_report_id: localReportId,
            client_id: crypto.randomUUID(),
            actor_id: actorId,
            project_id: projectId,
            unit: "buildings",
            operation_kind: "create",
            target_type: targetType,
            payload,
            predecessor_ids: [headerId],
            created_at: new Date().toISOString(),
            status: "pending",
          });
        }
      },
      { actorId, projectId, date, activityId, contractorId },
    );

    await page.context().setOffline(false);
    await expect.poll(async () => {
      return page.evaluate(async () => {
        const module = await import("/src/app/lib/offlineDB.ts");
        const db = await module.initDB();
        const ops = await db.getAll("offline_operations");
        return ops.filter((item: { status: string }) => item.status === "synced").length;
      });
    }, { timeout: 20_000 }).toBe(11); // Ten row operations and their report prerequisite.

    const headers = { Authorization: `Bearer ${access}` };
    const current = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/current/?date=${date}`,
      { headers },
    );
    expect(current.ok()).toBeTruthy();
    const report = (await current.json()) as { id: string };
    const activities = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${report.id}/activities/`,
      { headers },
    );
    const labor = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${report.id}/labor/`,
      { headers },
    );
    const materials = await page.request.get(
      `${API_BASE}/v1/projects/${projectId}/units/buildings/daily-reports/${report.id}/materials/`,
      { headers },
    );
    const activityRows = (await activities.json()) as Array<{ id: string; activity_description: string }>;
    const laborRows = (await labor.json()) as Array<{ id: string; present_count: number }>;
    const materialRows = (await materials.json()) as Array<{ id: string; material_description: string }>;
    expect(activityRows.map((row) => row.activity_description).sort()).toEqual(["activity-1", "activity-2", "activity-3"]);
    expect(laborRows.map((row) => row.present_count).sort()).toEqual([1, 2, 3]);
    expect(materialRows.map((row) => row.material_description).sort()).toEqual(["material-1", "material-2", "material-3", "material-4"]);
    const operations = await page.evaluate(async () => {
      const db = await (await import("/src/app/lib/offlineDB.ts")).initDB();
      return db.getAll("offline_operations");
    });
    expect(new Set(operations.map((op) => op.operation_id)).size).toBe(11);
    const serverIds = new Set([...activityRows, ...laborRows, ...materialRows].map((row) => row.id));
    const rowOperations = operations.filter((op) => op.operation_kind === "create");
    expect(rowOperations).toHaveLength(10);
    expect(new Set(rowOperations.map((op) => op.client_id)).size).toBe(10);
    for (const op of rowOperations) {
      const receipt = op.result as { operationId: string; clientId: string; serverId: string };
      expect(receipt.operationId).toBe(op.operation_id);
      expect(receipt.clientId).toBe(op.client_id);
      expect(serverIds.has(receipt.serverId)).toBe(true);
      serverIds.delete(receipt.serverId);
    }
    expect(serverIds.size).toBe(0);
  });
});
