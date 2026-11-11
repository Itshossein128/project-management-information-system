import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

// Real browser, real API, isolated PostgreSQL. Expectations are explicit rather
// than generated from the permission implementation being checked.
const f = JSON.parse(readFileSync(process.env.A6_P1_E2E_FIXTURES!, "utf8"));
const api = process.env.A6_P1_E2E_API!;
type Scope = "activities" | "costs" | "documents" | "contracts" | "procurement" | "resource-allocations" | "daily-reports";
type RoleCase = { read: Scope[]; activityEdit?: boolean; activityDelete?: boolean; costsEdit?: boolean; upload?: boolean; contractEdit?: boolean; requestCreate?: boolean; hrEdit?: boolean; reportEdit?: boolean };
const cases: Record<string, RoleCase> = {
  project_manager: { read: ["activities", "costs", "documents", "contracts", "procurement", "resource-allocations", "daily-reports"], activityEdit: true, activityDelete: true, costsEdit: true, upload: true, contractEdit: true, requestCreate: true, hrEdit: true, reportEdit: true },
  planning_engineer: { read: ["activities", "costs", "contracts", "resource-allocations", "daily-reports"], activityEdit: true, activityDelete: true },
  site_supervisor: { read: ["activities", "procurement", "daily-reports"], requestCreate: true, reportEdit: true },
  field_supervisor: { read: ["activities", "daily-reports"], reportEdit: true },
  finance_manager: { read: ["costs", "contracts", "procurement", "resource-allocations"], costsEdit: true, contractEdit: true },
  procurement_officer: { read: ["costs", "documents", "procurement"], upload: true },
  document_controller: { read: ["documents"], upload: true },
  viewer: { read: ["activities", "resource-allocations"] },
  executive_approver: { read: ["costs", "contracts", "daily-reports"] },
  project_controls: { read: ["activities", "costs", "contracts", "resource-allocations", "daily-reports"], activityEdit: true, activityDelete: true },
  site_specialist: { read: ["activities", "procurement", "resource-allocations", "daily-reports"], requestCreate: true, reportEdit: true },
  supervisor_consultant: { read: ["activities", "costs", "documents", "contracts", "daily-reports"] },
  hr_officer: { read: ["resource-allocations"], hrEdit: true },
};
const scopes: Scope[] = ["activities", "costs", "documents", "contracts", "procurement", "resource-allocations", "daily-reports"];
const navGroup: Record<Scope, string> = {
  activities: "Planning", costs: "Commercial", documents: "Commercial", contracts: "Commercial",
  procurement: "Commercial", "resource-allocations": "Resources", "daily-reports": "Field",
};
const endpoint = (scope: Scope) => scope === "costs" ? "costs/summary/" : scope === "procurement" ? "requisitions/" : `${scope}/`;

