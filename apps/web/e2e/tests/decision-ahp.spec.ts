import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";
import { readFileSync } from "node:fs";
const en = JSON.parse(readFileSync("apps/web/src/app/locales/en.json", "utf8"));
const fa = JSON.parse(readFileSync("apps/web/src/app/locales/fa.json", "utf8"));

let authentication: Awaited<ReturnType<BrowserContext["storageState"]>>;
test.beforeAll(async ({ browser }) => {
  const context = await browser.newContext({ baseURL: "http://127.0.0.1:5173" });
  await loginAs(await context.newPage());
  authentication = await context.storageState();
  await context.close();
});
test.beforeEach(async ({ context }) => {
  await context.addCookies(authentication.cookies);
  await context.addInitScript(state => {
    for (const origin of state.origins) {
      if (origin.origin !== location.origin) continue;
      for (const item of origin.localStorage) {
        if (item.name.startsWith("auth_")) localStorage.setItem(item.name, item.value);
      }
    }
  }, authentication);
});

const api = "http://127.0.0.1:8000/api/v1";
async function setup(page: Page, locale: "en" | "fa", criteria: string[], matrix: (number | null)[][] = []) {
  await page.goto("/projects");
  const path = await createProjectViaApi(page);
  const projectId = path.split("/").pop()!;
  await page.evaluate((lang) => { localStorage.setItem("app-language", lang); localStorage.setItem("i18nextLng", lang); }, locale);
  const token = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  const headers = { Authorization: "Bearer " + token };
  const base = api + "/projects/" + projectId + "/decision-cases/";
  const res = await page.request.post(base, { headers, data: {
    title: "AHP browser " + Date.now(), selected_methods: ["ahp"], criteria, ahp_matrix: matrix,
  }});
  expect(res.status(), await res.text()).toBe(201);
  const c = await res.json();
  await page.goto(path + "/decision-support");
  await page.locator("#button-language-" + locale).click();
  await page.getByRole("button", { name: c.title, exact: true }).click();
  const copy = (locale === "en" ? en : fa).decisionSupport;
  await expect(page.getByRole("heading", { name: copy.ahpPanelTitle, exact: true })).toBeVisible();
  return { base, headers, c, copy };
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " fresh single criterion owns diagonal and runs without ranking", async ({ page }) => {
    const { base, headers, c, copy } = await setup(page, locale, ["Only"]);
    await expect(page.getByRole("spinbutton", { name: "Only × Only", exact: true })).toHaveValue("1");
    await page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true }).click();
    await expect(page.getByRole("heading", { name: copy.resultTitle.replace("{{method}}", "AHP"), exact: true })).toBeVisible();
    const runs = await (await page.request.get(base + c.id + "/runs/", { headers })).json();
    expect(runs.count).toBe(1);
    expect(runs.results[0].input_snapshot.ahp_matrix).toEqual([[1]]);
    expect(runs.results[0].result.weights).toEqual([{ criterion: "Only", weight: 1, rank: 1 }]);
    await expect(page.locator("html")).toHaveAttribute("dir", locale === "fa" ? "rtl" : "ltr");
  });

  test(locale + " blank comparisons require judgment; fractions persist at full precision", async ({ page }) => {
    const { base, headers, c, copy } = await setup(page, locale, ["A", "B"]);
    const cell = page.getByRole("spinbutton", { name: "A × B", exact: true });
    await expect(cell).toHaveValue("");
    await page.getByRole("combobox", { name: copy.pairwisePreset + " A × B", exact: true }).selectOption(String(1/3));
    await expect(cell).toHaveValue(String(1/3));
    await expect(page.getByRole("spinbutton", { name: "B × A", exact: true })).toHaveValue("3");
    await page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true }).click();
    await expect(page.getByRole("heading", { name: copy.resultTitle.replace("{{method}}", "AHP"), exact: true })).toBeVisible();
    const runs = await (await page.request.get(base + c.id + "/runs/", { headers })).json();
    expect(runs.results[0].result.weights[0].weight).toBeCloseTo(0.25, 12);
    expect(runs.results[0].result.weights[1].weight).toBeCloseTo(0.75, 12);
    await page.reload();
    await page.locator("#button-language-" + locale).click();
    await page.getByRole("button", { name: c.title, exact: true }).click();
    await expect(cell).toHaveValue(String(1/3));
    await cell.fill("12");
    await expect(page.getByText(copy.scaleAdvisory, { exact: true }).first()).toBeVisible();
    await page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true }).click();
    await expect(page.getByRole("region", { name: copy.currentAhpResult, exact: true })).toBeVisible();
    await cell.fill("");
    await expect(page.getByRole("spinbutton", { name: "B × A", exact: true })).toHaveValue("");
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " criterion identity survives reorder and new/renamed pairs stay blank", async ({ page }) => {
    const { copy } = await setup(page, locale, ["A", "B"], [[1, 3], [1/3, 1]]);
    await page.getByRole("button", { name: copy.moveCriterionUp.replace("{{index}}", "2"), exact: true }).click();
    await expect(page.getByRole("spinbutton", { name: "B × A", exact: true })).toHaveValue(String(1/3));
    await page.getByPlaceholder(copy.addName).first().fill("C");
    await page.getByPlaceholder(copy.addName).first().press("Enter");
    await expect(page.getByRole("spinbutton", { name: "A × C", exact: true })).toHaveValue("");
    await page.getByRole("textbox", { name: copy.criterionName.replace("{{index}}", "3"), exact: true }).fill("Renamed");
    await expect(page.getByRole("spinbutton", { name: "A × Renamed", exact: true })).toHaveValue("");
    await page.getByRole("textbox", { name: copy.criterionName.replace("{{index}}", "2"), exact: true }).fill("Other");
    await expect(page.getByRole("spinbutton", { name: "B × Other", exact: true })).toHaveValue("");
    const third = page.getByRole("textbox", { name: copy.criterionName.replace("{{index}}", "3"), exact: true });
    await third.locator("..").getByRole("button", { name: (locale === "en" ? en : fa).common.remove, exact: true }).click();
    await expect(page.getByRole("spinbutton", { name: "B × Renamed", exact: true })).toHaveCount(0);
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " consistent 2/3/6 comparisons display named weights and ordinal ranks", async ({ page }) => {
    const { copy } = await setup(page, locale, ["Low", "Middle", "High"],
      [[1, 1/3, 1/6], [3, 1, 1/2], [6, 2, 1]]);
    await page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true }).click();
    await expect(page.getByRole("heading", { name: copy.resultTitle.replace("{{method}}", "AHP"), exact: true })).toBeVisible();
    const rows = page.locator("table").last().locator("tbody tr");
    await expect(rows.nth(0)).toContainText("Low");
    await expect(rows.nth(0)).toContainText("0.1000");
    await expect(rows.nth(0)).toContainText("10.0%");
    await expect(rows.nth(0).locator("td").first()).toHaveText("3");
    await expect(rows.nth(2)).toContainText("0.6000");
    await page.screenshot({ path: test.info().outputPath("ahp-" + locale + "-result.png"), fullPage: true });
    await expect(page.getByRole("status").filter({ hasText: copy.crConsistent.split("{{cr}}")[0] })).toBeVisible();
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " inconsistent circular judgments are saved with advisory then revised", async ({ page }) => {
    const { base, headers, c, copy } = await setup(page, locale, ["A", "B", "C"],
      [[1, 5, .2], [.2, 1, 5], [5, .2, 1]]);
    const run = page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true });
    await run.click();
    await expect(page.getByRole("alert").filter({ hasText: copy.crInconsistent.split("{{cr}}")[0] })).toContainText("2.7586");
    let runs = await (await page.request.get(base + c.id + "/runs/", { headers })).json();
    expect(runs.count).toBe(1);
    expect(runs.results[0].result.is_consistent).toBe(false);
    for (const pair of ["A × B", "A × C", "B × C"]) await page.getByRole("spinbutton", { name: pair, exact: true }).fill("1");
    await run.click();
    await expect(page.getByRole("status").filter({ hasText: copy.crConsistent.split("{{cr}}")[0] })).toBeVisible();
    runs = await (await page.request.get(base + c.id + "/runs/", { headers })).json();
    expect(runs.count).toBe(2);
    expect(runs.results[1].result.is_consistent).toBe(false);
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " blank and invalid comparisons link errors to keyboard-focusable cells without a run", async ({ page }) => {
    const { base, headers, c, copy } = await setup(page, locale, ["A", "B"]);
    const run = page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true });
    const cell = page.getByRole("spinbutton", { name: "A × B", exact: true });
    await run.click();
    await expect(cell).toHaveAttribute("aria-invalid", "true");
    await expect(cell).toHaveAttribute("aria-describedby", /.+/);
    await expect(cell).toBeFocused();
    await page.getByRole("button", { name: "ahp_matrix.1.0: " + copy.errors.cell_empty, exact: true }).focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("spinbutton", { name: "B × A", exact: true })).toBeFocused();
    await cell.fill("0");
    await run.click();
    await expect(page.getByRole("alert")).toContainText(copy.errors.cell_non_positive);
    const runs = await (await page.request.get(base + c.id + "/runs/", { headers })).json();
    expect(runs.count).toBe(0);
  });
}

