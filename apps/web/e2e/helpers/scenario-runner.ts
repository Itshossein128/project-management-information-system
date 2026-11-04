import { expect, type Page, type Response } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { E2E_USERS, loginAs, loginViaUI } from "./auth";
import {
  type DecisionScenario,
  type StoryScenario,
  repoRoot,
} from "./doc-catalog";
import { createActivityViaApi, createDailyReportViaApi, createProjectViaApi, createRootWbs } from "./project";

const API_ORIGIN = "http://127.0.0.1:8000";

export type ScenarioFixture = {
  projectId?: string;
  reportId?: string;
  contractId?: string;
  activityName?: string;
  wbsName?: string;
  errors: Record<string, string>;
};

const fixtures = new Map<number, Promise<ScenarioFixture>>();

async function authHeaders(page: Page): Promise<Record<string, string>> {
  const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  if (!access) throw new Error("missing access token");
  return { Authorization: `Bearer ${access}`, "Content-Type": "application/json" };
}

async function buildFixture(page: Page): Promise<ScenarioFixture> {
  const errors: Record<string, string> = {};
  const base = await createProjectViaApi(page);
  const projectId = base.split("/").pop();
  if (!projectId) throw new Error("project id missing");
  const headers = await authHeaders(page);
  const fixture: ScenarioFixture = { projectId, errors };

  try {
    const wbsName = `E2E WBS ${Date.now()}`;
    fixture.wbsName = wbsName;
    const wbsId = await createRootWbs(page, base, { code: `e${Date.now() % 100000}`, name: wbsName });
    const activityName = `E2E Activity ${Date.now()}`;
    fixture.activityName = activityName;
    await createActivityViaApi(page, base, { code: `a${Date.now() % 100000}`, name: activityName, wbsId });
  } catch (error) {
    errors.wbs = error instanceof Error ? error.message : String(error);
  }

  try {
    fixture.reportId = await createDailyReportViaApi(page, base);
  } catch (error) {
    errors.report = error instanceof Error ? error.message : String(error);
  }

  try {
    const response = await page.request.post(`${API_ORIGIN}/api/v1/projects/${projectId}/contracts/`, {
      headers,
      data: {
        contract_number: `E2E-${Date.now()}`,
        contract_type: "main",
        counterparty: "E2E counterparty",
        original_amount: "1000",
      },
    });
    if (!response.ok()) errors.contract = `${response.status()} ${await response.text()}`;
    else fixture.contractId = ((await response.json()) as { id?: string }).id;
  } catch (error) {
    errors.contract = error instanceof Error ? error.message : String(error);
  }

  return fixture;
}

export async function getFixture(page: Page, workerIndex: number): Promise<ScenarioFixture> {
  let pending = fixtures.get(workerIndex);
  if (!pending) {
    pending = buildFixture(page);
    fixtures.set(workerIndex, pending);
  }
  try {
    return await pending;
  } catch (error) {
    fixtures.delete(workerIndex);
    throw error;
  }
}

export function needsAuth(scenarioPath: string): boolean {
  return scenarioPath.includes("submit-valid-credentials");
}

export function materialize(template: string, fixture: ScenarioFixture | null): { url: string; missing: string[] } {
  let route = template.split("→")[0]?.trim() ?? "";
  route = route.replace(/\{([^}]+)\}/g, (_, options: string) => options.split(",")[0].trim());
  const missing: string[] = [];
  const values: Record<string, string | undefined> = {
    projectId: fixture?.projectId,
    businessId: fixture?.projectId,
    project_pk: fixture?.projectId,
    reportId: fixture?.reportId,
    report_id: fixture?.reportId,
    contractId: fixture?.contractId,
    id: fixture?.reportId ?? fixture?.contractId,
    unit: "buildings",
  };
  const replaceKey = (key: string, token: string) => {
    if (!(key in values)) {
      missing.push(key);
      return token;
    }
    const value = values[key];
    if (!value) {
      missing.push(key);
      return token;
    }
    return value;
  };
  route = route.replace(/\{([A-Za-z_]+)\}/g, (token, key: string) => replaceKey(key, token));
  route = route.replace(/:([A-Za-z_]+)/g, (token, key: string) => replaceKey(key, token));
  const pathname = route.split("?")[0]?.trim() || "/";
  return { url: pathname.startsWith("/") ? pathname : `/${pathname}`, missing };
}