async function login(page: Page, actor: string) {
  await page.addInitScript(() => { localStorage.setItem("app-language", "en"); localStorage.setItem("i18nextLng", "en"); });
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.locator("#login-phone").fill(f.users[actor].mobile);
  await page.locator("#login-password").fill(f.password);
  const response = page.waitForResponse(r => r.url().endsWith("/auth/login/") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const result = await response;
  if (result.status() === 429) {
    // Respect the real isolated single-process limiter; never disable it.
    await page.waitForTimeout(61_000);
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
  }
  await expect(page).not.toHaveURL(/\/login/);
}

async function open(page: Page, project: string, path: string) {
  await page.goto(`/projects/${project}/${path}`);
  await page.waitForLoadState("networkidle");
  // First-visit product tours are real UI overlays; close them as a user would
  // before interacting with the underlying controls.
  const tourClose = page.locator(".driver-popover-close-btn");
  if (await tourClose.isVisible()) await tourClose.click();
  await expect(page.getByText("Unexpected Application Error!")).toHaveCount(0);
}

async function affordance(page: Page, locator: ReturnType<Page["locator"]>, allowed: boolean, label: string) {
  if (allowed) await expect.soft(locator.first(), label).toBeVisible();
  else await expect.soft(locator, label).toHaveCount(0);
}

for (const [actor, expected] of Object.entries(cases)) {
  test(`${actor}: browser journeys and server parity`, async ({ page, request }, testInfo) => {
    const errors: string[] = [];
    page.on("pageerror", e => errors.push(e.message));
    await login(page, actor);
    await open(page, f.project_a, "settings/members");
    for (const group of new Set(Object.values(navGroup))) {
      const trigger = page.locator("#nav-projectNavigation").getByRole("button", { name: group, exact: true });
      const grouped = scopes.filter(scope => navGroup[scope] === group);
      if (await trigger.count()) {
        await trigger.click();
        const menu = page.getByRole("dialog", { name: group, exact: true });
        for (const scope of grouped) {
          await expect.soft(menu.locator(`a[href="/projects/${f.project_a}/${scope}"]`), `${actor} navigation to ${scope}`).toHaveCount(expected.read.includes(scope) ? 1 : 0);
        }
        await page.keyboard.press("Escape");
      } else {
        expect.soft(grouped.some(scope => expected.read.includes(scope)), `${actor}: authorized ${group} menu missing`).toBe(false);
      }
    }
    const observations: object[] = [];
    for (const scope of scopes) {
      await test.step(scope, async () => {
        const allowed = expected.read.includes(scope);
        // Independent direct request verifies that a hidden button is not the guard.
        const response = await request.get(`${api}/v1/projects/${f.project_a}/${endpoint(scope)}`, { headers: { Authorization: `Bearer ${f.tokens[actor]}` } });
        expect.soft(response.status(), `${actor}/${scope} direct read`).toBe(allowed ? 200 : 403);
        await open(page, f.project_a, scope);
        if (!allowed) {
          // No seeded activity, write control, or protected data may leak on a
          // manually entered URL. Some legacy screens use a controlled query error.
          await expect.soft(page.getByRole("button", { name: /(?:Edit|View) A6-1/ })).toHaveCount(0);
          await expect.soft(page.getByTestId("costs-kpi-grid")).toHaveCount(0);
          await expect.soft(page.getByRole("button", { name: "بارگذاری مدرک", exact: true })).toHaveCount(0);
          await expect.soft(page.locator(`a[href="/projects/${f.project_a}/contracts/new"]`)).toHaveCount(0);
          await expect.soft(page.getByTestId(`daily-report-row-${f.daily_report}`)).toHaveCount(0);
        } else if (scope === "activities") {
          await expect.soft(page.getByRole("button", { name: `${expected.activityEdit ? "Edit" : "View"} A6-1`, exact: true })).toBeVisible();
          await affordance(page, page.getByRole("button", { name: "حذف", exact: true }), Boolean(expected.activityDelete), "activity delete");
          await page.getByRole("button", { name: `${expected.activityEdit ? "Edit" : "View"} A6-1`, exact: true }).click();
          const dialog = page.getByRole("dialog");
          if (expected.activityEdit) await expect.soft(dialog.getByRole("textbox", { name: "نام فعالیت" })).toBeEnabled();
          else await expect.soft(dialog.getByRole("textbox", { name: "نام فعالیت" })).toBeDisabled();
        } else if (scope === "costs") {
          await expect.soft(page.getByTestId("costs-kpi-grid")).toBeVisible();
          await affordance(page, page.getByTestId("budget-version-create"), Boolean(expected.costsEdit), "create budget");
          await page.getByTestId("costs-tab-actual").click();
          await affordance(page, page.getByTestId("actual-cost-add-btn"), Boolean(expected.costsEdit), "add actual cost");
        } else if (scope === "documents") {
          await expect.soft(page.locator("#doc-search")).toBeVisible();
          await affordance(page, page.getByRole("button", { name: "بارگذاری مدرک", exact: true }), Boolean(expected.upload), "upload document");
          if (expected.upload) {
            await page.getByRole("button", { name: "بارگذاری مدرک", exact: true }).click();
            await expect.soft(page.getByRole("dialog")).toBeVisible();
          }
        } else if (scope === "contracts") {
          await expect.soft(page.getByTestId("contracts-kpi-grid")).toBeVisible();
          await affordance(page, page.locator(`a[href="/projects/${f.project_a}/contracts/new"]`), Boolean(expected.contractEdit), "new contract");
        } else if (scope === "procurement") {
          await expect.soft(page.locator('[data-tour="list-filters"]')).toBeVisible();
          await affordance(page, page.locator(`a[href="/projects/${f.project_a}/procurement/new"]`), Boolean(expected.requestCreate), "new requisition");
        } else if (scope === "resource-allocations") {
          await affordance(page, page.getByRole("button", { name: "New allocation", exact: true }), Boolean(expected.hrEdit), "new HR allocation");
        } else if (scope === "daily-reports") {
          await expect.soft(page.getByTestId(`daily-report-row-${f.daily_report}`)).toBeVisible();
          await affordance(page, page.getByTestId(`daily-report-edit-${f.daily_report}`), Boolean(expected.reportEdit), "edit daily report");
        }
        await page.screenshot({ path: testInfo.outputPath(`${actor}-${scope}.png`) });
        observations.push({ scope, read: allowed, http: response.status(), url: new URL(page.url()).pathname });
      });
    }
    await open(page, f.project_a, "settings/members");
    await expect.soft(page.getByText(f.users[actor].name, { exact: true }).last()).toBeVisible();
    await affordance(page, page.getByRole("button", { name: "Add member", exact: true }), actor === "project_manager", "manage membership");
    // A project role must never confer organization account administration.
    await expect.soft(page.locator('a[href="/hr/users"]')).toHaveCount(0);
    await page.screenshot({ path: testInfo.outputPath(`${actor}-members.png`) });
    expect.soft((await request.get(`${api}/v1/projects/${f.project_b}/`, { headers: { Authorization: `Bearer ${f.tokens[actor]}` } })).status(), "nonmember project").toBe(403);
    await open(page, f.project_b, "overview");
    await expect.soft(page.getByText(`A6-P1 B ${f.run}`, { exact: true })).toHaveCount(0);
    await testInfo.attach("observations", { body: JSON.stringify({ actor, observations, hydrationMessages: errors.filter(e => e.includes("Hydration failed")).length, otherErrors: errors.filter(e => !e.includes("Hydration failed")) }, null, 2), contentType: "application/json" });
    expect.soft(errors, "browser runtime and hydration errors").toEqual([]);
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await expect(page).toHaveURL(/\/login/);
  });
}

test("viewer in B, inactive member, and nonmember cannot gain project write access", async ({ page, request }) => {
  await login(page, "manager");
  await open(page, f.project_b, "settings/members");
  await expect(page.getByText(f.users.manager.name).first()).toBeVisible();
  await expect(page.getByRole("button", { name: "Add member", exact: true })).toHaveCount(0);
  const denied = await request.post(`${api}/v1/projects/${f.project_b}/members/`, { headers: { Authorization: `Bearer ${f.tokens.manager}` }, data: { user_id: f.users.new.id, role_ids: [f.viewer_role] } });
  expect(denied.status()).toBe(403);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "inactive");
  await open(page, f.project_a, "settings/members");
  await expect(page.getByRole("button", { name: "Add member", exact: true })).toHaveCount(0);
  await expect(page.getByText(f.users.manager.name, { exact: true })).toHaveCount(0);
  expect((await request.get(`${api}/v1/projects/${f.project_a}/members/`, { headers: { Authorization: `Bearer ${f.tokens.inactive}` } })).status()).toBe(403);
});

