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

    const actorId = await page.evaluate(() => String(JSON.parse(localStorage.getItem("auth_user")!).id));
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
            activities: ["pending", "sending", "synced", "failed", "conflict"].map((status) => ({ client_id: `${status}-row`, activity_description: `${status} activity`, quantity: 1 })),
          },
          tombstones: {},
          field_errors: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
        for (const status of ["pending", "sending", "synced", "failed", "conflict"]) {
          await module.saveOperation({ operation_id: crypto.randomUUID(), local_report_id: "22222222-2222-4222-8222-222222222222",
            client_id: `${status}-row`, actor_id: actorId, project_id: projectId, unit: "electrical", operation_kind: "create", target_type: "activities",
            payload: {}, predecessor_ids: [], created_at: new Date().toISOString(), status: status === "sending" ? "syncing" : status });
        }
      },
      { actorId, projectId, date },
    );

    // Keep Vite reachable but emulate offline state so auto-sync does not
    // recover the deliberately seeded in-flight operation during this UI test.
    await page.addInitScript(() => Object.defineProperty(navigator, "onLine", { configurable: true, get: () => false }));
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

    const persianLabels: string[] = [];
    for (const status of STATUSES) {
      const sample = page.locator(`[data-testid="row-sync-status"][data-status="${status}"]`);
      await expect(sample.first()).toBeVisible();
      await expect(sample.first()).toHaveAttribute("aria-label", /.+/);
      persianLabels.push((await sample.first().getAttribute("aria-label"))!);
      await sample.first().focus();
      await expect(sample.first()).toBeFocused();
    }
    expect(new Set(persianLabels).size).toBe(STATUSES.length);

    await page.evaluate(() => {
      localStorage.setItem("i18nextLng", "en");
    });
    await page.reload();
    const english = await page.getByTestId("row-sync-status").first().getAttribute("aria-label");
    expect(english?.toLowerCase()).toContain("pending");
    const englishLabels: string[] = [];
    for (const status of STATUSES) {
      const badgeForStatus = page.locator(`[data-testid="row-sync-status"][data-status="${status}"]`).first();
      await expect(badgeForStatus).toBeVisible();
      englishLabels.push((await badgeForStatus.getAttribute("aria-label"))!);
    }
    expect(new Set(englishLabels).size).toBe(STATUSES.length);
    expect(englishLabels.every((value, index) => value !== persianLabels[index])).toBe(true);
  });
});
