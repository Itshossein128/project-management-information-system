import { test, expect, type Page, type BrowserContext } from "@playwright/test";
import { loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { cpus, platform, release, totalmem } from "node:os";
const en = JSON.parse(readFileSync("apps/web/src/app/locales/en.json", "utf8"));
const fa = JSON.parse(readFileSync("apps/web/src/app/locales/fa.json", "utf8"));

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
    for (const origin of state.origins) {
      if (origin.origin !== location.origin) continue;
      for (const item of origin.localStorage) {
        if (item.name.startsWith("auth_"))
          localStorage.setItem(item.name, item.value);
      }
    }
  }, authentication);
});

const api = "http://127.0.0.1:8000/api/v1";
async function setup(
  page: Page,
  locale: "en" | "fa" = "en",
  overrides: Record<string, unknown> = {},
) {
  await page.goto("/projects");
  const path = await createProjectViaApi(page);
  const projectId = path.split("/").pop()!;
  const token = await page.evaluate(() =>
    localStorage.getItem("auth_access_token"),
  );
  const headers = { Authorization: "Bearer " + token };
  const base = api + "/projects/" + projectId + "/decision-cases/";
  const response = await page.request.post(base, {
    headers,
    data: {
      title: "ISM browser " + Date.now(),
      selected_methods: ["ahp", "saw", "topsis"],
      criteria: ["A"],
      ahp_matrix: [[1]],
      alternatives: ["X", "Y"],
      weights: [1],
      types: ["benefit"],
      performance_matrix: [[1], [2]],
      ...overrides,
    },
  });
  expect(response.status(), await response.text()).toBe(201);
  const c = await response.json();
  await page.goto(path + "/decision-support");
  await page.locator("#button-language-" + locale).click();
  await page.getByRole("button", { name: c.title, exact: true }).click();
  await expect(page.locator("#ds-title")).toHaveValue(c.title);
  const copy = (locale === "en" ? en : fa).decisionSupport;
  return { path, projectId, base, headers, c, copy };
}

test("foundation serializes existing method saves and global save", async ({
  page,
}) => {
  const { c, copy } = await setup(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  let patches = 0;
  await page.route("**/decision-cases/" + c.id + "/", async (route) => {
    if (route.request().method() !== "PATCH") return route.continue();
    patches++;
    await gate;
    await route.continue();
  });
  const run = page.getByRole("button", {
    name: copy.runMethod.replace("{{method}}", "AHP"),
    exact: true,
  });
  await run.click();
  try {
    await expect(
      page.getByRole("button", { name: copy.save, exact: true }),
    ).toBeDisabled();
    await expect(
      page.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", "SAW"),
        exact: true,
      }),
    ).toBeDisabled();
    await expect(page.locator("#ds-title")).toBeDisabled();
    expect(patches).toBe(1);
  } finally {
    release();
  }
  await expect(
    page.getByRole("heading", {
      name: copy.resultTitle.replace("{{method}}", "AHP"),
      exact: true,
    }),
  ).toBeVisible();
});