test("navigation follows project changes and effective grant/deny overrides", async ({ page, request }, testInfo) => {
  await login(page, "manager");
  const hasCostLink = async (project: string, allowed: boolean) => {
    await open(page, project, "settings/members");
    await page.locator("#nav-projectNavigation").getByRole("button", { name: "Commercial", exact: true }).click();
    await expect(page.getByRole("dialog", { name: "Commercial" }).locator(`a[href="/projects/${project}/costs"]`)).toHaveCount(allowed ? 1 : 0);
    await page.screenshot({ path: testInfo.outputPath(`project-${project === f.project_a ? "a" : "b"}-navigation.png`), animations: "disabled" });
    await page.keyboard.press("Escape");
  };
  await hasCostLink(f.project_a, true);
  await hasCostLink(f.project_b, false);
  await hasCostLink(f.project_a, true);
  const permissions = `${api}/v1/projects/${f.project_a}/members/${f.users.manager.id}/permissions/`;
  const headers = { Authorization: `Bearer ${f.tokens.manager}` };
  const denied = await request.post(permissions, { headers, data: { permission_codename: "view_costs", is_granted: false } });
  expect(denied.status()).toBe(200);
  expect((await request.get(`${api}/v1/projects/${f.project_a}/costs/summary/`, { headers })).status()).toBe(403);
  await hasCostLink(f.project_a, false);
  const inherited = await request.delete(`${permissions}?permission_codename=view_costs`, { headers });
  expect(inherited.status()).toBe(200);
  expect((await request.get(`${api}/v1/projects/${f.project_a}/costs/summary/`, { headers })).status()).toBe(200);
  await hasCostLink(f.project_a, true);
});