for (const locale of ["en", "fa"] as const) {
  for (const [name, matrix, code, pair] of [
    ["diagonal", [[1.00005, 2], [.5, 1]], "ahp_diagonal_invalid", "A × A"],
    ["reciprocal", [[1, 2], [.6, 1]], "ahp_reciprocal_mismatch", "B × A"],
  ] as const) {
    test(locale + " malformed saved " + name + " stays visible and invalid", async ({ page }) => {
      const { copy, base, headers, c } = await setup(page, locale, ["A", "B"], matrix.map(row => [...row]));
      await page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true }).click();
      await expect(page.getByRole("spinbutton", { name: pair, exact: true })).toBeFocused();
      await expect(page.getByRole("alert")).toContainText(copy.errors[code]);
      expect((await (await page.request.get(base + c.id + "/runs/", { headers })).json()).count).toBe(0);
    });
  }
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " mixed paginated history is frozen and separate from draft", async ({ page }) => {
    const { copy, c, base, headers } = await setup(page, locale, ["A", "B"], [[1, 3], [1/3, 1]]);
    expect((await page.request.patch(base + c.id + "/", { headers, data: {
      selected_methods: ["ahp", "saw"], alternatives: ["X", "Y"], weights: [10, 20],
      types: ["benefit", "cost"], performance_matrix: [[2, 3], [4, 5]],
    }})).status()).toBe(200);
    let first: { id: string } | null = null;
    for (let i = 0; i < 12; i++) {
      const res = await page.request.post(base + c.id + "/runs/", { headers, data: { method: "ahp" } });
      expect(res.status()).toBe(201);
      if (!first) first = await res.json();
    }
    expect((await page.request.post(base + c.id + "/runs/", { headers, data: { method: "saw" } })).status()).toBe(201);
    await page.reload();
    await page.locator("#button-language-" + locale).click();
    await page.getByRole("button", { name: c.title, exact: true }).click();
    const cell = page.getByRole("spinbutton", { name: "A × B", exact: true });
    await cell.fill("2");
    await page.getByRole("combobox", { name: copy.historyMethod, exact: true }).selectOption("ahp");
    await expect(page.getByRole("button", { name: copy.historyNext, exact: true })).toBeEnabled();
    await page.getByRole("button", { name: copy.historyNext, exact: true }).click();
    await page.locator('[data-run-id="' + first!.id + '"]').click();
    const frozen = page.getByRole("region", { name: copy.historicalRun, exact: true });
    await expect(frozen).toBeVisible();
    await expect(frozen.getByRole("cell", { name: "0.7500", exact: true })).toBeVisible();
    await expect(frozen.getByRole("cell", { name: "3", exact: true })).toBeVisible();
    await expect(cell).toHaveValue("2");
    await expect(frozen.getByRole("spinbutton")).toHaveCount(0);
    await expect(frozen).toContainText(copy.historyReadOnly);
    const snapshot = await (await page.request.get(base + c.id + "/runs/" + first!.id + "/", { headers })).json();
    expect(snapshot.input_snapshot.ahp_matrix).toEqual([[1, 3], [1/3, 1]]);
    await page.getByRole("combobox", { name: copy.historyMethod, exact: true }).selectOption("saw");
    await expect(page.locator("[data-run-id]")).toHaveCount(1);
  });

  test(locale + " delayed case and history responses cannot replace current case draft", async ({ page }) => {
    const { copy, c, base, headers } = await setup(page, locale, ["A", "B"], [[1, 3], [1/3, 1]]);
    const res = await page.request.post(base, { headers, data: {
      title: "Second case", selected_methods: ["ahp"], criteria: ["New"], ahp_matrix: [[1]],
    }});
    expect(res.status()).toBe(201);
    const other = await res.json();
    const run = await (await page.request.post(base + c.id + "/runs/", { headers, data: { method: "ahp" } })).json();
    await page.reload(); await page.locator("#button-language-" + locale).click();
    await page.getByRole("button", { name: c.title, exact: true }).click();
    await expect(page.locator('[data-run-id="' + run.id + '"]')).toBeVisible();
    let release!: () => void;
    const gate = new Promise<void>(resolve => { release = resolve; });
    await page.route("**/decision-cases/" + c.id + "/runs/" + run.id + "/", async route => {
      const response = await route.fetch(); await gate; await route.fulfill({ response });
    });
    await page.locator('[data-run-id="' + run.id + '"]').click();
    await page.getByRole("button", { name: other.title, exact: true }).click();
    await expect(page.getByRole("spinbutton", { name: "New × New", exact: true })).toHaveValue("1");
    release();
    await page.waitForResponse(response => response.url().endsWith("/runs/" + run.id + "/"));
    await expect(page.getByRole("region", { name: copy.historicalRun, exact: true })).toHaveCount(0);

    let releaseCase!: () => void;
    const caseGate = new Promise<void>(resolve => { releaseCase = resolve; });
    await page.route("**/decision-cases/" + c.id + "/", async route => {
      const response = await route.fetch(); await caseGate; await route.fulfill({ response });
    });
    await page.getByRole("button", { name: c.title, exact: true }).click();
    await page.getByRole("button", { name: other.title, exact: true }).click();
    await expect(page.getByRole("spinbutton", { name: "New × New", exact: true })).toHaveValue("1");
    releaseCase();
    await page.waitForResponse(response => response.url().endsWith("/decision-cases/" + c.id + "/"));
    await expect(page.getByRole("spinbutton", { name: "New × New", exact: true })).toHaveValue("1");
    await expect(page.getByRole("spinbutton", { name: "A × B", exact: true })).toHaveCount(0);
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " failed save prevents execution; pending save prevents repeated run", async ({ page }) => {
    const { copy, c, base, headers } = await setup(page, locale, ["A", "B"], [[1, 2], [.5, 1]]);
    const run = page.getByRole("button", { name: copy.runMethod.replace("{{method}}", "AHP"), exact: true });
    const url = "**/decision-cases/" + c.id + "/";
    await page.route(url, async route => {
      if (route.request().method() !== "PATCH") return route.continue();
      expect(Object.keys(route.request().postDataJSON())).toEqual(["ahp_matrix"]);
      await route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({
        error: { code: "decision_input_invalid", details: { issues: [
          { code: "cell_non_positive", path: "ahp_matrix.0.1", message: "Positive required" },
        ]}},
      })});
    });
    await run.click();
    await expect(page.getByRole("alert")).toContainText(copy.errors.cell_non_positive);
    expect((await (await page.request.get(base + c.id + "/runs/", { headers })).json()).count).toBe(0);
    await page.unroute(url);
    let release!: () => void;
    const gate = new Promise<void>(resolve => { release = resolve; });
    let saves = 0;
    await page.route(url, async route => {
      if (route.request().method() !== "PATCH") return route.continue();
      saves++; await gate; await route.continue();
    });
    await run.click();
    await expect(page.getByRole("button", { name: copy.running, exact: true })).toBeDisabled();
    await page.keyboard.press("Enter");
    expect(saves).toBe(1);
    release();
    await expect(page.getByRole("heading", { name: copy.resultTitle.replace("{{method}}", "AHP"), exact: true })).toBeVisible();
    expect((await (await page.request.get(base + c.id + "/runs/", { headers })).json()).count).toBe(1);
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " ten-criterion matrix supports keyboard presets and horizontal navigation", async ({ page }) => {
    const names = Array.from({ length: 10 }, (_, index) => "C" + (index + 1));
    const { copy } = await setup(page, locale, names);
    const first = page.getByRole("spinbutton", { name: "C1 × C2", exact: true });
    const preset = page.getByRole("combobox", { name: copy.pairwisePreset + " C1 × C2", exact: true });
    await preset.focus(); await page.keyboard.press("ArrowDown"); await page.keyboard.press("Enter");
    await expect(first).toHaveValue("1");
    await expect(page.getByRole("spinbutton", { name: "C2 × C1", exact: true })).toHaveValue("1");
    const end = page.getByRole("spinbutton", { name: "C10 × C9", exact: true });
    await end.focus();
    await expect(end).toBeFocused();
    const viewport = page.locator("div.overflow-x-auto").filter({ has: end }).first();
    expect(await viewport.evaluate(element => element.scrollWidth > element.clientWidth)).toBe(true);
    expect(await viewport.evaluate(element => Math.abs(element.scrollLeft))).toBeGreaterThan(0);
    await expect(page.locator("html")).toHaveAttribute("dir", locale === "fa" ? "rtl" : "ltr");
  });
}