test("foundation view-only presentation disables every mutation", async ({
  page,
}) => {
  const { path, c, copy } = await setup(page);
  await page.route("**/members/*/permissions/", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        effective: {
          edit_decision_support: false,
          view_decision_support: true,
        },
        permissions: [],
      }),
    }),
  );
  await page.goto(path + "/decision-support");
  await page.locator("#button-language-en").click();
  await page.getByRole("button", { name: c.title, exact: true }).click();
  await expect(page.locator("#ds-title")).toHaveValue(c.title);
  await expect(page.locator("#ds-title")).toBeDisabled();
  await expect(
    page.getByRole("button", { name: copy.save, exact: true }),
  ).toBeDisabled();
  for (const method of ["AHP", "SAW", "TOPSIS"])
    await expect(
      page.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", method),
        exact: true,
      }),
    ).toBeDisabled();
});

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " independent ISM chain, zero and both single diagonals",
    async ({ page }) => {
      const examples = [
        {
          criteria: ["A", "B", "C"],
          matrix: [
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0],
          ],
          layers: [["C"], ["B"], ["A"]],
          reach: [
            [1, 1, 1],
            [0, 1, 1],
            [0, 0, 1],
          ],
        },
        {
          criteria: ["A", "B", "C"],
          matrix: [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
          ],
          layers: [["A", "B", "C"]],
          reach: [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
          ],
        },
        { criteria: ["A"], matrix: [[0]], layers: [["A"]], reach: [[1]] },
        { criteria: ["A"], matrix: [[1]], layers: [["A"]], reach: [[1]] },
        {
          criteria: ["A", "B", "C", "D"],
          matrix: [
            [0, 1, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 0],
          ],
          layers: [["D"], ["B", "C"], ["A"]],
          reach: [
            [1, 1, 1, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
          ],
        },
      ];
      for (const item of examples) {
        const { c, copy, base, headers } = await setup(page, locale, {
          selected_methods: ["ism"],
          criteria: item.criteria,
          ism_matrix: item.matrix,
          alternatives: [],
          weights: [],
          types: [],
          performance_matrix: [],
        });
        await expect(page.locator("[data-ism-panel]")).toBeVisible();
        const response = page.waitForResponse(
          (r) =>
            r.url().endsWith("/decision-cases/" + c.id + "/runs/") &&
            r.request().method() === "POST",
        );
        await page
          .getByRole("button", {
            name: copy.runMethod.replace("{{method}}", "ISM"),
            exact: true,
          })
          .click();
        const run = await (await response).json();
        expect(run.result.layers).toEqual(
          item.layers.map((criteria, i) => ({ level: i + 1, criteria })),
        );
        expect(run.result.reachability_matrix).toEqual(item.reach);
        expect(run.input_snapshot.ism_matrix).toEqual(item.matrix);
        await expect(page.locator("[data-ism-result]")).toBeVisible();
        await expect(
          page.locator("[data-ism-result] [data-ism-level]"),
        ).toHaveCount(item.layers.length);
        expect(
          (
            await (
              await page.request.get(base + c.id + "/runs/", { headers })
            ).json()
          ).count,
        ).toBe(1);
        await expect(page.locator("html")).toHaveAttribute(
          "dir",
          locale === "fa" ? "rtl" : "ltr",
        );
      }
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale +
      " draft blank correction and criterion operations preserve directed pairs",
    async ({ page }) => {
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria: ["A", "B", "C"],
        ism_matrix: [
          [0, 1, null],
          [0, 1, 1],
          [1, 0, 0],
        ],
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const cell = (i: number, j: number) =>
        page.locator(`[data-ism-cell="${i}-${j}"]`);
      await expect(cell(0, 2)).toHaveValue("");
      await page.getByRole("button", { name: copy.save, exact: true }).click();
      await expect(
        page.getByRole("button", { name: copy.save, exact: true }),
      ).toBeEnabled();
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: c.title, exact: true }).click();
      await expect(cell(0, 2)).toHaveValue("");
      const run = page.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", "ISM"),
        exact: true,
      });
      await run.click();
      await expect(cell(0, 2)).toBeFocused();
      await expect(page.getByRole("alert")).toContainText(
        copy.ismCell.replace("{{from}}", "A").replace("{{to}}", "C"),
      );
      await expect(page.getByRole("alert").getByRole("button")).toHaveCount(1);
      await page.getByRole("alert").getByRole("button").click();
      await expect(cell(0, 2)).toBeFocused();
      await cell(0, 2).selectOption("0");
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      const name = page.getByRole("textbox", {
        name: copy.criterionName.replace("{{index}}", "1"),
        exact: true,
      });
      await name.click();
      await name.press("End");
      await name.pressSequentially("xyz", { delay: 40 });
      await expect(name).toHaveValue("Axyz");
      await expect(name).toBeFocused();
      await expect(cell(0, 1)).toHaveValue("1");
      await expect(cell(1, 0)).toHaveValue("0");
      await expect(page.locator("[data-ism-result]")).toHaveCount(0);
      await page
        .getByRole("button", {
          name: copy.moveCriterionUp.replace("{{index}}", "2"),
          exact: true,
        })
        .click();
      await expect(cell(0, 1)).toHaveValue("0");
      await expect(cell(1, 0)).toHaveValue("1");
      await expect(cell(0, 0)).toHaveValue("1");
      const add = page
        .locator('input[placeholder="' + copy.addName + '"]')
        .first();
      await add.fill("D");
      await add.press("Enter");
      await expect(cell(3, 3)).toHaveValue("0");
      await expect(cell(0, 3)).toHaveValue("");
      const renamed = page.getByRole("textbox", {
        name: copy.criterionName.replace("{{index}}", "2"),
        exact: true,
      });
      await page
        .locator("li")
        .filter({ has: renamed })
        .getByRole("button", {
          name: (locale === "en" ? en : fa).common.remove,
          exact: true,
        })
        .click();
      await expect(cell(0, 1)).toHaveValue("1");
      await expect(cell(1, 0)).toHaveValue("0");
      const response = page.waitForResponse(
        (r) =>
          r.url().endsWith("/decision-cases/" + c.id + "/") &&
          r.request().method() === "PATCH",
      );
      await page.getByRole("button", { name: copy.save, exact: true }).click();
      expect((await response).status()).toBe(200);
      const saved = await (
        await page.request.get(base + c.id + "/", { headers })
      ).json();
      expect(saved.criteria).toEqual(["B", "C", "D"]);
      expect(saved.ism_matrix).toEqual([
        [1, 1, null],
        [0, 0, null],
        [null, null, 0],
      ]);
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " invalid drafts and failed requests stay recoverable",
    async ({ page }) => {
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria: ["A"],
        ism_matrix: [[true]],
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const cell = page.locator('[data-ism-cell="0-0"]');
      await expect(cell).toHaveValue("invalid");
      const run = page.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", "ISM"),
        exact: true,
      });
      await run.click();
      await expect(page.getByRole("alert")).toContainText(
        copy.errors.non_numeric,
      );
      await expect(cell).toHaveValue("invalid");
      await cell.selectOption("0");
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      const before = (
        await (
          await page.request.get(base + c.id + "/runs/", { headers })
        ).json()
      ).count;
      for (const phase of ["save", "run"] as const) {
        for (const [status, code] of [
          [403, "permission_denied"],
          [404, "not_found"],
          [429, "throttled"],
          [500, "request_failed"],
        ] as const) {
          const url =
            "**/decision-cases/" +
            c.id +
            "/" +
            (phase === "run" ? "runs/" : "");
          await page.route(url, (route) =>
            route.request().method() === (phase === "save" ? "PATCH" : "POST")
              ? route.fulfill({
                  status,
                  contentType:
                    status === 500 ? "text/html" : "application/json",
                  body:
                    status === 500
                      ? "<html>Error</html>"
                      : JSON.stringify({ error: { code } }),
                })
              : route.continue(),
          );
          await run.click();
          await expect(page.getByRole("alert")).toContainText(
            (locale === "en" ? en : fa).decisionSupport.errors[code],
          );
          await expect(cell).toHaveValue("0");
          await expect(page.locator("[data-ism-result]")).toHaveCount(0);
          expect(
            (
              await (
                await page.request.get(base + c.id + "/runs/", { headers })
              ).json()
            ).count,
          ).toBe(before);
          await page.unroute(url);
        }
      }
      const url = "**/decision-cases/" + c.id + "/";
      await page.route(url, (route) =>
        route.request().method() === "PATCH"
          ? route.abort("failed")
          : route.continue(),
      );
      await run.click();
      await expect(page.getByRole("alert")).toContainText(
        (locale === "en" ? en : fa).decisionSupport.errors.request_failed,
      );
      await expect(cell).toHaveValue("0");
      await page.unroute(url);
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      await page.request.patch(base + c.id + "/", {
        headers,
        data: { ism_matrix: 9 },
      });
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: c.title, exact: true }).click();
      await expect(page.getByRole("alert")).toContainText("9");
      await page
        .getByRole("button", { name: copy.ismReset, exact: true })
        .click();
      await expect(cell).toHaveValue("0");
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " maximal cycles, interpretation and frozen history",
    async ({ page }) => {
      const direct = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 0, 0],
      ];
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria: ["A", "B", "C"],
        ism_matrix: direct,
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const run = page.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", "ISM"),
        exact: true,
      });
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      await expect(page.locator("[data-ism-group]")).toHaveCount(1);
      await expect(page.locator("[data-ism-group]")).toContainText("A, B");
      await expect(page.locator("[data-ism-result]")).toContainText(
        copy.ismInterpretation,
      );
      await expect(page.locator("[data-ism-result]")).toContainText(
        copy.ismNoRemoval,
      );
      const first = (
        await (
          await page.request.get(base + c.id + "/runs/", { headers })
        ).json()
      ).results[0];
      const detail = await (
        await page.request.get(base + c.id + "/runs/" + first.id + "/", {
          headers,
        })
      ).json();
      const name = page.getByRole("textbox", {
        name: copy.criterionName.replace("{{index}}", "1"),
        exact: true,
      });
      await name.fill("Changed");
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      await page.locator('[data-run-id="' + first.id + '"]').click();
      const frozen = page.getByRole("region", {
        name: copy.historicalRun,
        exact: true,
      });
      await expect(frozen.locator("[data-ism-group]")).toContainText("A, B");
      await expect(frozen).not.toContainText("Changed");
      await expect(frozen.getByRole("table")).toHaveCount(2);
      const other = locale === "en" ? "fa" : "en";
      await page.locator("#button-language-" + other).click();
      await expect(
        page
          .getByRole("region", {
            name: (other === "en" ? en : fa).decisionSupport.historicalRun,
            exact: true,
          })
          .locator("[data-ism-group]"),
      ).toContainText("A, B");
      expect(
        await (
          await page.request.get(base + c.id + "/runs/" + first.id + "/", {
            headers,
          })
        ).json(),
      ).toEqual(detail);
      // A real frozen record is intercepted only to exercise compatibility presentation.
      const url = "**/decision-cases/" + c.id + "/runs/" + first.id + "/";
      await page.route(url, async (route) => {
        const response = await route.fetch();
        const body = await response.json();
        body.result = { status: "stub", engine: null };
        await route.fulfill({ response, json: body });
      });
      await page.locator('[data-run-id="' + first.id + '"]').click();
      await expect(
        page.getByRole("region", {
          name: (other === "en" ? en : fa).decisionSupport.historicalRun,
          exact: true,
        }),
      ).toContainText(
        (other === "en" ? en : fa).decisionSupport.historyResultUnavailable,
      );
      await page.unroute(url);
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " keyboard ten criteria and localized frozen provenance",
    async ({ page }) => {
      const criteria = Array.from({ length: 10 }, (_, i) => "C" + i);
      const matrix: (number | null)[][] = criteria.map((_, i) =>
        criteria.map((_, j) => (i + 1 === j ? 1 : 0)),
      );
      matrix[0][1] = null;
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria,
        ism_matrix: matrix,
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const cell = page.locator('[data-ism-cell="0-1"]');
      await page
        .getByRole("button", {
          name: copy.runMethod.replace("{{method}}", "ISM"),
          exact: true,
        })
        .press("Enter");
      await expect(cell).toBeFocused();
      await cell.press("ArrowDown");
      await cell.press("ArrowDown");
      await cell.press("Tab");
      await expect(cell).toHaveValue("1");
      await expect(page.locator('[data-ism-cell="0-2"]')).toBeFocused();
      await expect(page.locator('[data-ism-cell="1-0"]')).toHaveValue("0");
      const viewport = page
        .locator("[data-ism-panel] table")
        .first()
        .locator("..");
      expect(
        await viewport.evaluate((el) => el.scrollWidth > el.clientWidth),
      ).toBe(true);
      await page.locator('[data-ism-cell="0-9"]').focus();
      await expect(page.locator('[data-ism-cell="0-9"]')).toBeFocused();
      await page
        .getByRole("button", {
          name: copy.runMethod.replace("{{method}}", "ISM"),
          exact: true,
        })
        .press("Enter");
      await expect(
        page.locator("[data-ism-result] [data-ism-level]"),
      ).toHaveCount(10);
      const frozen = (
        await (
          await page.request.get(base + c.id + "/runs/", { headers })
        ).json()
      ).results[0];
      await page.locator(`[data-run-id="${frozen.id}"]`).press("Enter");
      let region = page.getByRole("region", {
        name: copy.historicalRun,
        exact: true,
      });
      await expect(region).toContainText(
        frozen.extracted_by_name || frozen.extracted_by,
      );
      await expect(region).toContainText(
        await page.evaluate(
          ({ date, locale }) => new Date(date).toLocaleString(locale),
          { date: frozen.extracted_at, locale },
        ),
      );
      await expect(region.locator('[data-ism-level="10"]')).toContainText(
        (10).toLocaleString(locale),
      );
      const other = locale === "en" ? "fa" : "en";
      await page.locator("#button-language-" + other).click();
      region = page.getByRole("region", {
        name: (other === "en" ? en : fa).decisionSupport.historicalRun,
        exact: true,
      });
      await expect(region).toContainText(
        await page.evaluate(
          ({ date, locale }) => new Date(date).toLocaleString(locale),
          { date: frozen.extracted_at, locale: other },
        ),
      );
      expect(
        await (
          await page.request.get(base + c.id + "/runs/" + frozen.id + "/", {
            headers,
          })
        ).json(),
      ).toEqual(frozen);
    },
  );
  test(
    locale + " delayed mixed method operations and late case release",
    async ({ page }) => {
      test.setTimeout(90000);
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism", "ahp", "saw", "topsis"],
        ism_matrix: [[0]],
      });
      const button = (method: string) =>
        method === "global"
          ? page.getByRole("button", { name: copy.save, exact: true })
          : page.getByRole("button", {
              name: copy.runMethod.replace("{{method}}", method),
              exact: true,
            });
      for (const method of ["AHP", "SAW", "TOPSIS", "global", "ISM"]) {
        let release!: () => void;
        const gate = new Promise<void>((r) => (release = r));
        let count = 0;
        const url = "**/decision-cases/" + c.id + "/";
        await page.route(url, async (route) => {
          if (route.request().method() !== "PATCH") return route.continue();
          count++;
          await gate;
          await route.continue();
        });
        const completed = page.waitForResponse(
          (r) =>
            r
              .url()
              .endsWith(
                "/decision-cases/" +
                  c.id +
                  "/" +
                  (method === "global" ? "" : "runs/"),
              ) &&
            r.request().method() === (method === "global" ? "PATCH" : "POST"),
        );
        await button(method).click();
        try {
          await expect(page.locator("#ds-title")).toBeDisabled();
          await expect(page.locator('[data-ism-cell="0-0"]')).toBeDisabled();
          const pending =
            method === "global"
              ? button("global")
              : page.getByRole("button", { name: copy.running, exact: true });
          for (const target of ["AHP", "SAW", "TOPSIS", "global", "ISM"])
            await expect(
              target === method ? pending : button(target),
            ).toBeDisabled();
          await pending.evaluate((el) => (el as HTMLButtonElement).click());
          expect(count).toBe(1);
        } finally {
          release();
        }
        const response = await completed;
        expect(response.status()).toBe(method === "global" ? 200 : 201);
        if (method !== "global") {
          const run = await response.json();
          expect(run.input_snapshot.criteria).toEqual(["A"]);
          expect(run.input_snapshot.ism_matrix).toEqual([[0]]);
          expect(run.result.status).toBe("ok");
        }
        await expect(button("ISM")).toBeEnabled();
        await page.unroute(url);
      }
      const created = await page.request.post(base, {
        headers,
        data: {
          title: "Second " + Date.now(),
          selected_methods: ["ism"],
          criteria: ["Second"],
          ism_matrix: [[1]],
        },
      });
      expect(created.status()).toBe(201);
      const second = await created.json();
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: c.title, exact: true }).click();
      const releases: Record<string, () => void> = {};
      const entered = new Set<string>();
      await page.route("**/decision-cases/*/runs/", async (route) => {
        if (route.request().method() !== "POST") return route.continue();
        const id = route.request().url().split("/").at(-3)!;
        entered.add(id);
        await new Promise<void>((r) => (releases[id] = r));
        await route.continue();
      });
      const old = page.waitForResponse(
        (r) =>
          r.url().endsWith("/decision-cases/" + c.id + "/runs/") &&
          r.request().method() === "POST",
      );
      await button("ISM").click();
      await expect.poll(() => entered.has(c.id)).toBe(true);
      await page
        .getByRole("button", { name: second.title, exact: true })
        .click();
      await expect(page.locator("#ds-title")).toHaveValue(second.title);
      await expect(button("ISM")).toBeEnabled();
      const next = page.waitForResponse(
        (r) =>
          r.url().endsWith("/decision-cases/" + second.id + "/runs/") &&
          r.request().method() === "POST",
      );
      await button("ISM").click();
      await expect.poll(() => entered.has(second.id)).toBe(true);
      releases[c.id]();
      await old;
      await expect(page.locator("#ds-title")).toHaveValue(second.title);
      await expect(button("global")).toBeDisabled();
      await expect(page.locator("[data-ism-result]")).toHaveCount(0);
      releases[second.id]();
      const run = await (await next).json();
      await expect(page.locator(`[data-ism-result="${run.id}"]`)).toBeVisible();
      expect(run.input_snapshot.criteria).toEqual(["Second"]);
      await expect(button("global")).toBeEnabled();
    },
  );
  test(
    locale +
      " actual viewer sees frozen results with zero writable controls or bypass runs",
    async ({ page }) => {
      const { copy, c, path, projectId, base, headers } = await setup(
        page,
        locale,
        {
          selected_methods: ["ism", "ahp", "saw", "topsis"],
          ism_matrix: [[0]],
        },
      );
      const run = await (
        await page.request.post(base + c.id + "/runs/", {
          headers,
          data: { method: "ism" },
        })
      ).json();
      const login = await page.request.post(
        "http://127.0.0.1:8000/api/auth/login/",
        { data: { phone_number: "+10000000017", password: "devpass123" } },
      );
      expect(login.status()).toBe(200);
      const viewer = await login.json();
      const roles = await (
        await page.request.get(api + "/roles/", { headers })
      ).json();
      const role = (Array.isArray(roles) ? roles : roles.results).find(
        (r: any) => r.role_name === "viewer",
      );
      const added = await page.request.post(
        api + "/projects/" + projectId + "/members/",
        { headers, data: { user_id: viewer.user.id, role_ids: [role.id] } },
      );
      expect(added.status(), await added.text()).toBe(201);
      await page.evaluate((data) => {
        localStorage.setItem("auth_access_token", data.access);
        localStorage.setItem("auth_refresh_token", data.refresh);
        localStorage.setItem("auth_user", JSON.stringify(data.user));
        document.cookie = `auth_token=${data.access}; path=/`;
      }, viewer);
      // The test's admin init script is only for fresh contexts; replace it on this navigation.
      await page.addInitScript((data) => {
        localStorage.setItem("auth_access_token", data.access);
        localStorage.setItem("auth_refresh_token", data.refresh);
        localStorage.setItem("auth_user", JSON.stringify(data.user));
      }, viewer);
      await page.goto(path + "/decision-support");
      await page.locator("#button-language-" + locale).click();
      await page.getByRole("button", { name: c.title, exact: true }).click();
      await expect(page.locator("#ds-title")).toHaveValue(c.title);
      await expect(page.locator("#ds-title")).toBeDisabled();
      await expect(page.locator('[data-ism-cell="0-0"]')).toBeDisabled();
      for (const method of ["ISM", "AHP", "SAW", "TOPSIS"])
        await expect(
          page.getByRole("button", {
            name: copy.runMethod.replace("{{method}}", method),
            exact: true,
          }),
        ).toBeDisabled();
      for (const control of await page
        .locator(
          'fieldset input, fieldset select, fieldset textarea, input[placeholder="' +
            copy.addName +
            '"]',
        )
        .all())
        await expect(control).toBeDisabled();
      for (const control of await page.getByRole("checkbox").all())
        await expect(control).toBeDisabled();
      await expect(
        page.getByRole("textbox", {
          name: copy.criterionName.replace("{{index}}", "1"),
          exact: true,
        }),
      ).toBeDisabled();
      await expect(
        page.getByRole("button", { name: copy.save, exact: true }),
      ).toBeDisabled();
      await page.locator(`[data-run-id="${run.id}"]`).click();
      await expect(
        page.getByRole("region", { name: copy.historicalRun, exact: true }),
      ).toContainText(copy.ismInterpretation);
      const vh = { Authorization: "Bearer " + viewer.access };
      expect(
        (
          await page.request.patch(base + c.id + "/", {
            headers: vh,
            data: { ism_matrix: [[1]] },
          })
        ).status(),
      ).toBe(403);
      expect(
        (
          await page.request.post(base + c.id + "/runs/", {
            headers: vh,
            data: { method: "ism" },
          })
        ).status(),
      ).toBe(403);
      expect(
        (
          await page.request.post(base, {
            headers: vh,
            data: {
              title: "Forbidden",
              selected_methods: ["ism"],
              criteria: ["A"],
              ism_matrix: [[1]],
            },
          })
        ).status(),
      ).toBe(403);
      expect(
        (
          await (
            await page.request.get(base + c.id + "/runs/", { headers })
          ).json()
        ).count,
      ).toBe(1);
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " SC-008 forty real POST to visible layer trials",
    async ({ page, browser }) => {
      test.setTimeout(180000);
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria: ["Only"],
        ism_matrix: [[0]],
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const single = { name: "single", criteria: ["Only"], matrix: [[0]] };
      const names = Array.from({ length: 10 }, (_, i) => "N" + i);
      const examples = [
        single,
        {
          name: "ten-chain",
          criteria: names,
          matrix: names.map((_, i) =>
            names.map((_, j) => (i + 1 === j ? 1 : 0)),
          ),
        },
        {
          name: "ten-branch",
          criteria: names,
          matrix: names.map((_, i) =>
            names.map((_, j) =>
              (i === 0 && (j === 1 || j === 2)) ||
              (i === 1 && j === 3) ||
              (i === 2 && j === 3)
                ? 1
                : 0,
            ),
          ),
        },
        {
          name: "ten-dense-cycle",
          criteria: names,
          matrix: names.map((_, i) => names.map((_, j) => (i === j ? 0 : 1))),
        },
      ];
      const trials: any[] = [];
      for (const example of examples) {
        expect(
          (
            await page.request.patch(base + c.id + "/", {
              headers,
              data: { criteria: example.criteria, ism_matrix: example.matrix },
            })
          ).status(),
        ).toBe(200);
        await page.getByRole("button", { name: c.title, exact: true }).click();
        await expect(page.locator("[data-ism-cell]")).toHaveCount(
          example.criteria.length ** 2,
        );
        for (let trial = 0; trial < 10; trial++) {
          await page.evaluate(() => performance.clearResourceTimings());
          let runId: string | null = null;
          let durationMs: number | null = null;
          let error: string | null = null;
          try {
            const response = page.waitForResponse(
              (r) =>
                r.url().endsWith("/decision-cases/" + c.id + "/runs/") &&
                r.request().method() === "POST",
            );
            await page
              .getByRole("button", {
                name: copy.runMethod.replace("{{method}}", "ISM"),
                exact: true,
              })
              .click();
            const received = await response;
            if (received.status() !== 201)
              throw new Error("POST " + received.status());
            const run = await received.json();
            runId = run.id;
            await expect(
              page
                .locator(`[data-ism-result="${runId}"] [data-ism-level]`)
                .first(),
            ).toBeVisible({ timeout: 10000 });
            durationMs = await page.evaluate((url) => {
              const entry = performance.getEntriesByName(url).at(-1) as
                | PerformanceResourceTiming
                | undefined;
              if (!entry) throw new Error("Missing fetch resource timing");
              return performance.now() - entry.startTime;
            }, received.url());
            expect(run.input_snapshot.ism_matrix).toEqual(example.matrix);
          } catch (caught) {
            error = String(caught);
          }
          trials.push({
            network: example.name,
            criteria: example.criteria.length,
            trial: trial + 1,
            runId,
            durationMs,
            error,
            within2000ms:
              error === null && durationMs !== null && durationMs <= 2000,
          });
        }
      }
      const path = "specs/023-decision-ism/validation-performance.json";
      const previous = existsSync(path)
        ? JSON.parse(readFileSync(path, "utf8"))
        : {};
      const values = trials
        .filter((t) => t.durationMs !== null)
        .map((t) => t.durationMs)
        .sort((a, b) => a - b);
      const environment = {
        os: `${platform()} ${release()}`,
        cpu: cpus()[0]?.model,
        logicalCpus: cpus().length,
        memoryBytes: totalmem(),
        node: process.version,
        ...JSON.parse(
          execFileSync(
            "bash",
            [
              "apps/api/django.sh",
              "shell",
              "-c",
              "import platform,django,json; from django.db import connection; from decision_support.models import DecisionCase,DecisionRun; print(json.dumps({'python':platform.python_version(),'django':django.get_version(),'postgresServerVersion':connection.pg_version,'existingDecisionCases':DecisionCase.objects.count(),'existingDecisionRuns':DecisionRun.objects.count()}))",
            ],
            { encoding: "utf8" },
          ),
        ),
      };
      previous[locale] = {
        recordedAt: new Date().toISOString(),
        environment: {
          ...environment,
          browser: browser.version(),
          locale,
          workers: 1,
          transport: "127.0.0.1 HTTP; no emulated latency or throttling",
          warmth:
            "running Vite development server, Django development server and browser session; fresh result per trial",
          scale:
            "one disposable ISM-only case; 40 append-only runs; at most 10 criteria",
        },
        boundary:
          "browser PerformanceResourceTiming.startTime for execution POST to browser performance.now after returned-run layer visibility assertion; excludes entry and preparatory PATCH; includes automation visibility polling",
        sampleCount: trials.length,
        successfulWithin2000ms: trials.filter((t) => t.within2000ms).length,
        failedTrials: trials.filter((t) => t.error !== null).length,
        medianMs: (values[19] + values[20]) / 2,
        p95Ms: values[Math.ceil(values.length * 0.95) - 1],
        trials,
      };
      writeFileSync(path, JSON.stringify(previous, null, 2) + "\n");
      expect(trials).toHaveLength(40);
      expect(
        trials.filter((t) => t.within2000ms).length,
      ).toBeGreaterThanOrEqual(38);
      expect(trials.filter((t) => t.error !== null)).toHaveLength(0);
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale +
      " late responses from every method and global save isolate newer case",
    async ({ page }) => {
      test.setTimeout(90000);
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism", "ahp", "saw", "topsis"],
        ism_matrix: [[0]],
      });
      const response = await page.request.post(base, {
        headers,
        data: {
          title: "New gate " + Date.now(),
          selected_methods: ["ism"],
          criteria: ["Second"],
          ism_matrix: [[1]],
        },
      });
      expect(response.status()).toBe(201);
      const second = await response.json();
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      const button = (method: string) =>
        page.getByRole("button", {
          name:
            method === "global"
              ? copy.save
              : copy.runMethod.replace("{{method}}", method),
          exact: true,
        });
      for (const method of ["AHP", "SAW", "TOPSIS", "global", "ISM"]) {
        await page.getByRole("button", { name: c.title, exact: true }).click();
        await expect(page.locator("#ds-title")).toHaveValue(c.title);
        await expect(button(method)).toBeEnabled();
        const oldSuffix =
          "/decision-cases/" +
          c.id +
          "/" +
          (method === "global" ? "" : "runs/");
        const oldVerb = method === "global" ? "PATCH" : "POST";
        let releaseOld!: () => void;
        let releaseNew!: () => void;
        let oldEntered = false,
          newEntered = false;
        const oldGate = new Promise<void>((r) => (releaseOld = r)),
          newGate = new Promise<void>((r) => (releaseNew = r));
        const pattern = "**/decision-cases/**";
        await page.route(pattern, async (route) => {
          const request = route.request();
          if (
            request.url().endsWith(oldSuffix) &&
            request.method() === oldVerb
          ) {
            oldEntered = true;
            await oldGate;
          }
          if (
            request.url().endsWith("/decision-cases/" + second.id + "/runs/") &&
            request.method() === "POST"
          ) {
            newEntered = true;
            await newGate;
          }
          await route.continue();
        });
        const old = page.waitForResponse(
          (r) =>
            r.url().endsWith(oldSuffix) && r.request().method() === oldVerb,
        );
        await button(method).click();
        await expect.poll(() => oldEntered).toBe(true);
        await page
          .getByRole("button", { name: second.title, exact: true })
          .click();
        await expect(page.locator("#ds-title")).toHaveValue(second.title);
        await expect(button("ISM")).toBeEnabled();
        const next = page.waitForResponse(
          (r) =>
            r.url().endsWith("/decision-cases/" + second.id + "/runs/") &&
            r.request().method() === "POST",
        );
        await button("ISM").click();
        await expect.poll(() => newEntered).toBe(true);
        try {
          releaseOld();
          const previous = await old;
          expect(previous.status()).toBe(method === "global" ? 200 : 201);
          if (method !== "global")
            expect((await previous.json()).input_snapshot.criteria).toEqual([
              "A",
            ]);
          await expect(page.locator("#ds-title")).toHaveValue(second.title);
          await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue("1");
          await expect(button("global")).toBeDisabled();
          await expect(page.locator("[data-ism-result]")).toHaveCount(0);
        } finally {
          releaseOld();
          releaseNew();
        }
        const current = await (await next).json();
        await expect(
          page.locator(`[data-ism-result="${current.id}"]`),
        ).toBeVisible();
        expect(current.input_snapshot.criteria).toEqual(["Second"]);
        await expect(button("global")).toBeEnabled();
        await page.unroute(pattern);
      }
    },
  );
  test(
    locale +
      " disconnected, longer and multiple cycle groups match frozen server references",
    async ({ page }) => {
      const examples = [
        {
          names: ["A", "B", "C"],
          matrix: [
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
          ],
          layers: [{ level: 1, criteria: ["A", "B", "C"] }],
          groups: [{ level: 1, criteria: ["A", "B", "C"] }],
        },
        {
          names: ["A", "B", "C", "D", "E"],
          matrix: [
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
          ],
          layers: [{ level: 1, criteria: ["A", "B", "C", "D", "E"] }],
          groups: [
            { level: 1, criteria: ["A", "B"] },
            { level: 1, criteria: ["C", "D"] },
          ],
        },
        {
          names: ["A", "B", "C"],
          matrix: [
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0],
          ],
          layers: [
            { level: 1, criteria: ["B", "C"] },
            { level: 2, criteria: ["A"] },
          ],
          groups: [],
        },
      ];
      for (const item of examples) {
        const { c, copy } = await setup(page, locale, {
          selected_methods: ["ism"],
          criteria: item.names,
          ism_matrix: item.matrix,
          alternatives: [],
          weights: [],
          types: [],
          performance_matrix: [],
        });
        const response = page.waitForResponse(
          (r) =>
            r.url().endsWith("/decision-cases/" + c.id + "/runs/") &&
            r.request().method() === "POST",
        );
        await page
          .getByRole("button", {
            name: copy.runMethod.replace("{{method}}", "ISM"),
            exact: true,
          })
          .click();
        const run = await (await response).json();
        expect(run.result.layers).toEqual(item.layers);
        expect(run.result.mutual_groups).toEqual(item.groups);
        expect(run.input_snapshot.ism_matrix).toEqual(item.matrix);
        await expect(
          page.locator("[data-ism-result] [data-ism-group]"),
        ).toHaveCount(item.groups.length);
      }
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " convergence pending case reselect and return cannot reacquire",
    async ({ page }) => {
      test.setTimeout(180000);
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism", "ahp", "saw", "topsis"],
        ism_matrix: [[0]],
      });
      const created = await page.request.post(base, {
        headers,
        data: {
          title: "Other pending scope " + Date.now(),
          selected_methods: ["ism"],
          criteria: ["Other"],
          ism_matrix: [[0]],
        },
      });
      expect(created.status()).toBe(201);
      const other = await created.json();
      await page.reload();
      await page.locator("#button-language-" + locale).click();
      const run = (method: string) =>
        page.getByRole("button", {
          name:
            method === "global"
              ? copy.save
              : copy.runMethod.replace("{{method}}", method),
          exact: true,
        });
      for (const method of ["AHP", "SAW", "TOPSIS", "ISM", "global"]) {
        for (const phase of method === "global"
          ? ["PATCH"]
          : ["PATCH", "POST"]) {
          for (const navigation of ["reselect", "return"]) {
            await page
              .getByRole("button", { name: c.title, exact: true })
              .click();
            await expect(page.locator("#ds-title")).toHaveValue(c.title);
            await expect(run(method)).toBeEnabled();
            const cell = page.locator('[data-ism-cell="0-0"]');
            const submitted =
              method === "ISM" || method === "global" ? "1" : "0";
            await cell.selectOption(submitted);
            let release!: () => void;
            const gate = new Promise<void>((r) => (release = r));
            let requests = 0;
            const suffix =
              "/decision-cases/" +
              c.id +
              "/" +
              (phase === "POST" ? "runs/" : "");
            const pattern = "**/decision-cases/**";
            await page.route(pattern, async (route) => {
              if (
                route.request().url().endsWith(suffix) &&
                route.request().method() === phase
              ) {
                requests++;
                await gate;
              }
              await route.continue();
            });
            const completed = page.waitForResponse(
              (r) =>
                r
                  .url()
                  .endsWith(
                    "/decision-cases/" +
                      c.id +
                      "/" +
                      (method === "global" ? "" : "runs/"),
                  ) &&
                r.request().method() ===
                  (method === "global" ? "PATCH" : "POST"),
            );
            await run(method).click();
            await expect.poll(() => requests).toBe(1);
            try {
              if (navigation === "return") {
                await page
                  .getByRole("button", { name: other.title, exact: true })
                  .click();
                await expect(page.locator("#ds-title")).toHaveValue(
                  other.title,
                );
                await expect(run("ISM")).toBeEnabled();
                await expect(page.locator("#ds-title")).toBeEnabled();
              }
              await page
                .getByRole("button", { name: c.title, exact: true })
                .click();
              await expect(page.locator("#ds-title")).toHaveValue(c.title);
              await expect(cell).toBeVisible();
              await expect(page.locator("#ds-title")).toBeDisabled();
              await expect(cell).toBeDisabled();
              await expect(run("global")).toBeDisabled();
              await run("global").evaluate((el) =>
                (el as HTMLButtonElement).click(),
              );
              expect(requests).toBe(1);
            } finally {
              release();
            }
            expect((await completed).status()).toBe(
              method === "global" ? 200 : 201,
            );
            await expect(run("ISM")).toBeEnabled();
            await expect(cell).toHaveValue(submitted);
            await page.unroute(pattern);
          }
        }
      }
    },
  );
}

