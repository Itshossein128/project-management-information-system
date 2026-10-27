/**
 * Feature 037 — US5: a failed row keeps its field error and is not announced as success (T046).
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

test.describe("US5 — row validation retry (T046)", () => {
  test.setTimeout(120_000);

  test("shows the stable field error and does not toast success when nothing synced", async ({ page }) => {
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
      const clientId = crypto.randomUUID();
      await module.saveLocalSnapshot({
        local_report_id: localReportId,
        actor_id: actorId,
        project_id: projectId,
        unit: "electrical",
        report_date: date,
        status: "draft",
        base_header: {},
        base_rows: { activities: [] },
        overlay_header: { notes: "retry notes" },
        overlay_rows: {
          activities: [{ client_id: clientId, activity_description: "bad quantity", quantity: -1 }],
        },
        tombstones: {},
        field_errors: { [clientId]: { quantity: "quantity_must_be_positive" } },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    }, { actorId, projectId, date });

    await page.context().route("http://127.0.0.1:8000/**", (route) => route.abort());
    await page.reload();
    await expect(page.getByTestId("row-field-error")).toContainText("quantity: quantity_must_be_positive");
    await expect(page.getByText(/مورد همگام‌سازی شد/)).toHaveCount(0);
  });
});
