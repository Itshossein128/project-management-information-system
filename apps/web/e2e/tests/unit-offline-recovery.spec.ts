/**
 * Feature 037 — US2: full local recovery after refresh and profile reopen (T025).
 */
import { expect, test, chromium } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("US2 — local draft recovery (T025)", () => {
  test.setTimeout(180_000);

  test("refresh and persistent-profile reopen restore header, rows, and tombstones offline", async () => {
    const profileDir = mkdtempSync(join(tmpdir(), "velora-us2-"));
    const context = await chromium.launchPersistentContext(profileDir, {
      baseURL: "http://127.0.0.1:5173",
    });
    const page = context.pages()[0] ?? (await context.newPage());
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    const date = "2026-10-27";
    const unitPage = `${projectBase}/electrical?date=${date}`;
    await page.goto(unitPage);
    await expect(page.locator("body")).toBeVisible();

    const actorId = await page.evaluate(() => String(JSON.parse(localStorage.getItem("auth_user")!).id));
    const projectId = projectBase.split("/").filter(Boolean).at(-1) ?? "";
    const localReportId = "11111111-1111-4111-8111-111111111111";

    await page.evaluate(
      async ({ actorId, projectId, date, localReportId }) => {
        const module = await import("/src/app/lib/offlineDB.ts");
        await module.saveLocalSnapshot({
          local_report_id: localReportId,
          actor_id: actorId,
          project_id: projectId,
          unit: "electrical",
          report_date: date,
          status: "draft",
          server_report_id: null,
          server_version: 1,
          base_revision: null,
          base_header: { notes: "server notes", form_code: "EL-1" },
          base_rows: {
            activities: [
              { id: "row-keep", activity_description: "kept server row", quantity: 1 },
              { id: "row-gone", activity_description: "deleted locally", quantity: 2 },
            ],
          },
          overlay_header: { notes: "recovered local notes" },
          overlay_rows: {
            activities: [
              { id: "row-keep", client_id: "row-keep", activity_description: "edited locally", quantity: 9 },
              { client_id: "row-new", activity_description: "created locally", quantity: 3 },
            ],
          },
          tombstones: { activities: ["row-gone"] },
          field_errors: { "row-new": { quantity: "invalid_quantity" } },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      },
      { actorId, projectId, date, localReportId },
    );

    // Dev Vite cannot serve the module graph with Chrome offline mode. Block the API
    // so refresh and profile reopen still exercise local recovery against a dead server.
    await context.route("http://127.0.0.1:8000/**", (route) => route.abort());
    await page.reload();
    await expect(page.getByTestId("unit-report-general-notes")).toHaveValue("recovered local notes");
    await expect(page.getByTestId("local-draft-list")).toBeVisible();
    await expect(page.getByRole("cell", { name: "edited locally" })).toBeVisible();
    await expect(page.getByRole("cell", { name: "created locally" })).toBeVisible();
    await expect(page.getByRole("cell", { name: "deleted locally" })).toHaveCount(0);
    await context.close();

    const reopenedContext = await chromium.launchPersistentContext(profileDir, {
      baseURL: "http://127.0.0.1:5173",
    });
    const reopened = reopenedContext.pages()[0] ?? (await reopenedContext.newPage());
    await reopenedContext.route("http://127.0.0.1:8000/**", (route) => route.abort());
    await reopened.goto(unitPage);
    await expect(reopened.getByTestId("unit-report-general-notes")).toHaveValue("recovered local notes");
    await expect(reopened.getByRole("cell", { name: "created locally" })).toBeVisible();
    await reopenedContext.close();
  });
});