test("edit-only activity user saves in the browser while delete and approval stay denied", async ({ page, request }) => {
  await login(page, "editor");
  await open(page, f.project_a, "activities");
  await page.getByRole("button", { name: "Edit A6-1", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByTestId("measurement-approve-btn")).toHaveCount(0);
  const changed = `Browser-reviewed ${f.run}`;
  await dialog.getByRole("textbox", { name: "نام فعالیت" }).fill(changed);
  const saved = page.waitForResponse(r => r.url().endsWith(`/activities/${f.activity}/`) && r.request().method() === "PATCH");
  await dialog.getByRole("button", { name: "ذخیره", exact: true }).click();
  expect((await saved).status()).toBe(200);
  await expect(dialog).toBeHidden();
  await expect(page.getByText(changed, { exact: true })).toBeVisible();
  const headers = { Authorization: `Bearer ${f.tokens.editor}` };
  const persisted = await request.get(`${api}/v1/projects/${f.project_a}/activities/${f.activity}/`, { headers });
  expect((await persisted.json()).activity_name).toBe(changed);
  expect((await request.delete(`${api}/v1/projects/${f.project_a}/activities/${f.activity}/`, { headers })).status()).toBe(403);
  expect((await request.post(`${api}/v1/projects/${f.project_a}/activities/${f.activity}/measurement/approve/`, { headers, data: {} })).status()).toBe(403);
});

for (const actor of ["admin", "hr", "superuser", "staff", "visitor"]) {
  test(`${actor}: organization authority stays separate from project writes`, async ({ page, request }) => {
    await login(page, actor);
    const headers = { Authorization: `Bearer ${f.tokens[actor]}` };
    const orgAdmin = ["admin", "hr", "superuser"].includes(actor);
    expect((await request.get(`${api}/auth/users/`, { headers })).status()).toBe(orgAdmin ? 200 : 403);
    await page.goto("/hr/users");
    await page.waitForLoadState("networkidle");
    await affordance(page, page.getByRole("button", { name: "New user", exact: true }), orgAdmin, "organization account creation");
    if (orgAdmin) {
      await page.getByRole("button", { name: "New user", exact: true }).click();
      await expect(page.getByRole("dialog")).toBeVisible();
    }
    await open(page, f.project_a, "settings/members");
    await expect(page.getByRole("button", { name: "Add member", exact: true })).toHaveCount(0);
    expect((await request.post(`${api}/v1/projects/${f.project_a}/members/`, { headers, data: { user_id: f.users.new.id, role_ids: [f.viewer_role] } })).status()).toBe(403);
  });
}
