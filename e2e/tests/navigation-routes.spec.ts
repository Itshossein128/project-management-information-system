import { expect, test, type Page } from "@playwright/test";
import { session, visit } from "../helpers/navigation";
import { registeredRoutes } from "../helpers/registered-routes";

const id = "11111111-1111-4111-8111-111111111111";
const base = `/projects/${id}`;
const routes = registeredRoutes();
const resolvePath = (path: string) => path.replace(/:(projectId|businessId)/g, id);
// These screens need an entity or an action, rather than a top-level menu link.
const workflowRoutes = new Set([
  "BUSINESS_CREATE", "USERS", "HR_JOB_POSITIONS", "BUSINESS_SETUP_SCHEMA", "BUSINESS_TABLE", "BUSINESS_JOB_POSITIONS", "BUSINESS_USERS",
  "PROJECT_PROCUREMENT_NEW", "PROJECT_PROCUREMENT_OFFICER", "PROJECT_PROCUREMENT_INVENTORY", "PROJECT_PROCUREMENT_REPORTS", "PROJECT_PROCUREMENT_BLOCKS", "PROJECT_PROCUREMENT_TRANSFERS", "PROJECT_PROCUREMENT_DETAIL",
  "PROJECT_CONTRACT_NEW", "PROJECT_CONTRACT_DETAIL", "PROJECT_IPC_DETAIL", "PROJECT_SUBCONTRACTOR_DETAIL",
  "PROJECT_DAILY_REPORT_NEW", "PROJECT_DAILY_REPORT_EDIT", "PROJECT_DAILY_REPORT_VIEW",
]);
const authAndAliases = new Set(["INDEX", "HOME", "LOGIN", "REGISTER", "FORGOT_PASSWORD", "RESET_PASSWORD"]);
const menuRoutes = routes.filter((route) => !workflowRoutes.has(route.key) && !authAndAliases.has(route.key));

async function fullSession(page: Page) {
  await session(page, ["admin", "business-setup"]);
  await page.route(/^https?:\/\/[^/]+\/api\/v1\//, (route) => {
    const path = new URL(route.request().url()).pathname;
    const project = { project_id: id, id, project_name: "Navigation project", name: "Navigation project", project_code: "NAV", slug: "nav", status: "draft", currency: "IRR", start_date: null, planned_finish_date: null, contract_amount: null };
    const row = { id: "record-1", contract_number: "NAV-1", contract_type: "main", counterparty: "Test supplier", effective_amount: 100, status: "draft", company_name: "Test subcontractor", latest_score: null, financial_summary: { outstanding: 0 }, warning_count: 0, risk_flag: false, risk_reasons: [], ipc_number: 1, gross_amount: 0, report_id: "record-1", report_date: "2026-10-15", site_status: "active", weather_condition: "sunny", activity_count: 0, total_headcount: 0, prepared_by_name: "Tester", requisition_number: "NAV-1", scope: "workshop", block: null };
    const list = (results: unknown[]) => ({ results, count: results.length, next: null, previous: null });
    const permissions = Object.fromEntries(["view_project", "edit_project", "view_dashboard", "view_reports", "edit_reports", "view_procurement", "view_contracts", "edit_contracts", "view_ipcs"].map((key) => [key, true]));
    let json: unknown = list([]);
    if (path.endsWith("/permissions/")) json = { effective: permissions, permissions: [] };
    else if (path === "/api/v1/projects/") json = list([project]);
    else if (path === `/api/v1/projects/${id}/`) json = project;
    else if (/\/(capabilities|roles|members|project-templates|job-titles)\/$/.test(path)) json = [];
    else if (path.endsWith("/portfolio/summary/")) json = { totals: { project_count: 1 }, totals_by_currency: {} };
    else if (path.endsWith("/portfolio/dashboard/")) json = { projects: [] };
    else if (path.endsWith("/tables/")) json = list([{ id: 1, name: "Sample table", slug: "sample-table", ordering: 1 }]);
    else if (path.includes("/tables/by_slug/")) json = { id: 1, name: "Sample table", slug: "sample-table", fields: [] };
    else if (/\/(contracts|ipcs|subcontractors|requisitions|daily-reports)\/$/.test(path)) json = list([row]);
    return route.fulfill({ json });
  });
}