for (const locale of ["en", "fa"] as const) {
  test(locale + " historical stub and legacy sorted results retain stored criterion identity", async ({ page }) => {
    const { copy, c, base, headers } = await setup(page, locale, ["A", "B"], [[1, 3], [1/3, 1]]);
    const response = await page.request.post(base + c.id + "/runs/", { headers, data: { method: "ahp" } });
    expect(response.status()).toBe(201);
    const stored = await response.json();
    await page.reload(); await page.locator("#button-language-" + locale).click();
    await page.getByRole("button", { name: c.title, exact: true }).click();
    const detail = "**/decision-cases/" + c.id + "/runs/" + stored.id + "/";
    let stub = true;
    await page.route(detail, async route => {
      const real = await route.fetch();
      const body = await real.json();
      body.result = stub ? { status: "stub", engine: null } :
        { ...body.result, weights: [...body.result.weights].reverse() };
      await route.fulfill({ response: real, json: body });
    });
    await page.locator('[data-run-id="' + stored.id + '"]').click();
    const frozen = page.getByRole("region", { name: copy.historicalRun, exact: true });
    await expect(frozen).toContainText(copy.historyResultUnavailable);
    await expect(frozen.getByRole("table")).toHaveCount(1);
    stub = false;
    await page.locator('[data-run-id="' + stored.id + '"]').click();
    const rows = frozen.getByRole("table").last().locator("tbody tr");
    await expect(rows.first()).toContainText("B");
    await expect(rows.first()).toContainText("0.2500");
    await expect(rows.last()).toContainText("A");
    await expect(rows.last()).toContainText("0.7500");
    await expect(page.getByRole("spinbutton", { name: "A × B", exact: true })).toHaveValue("3");
    expect((await (await page.request.get(base + c.id + "/runs/" + stored.id + "/", { headers })).json()).result).toEqual(stored.result);
  });
}