for (const locale of ["en", "fa"] as const) {
  test(
    locale + " convergence root JSON null is explicitly reset and corrected",
    async ({ page }) => {
      const { copy, c, base, headers } = await setup(page, locale, {
        selected_methods: ["ism"],
        criteria: ["A"],
        ism_matrix: null,
        alternatives: [],
        weights: [],
        types: [],
        performance_matrix: [],
      });
      const panel = page.locator("[data-ism-panel]");
      await expect(panel.locator("pre")).toHaveText("null");
      const run = panel.getByRole("button", {
        name: copy.runMethod.replace("{{method}}", "ISM"),
        exact: true,
      });
      await run.click();
      await expect(panel.getByRole("alert").last()).toContainText(
        copy.errors.dimension_invalid,
      );
      expect(
        (
          await (
            await page.request.get(base + c.id + "/runs/", { headers })
          ).json()
        ).count,
      ).toBe(0);
      await page.getByRole("button", { name: copy.save, exact: true }).click();
      await expect(run).toBeEnabled();
      expect(
        (await (await page.request.get(base + c.id + "/", { headers })).json())
          .ism_matrix,
      ).toBeNull();
      await panel
        .getByRole("button", { name: copy.ismReset, exact: true })
        .click();
      await expect(panel.locator('[data-ism-cell="0-0"]')).toHaveValue("0");
      await run.click();
      await expect(page.locator("[data-ism-result]")).toBeVisible();
      expect(
        (await (await page.request.get(base + c.id + "/", { headers })).json())
          .ism_matrix,
      ).toEqual([[0]]);
      expect(
        (
          await (
            await page.request.get(base + c.id + "/runs/", { headers })
          ).json()
        ).count,
      ).toBe(1);
    },
  );

  for (const recovery of ["success", "failure", "timeout"] as const) {
    test(
      locale +
        " convergence committed run lost response with history " +
        recovery,
      async ({ page }) => {
        const { copy, c, base, headers } = await setup(page, locale, {
          selected_methods: ["ism"],
          criteria: ["A"],
          ism_matrix: [[0]],
          alternatives: [],
          weights: [],
          types: [],
          performance_matrix: [],
        });
        const run = () =>
          page.locator("[data-ism-panel]").getByRole("button", {
            name: copy.runMethod.replace("{{method}}", "ISM"),
            exact: true,
          });
        await run().click();
        await expect(page.locator("[data-ism-result]")).toBeVisible();
        const initialId = await page
          .locator("[data-ism-result]")
          .getAttribute("data-ism-result");
        await expect(
          page.locator(`[data-run-id="${initialId}"]`),
        ).toBeVisible();
        const otherResponse = await page.request.post(base, {
          headers,
          data: {
            title: "Recovery independent " + locale + recovery,
            criteria: ["B"],
            selected_methods: ["ism"],
            ism_matrix: [[0]],
          },
        });
        expect(otherResponse.status()).toBe(201);
        const other = await otherResponse.json();
        // Refresh the list without changing the captured draft or run.
        await page.reload();
        await page.locator("#button-language-" + locale).click();
        await page.getByRole("button", { name: c.title, exact: true }).click();
        await expect(run()).toBeEnabled();
        await expect(
          page.locator(`[data-run-id="${initialId}"]`),
        ).toBeVisible();
        await page.locator('[data-ism-cell="0-0"]').selectOption("1");
        let release!: () => void;
        const gate = new Promise<void>((resolve) => (release = resolve));
        let lost = false,
          posts = 0,
          histories = 0;
        let committedId = "";
        const pattern = "**/decision-cases/" + c.id + "/runs/**";
        await page.route(pattern, async (route) => {
          const request = route.request();
          const url = new URL(request.url());
          if (url.pathname !== new URL(base + c.id + "/runs/").pathname)
            return route.continue();
          if (request.method() === "POST") {
            posts++;
            const response = await route.fetch();
            expect(response.status()).toBe(201);
            committedId = (await response.json()).id;
            lost = true;
            return route.abort("failed");
          }
          if (request.method() === "GET" && lost) {
            histories++;
            await gate;
            if (recovery === "failure")
              return route.fulfill({
                status: 503,
                contentType: "text/html",
                body: "History temporarily unavailable",
              });
          }
          return route.continue();
        });
        await run().click();
        await expect.poll(() => histories).toBe(1);
        try {
          expect(posts).toBe(1);
          expect(committedId).not.toBe(initialId);
          expect(
            (
              await (
                await page.request.get(base + c.id + "/runs/", { headers })
              ).json()
            ).count,
          ).toBe(2);
          await expect(page.locator("[data-ism-result]")).toHaveCount(0);
          await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue("1");
          await expect(page.locator("#ds-title")).toBeDisabled();
          await expect(
            page.getByRole("button", { name: copy.save, exact: true }),
          ).toBeDisabled();
          await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
            "data-ism-recovery",
            "checking",
          );
          await expect(page.locator("[data-ism-recovery]")).toContainText(
            copy.ismRecoveryChecking,
          );
          await page.locator(`[data-run-id="${initialId}"]`).click();
          await expect(page.locator("[data-run-id]").first()).toBeEnabled();
          if (recovery === "success") {
            await page
              .getByRole("button", { name: other.title, exact: true })
              .click();
            await expect(page.locator("#ds-title")).toHaveValue(other.title);
            await expect(run()).toBeEnabled();
            await run().click();
            await expect(page.locator("[data-ism-result]")).toBeVisible();
            await page
              .getByRole("button", { name: c.title, exact: true })
              .click();
            await expect(page.locator("#ds-title")).toHaveValue(c.title);
            await expect(page.locator("#ds-title")).toBeDisabled();
            await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue(
              "1",
            );
            await expect(page.locator("[data-ism-result]")).toHaveCount(0);
            await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
              "data-ism-recovery",
              "checking",
            );
          }
          if (recovery === "timeout") {
            await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
              "data-ism-recovery",
              "failed",
              { timeout: 15_000 },
            );
            await expect(run()).toBeEnabled();
            expect(posts).toBe(1);
          }
        } finally {
          release();
        }
        await expect(run()).toBeEnabled();
        expect(posts).toBe(1);
        if (recovery === "success") {
          await expect(
            page.locator(`[data-run-id="${committedId}"]`),
          ).toBeVisible();
        } else {
          await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
            "data-ism-recovery",
            "failed",
          );
          await expect(page.locator("[data-ism-recovery]")).toContainText(
            copy.ismRecoveryFailed,
          );
          expect(histories).toBe(1);
        }
        await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue("1");
        await page.unroute(pattern);
        await run().click();
        await expect(page.locator("[data-ism-result]")).toBeVisible();
        await expect(page.locator("[data-ism-recovery]")).toHaveCount(0);
        expect(
          (
            await (
              await page.request.get(base + c.id + "/runs/", { headers })
            ).json()
          ).count,
        ).toBe(3);
      },
    );
  }
}

