import { test, expect, type BrowserContext } from "@playwright/test";
import { loginAs } from "../helpers/auth";
import {
  setup,
  gate,
  commitThenReplace,
} from "./helpers/decision-execution-records";
let authentication: Awaited<ReturnType<BrowserContext["storageState"]>>;
test.beforeAll(async ({ browser }) => {
  const context = await browser.newContext({
    baseURL: "http://127.0.0.1:5173",
  });
  await loginAs(await context.newPage());
  authentication = await context.storageState();
  await context.close();
});
test.beforeEach(async ({ context }) => {
  await context.addCookies(authentication.cookies);
  await context.addInitScript((state) => {
    for (const origin of state.origins)
      if (origin.origin === location.origin)
        for (const item of origin.localStorage)
          if (item.name.startsWith("auth_"))
            localStorage.setItem(item.name, item.value);
  }, authentication);
});
for (const locale of ["en", "fa"] as const) {
  test(
    locale + " clears prior success when ranking input becomes invalid",
    async ({ page }) => {
      const s = await setup(page, locale);
      const panel = page.locator("fieldset").filter({
        has: page.getByRole("heading", {
          name: s.copy.sawPanelTitle,
          exact: true,
        }),
      });
      await panel
        .getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", "SAW"),
          exact: true,
        })
        .click();
      await expect(
        panel.getByText("Alpha", { exact: true }).last(),
      ).toBeVisible();
      const result = panel.locator("table").last();
      await expect(
        result.getByRole("cell", { name: "Alpha", exact: true }),
      ).toBeVisible();
      await panel.locator('input[type="number"]').first().fill("-1");
      await expect(
        result.getByRole("cell", { name: "Alpha", exact: true }),
      ).toHaveCount(0);
      await panel
        .getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", "SAW"),
          exact: true,
        })
        .click();
      expect(
        (
          await (
            await page.request.get(s.base + s.c.id + "/runs/", {
              headers: s.headers,
            })
          ).json()
        ).count,
      ).toBe(1);
    },
  );
}
for (const locale of ["en", "fa"] as const) {
  test(
    locale +
      " frozen named ranking review leaves current result and live draft unchanged",
    async ({ page }) => {
      const s = await setup(page, locale);
      const runs = s.base + s.c.id + "/runs/";
      const a = await page.request.post(runs, {
        headers: s.headers,
        data: { method: "saw" },
      });
      expect(a.status()).toBe(201);
      const first = await a.json();
      await page.request.patch(s.base + s.c.id + "/", {
        headers: s.headers,
        data: {
          criteria: ["Live cost", "Live quality"],
          weights: [3, 2],
          performance_matrix: [
            [8, 9],
            [3, 4],
          ],
        },
      });
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      await expect(page.locator("#ds-title")).toHaveValue(s.c.title);
      await page.locator('[data-run-id="' + first.id + '"]').click();
      const history = page.getByRole("region", {
        name: s.copy.historicalRun,
        exact: true,
      });
      await expect(
        history.getByRole("table", {
          name: s.copy.frozenRankingInputs || "Frozen ranking inputs",
        }),
      ).toBeVisible();
      await expect(
        history.getByRole("columnheader", { name: "Cost", exact: true }),
      ).toBeVisible();
      await expect(
        history.getByRole("cell", { name: "0.4", exact: true }),
      ).toBeVisible();
      const panel = page.locator("fieldset").filter({
        has: page.getByRole("heading", {
          name: s.copy.sawPanelTitle,
          exact: true,
        }),
      });
      await expect(
        panel.getByRole("cell", { name: "Alpha", exact: true }),
      ).toHaveCount(0);
      expect(
        await (
          await page.request.get(runs + first.id + "/", { headers: s.headers })
        ).json(),
      ).toEqual(first);
    },
  );
}
for (const method of ["saw", "topsis", "ahp", "ism"]) {
  test(
    method +
      " unconfirmed save stops before POST and real committed lost response recovers",
    async ({ page }) => {
      const s = await setup(page);
      const button = page.getByRole("button", {
        name: s.copy.runMethod.replace("{{method}}", method.toUpperCase()),
        exact: true,
      });
      let posts = 0;
      await page.route(
        "**/decision-cases/" + s.c.id + "/runs/",
        async (route) => {
          if (route.request().method() === "POST") posts++;
          await route.continue();
        },
      );
      await page.route("**/decision-cases/" + s.c.id + "/", async (route) => {
        if (route.request().method() === "PATCH")
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: "null",
          });
        else await route.continue();
      });
      await button.click();
      await expect(
        page.getByRole("button", { name: s.copy.save, exact: true }),
      ).toBeEnabled();
      await page.waitForTimeout(250);
      expect(posts).toBe(0);
      await page.unroute("**/decision-cases/" + s.c.id + "/");
      await page.unroute("**/decision-cases/" + s.c.id + "/runs/");
      const hold = gate();
      let id = "";
      let committed = false;
      await page.route(
        "**/decision-cases/" + s.c.id + "/runs/**",
        async (route) => {
          if (route.request().method() === "POST") {
            posts++;
            id = await commitThenReplace(route, "null");
            committed = true;
          } else if (committed) {
            await hold.held;
            await route.continue();
          } else await route.continue();
        },
      );
      await button.click();
      await expect.poll(() => id, { timeout: 15_000 }).not.toBe("");
      try {
        await expect(
          page.getByRole("button", { name: s.copy.save, exact: true }),
        ).toBeDisabled();
        expect(posts).toBe(1);
      } finally {
        hold.release();
      }
      await expect(
        page.locator('[data-run-id="' + id + '"]').first(),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: s.copy.save, exact: true }),
      ).toBeEnabled();
      expect(posts).toBe(1);
    },
  );
}
import { insertHistorical } from "./helpers/decision-execution-records";
import {
  saw,
  ahp,
  dematel,
  partial,
} from "../../src/components/decision-support/execution-record-fixtures";
for (const locale of ["en", "fa"] as const) {
  test(
    locale +
      " partial legacy and completed DEMATEL fixture review is safe and read-only",
    async ({ page }) => {
      const s = await setup(page, locale);
      const examples = [
        { ...saw, input_snapshot: null, result: null },
        partial,
        ahp,
        dematel,
      ];
      insertHistorical(
        s.c.id,
        examples.map(({ method, input_snapshot, result }) => ({
          method,
          input_snapshot,
          result,
        })),
      );
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      let mutations = 0;
      page.on("request", (r) => {
        if (/decision-cases/.test(r.url()) && r.method() !== "GET") mutations++;
      });
      for (const method of ["dematel", "ahp", "saw"]) {
        await page
          .getByRole("combobox", { name: s.copy.historyMethod })
          .selectOption(method);
        for (const row of await page.locator("[data-run-id]").all()) {
          await row.focus();
          await page.keyboard.press("Enter");
          const view = page.locator("[data-history-detail]");
          await expect(view).toBeVisible();
          if (method === "dematel") {
            await expect(
              view.getByRole("table", { name: s.copy.dematelIndicators }),
            ).toBeVisible();
            await expect(
              view.getByRole("cell", { name: "-0.5", exact: true }),
            ).toBeVisible();
          }
          if (method === "saw")
            await expect(
              view
                .getByText(s.copy.historyResultUnavailable, { exact: true })
                .first(),
            ).toBeVisible();
        }
      }
      expect(mutations).toBe(0);
    },
  );
  test(
    locale +
      " history failure clears previous detail and late page/filter/case reads cannot publish",
    async ({ page }) => {
      const s = await setup(page, locale);
      for (let i = 0; i < 12; i++)
        expect(
          (
            await page.request.post(s.base + s.c.id + "/runs/", {
              headers: s.headers,
              data: { method: "saw" },
            })
          ).status(),
        ).toBe(201);
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      const rows = page.locator("[data-run-id]");
      await expect(rows).toHaveCount(10);
      const first = await rows.nth(0).getAttribute("data-run-id");
      const second = await rows.nth(1).getAttribute("data-run-id");
      await rows.nth(0).click();
      await expect(
        page.locator('[data-history-detail="' + first + '"]').first(),
      ).toBeVisible();
      const pattern = "**/runs/" + second + "/";
      await page.route(pattern, (r) =>
        r.fulfill({ status: 503, contentType: "application/json", body: "{}" }),
      );
      await rows.nth(1).click();
      await expect(page.locator("[data-history-detail]")).toHaveCount(0);
      await expect(
        page.getByText(s.copy.historyReadError, { exact: true }),
      ).toBeVisible();
      await page.unroute(pattern);
      const hold = gate();
      await page.route(pattern, async (r) => {
        await hold.held;
        await r.continue();
      });
      await rows.nth(1).click();
      await page
        .getByRole("button", { name: s.copy.historyNext, exact: true })
        .click();
      await expect(rows).toHaveCount(2);
      hold.release();
      await page.waitForTimeout(250);
      await expect(page.locator("[data-history-detail]")).toHaveCount(0);
      await page
        .getByRole("combobox", { name: s.copy.historyMethod })
        .selectOption("topsis");
      await expect(rows).toHaveCount(0);
    },
  );
  test(
    locale +
      " independent disagreement ties and deselection retain stored results without writes",
    async ({ page }) => {
      const s = await setup(page, locale);
      const independent = [
        {
          method: "saw",
          input_snapshot: saw.input_snapshot,
          result: saw.result,
        },
        {
          method: "topsis",
          input_snapshot: saw.input_snapshot,
          result: {
            status: "ok",
            engine: "topsis",
            ranking: [
              {
                option: "Beta",
                score: 0.9,
                rank: 1,
                d_best: 0.1,
                d_worst: 0.9,
                closeness: 0.9,
              },
              {
                option: "Alpha",
                score: 0.2,
                rank: 2,
                d_best: 0.8,
                d_worst: 0.2,
                closeness: 0.2,
              },
            ],
          },
        },
      ];
      insertHistorical(s.c.id, independent);
      await page.request.patch(s.base + s.c.id + "/", {
        headers: s.headers,
        data: { selected_methods: [] },
      });
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      let mutations = 0;
      page.on("request", (r) => {
        if (r.url().includes("/decision-cases/") && r.method() !== "GET")
          mutations++;
      });
      for (const method of ["saw", "topsis"]) {
        await page
          .getByRole("combobox", { name: s.copy.historyMethod })
          .selectOption(method);
        await page.locator("[data-run-id]").first().click();
        const view = page.locator("[data-history-detail]");
        await expect(view).toBeVisible();
        await expect(
          view.locator("table").last().getByRole("row").nth(1),
        ).toContainText(method === "saw" ? "Alpha" : "Beta");
      }
      expect(mutations).toBe(0);
    },
  );
}
for (const locale of ["en", "fa"] as const)
  for (const method of ["saw", "topsis", "ahp", "ism"]) {
    test(
      locale + " " + method + " malformed save variants send zero executions",
      async ({ page }) => {
        const s = await setup(page, locale);
        let posts = 0;
        let raw = "";
        page.on("request", (r) => {
          if (r.url().includes(s.c.id + "/runs/") && r.method() === "POST")
            posts++;
        });
        await page.route("**/decision-cases/" + s.c.id + "/", (r) =>
          r.request().method() === "PATCH"
            ? r.fulfill({
                status: 200,
                contentType: "application/json",
                body: raw,
              })
            : r.continue(),
        );
        const run = page.getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", method.toUpperCase()),
          exact: true,
        });
        for (raw of [
          "",
          "<html>bad</html>",
          '{"id":',
          "null",
          "{}",
          JSON.stringify({ ...s.c, id: "wrong" }),
          JSON.stringify({ ...s.c, criteria: null }),
        ]) {
          await run.click();
          await expect(
            page.getByRole("button", { name: s.copy.save, exact: true }),
          ).toBeEnabled();
          await page.waitForTimeout(60);
          expect(posts).toBe(0);
          await expect(page.locator("#ds-title")).toHaveValue(s.c.title);
        }
      },
    );
    test(
      locale +
        " " +
        method +
        " committed malformed execution held recovery failure timeout and manual retry",
      async ({ page }) => {
        test.setTimeout(90_000);
        const s = await setup(page, locale);
        let posts = 0;
        let mode = "held";
        const hold = gate();
        let committed = "";
        let recovery = false;
        await page
          .getByRole("combobox", { name: s.copy.historyMethod })
          .selectOption("dematel");
        await page.route(
          "**/decision-cases/" + s.c.id + "/runs/**",
          async (r) => {
            if (r.request().method() === "POST") {
              posts++;
              const real = await r.fetch();
              expect(real.status()).toBe(201);
              committed = (await real.json()).id;
              recovery = true;
              await r.fulfill({
                status: 201,
                contentType: "application/json",
                body: "null",
              });
            } else if (recovery) {
              if (mode === "held") await hold.held;
              else if (mode === "fail")
                return r.fulfill({
                  status: 503,
                  contentType: "application/json",
                  body: "{}",
                });
              else if (mode === "malformed")
                return r.fulfill({
                  status: 200,
                  contentType: "application/json",
                  body: "{}",
                });
              else if (mode === "timeout")
                await new Promise((resolve) => setTimeout(resolve, 11_000));
              await r.continue();
            } else await r.continue();
          },
        );
        const run = page.getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", method.toUpperCase()),
          exact: true,
        });
        await run.click();
        await expect.poll(() => committed, { timeout: 15_000 }).not.toBe("");
        try {
          await expect(
            page.getByRole("button", { name: s.copy.save, exact: true }),
          ).toBeDisabled();
          expect(posts).toBe(1);
        } finally {
          hold.release();
        }
        await expect(
          page.locator('[data-run-id="' + committed + '"]').first(),
        ).toBeVisible();
        await expect(
          page.getByRole("combobox", { name: s.copy.historyMethod }),
        ).toHaveValue("");
        await expect(run).toBeEnabled();
        for (mode of ["fail", "malformed", "timeout"]) {
          const previousPosts = posts;
          const previousId = committed;
          await run.click();
          await expect
            .poll(() => posts, { timeout: 15_000 })
            .toBe(previousPosts + 1);
          await expect
            .poll(() => committed, { timeout: 15_000 })
            .not.toBe(previousId);
          await expect(run).toBeEnabled({ timeout: 15_000 });
          const status =
            method === "ism"
              ? page.locator('[data-ism-recovery="failed"]')
              : page.locator('[data-execution-recovery="failed"]').first();
          await expect(status).toBeVisible();
        }
        expect(posts).toBe(4);
        expect(
          (
            await (
              await page.request.get(s.base + s.c.id + "/runs/", {
                headers: s.headers,
              })
            ).json()
          ).count,
        ).toBe(4);
      },
    );
  }
