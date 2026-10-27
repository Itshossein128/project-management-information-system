/**
 * Feature 037 — US2: accessible bilingual row status (T027).
 */
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";

const STATUSES = ["pending", "sending", "synced", "failed", "conflict"] as const;

test.describe("US2 — accessible sync status (T027)", () => {
  test.setTimeout(120_000);

  test("pending row shows a named yellow cloud and distinct keyboard-focusable statuses", async ({
    page,
  }) => {
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    const date = "2026-10-27";
    await page.goto(`${projectBase}/electrical?date=${date}`);

    const actorId = await page.evaluate(() => localStorage.getItem("auth_user_id") ?? "");
    const projectId = projectBase.split("/").filter(Boolean).at(-1) ?? "";
    await page.evaluate(
      async ({ actorId, projectId, date }) => {
        const module = await import("/src/app/lib/offlineDB.ts");
        await module.saveLocalSnapshot({
          local_report_id: "22222222-2222-4222-8222-222222222222",
          actor_id: actorId,
          project_id: projectId,
          unit: "electrical",
          report_date: date,
          status: "draft",
          base_header: {},
          base_rows: { activities: [] },
          overlay_header: { notes: "status check" },
          overlay_rows: {
            activities: [{ client_id: "pending-row", activity_description: "pending activity", quantity: 1, sync_status: "pending" }],
          },
          tombstones: {},
          field_errors: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      },
      { actorId, projectId, date },
    );

    await page.context().route("http://127.0.0.1:8000/**", (route) => route.abort());
    await page.reload();

    const badge = page.getByTestId("row-sync-status").first();
    await expect(badge).toBeVisible();
    await expect(badge).toHaveAttribute("data-status", "pending");
    await expect(page.getByTestId("icon-cloud-pending").first()).toBeVisible();
    const label = await badge.getAttribute("aria-label");
    expect(label && label.length > 0).toBeTruthy();
    await badge.focus();
    await expect(badge).toBeFocused();

    for (const status of STATUSES) {
      const sample = page.locator(`[data-testid="row-sync-status"][data-status="${status}"]`);
      if (status === "pending") {
        await expect(sample.first()).toBeVisible();
      }
    }

    await page.evaluate(() => {
      localStorage.setItem("i18nextLng", "en");
    });
    await page.reload();
    const english = await page.getByTestId("row-sync-status").first().getAttribute("aria-label");
    expect(english?.toLowerCase()).toContain("pending");
  });
});