import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

const api = process.env.B04_TEST_API_URL ?? "http://127.0.0.1:18084/api";
const frontend = process.env.B04_TEST_WEB_URL ?? "http://localhost:5173";
const project = process.env.B04_TEST_PROJECT;
const password = process.env.B04_TEST_PASSWORD;
const contractor = process.env.B04_TEST_CONTRACTOR;
const matchedReports = (process.env.B04_TEST_MATCHED_REPORTS ?? "").split(",").filter(Boolean);

const signedInActors = new Map<string, Promise<{ access: string; refresh: string; user: unknown }>>();

function authenticate(request: APIRequestContext, user: string) {
  const existing = signedInActors.get(user);
  if (existing) return existing;
  const pending = (async () => {
    const response = await request.post(`${api}/auth/login/`, { data: { username: user, password } });
    expect(response.status()).toBe(200);
    return response.json();
  })();
  signedInActors.set(user, pending);
  return pending;
}

async function signIn(request: APIRequestContext, page: Page, language: string, user: string) {
  const session = await authenticate(request, user);
  await page.addInitScript(({ session, language }) => {
    localStorage.setItem("app-language", language);
    localStorage.setItem("i18nextLng", language);
    localStorage.setItem("auth_access_token", session.access);
    localStorage.setItem("auth_refresh_token", session.refresh);
    localStorage.setItem("auth_user", JSON.stringify(session.user));
  }, { session, language });
}

for (const language of ["fa", "en"] as const) {
  test(`B04 daily filters and page recovery in ${language}`, async ({ browser, page, request }) => {
    test.skip(!project || !password || !contractor || matchedReports.length !== 21, "Seed the isolated B04 browser fixture");
    await signIn(request, page, language, "b04-viewer-1");
    const url = new URL(`/projects/${project}/daily-reports`, frontend);
    const filterDate = "2027-05-22";
    url.search = new URLSearchParams({ date_from: filterDate, status: "approved" }).toString();
    await page.goto(url.toString());
    const civil = page.getByLabel(language === "fa" ? "دیسیپلین" : "Discipline", { exact: true });
    const company = page.getByLabel(language === "fa" ? "پیمانکار" : "Contractor", { exact: true });
    const block = page.getByLabel(language === "fa" ? "بلوک" : "Block", { exact: true });
    await civil.click();
    await page.getByRole("option", { name: "CIVIL", exact: true }).click();
    await company.click();
    await page.getByRole("option", { name: "آرماتوربند الف", exact: true }).click();
    await block.click();
    await page.getByRole("option", { name: "Block 1", exact: true }).click();
    await expect(page).toHaveURL(/block=Block\+1/);

    const assertReports = async (target: Page, ids: string[]) => {
      const links = target.getByTestId("daily-reports-list").getByTestId(/^daily-report-row-/);
      await expect(links).toHaveCount(ids.length);
      await expect.poll(() => links.evaluateAll((rows) => rows.map((row) => row.getAttribute("data-testid")?.replace("daily-report-row-", "")))).toEqual(ids);
    };
    await assertReports(page, matchedReports.slice(0, 20));
    await page.getByRole("button", { name: language === "fa" ? "صفحه بعد" : "Next page" }).click();
    await expect(page).toHaveURL(/page=2/);
    await assertReports(page, matchedReports.slice(20));
    const second = await browser.newContext();
    try {
      const shared = await second.newPage();
      await signIn(request, shared, language, "b04-viewer-2");
      await shared.goto(page.url());
      await assertReports(shared, matchedReports.slice(20));
      await shared.reload();
      await assertReports(shared, matchedReports.slice(20));
      await expect(shared.locator("html")).toHaveAttribute("dir", language === "fa" ? "rtl" : "ltr");
      await expect(shared.getByLabel(language === "fa" ? "پیمانکار" : "Contractor", { exact: true })).toHaveText("آرماتوربند الف");
    } finally {
      await second.close();
    }
    await page.goBack();
    await assertReports(page, matchedReports.slice(0, 20));
    await page.goForward();
    await assertReports(page, matchedReports.slice(20));
  });
}