for (const method of ["saw", "topsis", "ahp", "ism"]) {
  test(
    method +
      " captured recovery cannot change case B or release its pending save",
    async ({ page }) => {
      const s = await setup(page);
      const r = await page.request.post(s.base, {
        headers: s.headers,
        data: { ...s.c, id: undefined, title: "Case B " + Date.now() },
      });
      expect(r.status()).toBe(201);
      const b = await r.json();
      await page.reload();
      await page.locator("#button-language-en").click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      const hold = gate(),
        bhold = gate();
      let id = "";
      let recovering = false;
      await page.route(
        "**/decision-cases/" + s.c.id + "/runs/**",
        async (route) => {
          if (route.request().method() === "POST") {
            const real = await route.fetch();
            id = (await real.json()).id;
            recovering = true;
            await route.fulfill({
              status: 201,
              contentType: "application/json",
              body: "null",
            });
          } else if (recovering) {
            await hold.held;
            await route.continue();
          } else await route.continue();
        },
      );
      await page.route("**/decision-cases/" + b.id + "/", async (route) => {
        if (route.request().method() === "PATCH") {
          await bhold.held;
        }
        await route.continue();
      });
      await page
        .getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", method.toUpperCase()),
          exact: true,
        })
        .click();
      await expect.poll(() => id, { timeout: 15_000 }).not.toBe("");
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      await expect(page.locator("#ds-title")).toBeDisabled();
      await page.getByRole("button", { name: b.title, exact: true }).click();
      await expect(page.locator("#ds-title")).toHaveValue(b.title);
      await page
        .getByRole("combobox", { name: s.copy.historyMethod })
        .selectOption("topsis");
      await page.locator("#ds-title").fill(b.title + " pending");
      await page
        .getByRole("button", { name: s.copy.save, exact: true })
        .click();
      try {
        hold.release();
        await page.waitForTimeout(350);
        await expect(page.locator("#ds-title")).toBeDisabled();
        await expect(
          page.getByRole("combobox", { name: s.copy.historyMethod }),
        ).toHaveValue("topsis");
        await expect(
          page.locator('[data-run-id="' + id + '"]').first(),
        ).toHaveCount(0);
      } finally {
        hold.release();
        bhold.release();
      }
      await expect(page.locator("#ds-title")).toBeEnabled();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      await expect(page.locator("#ds-title")).toHaveValue(s.c.title);
      await expect(
        page.locator('[data-run-id="' + id + '"]').first(),
      ).toBeVisible();
    },
  );
}
import { writeFileSync, existsSync, readFileSync } from "node:fs";
import { cpus, platform, release, totalmem } from "node:os";
for (const locale of ["en", "fa"] as const)
  test(
    locale + " SC004 fixed 100-record history selection timing",
    async ({ page, browser }) => {
      test.setTimeout(180_000);
      const s = await setup(page, locale, {
        selected_methods: ["saw", "topsis", "ahp", "ism", "dematel"],
      });
      const methods = ["saw", "topsis", "ahp", "ism", "dematel"];
      for (let i = 0; i < 100; i++) {
        const r = await page.request.post(s.base + s.c.id + "/runs/", {
          headers: s.headers,
          data: { method: methods[i % 5] },
        });
        expect(r.status(), await r.text()).toBe(201);
      }
      const expected = await (
        await page.request.get(s.base + s.c.id + "/runs/?page_size=100", {
          headers: s.headers,
        })
      ).json();
      expect(expected.count).toBe(100);
      const ids = expected.results.map((r: any) => r.id);
      expect(new Set(ids).size).toBe(100);
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      const rows = page.locator("[data-run-id]");
      const filter = page.getByRole("combobox", { name: s.copy.historyMethod });
      // Full each-method traversal separately verifies complete filters/counts.
      for (const method of methods) {
        await filter.selectOption(method);
        const all: string[] = [];
        for (let p = 1; p <= 2; p++) {
          if (p > 1)
            await page
              .getByRole("button", { name: s.copy.historyNext, exact: true })
              .click();
          await expect(rows).toHaveCount(10);
          await expect(rows.first()).toHaveAttribute(
            "data-run-id",
            expected.results.filter((r: any) => r.method === method)[
              (p - 1) * 10
            ].id,
          );
          all.push(
            ...(await rows.evaluateAll((nodes) =>
              nodes.map((n) => n.getAttribute("data-run-id")!),
            )),
          );
        }
        expect(all).toEqual(
          expected.results
            .filter((r: any) => r.method === method)
            .map((r: any) => r.id),
        );
      }
      await filter.selectOption("");
      await expect(rows.first()).toHaveAttribute("data-run-id", ids[0]);
      const samples: any[] = [];
      let reads = 0;
      page.on("request", (r) => {
        if (r.method() === "GET" && r.url().includes(s.c.id + "/runs/"))
          reads++;
      });
      const displayPage = async (p: number) => {
        await expect(rows).toHaveCount(10);
        await expect(rows.first()).toHaveAttribute(
          "data-run-id",
          ids[(p - 1) * 10],
        );
        await expect(rows.last()).toHaveAttribute(
          "data-run-id",
          ids[p * 10 - 1],
        );
      };
      const seen = new Set<string>();
      for (let cycle = 0; cycle < 4; cycle++)
        for (let p = 2; p <= 11; p++) {
          const pageNumber = p === 11 ? 1 : p;
          const before = reads,
            start = performance.now();
          let error: string | null = null;
          try {
            if (p === 11) {
              await filter.selectOption("saw");
              await filter.selectOption("");
            } else
              await page
                .getByRole("button", { name: s.copy.historyNext, exact: true })
                .click();
            await displayPage(pageNumber);
            for (const id of ids.slice((pageNumber - 1) * 10, pageNumber * 10))
              seen.add(id);
          } catch (e) {
            error = String(e);
          }
          samples.push({
            locale,
            category: "page",
            page: pageNumber,
            duration_ms: performance.now() - start,
            network: reads > before,
            error,
          });
        }
      expect(seen.size).toBe(100);
      for (let i = 0; i < 40; i++) {
        const index = i % 10,
          id = ids[index],
          before = reads,
          start = performance.now();
        let error: string | null = null;
        try {
          await rows.nth(index).focus();
          await page.keyboard.press("Enter");
          await expect(
            page.locator('[data-history-detail="' + id + '"]').first(),
          ).toBeVisible();
          await expect(
            page.locator('[data-history-detail="' + id + '"]').first(),
          ).toContainText(expected.results[index].method.toUpperCase());
        } catch (e) {
          error = String(e);
        }
        samples.push({
          locale,
          category: "detail",
          id,
          duration_ms: performance.now() - start,
          network: reads > before,
          error,
        });
      }
      const file =
        "specs/024-decision-execution-records/validation-performance.json";
      const previous = existsSync(file)
        ? JSON.parse(readFileSync(file, "utf8"))
        : { runs: {} };
      previous.runs[locale] = {
        case_id: s.c.id,
        method_counts: Object.fromEntries(methods.map((m) => [m, 20])),
        samples,
        environment: {
          os: platform(),
          release: release(),
          cpu: cpus()[0]?.model,
          memory_bytes: totalmem(),
          node: process.version,
          chromium: browser.version(),
          workers: 1,
          api: "local Django runserver --nothreading",
          web: "Vite development",
          boundary:
            "user selection to matching readable IDs and stored detail; cached and fresh samples identified by GET observation",
          artificial_latency: false,
        },
      };
      writeFileSync(file, JSON.stringify(previous, null, 2) + "\n");
      for (const category of ["page", "detail"]) {
        const trials = samples.filter((r) => r.category === category);
        expect(trials).toHaveLength(40);
        expect(
          trials.filter((r) => !r.error && r.duration_ms <= 2000).length,
        ).toBeGreaterThanOrEqual(38);
      }
    },
  );