export function quotedLabels(text: string): string[] {
  const labels = new Set<string>();
  for (const match of text.matchAll(/[«"“']([^"”'«\n]{2,90})[»"”']/g)) {
    const label = match[1].trim();
    if (label && !/^https?:/i.test(label) && !label.startsWith("/api/")) labels.add(label);
  }
  const click = text.match(/^Click ([^.(]{2,70})/);
  if (click) labels.add(click[1].replace(/\s+button$/i, "").trim());
  return [...labels];
}

function exactFieldLabels(then: string): string[] {
  const match = then.match(/exactly:\s*([^\n.]+)/i);
  if (!match) return [];
  return match[1].split(/[،,]/).map((part) => part.replace(/[`*]/g, "").trim()).filter((part) => part.length >= 2 && part.length <= 40);
}

function filenamePattern(text: string): RegExp | null {
  if (/daily-report-/i.test(text) && /\.pdf/i.test(text)) return /daily-report-.+\.pdf/i;
  if (/daily-report-/i.test(text) && /\.xlsx/i.test(text)) return /daily-report-.+\.xlsx/i;
  return null;
}

function contentType(text: string): string | null {
  const match = text.match(/application\/(?:vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet|pdf|json)/i);
  return match?.[0] ?? null;
}

function documentedEndpoints(text: string): Array<{ method: string; path: string }> {
  const found: Array<{ method: string; path: string }> = [];
  for (const match of text.matchAll(/\b(GET|POST|PUT|PATCH|DELETE)\s+`?(\/api\/[^\s`)]+)/gi)) {
    found.push({ method: match[1].toUpperCase(), path: match[2].replace(/[.,;]+$/, "") });
  }
  return found;
}

function readmeMentions(text: string): string[] {
  const files = new Set<string>();
  for (const match of text.matchAll(/`([^`]+\.md)`/g)) files.add(match[1]);
  for (const match of text.matchAll(/\[([a-z0-9-]+)\]\/README\.md/gi)) {
    files.add(match[0]);
  }
  return [...files];
}

async function expectLabels(page: Page, labels: string[], exactAll: boolean, source: string) {
  const missing: string[] = [];
  for (const label of labels) {
    const locator = page
      .getByRole("button", { name: label })
      .or(page.getByRole("link", { name: label }))
      .or(page.getByText(label, { exact: label.length < 12 }))
      .first();
    const visible = await locator.isVisible().catch(() => false);
    if (!visible) missing.push(label);
    if (!exactAll && visible) return;
  }
  if (exactAll) {
    expect(missing, `${source}\nMissing documented labels at ${page.url()}`).toEqual([]);
    return;
  }
  expect(missing.length, `${source}\nNone of the documented controls were visible at ${page.url()}: ${labels.join(" | ")}`).toBeLessThan(labels.length);
}

async function openRoute(page: Page, url: string): Promise<Response | null> {
  const response = await page.goto(url, { waitUntil: "domcontentloaded" });
  expect(response === null || response.status() < 500, `navigation failed for ${url}`).toBeTruthy();
  return response;
}

async function clickLabel(page: Page, label: string) {
  const locator = page
    .getByRole("button", { name: label })
    .or(page.getByRole("link", { name: label }))
    .or(page.getByText(label, { exact: false }))
    .first();
  await expect(locator, `control "${label}"`).toBeVisible({ timeout: 10_000 });
  await locator.click();
}

function assertStayedOffLogin(page: Page) {
  expect(new URL(page.url()).pathname).not.toMatch(/^\/login\/?$/);
}

export async function exerciseDecision(page: Page, scenario: DecisionScenario, workerIndex: number) {
  expect(scenario.missingReadme, `missing decision README ${scenario.readme}`).toBeFalsy();
  const source = `${scenario.readme}\nTrigger: ${scenario.trigger}`;
  const authed = needsAuth(scenario.path);

  if (scenario.path === "login/submit-valid-credentials" || /submit valid credentials/i.test(scenario.trigger)) {
    await loginViaUI(page, E2E_USERS.admin);
    await expect(page).toHaveURL(/\/projects\/?$/);
    return;
  }
  if (/submit-invalid-credentials/.test(scenario.path) || /invalid credentials/i.test(scenario.trigger)) {
    await page.goto("/login");
    await page.locator("#login-phone").fill(E2E_USERS.admin.phone);
    await page.locator("#login-password").fill("wrong-password");
    const loginResponse = page.waitForResponse((res) => res.url().includes("/auth/login/") && res.request().method() === "POST");
    await page.locator('button[type="submit"]').click();
    expect((await loginResponse).status()).toBe(401);
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("alert")).toBeVisible();
    return;
  }
  if (/\/logout$/.test(scenario.path) || /^Click Sign out|^Logout|sign out/i.test(scenario.trigger)) {
    await loginAs(page, E2E_USERS.admin);
    await page.goto("/projects");
    await page.locator("#button-appHeaderSignOut").click();
    await expect(page).toHaveURL(/\/login/);
    expect(await page.evaluate(() => localStorage.getItem("auth_access_token"))).toBeNull();
    return;
  }

  if (authed) await loginAs(page, E2E_USERS.admin);
  const fixture = authed ? await getFixture(page, workerIndex) : null;
  const { url, missing } = materialize(scenario.route || "/login", fixture);
  expect(missing, `${source}\nUnresolved route params ${missing.join(", ")} ${JSON.stringify(fixture?.errors ?? {})}`).toEqual([]);

  if (/themeToggle|toggle theme/i.test(scenario.trigger)) {
    await page.goto(url, { waitUntil: "networkidle" });
    if (url === "/login") await expect(page.locator("#login-phone")).toBeVisible();
    const toggle = page.locator("#button-themeToggle");
    await expect(toggle).toBeEnabled();
    const before = await page.evaluate(() => ({
      dark: document.documentElement.classList.contains("dark"),
      stored: localStorage.getItem("app-theme"),
    }));
    await toggle.click();
    await expect.poll(() => page.evaluate(() => ({
      dark: document.documentElement.classList.contains("dark"),
      stored: localStorage.getItem("app-theme"),
    }))).toEqual({
      dark: !before.dark,
      stored: before.dark ? "light" : "dark",
    });
    await toggle.click();
    return;
  }
  if (/LanguageSwitcher|change-language|switch language/i.test(`${scenario.path} ${scenario.trigger}`)) {
    await openRoute(page, url);
    const html = page.locator("html");
    await page.locator("#button-language-en").click();
    await expect(html).toHaveAttribute("dir", "ltr");
    await page.locator("#button-language-fa").click();
    await expect(html).toHaveAttribute("dir", "rtl");
    return;
  }
  if (/password visibility/i.test(scenario.trigger)) {
    await page.goto("/login");
    const password = page.locator("#login-password");
    await expect(password).toHaveAttribute("type", "password");
    await password.locator("xpath=ancestor::*[self::div][1]").locator("button").last().click();
    await expect(password).toHaveAttribute("type", "text");
    return;
  }
  if (/QueryErrorState|Click Retry/i.test(scenario.trigger)) {
    await page.route("**/api/v1/**", (route) => {
      if (route.request().method() !== "GET") return route.continue();
      return route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "e2e" }) });
    });
    try {
      await openRoute(page, url);
      await expect(page.getByRole("button", { name: /تلاش مجدد|Retry/i })).toBeVisible({ timeout: 10_000 });
    } finally {
      await page.unroute("**/api/v1/**");
    }
    return;
  }

  await openRoute(page, url);
  if (authed) assertStayedOffLogin(page);
  const labels = quotedLabels(scenario.trigger);
  const download = /Export|دانلود|خروجی|download/i.test(scenario.trigger);
  if (download && labels.length > 0) {
    const pattern = filenamePattern(`${scenario.trigger} ${scenario.desired} ${scenario.navigation}`) ?? /^.+\.(pdf|xlsx|json)$/i;
    const [file] = await Promise.all([
      page.waitForEvent("download", { timeout: 20_000 }),
      clickLabel(page, labels[0]),
    ]);
    expect(file.suggestedFilename()).toMatch(pattern);
    return;
  }
  if (labels.length > 0) {
    await expectLabels(page, labels, false, source);
  }
  const expected = scenario.navigation.match(/(?:Remains on|Navigates to|Redirects to)\s+`?(\/[^`\s]+)/i)?.[1];
  if (expected && !expected.includes(":")) {
    await expect(page).toHaveURL(new RegExp(`${expected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}/?`));
  } else if (!labels.length) {
    await expect(page.locator("body")).toBeVisible();
    const pathname = new URL(page.url()).pathname;
    expect(pathname === url || pathname.startsWith(url.replace(/\/$/, "")), `${source}\nExpected ${url} but was ${pathname}`).toBeTruthy();
  }
}