const activityDay = "2027-04-01";

for (const language of ["fa", "en"] as const) {
  test(`B04 activity selection and FILE1 recovery in ${language}`, async ({ browser, page, request }, testInfo) => {
    test.skip(!project || !password || !contractor, "Seed the isolated B04 browser fixture");
    await signIn(request, page, language, "b04-viewer-1");
    const url = new URL(`/projects/${project}/activity-log`, frontend);
    url.search = new URLSearchParams({ date_from: activityDay, date_to: activityDay }).toString();
    await page.goto(url.toString());
    const fa = language === "fa";
    await page.getByLabel(fa ? "دیسیپلین" : "Discipline", { exact: true }).selectOption(["CIVIL"]);
    await expect(page).toHaveURL(/discipline=CIVIL/);
    await page.getByLabel(fa ? "قطعه" : "Parcel", { exact: true }).selectOption(["P1", "P2"]);
    await expect(page).toHaveURL(/parcel=P1%2CP2/);
    await page.getByLabel(fa ? "پیمانکار" : "Contractor", { exact: true }).selectOption(contractor!);
    await expect(page).toHaveURL(/contractor_id=/);
    await page.getByLabel(fa ? "بلوک" : "Block", { exact: true }).selectOption("Block 1");
    await expect(page).toHaveURL(/block=Block\+1/);

    const pageRows = (target: Page) => target.getByTestId("activity-log-row");
    const expectPage = async (target: Page, size: number) => {
      await expect(pageRows(target)).toHaveCount(size);
      await expect(target.locator("html")).toHaveAttribute("dir", fa ? "rtl" : "ltr");
      const totals = target.getByTestId("activity-log-totals");
      await expect(totals.getByTestId("activity-result-count")).toHaveAttribute("data-count", "51");
      await expect(totals.getByTestId("activity-headcount-sum")).toHaveAttribute("data-count", "51");
      await expect(totals).toContainText(fa ? "جمع تعداد نفرات ردیف‌ها" : "Activity-row headcount sum");
      await expect(totals.locator('[data-unit="m²"]')).toHaveAttribute("data-total", "45.0000");
      await expect(totals.locator('[data-unit="m³"]')).toHaveAttribute("data-total", "25.0000");
      await expect(totals.locator('[data-unit="kg"]')).toContainText(fa ? "نامشخص" : "Unknown");
    };
    const firstPage = async () => pageRows(page).evaluateAll((rows) => rows.map((row) => row.getAttribute("data-row-id")));
    const download = async (name: string) => {
      const pending = page.waitForEvent("download");
      await page.getByRole("button", { name: /FILE 1/ }).click();
      const file = await pending;
      await file.saveAs(testInfo.outputPath(name));
    };

    await expectPage(page, 50);
    const first = await firstPage();
    const measurementText: Record<string, string> = {};
    const recordMeasurements = async () => {
      for (const item of await pageRows(page).all()) {
        const description = await item.locator('[data-field="description"]').innerText();
        if (/B04 row 0[0-4]$/.test(description)) {
          measurementText[description] = await item.locator('[data-field="quantity"]').innerText();
        }
      }
    };
    await recordMeasurements();
    await download("page-1.xlsx");
    await page.getByRole("button", { name: fa ? "صفحه بعد" : "Next page" }).click();
    await expect(page).toHaveURL(/page=2/);
    await expectPage(page, 1);
    const last = await firstPage();
    expect(new Set([...first, ...last]).size).toBe(51);
    await recordMeasurements();
    const unknown = fa ? "نامشخص" : "Unknown";
    expect(measurementText).toEqual({
      "B04 row 00": fa ? "۰" : "0", "B04 row 01": unknown, "B04 row 02": unknown,
      "B04 row 03": unknown, "B04 row 04": unknown,
    });
    await download("page-2.xlsx");
    const workbooks = ["page-1.xlsx", "page-2.xlsx"].map((name) => testInfo.outputPath(name));
    execFileSync(process.env.B04_TEST_PYTHON ?? "apps/api/.venv/bin/python", [
      "e2e/fixtures/check_b04_workbook.py", ...workbooks,
    ]);
    await testInfo.attach("FILE1 SHA-256", {
      body: JSON.stringify(await Promise.all(workbooks.map(async (path) => ({
        path, sha256: createHash("sha256").update(await readFile(path)).digest("hex"),
      }))), null, 2),
      contentType: "application/json",
    });

    const context = await browser.newContext();
    try {
      const shared = await context.newPage();
      await signIn(request, shared, language, "b04-viewer-2");
      await shared.goto(page.url());
      await expectPage(shared, 1);
      await shared.reload();
      await expectPage(shared, 1);
      await expect(shared.getByLabel(fa ? "پیمانکار" : "Contractor", { exact: true })).toHaveValue(contractor!);
      await expect(pageRows(shared)).toHaveAttribute("data-row-id", last[0]!);
    } finally {
      await context.close();
    }

    await page.goBack();
    await expectPage(page, 50);
    expect(await firstPage()).toEqual(first);
    await page.goForward();
    await expectPage(page, 1);
    expect(await firstPage()).toEqual(last);
  });
}

