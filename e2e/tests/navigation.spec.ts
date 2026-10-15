import { expect, test } from "@playwright/test";

const projectId = "11111111-1111-4111-8111-111111111111";
const base = `/projects/${projectId}`;

import { session, visit } from "../helpers/navigation";

test.describe("Workspace navigation", () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name === "pwa-offline", "Requires the dev server");
  });

  test("keeps the global sidebar identical while moving through project and workspace pages", async ({ page, isMobile }) => {
    await session(page);
    await visit(page, "/projects");
    const nav = page.locator("#nav-mainSidebar");
    const openGlobal = async () => {
      if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    };
    const snapshot = async () => {
      await openGlobal();
      if (isMobile) await expect.poll(() => page.getByRole("dialog", { name: "Main", exact: true }).evaluate((node) => node.getAnimations().every((animation) => animation.playState === "finished"))).toBe(true);
      const result = await nav.locator("a, button, h2").evaluateAll((nodes) => nodes.map((node) => ({
        text: node.textContent?.trim(), href: node.getAttribute("href"),
        x: Math.round(node.getBoundingClientRect().x), y: Math.round(node.getBoundingClientRect().y),
      })));
      if (isMobile) {
        await page.keyboard.press("Escape");
        await expect(nav).not.toBeVisible();
      }
      return result;
    };
    const initial = await snapshot();
    await page.getByRole("main").last().getByRole("link", { name: "Create project", exact: true }).first().click();
    await expect(page).toHaveURL(/\/projects\/new$/);
    await expect(page.getByRole("heading", { name: "Create new project", exact: true })).toBeVisible();
    expect(await snapshot()).toEqual(initial);
    await visit(page, `${base}/settings/members`);
    expect(await snapshot()).toEqual(initial);
    const tools = page.locator("#nav-projectNavigation");
    const labels = await tools.getByRole("button").allTextContents();
    await tools.getByRole("button", { name: "Overview", exact: true }).click();
    await page.getByRole("dialog", { name: "Overview", exact: true }).getByRole("link", { name: "Standard reports", exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`${base}/standard-reports$`));
    await expect(tools.getByRole("button")).toHaveText(labels);
    await expect(tools.locator('[aria-current="location"]')).toHaveText("Overview");
    expect(await snapshot()).toEqual(initial);
    await openGlobal();
    await nav.getByRole("link", { name: "Portfolio dashboard", exact: true }).click();
    await expect(page).toHaveURL(/\/portfolio\/dashboard$/);
    expect(await snapshot()).toEqual(initial);
    await openGlobal();
    await nav.getByRole("link", { name: "Projects", exact: true }).click();
    await expect(page).toHaveURL(/\/projects$/);
    expect(await snapshot()).toEqual(initial);
  });

  test("keeps project sections stable while capability data loads", async ({ page }) => {
    await session(page);
    let release!: () => void;
    const ready = new Promise<void>((resolve) => { release = resolve; });
    await page.route(`**/api/v1/projects/${projectId}/capabilities/`, async (route) => {
      await ready;
      await route.fulfill({ json: [{ capability_key: "risk", enabled: false, mode: "disabled" }] });
    });
    try {
      await visit(page, `${base}/settings/members`);
      const tools = page.locator("#nav-projectNavigation");
      const labels = await tools.getByRole("button").allTextContents();
      await tools.getByRole("button", { name: "Field", exact: true }).click();
      const popup = page.getByRole("dialog", { name: "Field", exact: true });
      await expect(popup.getByRole("status")).toHaveText("Loading...");
      await expect(popup.getByRole("link")).toHaveCount(0);
      release();
      await expect(popup.getByRole("link", { name: "Daily Reports", exact: true })).toBeVisible();
      await expect(popup.locator(`a[href="${base}/risk-register"]`)).toHaveCount(0);
      await expect(tools.getByRole("button")).toHaveText(labels);
    } finally { release(); }
  });

  test("groups daily work before administration and keeps portfolio accessible", async ({ page, isMobile }) => {
    await session(page);
    await visit(page, "/projects");
    if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    const nav = page.locator("#nav-mainSidebar");
    await expect(nav.getByRole("heading")).toHaveText(["Workspace", "Administration"]);
    await expect(nav.getByRole("link")).toHaveText([
      "Projects", "Portfolio dashboard", "Portfolio liquidity", "Human resources",
      "Organization references", "Templates", "Roles & permissions",
    ]);
    await nav.getByRole("link", { name: "Portfolio dashboard", exact: true }).click();
    await expect(page).toHaveURL(/\/portfolio\/dashboard$/);
    if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    await expect(nav.locator('[aria-current="page"]')).toHaveText("Portfolio dashboard");
  });

  test("hides role-restricted administration and HR for visitors", async ({ page, isMobile }) => {
    await session(page, ["visitor"]);
    await visit(page, "/projects");
    if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    const nav = page.locator("#nav-mainSidebar");
    await expect(nav.getByRole("link")).toHaveText(["Projects", "Portfolio dashboard", "Portfolio liquidity"]);
    await expect(nav.getByRole("heading", { name: "Administration" })).toHaveCount(0);
  });

  test("opens sections with keyboard and selects only the most specific route", async ({ page, isMobile }) => {
    await session(page);
    await visit(page, `${base}/settings/members`);
    const nav = page.locator("#nav-projectNavigation");
    await expect(nav.getByRole("button")).toHaveText(["Overview", "Planning", "Field", "Commercial", "Resources", "Departments", "Settings"]);
    await nav.getByRole("button", { name: "Settings", exact: true }).click();
    const settings = page.getByRole("dialog", { name: "Settings", exact: true });
    await expect(settings.locator('[aria-current="page"]')).toHaveText("Members");
    await settings.getByRole("link", { name: "Members", exact: true }).press("Escape");
    const field = nav.getByRole("button", { name: "Field", exact: true });
    await field.press("Enter");
    await expect(field).toHaveAttribute("aria-expanded", "true");
    const fieldLinks = page.getByRole("dialog", { name: "Field", exact: true });
    await expect(fieldLinks.getByRole("link", { name: "Daily Reports", exact: true })).toBeVisible();
    await expect(fieldLinks.locator(`a[href="${base}/risk-register"]`)).toHaveCount(0);
    await expect(fieldLinks.locator(`a[href="${base}/quality-hse"]`)).toHaveCount(0);
    await field.press("Space");
    await expect(field).toHaveAttribute("aria-expanded", "false");
    await nav.getByRole("button", { name: "Resources", exact: true }).click();
    const resources = page.getByRole("dialog", { name: "Resources", exact: true });
    await expect(resources.locator(`a[href="${base}/manpower"]`)).toHaveCount(0);
    await expect(resources.locator(`a[href="${base}/equipment-utilization"]`)).toBeVisible();
  });

  test("places the desktop sidebar at the language's leading edge", async ({ page, isMobile }) => {
    test.skip(isMobile, "Desktop layout");
    for (const language of ["fa", "en"]) {
      await session(page, ["admin"], language);
      await visit(page, "/projects", language);
      await expect(page.locator("html")).toHaveAttribute("dir", language === "fa" ? "rtl" : "ltr");
      const sidebar = await page.locator("#container-mainSidebar").boundingBox();
      const content = await page.locator("#container-appShellMain").boundingBox();
      expect(sidebar).not.toBeNull();
      expect(content).not.toBeNull();
      if (language === "fa") expect(content!.x + content!.width).toBeLessThanOrEqual(sidebar!.x + 1);
      else expect(content!.x).toBeGreaterThanOrEqual(sidebar!.x + sidebar!.width - 1);
    }
  });

  test("mobile navigation traps focus, closes with Escape and restores focus", async ({ page, isMobile }) => {
    test.skip(!isMobile, "Mobile layout");
    await session(page);
    await visit(page, "/projects");
    await expect(page.locator("#nav-mainSidebar")).not.toBeVisible();
    const trigger = page.getByRole("button", { name: "Open navigation menu", exact: true });
    await trigger.click();
    const dialog = page.getByRole("dialog", { name: "Main" });
    await expect(dialog).toBeVisible();
    for (let i = 0; i < 15; i++) {
      await page.keyboard.press("Tab");
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true);
    }
    await page.keyboard.press("Escape");
    await expect(dialog).not.toBeVisible();
    await expect(trigger).toBeFocused();
  });
});
