/**
 * Feature 037 — US7: conflict comparison asks before discarding local rows (T055).
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("US7 — conflict comparison (T055)", () => {
  test.setTimeout(120_000);

  test("shows section rows and requires confirmation before choosing a side", async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    const projectId = projectBase.split("/").pop() ?? "";
    await page.evaluate(async (projectId) => {
      const module = await import("/src/app/lib/offlineDB.ts");
      await module.addConflict({
        conflict_id: "conflict-us7",
        queue_id: "queue-us7",
        project_id: projectId,
        entity_type: "daily_report",
        local_payload: {
          notes: "local notes",
          activities: [{ activity_description: "local activity" }],
          labor: [{ job_title: "local labor" }],
          materials: [{ material_description: "local material" }],
        },
        server_payload: {
          notes: "server notes",
          activities: [{ activity_description: "server activity" }],
          labor: [{ job_title: "server labor" }],
          materials: [{ material_description: "server material" }],
        },
        conflict_fields: ["notes"],
        conflict_reason: "version mismatch",
        status: "unresolved",
        created_at: new Date().toISOString(),
      });
    }, projectId);

    await page.goto(`${projectBase}/sync-conflicts`);
    await page.getByTestId("conflict-option-merge").check();
    await page.getByTestId("conflict-apply-btn").click();
    await expect(page.getByTestId("conflict-section-activities")).toContainText("local activity");
    await expect(page.getByTestId("conflict-section-activities")).toContainText("server activity");
    await expect(page.getByTestId("conflict-section-labor")).toContainText("local labor");
    await expect(page.getByTestId("conflict-section-materials")).toContainText("server material");
    await expect(page.getByTestId("conflict-use-server")).toBeDisabled();
    await expect(page.getByTestId("conflict-keep-mine")).toBeDisabled();
    await page.getByTestId("conflict-scope-confirm").check();
    await expect(page.getByTestId("conflict-use-server")).toBeEnabled();
    await expect(page.getByTestId("conflict-keep-mine")).toBeEnabled();
  });
});