test("B04 report access rejects both unauthorized actors against a warm selection", async ({ request }) => {
  test.skip(!project || !password || !contractor, "Seed the isolated B04 browser fixture");
  const endpoint = `${api}/v1/projects/${project}/activity-log/`;
  const headers = { Authorization: `Bearer ${(await authenticate(request, "b04-viewer-1")).access}` };
  const selection = { contractor_id: contractor!, date_from: activityDay, date_to: activityDay };
  const warm = await request.get(endpoint, { headers, params: selection });
  expect(warm.status()).toBe(200);
  expect((await warm.json()).count).toBe(51);
  for (const member of ["b04-no-reports", "b04-other-project"]) {
    const unauthorized = { Authorization: `Bearer ${(await authenticate(request, member)).access}` };
    for (const path of ["", "filters/", "filter-options/", "excel/"]) {
      const attempt = await request.get(endpoint + path, { headers: unauthorized, params: selection });
      expect(attempt.status()).toBe(403);
    }
  }
});

test("B04 SC-004 approval visibility and last-month filter timing", async ({ page, request, browser }, testInfo) => {
  const report = process.env.B04_TEST_TIMING_REPORT;
  const dateFrom = process.env.B04_TEST_TIMING_FROM;
  const dateTo = process.env.B04_TEST_TIMING_TO;
  test.skip(!project || !password || !contractor || !report || !dateFrom || !dateTo || !process.env.DATABASE_URL,
    "Seed a fresh submitted report and provide the isolated timing database");
  await signIn(request, page, "en", "b04-viewer-2");
  const approverHeaders = { Authorization: `Bearer ${(await authenticate(request, "b04-approver")).access}` };
  const root = new URL(`/projects/${project}/activity-log`, frontend);
  root.search = new URLSearchParams({ date_from: dateFrom!, date_to: dateTo!, q: "B04 row", page_size: "100" }).toString();
  await page.goto(root.toString());
  const count = (target: Page) => target.getByTestId("activity-result-count");
  await expect(count(page)).toHaveAttribute("data-count", "0");

  const readRender = (target: Page) => target.evaluate(() => {
    const snapshot = () => ({
      count: document.querySelector('[data-testid="activity-result-count"]')?.getAttribute("data-count"),
      headcount: document.querySelector('[data-testid="activity-headcount-sum"]')?.getAttribute("data-count"),
      rows: document.querySelectorAll('[data-testid="activity-log-row"]').length,
      quantity: document.querySelector('[data-unit="m²"]')?.getAttribute("data-total"),
    });
    return new Promise<number>((resolve) => {
      const observed = () => {
        const state = snapshot();
        if (state.count === "51" && state.headcount === "51" && state.rows === 51 && state.quantity === "63.7500") {
          watcher.disconnect();
          requestAnimationFrame(() => requestAnimationFrame(() => resolve(performance.timeOrigin + performance.now())));
        }
      };
      const watcher = new MutationObserver(observed);
      watcher.observe(document.body, { subtree: true, childList: true, attributes: true });
      observed();
    });
  });
  const { spawn } = await import("node:child_process");
  const observer = spawn(process.env.B04_TEST_PYTHON ?? "apps/api/.venv/bin/python", [
    "e2e/fixtures/observe_b04_approval.py", report!, project!,
  ], { stdio: ["ignore", "pipe", "pipe"] });
  const { createInterface } = await import("node:readline");
  const lines = createInterface({ input: observer.stdout })[Symbol.asyncIterator]();
  const first = await lines.next();
  expect(first.value).toBe("ready");
  const visible = readRender(page);
  const approvalResponse = request.post(`${api}/v1/projects/${project}/daily-reports/${report}/approve/`, {
    headers: approverHeaders, data: {},
  }).then((response) => ({ response, responseAt: Date.now() }));
  const committed = JSON.parse((await lines.next()).value) as { commit_lower_ms: number; commit_upper_ms: number };
  const visibleAt = await visible;
  const { response, responseAt } = await approvalResponse;
  expect(response.status(), await response.text()).toBe(200);
  const upperVisibilityMs = visibleAt - committed.commit_lower_ms;

  const cold = await browser.newContext();
  const filterMs: number[] = [];
  const requests: { durationMs: number; status: number }[] = [];
  try {
    const filterPage = await cold.newPage();
    filterPage.on("requestfinished", async (finished) => {
      if (!finished.url().includes("/activity-log/") || !finished.url().includes(`date_from=${dateFrom}`)) return;
      const response = await finished.response();
      if (response) requests.push({ durationMs: finished.timing().responseEnd, status: response.status() });
    });
    await signIn(request, filterPage, "en", "b04-viewer-1");
    root.search = new URLSearchParams({
      date_from: "2027-04-02", date_to: "2027-04-02", discipline: "CIVIL",
      contractor_id: contractor!, page_size: "100",
    }).toString();
    await filterPage.goto(root.toString());
    const preset = filterPage.getByRole("button", { name: "Last month" });
    for (let attempt = 0; attempt < 2; attempt++) {
      await expect(count(filterPage)).toHaveAttribute("data-count", "0");
      const applied = "b04-filter-applied";
      await preset.evaluate((button, mark) => button.addEventListener("click", () => performance.mark(mark), {
        capture: true, once: true,
      }), applied);
      const rendered = readRender(filterPage);
      await preset.click();
      const renderTime = await rendered;
      const applyTime = await filterPage.evaluate((mark) =>
        performance.timeOrigin + performance.getEntriesByName(mark).at(-1)!.startTime, applied,
      );
      filterMs.push(renderTime - applyTime);
      if (attempt === 0) await filterPage.goBack();
    }

  } finally {
    await cold.close();
    observer.kill();
  }

  const timings = {
    browser: browser.version(), base: frontend, api, window: [dateFrom, dateTo], rows: 51,
    ...committed, visibleAt, approvalResponseAt: responseAt, upperVisibilityMs,
    coldFilterMs: filterMs[0], warmFilterMs: filterMs[1], requests,
  };
  await testInfo.attach("SC-004 timings", { body: JSON.stringify(timings, null, 2), contentType: "application/json" });
  console.log(JSON.stringify(timings));
  expect(upperVisibilityMs).toBeLessThanOrEqual(1000);
  for (const elapsed of filterMs) expect(elapsed).toBeLessThan(1000);
});