for (const locale of ["en", "fa"] as const) {
  test(locale + " request failures show feedback for save and run and allow recovery", async ({ page }) => {
    const {copy,c,base,headers}=await setup(page,locale,["A"],[[1]]);
    const run=page.getByRole("button",{name:copy.runMethod.replace("{{method}}","AHP"),exact:true});
    for (const phase of ["save", "run"] as const) {
      for (const [status,code] of [[403,"permission_denied"],[404,"not_found"],[429,"throttled"],[500,"request_failed"]] as const) {
        const url=phase==="save" ? "**/decision-cases/"+c.id+"/" : "**/decision-cases/"+c.id+"/runs/";
        let attempts=0;
        await page.route(url,async route => {
          if(route.request().method()!==(phase==="save" ? "PATCH":"POST")) return route.continue();
          attempts++;
          await route.fulfill({status,contentType:status===500 ? "text/html":"application/json",body:status===500 ? "<html>Server failed</html>":JSON.stringify({error:{code,message:"Server rejected request",details:{detail:"Server rejected request"}}})});
        });
        await run.click();
        const alert=page.getByRole("alert");
        await expect(alert).toBeVisible();
        const translations=locale==="en" ? en : fa;
        await expect(alert).toContainText(translations.decisionSupport.errors[code]);
        expect(attempts).toBe(1);
        expect((await (await page.request.get(base+c.id+"/runs/",{headers})).json()).count).toBe(0);
        await page.unroute(url);
      }
    }
    // The global case-save button uses the same general failure handling.
    const url="**/decision-cases/"+c.id+"/";
    await page.route(url,route=>route.request().method()==="PATCH" ? route.fulfill({status:403,contentType:"application/json",body:JSON.stringify({error:{code:"permission_denied",details:{detail:"Denied"}}})}):route.continue());
    await page.getByRole("button",{name:copy.save,exact:true}).click();
    await expect(page.getByRole("alert").filter({hasText:(locale==="en" ? en:fa).decisionSupport.errors.permission_denied})).toBeVisible();
    await page.unroute(url);
    await page.getByRole("button",{name:copy.save,exact:true}).click();
    await run.click();
    await expect(page.getByRole("heading",{name:copy.resultTitle.replace("{{method}}","AHP"),exact:true})).toBeVisible();
    expect((await (await page.request.get(base+c.id+"/runs/",{headers})).json()).count).toBe(1);
  });
}