for (const locale of ["en", "fa"] as const) {
  for (const phase of ["save", "run"] as const) {
    test(
      locale +
        " convergence malformed successful " +
        phase +
        " response stays guarded",
      async ({ page }) => {
        test.setTimeout(90_000);
        const { copy, c, base, headers } = await setup(page, locale, {
          selected_methods: ["ism"],
          criteria: ["A"],
          ism_matrix: [[0]],
          alternatives: [],
          weights: [],
          types: [],
          performance_matrix: [],
        });
        const errors: string[] = [];
        page.on("pageerror", (error) => errors.push(error.message));
        const run = () =>
          page.locator("[data-ism-panel]").getByRole("button", {
            name: copy.runMethod.replace("{{method}}", "ISM"),
            exact: true,
          });
        await run().click();
        await expect(page.locator("[data-ism-result]")).toBeVisible();
        await page.locator('[data-ism-cell="0-0"]').selectOption("1");
        let count = 1;
        for (const corruption of [
          "empty",
          "html",
          "truncated",
          "null",
          "object",
          "identity",
          "snapshot",
          "result",
        ] as const) {
          let release!: () => void;
          const gate = new Promise<void>((resolve) => (release = resolve));
          let posts = 0,
            histories = 0,
            corrupted = false;
          let committedId = "";
          const pattern = "**/decision-cases/" + c.id + "/**";
          await page.route(pattern, async (route) => {
            const request = route.request();
            const pathname = new URL(request.url()).pathname;
            const casePath = new URL(base + c.id + "/").pathname;
            if (
              request.method() === "GET" &&
              pathname === casePath + "runs/" &&
              corrupted &&
              phase === "run"
            ) {
              histories++;
              await gate;
              if (corruption === "null")
                return route.fulfill({
                  status: 503,
                  body: "History unavailable",
                });
            }
            if (
              request.method() === "POST" &&
              pathname === casePath + "runs/"
            ) {
              posts++;
              if (phase === "save")
                return route.fulfill({
                  status: 403,
                  json: { error: { code: "permission_denied" } },
                });
            }
            if (
              request.method() !== (phase === "save" ? "PATCH" : "POST") ||
              pathname !== casePath + (phase === "save" ? "" : "runs/")
            )
              return route.continue();
            const response = await route.fetch();
            expect(response.status()).toBe(phase === "save" ? 200 : 201);
            const body = await response.json();
            if (phase === "run") committedId = body.id;
            let raw = "";
            if (corruption === "html") raw = "<html>Broken response</html>";
            if (corruption === "truncated") raw = '{"id":';
            if (corruption === "null") raw = "null";
            if (corruption === "object") raw = "{}";
            if (corruption === "identity") {
              if (phase === "save") body.id = "another-case";
              else body.method = "ahp";
              raw = JSON.stringify(body);
            }
            if (corruption === "snapshot") {
              if (phase === "save") delete body.criteria;
              else delete body.input_snapshot;
              raw = JSON.stringify(body);
            }
            if (corruption === "result") {
              if (phase === "save") delete body.ism_matrix;
              else body.result = { status: "stub", engine: null };
              raw = JSON.stringify(body);
            }
            corrupted = true;
            await route.fulfill({
              response,
              body: raw,
              contentType: "application/json",
            });
          });
          await run().click();
          try {
            if (phase === "save") {
              await expect
                .poll(() => corrupted, { timeout: 15_000 })
                .toBe(true);
              await expect(run()).toBeEnabled();
              expect(posts).toBe(0);
              await expect(
                page.locator("[data-ism-panel]").getByRole("alert"),
              ).toContainText(copy.errors.request_failed);
            } else {
              await expect.poll(() => histories, { timeout: 15_000 }).toBe(1);
              expect(posts).toBe(1);
              expect(committedId).not.toBe("");
              await expect(page.locator("#ds-title")).toBeDisabled();
              await expect(
                page.getByRole("button", { name: copy.save, exact: true }),
              ).toBeDisabled();
              await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
                "data-ism-recovery",
                "checking",
              );
              await expect(page.locator("[data-ism-recovery]")).toContainText(
                copy.ismRecoveryChecking,
              );
            }
            await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue(
              "1",
            );
            await expect(page.locator("[data-ism-result]")).toHaveCount(0);
          } finally {
            release();
          }
          await expect(run()).toBeEnabled();
          if (phase === "run") {
            count++;
            await expect(
              page.locator("[data-ism-panel]").getByRole("alert"),
            ).toContainText(copy.errors.request_failed);
            await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
              "data-ism-recovery",
              corruption === "null" ? "failed" : "refreshed",
            );
            if (corruption !== "null")
              await expect(
                page.locator(`[data-run-id="${committedId}"]`),
              ).toBeVisible();
          }
          expect(
            (
              await (
                await page.request.get(base + c.id + "/runs/", { headers })
              ).json()
            ).count,
          ).toBe(count);
          await page.unroute(pattern);
          expect(errors).toEqual([]);
          // An explicit valid attempt recovers and gives the next corruption an older result to clear.
          await run().click();
          await expect(page.locator("[data-ism-result]")).toBeVisible();
          count++;
          await expect(page.locator("[data-run-id]").first()).toBeVisible();
        }
        expect(
          (
            await (
              await page.request.get(base + c.id + "/runs/", { headers })
            ).json()
          ).count,
        ).toBe(count);
      },
    );
  }
}