import { execFileSync } from "node:child_process";
for (const locale of ["en", "fa"] as const)
  test(
    locale + " real viewer access keyboard ten axes dates and revoked read",
    async ({ page, browser }) => {
      const names = Array.from({ length: 10 }, (_, i) => "Criterion " + i);
      const s = await setup(page, locale, {
        criteria: names,
        weights: Array(10).fill(1),
        types: Array(10).fill("benefit"),
        performance_matrix: [Array(10).fill(1), Array(10).fill(2)],
        selected_methods: ["saw"],
      });
      const r = await page.request.post(s.base + s.c.id + "/runs/", {
        headers: s.headers,
        data: { method: "saw" },
      });
      expect(r.status()).toBe(201);
      const run = await r.json();
      const phone = "+199" + Date.now();
      const code =
        "from django.contrib.auth import get_user_model\nfrom master_data.models import ProjectMember,ProjectMemberRole,Role\nu=get_user_model().objects.create_user(username=" +
        JSON.stringify(phone) +
        ",mobile=" +
        JSON.stringify(phone) +
        ',password="local-records-pass")\nm=ProjectMember.objects.create(project_id=' +
        JSON.stringify(s.projectId) +
        ',user=u,status="active")\nProjectMemberRole.objects.create(member=m,role=Role.objects.get(role_name="viewer"))';
      execFileSync("bash", ["apps/api/django.sh", "shell", "-c", code], {
        stdio: "pipe",
      });
      const context = await browser.newContext({
        baseURL: "http://127.0.0.1:5173",
      });
      const viewer = await context.newPage();
      const login = await viewer.request.post(
        "http://127.0.0.1:8000/api/auth/login/",
        { data: { phone_number: phone, password: "local-records-pass" } },
      );
      expect(login.status()).toBe(200);
      const auth = await login.json();
      await viewer.goto("/login");
      await viewer.evaluate((data) => {
        localStorage.setItem("auth_access_token", data.access);
        localStorage.setItem("auth_refresh_token", data.refresh);
        localStorage.setItem("auth_user", JSON.stringify(data.user));
        document.cookie =
          "auth_token=" + encodeURIComponent(data.access) + "; path=/";
      }, auth);
      await viewer.goto(s.path + "/decision-support");
      await viewer.locator("#button-language-" + locale).click();
      await viewer
        .getByRole("button", { name: s.c.title, exact: true })
        .click();
      await expect(viewer.locator("#ds-title")).toBeDisabled();
      await expect(
        viewer.getByRole("button", { name: s.copy.save, exact: true }),
      ).toBeDisabled();
      const row = viewer.locator('[data-run-id="' + run.id + '"]').first();
      await row.focus();
      await viewer.keyboard.press("Enter");
      const detail = viewer
        .locator('[data-history-detail="' + run.id + '"]')
        .first();
      await expect(detail).toBeVisible();
      for (const name of names)
        await expect(
          detail.getByRole("columnheader", { name, exact: true }),
        ).toBeVisible();
      const headers = { Authorization: "Bearer " + auth.access };
      expect(
        (
          await viewer.request.post(s.base + s.c.id + "/runs/", {
            headers,
            data: { method: "saw" },
          })
        ).status(),
      ).toBe(403);
      expect(
        await (
          await viewer.request.get(s.base + s.c.id + "/runs/" + run.id + "/", {
            headers,
          })
        ).json(),
      ).toEqual(run);
      await viewer
        .locator("#button-language-" + (locale === "en" ? "fa" : "en"))
        .click();
      await expect(detail).toContainText(run.id);
      expect(
        await (
          await viewer.request.get(s.base + s.c.id + "/runs/" + run.id + "/", {
            headers,
          })
        ).json(),
      ).toEqual(run);
      execFileSync(
        "bash",
        [
          "apps/api/django.sh",
          "shell",
          "-c",
          "from master_data.models import ProjectMember,ProjectMemberPermissionOverride\nm=ProjectMember.objects.get(project_id=" +
            JSON.stringify(s.projectId) +
            ",user__mobile=" +
            JSON.stringify(phone) +
            ')\nProjectMemberPermissionOverride.objects.create(member=m,permission_codename="view_decision_support",is_granted=False)',
        ],
        { stdio: "pipe" },
      );
      expect(
        (
          await viewer.request.get(s.base + s.c.id + "/runs/" + run.id + "/", {
            headers,
          })
        ).status(),
      ).toBe(403);
      await viewer.reload();
      await expect(viewer.locator("[data-history-detail]")).toHaveCount(0);
      await context.close();
    },
  );