export async function exerciseDenial(page: Page, scenario: DecisionScenario, workerIndex: number) {
  const endpoints = documentedEndpoints(scenario.apiCall).filter((item) => item.method === "GET");
  const labels = quotedLabels(scenario.trigger).filter((label) => label.length > 3);
  await loginAs(page, E2E_USERS.admin);
  const fixture = await getFixture(page, workerIndex);
  if (endpoints.length > 0) {
    await loginAs(page, E2E_USERS.visitor);
    const headers = await authHeaders(page);
    const target = materialize(endpoints[0].path, fixture);
    expect(target.missing, scenario.path).toEqual([]);
    const response = await page.request.get(`${API_ORIGIN}${target.url}`, { headers });
    expect([401, 403], `${scenario.readme} visitor ${endpoints[0].path} returned ${response.status()} ${await response.text()}`).toContain(response.status());
    return;
  }
  if (labels.length === 0) {
    const { url, missing } = materialize(scenario.route, fixture);
    expect(missing, scenario.path).toEqual([]);
    await loginAs(page, E2E_USERS.visitor);
    await openRoute(page, url);
    const denied = await page.getByText(/عدم دسترسی|access denied|مجوز کافی/i).first().isVisible().catch(() => false);
    const onLogin = /\/login\/?$/.test(new URL(page.url()).pathname);
    expect(denied || onLogin, `${scenario.readme} visitor opened the protected screen at ${page.url()}`).toBeTruthy();
    return;
  }
  const { url, missing } = materialize(scenario.route, fixture);
  expect(missing, scenario.path).toEqual([]);
  await loginAs(page, E2E_USERS.visitor);
  await openRoute(page, url);
  for (const label of labels) {
    const locator = page.getByRole("button", { name: label }).or(page.getByRole("link", { name: label })).first();
    await expect(locator, `${scenario.readme} visitor can see ${label}`).toBeHidden();
  }
}