for (const locale of ["en", "fa"] as const) {
  test.describe(locale + " history locale", () => {
    test.use({locale:locale === "en" ? "fa-IR" : "en-US"});
    test("history timestamps follow application language and switch without changing stored time", async ({ page }) => {
      const {copy,c,base,headers}=await setup(page,locale,["A"],[[1]]);
      const response=await page.request.post(base+c.id+"/runs/",{headers,data:{method:"ahp"}});
      expect(response.status()).toBe(201);
      const run=await response.json();
      await page.reload();
      await page.locator("#button-language-"+locale).click();
      await page.getByRole("button",{name:c.title,exact:true}).click();
      const entry=page.locator('[data-run-id="'+run.id+'"]');
      const formatted=await page.evaluate(({stamp,lang})=>new Date(stamp).toLocaleString(lang),{stamp:run.extracted_at,lang:locale});
      await expect(entry).toContainText(formatted);
      await entry.click();
      await expect(page.getByRole("region",{name:copy.historicalRun,exact:true}).locator("dd").last()).toHaveText(formatted);
      const other=locale==="en" ? "fa":"en";
      await page.locator("#button-language-"+other).click();
      const changed=await page.evaluate(({stamp,lang})=>new Date(stamp).toLocaleString(lang),{stamp:run.extracted_at,lang:other});
      await expect(entry).toContainText(changed);
      await expect(page.getByRole("region",{name:(other==="en" ? en:fa).decisionSupport.historicalRun,exact:true}).locator("dd").last()).toHaveText(changed);
      const frozen=await (await page.request.get(base+c.id+"/runs/"+run.id+"/",{headers})).json();
      expect(frozen.extracted_at).toBe(run.extracted_at);
    });
  });
}