for (const locale of ["en", "fa"] as const) {
  test(
    locale +
      " global save create and PATCH malformed success preserve draft and never execute",
    async ({ page }) => {
      const s = await setup(page, locale);
      let posts = 0;
      let raw = "null";
      page.on("request", (r) => {
        if (r.method() === "POST" && r.url().includes("/runs/")) posts++;
      });
      await page.route("**/decision-cases/" + s.c.id + "/", (r) =>
        r.request().method() === "PATCH"
          ? r.fulfill({
              status: 200,
              contentType: "application/json",
              body: raw,
            })
          : r.continue(),
      );
      for (raw of [
        "null",
        "{}",
        "<html>bad</html>",
        '{"id":',
        JSON.stringify({ ...s.c, id: "wrong" }),
      ]) {
        await page.locator("#ds-title").fill("Retained draft");
        await page
          .getByRole("button", { name: s.copy.save, exact: true })
          .click();
        await expect(
          page.getByRole("button", { name: s.copy.save, exact: true }),
        ).toBeEnabled();
        await expect(page.locator("#ds-title")).toHaveValue("Retained draft");
      }
      await page
        .getByRole("button", { name: s.copy.createCase, exact: true })
        .click();
      await page.locator("#ds-title").fill("New recoverable draft");
      await page.route("**/decision-cases/", (r) =>
        r.request().method() === "POST"
          ? r.fulfill({
              status: 201,
              contentType: "application/json",
              body: "null",
            })
          : r.continue(),
      );
      await page
        .getByRole("button", { name: s.copy.save, exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: s.copy.save, exact: true }),
      ).toBeEnabled();
      await expect(page.locator("#ds-title")).toHaveValue(
        "New recoverable draft",
      );
      expect(posts).toBe(0);
    },
  );
  for (const method of ["saw", "topsis", "ahp", "ism"])
    test(
      locale +
        " " +
        method +
        " malformed completed responses require recovery and never current success",
      async ({ page }) => {
        test.setTimeout(90_000);
        const s = await setup(page, locale);
        let posts = 0;
        let variant = 0;
        let committed = "";
        await page.route(
          "**/decision-cases/" + s.c.id + "/runs/",
          async (r) => {
            if (r.request().method() !== "POST") return r.continue();
            posts++;
            const selectedVariant = variant;
            const real = await r.fetch();
            expect(real.status()).toBe(201);
            const valid = await real.json();
            committed = valid.id;
            const candidates = [
              "",
              "<html>bad</html>",
              '{"id":',
              "null",
              "{}",
              JSON.stringify({ ...valid, method: "wrong" }),
              JSON.stringify({ ...valid, input_snapshot: null }),
              JSON.stringify({ ...valid, result: null }),
              JSON.stringify({ ...valid, extracted_by: null }),
            ];
            await r.fulfill({
              status: 201,
              contentType: "application/json",
              body: candidates[selectedVariant],
            });
          },
        );
        const run = page.getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", method.toUpperCase()),
          exact: true,
        });
        for (variant = 0; variant < 9; variant++) {
          const previousId = committed;
          await run.click();
          await expect.poll(() => posts, { timeout: 15_000 }).toBe(variant + 1);
          await expect
            .poll(() => committed, { timeout: 15_000 })
            .not.toBe(previousId);
          await expect(
            page.locator('[data-run-id="' + committed + '"]').first(),
          ).toBeVisible();
          await expect(run).toBeEnabled();
        }
        expect(posts).toBe(9);
        expect(
          (
            await (
              await page.request.get(s.base + s.c.id + "/runs/", {
                headers: s.headers,
              })
            ).json()
          ).count,
        ).toBe(9);
      },
    );
}
for (const locale of ["en", "fa"] as const)
  test(
    locale + " named ranking feedback and no-match history are distinct",
    async ({ page }) => {
      const s = await setup(page, locale);
      await page
        .getByRole("combobox", { name: s.copy.historyMethod })
        .selectOption("dematel");
      await expect
        .soft(
          page.getByText(
            locale === "en"
              ? "No runs match this method"
              : "اجرایی برای این روش یافت نشد",
            { exact: true },
          ),
        )
        .toBeVisible();
      const panel = page.locator("fieldset").filter({
        has: page.getByRole("heading", {
          name: s.copy.sawPanelTitle,
          exact: true,
        }),
      });
      await panel
        .getByRole("spinbutton", {
          name: s.copy.weights + " Cost",
          exact: true,
        })
        .fill("-1");
      await panel
        .getByRole("button", {
          name: s.copy.runMethod.replace("{{method}}", "SAW"),
          exact: true,
        })
        .click();
      await expect(panel.getByRole("alert")).toContainText("Cost");
    },
  );
