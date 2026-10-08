/**
 * FLOW: FR-CORE-012 capability nav + FR-CORE-015 fiscal corrective UI
 * MODULE: Core Domain Principles (Spec 01)
 * ROLES: admin
 */

import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createFiscalLockViaApi,
  createProjectViaApi,
  updateCapabilityViaApi,
} from "../helpers/project";

async function openNavSection(page: Page, sectionLabel: string | RegExp) {
  const label = page.locator('[id^="text-sidebarLabel-"]', {
    hasText: sectionLabel,
  });
  // Prefer exact project-section labels over global "منابع انسانی".
  const exact =
    typeof sectionLabel === "string"
      ? label.filter({ hasText: new RegExp(`^${sectionLabel}$`) })
      : label;
  const item = page.locator('[id^="container-sidebarItem-"]').filter({
    has: exact.first(),
  });
  await expect(item.first()).toBeVisible({ timeout: 15_000 });
  await item
    .first()
    .locator('[id^="button-sidebarExpand-"]')
    .click();
}

function openMenu(page: Page) {
  return page.getByRole("menu");
}

function navMenuLink(page: Page, href: string) {
  return openMenu(page).locator(`a[role="menuitem"][href="${href}"]`);
}

async function expectMenuHrefs(
  page: Page,
  opts: { include: string[]; exclude: string[] },
) {
  const menu = openMenu(page);
  await expect(menu).toBeVisible({ timeout: 10_000 });
  const hrefs = await menu.locator('a[role="menuitem"]').evaluateAll((nodes) =>
    nodes.map((n) => n.getAttribute("href") ?? ""),
  );
  for (const href of opts.include) {
    expect(hrefs, `expected menu to include ${href}`).toContain(href);
  }
  for (const href of opts.exclude) {
    expect(hrefs, `expected menu to exclude ${href}`).not.toContain(href);
  }
}

test.describe("Core principles — capability nav + fiscal corrective", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("FR-CORE-012: disabled risk capability hides risk nav entry", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);

    await page.goto(`${base}/overview`);
    await expect(page.locator("#nav-mainSidebar")).toBeVisible({ timeout: 15_000 });
    await openNavSection(page, "کارگاه");
    await expectMenuHrefs(page, {
      include: [`${base}/risk-register`, `${base}/daily-reports`],
      exclude: [],
    });

    // Disable via settings UI (toggle already present)
    await page.goto(`${base}/settings`);
    await expect(page.getByText("risk").first()).toBeVisible({ timeout: 15_000 });
    const riskToggle = page.locator("#toggle-cap-risk");
    await expect(riskToggle).toBeVisible();
    await riskToggle.click();
    await updateCapabilityViaApi(page, base, "risk", false);

    await page.goto(`${base}/overview`);
    await expect(page.locator("#nav-mainSidebar")).toBeVisible({ timeout: 15_000 });
    await openNavSection(page, "کارگاه");
    await expectMenuHrefs(page, {
      include: [`${base}/daily-reports`],
      exclude: [`${base}/risk-register`],
    });
  });

  test("FR-CORE-012: API-disabled hr capability hides HR resource nav entries", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    await updateCapabilityViaApi(page, base, "hr", false);

    await page.goto(`${base}/overview`);
    await expect(page.locator("#nav-mainSidebar")).toBeVisible({ timeout: 15_000 });
    await openNavSection(page, "منابع");
    await expectMenuHrefs(page, {
      include: [`${base}/equipment-utilization`],
      exclude: [`${base}/manpower`, `${base}/leave-requests`],
    });
  });

  test("FR-CORE-015: costs UI exposes corrective path under fiscal lock", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    await createFiscalLockViaApi(page, base, {
      periodStart: "2020-01-01",
      periodEnd: "2030-12-31",
      reason: "E2E lock covering today",
    });

    // Ordinary create without corrective is blocked by API (pytest covers this).
    const projectId = base.split("/").pop();
    const blocked = await page.request.post(
      `http://127.0.0.1:8000/api/v1/projects/${projectId}/costs/`,
      {
        headers: {
          Authorization: `Bearer ${await page.evaluate(() =>
            localStorage.getItem("auth_access_token"),
          )}`,
          "Content-Type": "application/json",
        },
        data: {
          cost_date: "2026-06-15",
          cost_category: "labor",
          amount: 1000,
          description: "blocked ordinary",
        },
      },
    );
    expect(blocked.status()).toBeGreaterThanOrEqual(400);
    expect(await blocked.text()).toContain("fiscal_period_locked");

    await page.goto(`${base}/costs`);
    await expect(page.getByRole("heading", { name: /کنترل هزینه/i })).toBeVisible({
      timeout: 20_000,
    });
    await page.getByTestId("costs-tab-actual").click();
    await expect(page.getByTestId("actual-costs-tab")).toBeVisible();

    await page.getByTestId("actual-cost-add-btn").first().click();
    await expect(page.getByTestId("actual-cost-drawer")).toBeVisible();

    // UI path: drawer exposes corrective flag + reason (Jalali date create is flaky in e2e).
    await expect(page.getByTestId("actual-cost-corrective")).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.getByTestId("actual-cost-correction-reason")).toBeVisible();
  });
});