export async function exerciseStory(page: Page, scenario: StoryScenario, workerIndex: number) {
  const blob = `${scenario.given}\n${scenario.when}\n${scenario.then}`;
  const source = `${scenario.spec} · ${scenario.story}\n${scenario.then}`;
  const docFiles = readmeMentions(blob);
  if (/decision-tree|درخت تصمیم/i.test(blob) && docFiles.length > 0) {
    for (const mention of docFiles) {
      const absolute = mention.startsWith("docs/")
        ? path.join(repoRoot, mention)
        : path.join(repoRoot, "docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]", mention);
      expect(fs.existsSync(absolute), `${source}\nmissing ${absolute}`).toBeTruthy();
      if (/watermark|useSearchParams|view_reports|FILE 4|FILE 5|FILE 6/i.test(blob)) {
        const body = fs.readFileSync(absolute, "utf8");
        if (/watermark/i.test(blob)) expect(body).toMatch(/watermark|واترمارک|DRAFT/i);
        if (/useSearchParams/i.test(blob)) expect(body).toMatch(/useSearchParams|query/i);
        if (/view_reports/i.test(blob)) expect(body).toContain("view_reports");
      }
    }
    return;
  }

  const unauthorized = /unauthorized|without permission|بدون مجوز|403/i.test(scenario.given);
  await loginAs(page, unauthorized ? E2E_USERS.visitor : E2E_USERS.admin);
  const needsFixture = /:(projectId|businessId|reportId|contractId)|\{project_pk\}|\{id\}/.test(scenario.route + blob);
  const fixture = needsFixture && !unauthorized ? await getFixture(page, workerIndex) : needsFixture ? await (async () => {
    await loginAs(page, E2E_USERS.admin);
    const created = await getFixture(page, workerIndex);
    await loginAs(page, E2E_USERS.visitor);
    return created;
  })() : null;

  const offline = /offline|قطع شود|بدون شبکه|شبکه پیش از/i.test(scenario.when);
  if (offline) await page.context().setOffline(true);
  try {
    const { url, missing } = materialize(scenario.route, fixture);
    if (!unauthorized) expect(missing, `${source}\n${JSON.stringify(fixture?.errors ?? {})}`).toEqual([]);
    if (missing.length === 0) await openRoute(page, url);
    if (!unauthorized && needsAuthRoute(scenario.route)) assertStayedOffLogin(page);

    const fields = exactFieldLabels(scenario.then);
    if (fields.length > 0) await expectLabels(page, fields, true, source);

    const quotes = quotedLabels(`${scenario.when}\n${scenario.then}`);
    const exportLike = /download|export|spreadsheet|workbook|PDF|Excel|خروجی|دانلود/i.test(blob);
    const whenQuotes = quotedLabels(scenario.when);
    const clickable = whenQuotes.find((label) => /خروجی|دانلود|Export|Download|Excel|PDF|فایل/i.test(label));
    if (exportLike && clickable && missing.length === 0) {
      const pattern = filenamePattern(blob);
      const downloadPromise = page.waitForEvent("download", { timeout: 20_000 });
      await clickLabel(page, clickable);
      if (pattern) expect((await downloadPromise).suggestedFilename()).toMatch(pattern);
      else await downloadPromise;
    } else if (quotes.length > 0 && fields.length === 0 && missing.length === 0) {
      await expectLabels(page, quotes, false, source);
    }

    for (const endpoint of documentedEndpoints(blob)) {
      const target = materialize(endpoint.path, fixture);
      expect(target.missing, `${source}\n${endpoint.path}`).toEqual([]);
      const headers = await authHeaders(page);
      const response = await page.request.fetch(`${API_ORIGIN}${target.url}`, { method: endpoint.method, headers });
      if (unauthorized) {
        expect([401, 403]).toContain(response.status());
      } else {
        expect(response.status(), `${source}\n${endpoint.method} ${target.url}\n${await response.text()}`).toBeLessThan(400);
        const expectedType = contentType(blob);
        if (expectedType) expect(response.headers()["content-type"] ?? "").toContain(expectedType);
        const pattern = filenamePattern(blob);
        if (pattern) expect(response.headers()["content-disposition"] ?? "").toMatch(pattern);
      }
    }

    if (/useSearchParams|query string|query parameters|\?discipline=/i.test(blob) && missing.length === 0) {
      const { url } = materialize(scenario.route, fixture);
      await page.goto(`${url}?discipline=CIVIL&date_from=2026-09-01`);
      await expect(page).toHaveURL(/discipline=CIVIL/);
      await expect(page).toHaveURL(/date_from=2026-09-01/);
    }

    if (/WBS tree|appears in the project WBS/i.test(blob) && fixture?.wbsName) {
      const { url } = materialize("/projects/:projectId/wbs", fixture);
      await page.goto(url);
      await expect(page.getByText(fixture.wbsName)).toBeVisible();
    }
    if (/activity is saved|linked to that package/i.test(blob) && fixture?.activityName) {
      const { url } = materialize("/projects/:projectId/activities", fixture);
      await page.goto(url);
      await expect(page.getByText(fixture.activityName)).toBeVisible();
    }

    const observed = fields.length > 0 || quotes.length > 0 || documentedEndpoints(blob).length > 0 || docFiles.length > 0;
    if (!observed && missing.length === 0) {
      await expect(page.locator("main, [role=main], body").first()).toBeVisible();
      expect(new URL(page.url()).pathname, source).not.toBe("/login");
    }
  } finally {
    if (offline) await page.context().setOffline(false);
  }
}

function needsAuthRoute(route: string): boolean {
  return !/^\/(login|register|forgot-password|reset-password)?\/?$/.test(route);
}