test.describe("Registered route reachability", () => {
  test.beforeEach(({}, info) => { test.skip(info.project.name === "pwa-offline", "Requires dev server"); });

  test("every registered menu destination is exposed in the UI", async ({ page, isMobile }) => {
    await fullSession(page);
    await visit(page, `${base}/settings/members`);
    const hrefs = new Set<string>();
    if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    for (const href of await page.locator("#nav-mainSidebar a").evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")!))) hrefs.add(href);
    if (isMobile) {
      await page.keyboard.press("Escape");
      await expect(page.getByRole("dialog", { name: "Main", exact: true })).not.toBeVisible();
    }
    const tools = page.locator("#nav-projectNavigation");
    await expect(tools.getByRole("button").first()).toBeVisible();
    for (const button of await tools.getByRole("button").all()) {
      await button.click();
      const popup = page.getByRole("dialog");
      await expect(popup.getByRole("link").first()).toBeVisible();
      for (const href of await popup.getByRole("link").evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")!))) hrefs.add(href);
      await popup.getByRole("link").first().press("Escape");
    }
    const missing = menuRoutes.filter((route) => !hrefs.has(resolvePath(route.path)));
    expect(missing, "Registered pages without UI entry points").toEqual([]);
    for (const href of hrefs) expect(routes.some((route) => resolvePath(route.path) === href), `Unregistered menu link: ${href}`).toBe(true);
    expect(new Set([...menuRoutes.map((route) => route.key), ...workflowRoutes, ...authAndAliases])).toEqual(new Set(routes.map((route) => route.key)));
    await test.info().attach("registered-route-coverage", {
      body: JSON.stringify({ registered: routes.length, menu: menuRoutes.length, workflow: workflowRoutes.size, authAndAliases: authAndAliases.size, routes: routes.map((route) => ({ ...route, entry: workflowRoutes.has(route.key) ? "parent-screen workflow" : authAndAliases.has(route.key) ? "authentication or redirect" : "menu link" })) }, null, 2),
      contentType: "application/json",
    });
  });

  test("every menu destination can be opened by clicking its rendered link", async ({ page, isMobile }) => {
    test.skip(isMobile, "All destinations also checked for visibility on mobile");
    test.setTimeout(180_000);
    await fullSession(page);
    for (const route of menuRoutes) {
      await test.step(route.key, async () => {
        await visit(page, `${base}/settings/members`);
        const target = resolvePath(route.path);
        let link = page.locator(`#nav-mainSidebar a[href="${target}"]`);
        if (await link.count() === 0) {
          const tools = page.locator("#nav-projectNavigation");
          await expect(tools.getByRole("button").first()).toBeVisible();
          let found = false;
          for (const button of await tools.getByRole("button").all()) {
            await button.click();
            const popup = page.getByRole("dialog");
            await expect(popup.getByRole("link").first()).toBeVisible();
            link = popup.locator(`a[href="${target}"]`);
            if (await link.count()) { found = true; break; }
            await popup.getByRole("link").first().press("Escape");
          }
          expect(found, `No clickable menu entry for ${route.key}`).toBe(true);
        }
        await link.click();
        await expect.poll(async () => new URL(page.url()).pathname, { timeout: 20_000 }).toBe(target);
      });
    }
  });
});

// Each workflow route must be backed by an actual rendered control. Record IDs
// come from the fixture; no bogus ':id' links are added to the product menus.
const workflowCases = [
  { parent: "/projects", keys: ["BUSINESS_CREATE"] },
  { parent: "/hr", keys: ["USERS", "HR_JOB_POSITIONS"] },
  { parent: base, keys: ["BUSINESS_TABLE", "BUSINESS_JOB_POSITIONS", "BUSINESS_USERS"] },
  { parent: "/projects/setup", keys: ["BUSINESS_SETUP_SCHEMA"] },
  { parent: `${base}/procurement`, keys: ["PROJECT_PROCUREMENT_NEW", "PROJECT_PROCUREMENT_OFFICER", "PROJECT_PROCUREMENT_INVENTORY", "PROJECT_PROCUREMENT_REPORTS", "PROJECT_PROCUREMENT_BLOCKS", "PROJECT_PROCUREMENT_TRANSFERS", "PROJECT_PROCUREMENT_DETAIL"] },
  { parent: `${base}/contracts`, keys: ["PROJECT_CONTRACT_NEW", "PROJECT_CONTRACT_DETAIL", "PROJECT_IPC_DETAIL"] },
  { parent: `${base}/subcontractors`, keys: ["PROJECT_SUBCONTRACTOR_DETAIL"] },
  { parent: `${base}/daily-reports`, keys: ["PROJECT_DAILY_REPORT_NEW", "PROJECT_DAILY_REPORT_EDIT", "PROJECT_DAILY_REPORT_VIEW"] },
];
const examplePath = (key: string) => resolvePath(routes.find((route) => route.key === key)!.path).replace(/:tableSlug/g, "sample-table").replace(/:(reqId|contractId|ipcId|subId|reportId)/g, "record-1");

test.describe("Workflow route entry points", () => {
  test.beforeEach(({}, info) => { test.skip(info.project.name === "pwa-offline", "Requires dev server"); });
  for (const group of workflowCases) {
    test(`clickable entry points from ${group.parent}`, async ({ page }) => {
      test.setTimeout(90_000);
      await fullSession(page);
      for (const key of group.keys) {
        await visit(page, group.parent);
        if (key === "PROJECT_IPC_DETAIL") await page.getByRole("tab", { name: "صدور موقت", exact: true }).click();
        const target = examplePath(key);
        const link = page.locator(`a[href="${target}"]`).first();
        await expect(link, `UI entry for ${key}`).toBeVisible();
        await link.click();
        await expect(page).toHaveURL(new RegExp(`${target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`));
      }
    });
  }

  test("all workflow route keys have a UI exercise", () => {
    expect(new Set(workflowCases.flatMap((group) => group.keys))).toEqual(workflowRoutes);
  });

  test("project team shortcut uses the frontend route", async ({ page }) => {
    await fullSession(page);
    await visit(page, `${base}/users`);
    await page.locator("#button-openBusinessJobPositionsFromTeam").click();
    await expect(page).toHaveURL(new RegExp(`${base}/job-positions$`));
  });

  test("schema breadcrumb returns to data administration", async ({ page }) => {
    await fullSession(page);
    await visit(page, `${base}/setup`);
    await page.getByRole("link", { name: "Business setup", exact: true }).click();
    await expect(page).toHaveURL(/\/projects\/setup$/);
  });

  test("setup-only users can reach data administration without HR access", async ({ page, isMobile }) => {
    await session(page, ["business-setup"]);
    await visit(page, "/projects");
    if (isMobile) await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    const nav = page.locator("#nav-mainSidebar");
    await expect(nav.getByRole("link", { name: "Human resources", exact: true })).toHaveCount(0);
    await nav.getByRole("link", { name: "Data administration", exact: true }).click();
    await expect(page).toHaveURL(/\/projects\/setup$/);
  });
});

test.describe("Authentication entry points and redirect aliases", () => {
  test.beforeEach(({}, info) => { test.skip(info.project.name === "pwa-offline", "Requires dev server"); });
  test("sign-up, recovery, reset-code entry, sign-in and redirects stay connected", async ({ page }) => {
    const user = { id: "auth-navigation-user", full_name: "Navigation tester", roles: ["admin"] };
    let resetPayload: Record<string, string> | undefined;
    await page.route(/^https?:\/\/[^/]+\/api\//, (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path.endsWith("/auth/reset-password/")) resetPayload = route.request().postDataJSON();
      const json = path.endsWith("/auth/login/") ? { access: "navigation-test", refresh: "navigation-test", user }
        : path.endsWith("/auth/profile/") ? user
        : path.endsWith("/portfolio/summary/") ? { totals: { project_count: 0 }, totals_by_currency: {} }
        : path.includes("/auth/") ? { success: true } : { results: [], count: 0 };
      return route.fulfill({ json });
    });
    await visit(page, "/");
    await expect(page).toHaveURL(/\/login$/);
    await page.getByRole("button", { name: "Don't have an account? Register", exact: true }).click();
    await expect(page).toHaveURL(/\/register$/);
    await page.getByRole("link", { name: /Sign in/ }).click();
    await expect(page).toHaveURL(/\/login$/);
    await page.getByRole("button", { name: "Forgot password?", exact: true }).click();
    await expect(page).toHaveURL(/\/forgot-password$/);
    await page.locator("#forgot-phone").fill("+10000000001");
    await page.getByRole("button", { name: "Send reset code", exact: true }).click();
    await page.getByRole("link", { name: "Enter reset code", exact: true }).click();
    await expect(page).toHaveURL(/\/reset-password$/);
    await page.getByRole("textbox", { name: "Reset code", exact: true }).fill("123456");
    await page.locator("#reset-password").fill("navigation-test-only");
    await page.locator("#reset-password-confirm").fill("navigation-test-only");
    await page.getByRole("button", { name: "Update password", exact: true }).click();
    await expect(page.getByText("Password reset", { exact: true })).toBeVisible();
    expect(resetPayload?.token).toBe("123456");
    await page.getByRole("link", { name: "Sign in", exact: true }).click();
    await page.getByTestId("login-phone-input").fill("+10000000001");
    await page.getByTestId("login-password-input").fill("navigation-test-only");
    await page.getByTestId("login-submit-btn").click();
    await expect(page).toHaveURL(/\/projects$/);
    await page.goto("/home");
    await expect(page).toHaveURL(/\/projects$/);
    await page.goto("/");
    await expect(page).toHaveURL(/\/projects$/);
  });

  test("reset links with an existing token still populate the code field", async ({ page }) => {
    await visit(page, "/reset-password?token=123456");
    await expect(page.getByRole("textbox", { name: "Reset code", exact: true })).toHaveValue("123456");
  });
});