for (const locale of ["en", "fa"] as const) {
  for (const scenario of [
    { view: "filtered", outcome: "success" },
    { view: "filtered", outcome: "failure" },
    { view: "page2", outcome: "success" },
    { view: "page2", outcome: "failure" },
    { view: "switch", outcome: "success" },
  ] as const) {
    test(
      locale +
        " convergence visible recovery history " +
        scenario.view +
        " " +
        scenario.outcome,
      async ({ page }) => {
        test.setTimeout(60_000);
        const { copy, c, base, headers } = await setup(page, locale, {
          selected_methods: ["ism", "ahp"],
          criteria: ["A"],
          ahp_matrix: [[1]],
          ism_matrix: [[0]],
          alternatives: [],
          weights: [],
          types: [],
          performance_matrix: [],
        });
        const seeded: string[] = [];
        for (let i = 0; i < 12; i++) {
          const response = await page.request.post(base + c.id + "/runs/", {
            headers,
            data: { method: "ism" },
          });
          expect(response.status()).toBe(201);
          seeded.push((await response.json()).id);
        }
        expect(
          (
            await page.request.post(base + c.id + "/runs/", {
              headers,
              data: { method: "ahp" },
            })
          ).status(),
        ).toBe(201);
        const otherResponse = await page.request.post(base, {
          headers,
          data: {
            title:
              "Filtered recovery independent " +
              locale +
              scenario.view +
              scenario.outcome,
            criteria: ["B"],
            selected_methods: ["ism"],
            ism_matrix: [[0]],
          },
        });
        expect(otherResponse.status()).toBe(201);
        const other = await otherResponse.json();
        expect(
          (
            await page.request.post(base + other.id + "/runs/", {
              headers,
              data: { method: "ism" },
            })
          ).status(),
        ).toBe(201);
        await page.reload();
        await page.locator("#button-language-" + locale).click();
        await page.getByRole("button", { name: c.title, exact: true }).click();
        const filter = page.getByRole("combobox", {
          name: copy.historyMethod,
          exact: true,
        });
        await filter.selectOption("ism");
        const pageLabel = (pageIndex: number, count: number) =>
          copy.historyPage
            .replace("{{page}}", String(pageIndex))
            .replace("{{count}}", String(count));
        await expect(
          page.getByText(pageLabel(1, 12), { exact: true }),
        ).toBeVisible();
        if (scenario.view === "page2") {
          await page
            .getByRole("button", { name: copy.historyNext, exact: true })
            .click();
          await expect(
            page.getByText(pageLabel(2, 12), { exact: true }),
          ).toBeVisible();
        }
        const oldId = await page
          .locator("[data-run-id]")
          .first()
          .getAttribute("data-run-id");
        expect(seeded).toContain(oldId);
        const before = await (
          await page.request.get(base + c.id + "/runs/" + oldId + "/", {
            headers,
          })
        ).json();
        const run = () =>
          page.locator("[data-ism-panel]").getByRole("button", {
            name: copy.runMethod.replace("{{method}}", "ISM"),
            exact: true,
          });
        await page.locator('[data-ism-cell="0-0"]').selectOption("1");
        let release!: () => void;
        const gate = new Promise<void>((resolve) => (release = resolve));
        let lost = false,
          posts = 0,
          histories = 0,
          committedId = "";
        const pattern = "**/decision-cases/" + c.id + "/runs/**";
        await page.route(pattern, async (route) => {
          const request = route.request();
          if (
            new URL(request.url()).pathname !==
            new URL(base + c.id + "/runs/").pathname
          )
            return route.continue();
          if (request.method() === "POST") {
            posts++;
            const response = await route.fetch();
            expect(response.status()).toBe(201);
            committedId = (await response.json()).id;
            lost = true;
            return route.abort("failed");
          }
          if (request.method() === "GET" && lost) {
            histories++;
            await gate;
            if (scenario.outcome === "failure")
              return route.fulfill({
                status: 503,
                body: "History unavailable",
              });
          }
          return route.continue();
        });
        await run().click();
        await expect.poll(() => histories, { timeout: 15_000 }).toBe(1);
        const recovered = page.waitForResponse(
          (response) =>
            response.request().method() === "GET" &&
            new URL(response.url()).pathname ===
              new URL(base + c.id + "/runs/").pathname,
        );
        try {
          expect(posts).toBe(1);
          await expect(page.locator("#ds-title")).toBeDisabled();
          await expect(page.locator('[data-ism-cell="0-0"]')).toHaveValue("1");
          await page.locator(`[data-run-id="${oldId}"]`).click();
          await expect(
            page.getByRole("region", { name: copy.historicalRun, exact: true }),
          ).toBeVisible();
          if (scenario.view === "switch") {
            await page
              .getByRole("button", { name: other.title, exact: true })
              .click();
            await expect(page.locator("#ds-title")).toHaveValue(other.title);
            await filter.selectOption("ism");
            await expect(
              page.getByText(pageLabel(1, 1), { exact: true }),
            ).toBeVisible();
            await expect(run()).toBeEnabled();
          }
        } finally {
          release();
        }
        await recovered;
        if (scenario.view === "switch") {
          await expect(page.locator("#ds-title")).toHaveValue(other.title);
          await expect(filter).toHaveValue("ism");
          await expect(
            page.getByText(pageLabel(1, 1), { exact: true }),
          ).toBeVisible();
          await expect(page.locator("[data-ism-recovery]")).toHaveCount(0);
          await page
            .getByRole("button", { name: c.title, exact: true })
            .click();
        }
        await expect(run()).toBeEnabled();
        expect(posts).toBe(1);
        if (scenario.outcome === "success") {
          await expect(filter).toHaveValue("");
          await expect(
            page.getByText(pageLabel(1, 14), { exact: true }),
          ).toBeVisible();
          await expect(
            page.locator(`[data-run-id="${committedId}"]`),
          ).toBeVisible();
          await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
            "data-ism-recovery",
            "refreshed",
          );
          await expect(page.locator("[data-ism-recovery]")).toContainText(
            copy.ismRecoveryRefreshed,
          );
        } else {
          await expect(filter).toHaveValue("ism");
          await expect(
            page.getByText(pageLabel(scenario.view === "page2" ? 2 : 1, 12), {
              exact: true,
            }),
          ).toBeVisible();
          await expect(page.locator(`[data-run-id="${oldId}"]`)).toBeVisible();
          await expect(page.locator("[data-ism-recovery]")).toHaveAttribute(
            "data-ism-recovery",
            "failed",
          );
          await expect(page.locator("[data-ism-recovery]")).toContainText(
            copy.ismRecoveryFailed,
          );
        }
        await expect(page.locator("[data-ism-result]")).toHaveCount(0);
        expect(
          await (
            await page.request.get(base + c.id + "/runs/" + oldId + "/", {
              headers,
            })
          ).json(),
        ).toEqual(before);
        await page.unroute(pattern);
        await run().click();
        await expect(page.locator("[data-ism-result]")).toBeVisible();
        expect(
          (
            await (
              await page.request.get(base + c.id + "/runs/", { headers })
            ).json()
          ).count,
        ).toBe(15);
      },
    );
  }
}