for (const locale of ["en", "fa"] as const) {
  test(locale + " criterion rename preserves keyboard focus and caret", async ({ page }) => {
    const {copy}=await setup(page,locale,["A","B","C"],[[1,2,6],[.5,1,3],[1/6,1/3,1]]);
    const name=page.getByRole("textbox",{name:copy.criterionName.replace("{{index}}","1"),exact:true});
    await name.click();await name.press("End");await name.pressSequentially("xyz",{delay:70});
    await expect(name).toHaveValue("Axyz");await expect(name).toBeFocused();
    await name.press("Home");await name.press(locale==="fa" ? "ArrowLeft":"ArrowRight");await name.pressSequentially("MID",{delay:70});
    await expect(name).toHaveValue("AMIDxyz");await expect(name).toBeFocused();
    await name.press("Backspace");await expect(name).toHaveValue("AMIxyz");await expect(name).toBeFocused();
    await expect(page.getByRole("spinbutton",{name:"AMIxyz × B",exact:true})).toHaveValue("");
    await expect(page.getByRole("spinbutton",{name:"B × C",exact:true})).toHaveValue("3");
    await page.getByRole("button",{name:copy.moveCriterionUp.replace("{{index}}","2"),exact:true}).click();
    await expect(page.getByRole("textbox",{name:copy.criterionName.replace("{{index}}","1"),exact:true})).toHaveValue("B");
    const renamed=page.getByRole("textbox",{name:copy.criterionName.replace("{{index}}","2"),exact:true});
    await page.locator("li").filter({has:renamed}).getByRole("button",{name:(locale==="en" ? en:fa).common.remove,exact:true}).click();
    await expect(page.getByRole("spinbutton",{name:"B × C",exact:true})).toHaveValue("3");
    await expect(page.getByRole("spinbutton",{name:"C × B",exact:true})).toHaveValue(String(1/3));
  });
}