for (const locale of ["en", "fa"] as const)
  test(
    locale +
      " recovery replaces a pre-commit in-flight first-page history read",
    async ({ page }) => {
      const s = await setup(page, locale);
      const old = gate();
      let reads = 0,
        oldReady = false,
        committed = "";
      await page.route(
        "**/decision-cases/" + s.c.id + "/runs/**",
        async (r) => {
          if (r.request().method() === "POST") {
            const response = await r.fetch();
            expect(response.status()).toBe(201);
            committed = (await response.json()).id;
            return r.fulfill({
              status: 201,
              contentType: "application/json",
              body: "null",
            });
          }
          reads++;
          if (reads === 1) {
            const response = await r.fetch();
            oldReady = true;
            await old.held;
            try {
              await r.fulfill({ response });
            } catch {
              /* the obsolete read is deliberately aborted */
            }
          } else await r.continue();
        },
      );
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: s.c.title, exact: true }).click();
      await expect.poll(() => oldReady, { timeout: 15_000 }).toBe(true);
      try {
        await page
          .getByRole("button", {
            name: s.copy.runMethod.replace("{{method}}", "SAW"),
            exact: true,
          })
          .click();
        await expect.poll(() => committed, { timeout: 15_000 }).not.toBe("");
        await expect(
          page.locator('[data-run-id="' + committed + '"]').first(),
        ).toBeVisible();
        await expect(
          page.getByRole("button", { name: s.copy.save, exact: true }),
        ).toBeEnabled();
        expect(reads).toBeGreaterThanOrEqual(2);
      } finally {
        old.release();
      }
    },
  );
