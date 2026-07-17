/**
 * FLOW: WBS editor, activities CRUD/relations, MSP import (Sprint 3)
 * MODULE: Activities & Schedule Baseline
 * ROLES: admin
 */

import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import {
  createChildWbs,
  createProjectViaApi,
  createRootWbs,
  moveWbsViaApi,
} from "../helpers/project";

const FIXTURES_DIR = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "fixtures",
);

async function expectAppLoaded(page: import("@playwright/test").Page) {
  await expect(page.getByRole("heading", { name: /اوه!/ })).toHaveCount(0, {
    timeout: 5_000,
  });
}

test.describe("Sprint 3 — Activities & Schedule Baseline", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("WBS: inline rename and reparent (UI rename + move API)", async ({ page }) => {
    const base = await createProjectViaApi(page);
    const rootId = await createRootWbs(page, base, { code: "1", name: "Root Phase" });
    const childOneId = await createChildWbs(page, base, rootId, {
      code: "1.1",
      name: "Child One",
    });
    const childTwoId = await createChildWbs(page, base, rootId, {
      code: "1.2",
      name: "Child Two",
    });

    await page.goto(`${base}/wbs`);
    await expect(
      page.getByRole("heading", { name: /ساختار شکست کار|WBS/i }).first(),
    ).toBeVisible({ timeout: 20_000 });
    await expectAppLoaded(page);
    await expect(page.getByTestId("wbs-row-1")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("wbs-row-1.1")).toBeVisible();
    await expect(page.getByTestId("wbs-row-1.2")).toBeVisible();
    // DnD affordance present (HTML5 dataTransfer cannot be set via synthetic events in Chromium)
    await expect(page.getByTestId("wbs-row-1.1")).toHaveAttribute("draggable", "true");

    // Inline rename child 1.1
    const childOne = page.getByTestId("wbs-row-1.1");
    await childOne.hover();
    await childOne.getByRole("button", { name: /ویرایش|Edit/i }).click();
    const renameInput = childOne.locator("input").first();
    await renameInput.fill("Child One Renamed");
    await renameInput.press("Enter");
    await expect(page.getByText("Child One Renamed")).toBeVisible({
      timeout: 10_000,
    });

    // Reparent 1.2 under 1.1 via move API (same endpoint the drag drop handler calls)
    await moveWbsViaApi(page, base, childTwoId, childOneId);
    await page.reload();
    await expect(page.getByTestId("wbs-node-1.1").getByText("Child Two")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Activities: create two activities and add FS relation; reject cycle", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    await createRootWbs(page, base, { code: "1", name: "Act Root" });

    await page.goto(`${base}/activities`);
    await expect(page.getByRole("heading", { name: /فعالیت/i }).first()).toBeVisible({
      timeout: 20_000,
    });
    await expectAppLoaded(page);

    async function createActivity(code: string, name: string) {
      await page.getByRole("button", { name: /افزودن فعالیت/i }).click();
      await expect(page.getByText(/افزودن فعالیت/i).first()).toBeVisible();
      await page.locator("#act-code").fill(code);
      await page.locator("#act-name").fill(name);
      // Ensure a WBS option is selected
      const wbsSelect = page.locator("select").filter({ has: page.locator("option") }).first();
      const options = await wbsSelect.locator("option").count();
      expect(options).toBeGreaterThan(0);
      await page.getByRole("button", { name: /^ذخیره$/i }).click();
      await expect(page.getByRole("button", { name: code })).toBeVisible({
        timeout: 15_000,
      });
    }

    await createActivity("A1", "Activity One");
    await createActivity("A2", "Activity Two");

    const a1Row = page.locator("tr", { has: page.getByRole("button", { name: "A1" }) });
    await a1Row.getByRole("button", { name: /ارتباط/i }).click();
    await expect(page.getByText(/افزودن ارتباط/i).first()).toBeVisible();
    const picker = page.locator("select").filter({ has: page.locator("option", { hasText: "A2" }) });
    await picker.selectOption({ label: "A2 — Activity Two" });
    await page.getByRole("button", { name: /^ذخیره$/i }).click();
    await expect(page.getByText(/افزودن ارتباط/i).first()).toBeHidden({
      timeout: 10_000,
    });

    const a2Row = page.locator("tr", { has: page.getByRole("button", { name: "A2" }) });
    await a2Row.getByRole("button", { name: /ارتباط/i }).click();
    await expect(page.getByText(/افزودن ارتباط/i).first()).toBeVisible();
    const picker2 = page.locator("select").filter({ has: page.locator("option", { hasText: "A1" }) });
    await picker2.selectOption({ label: "A1 — Activity One" });
    await page.getByRole("button", { name: /^ذخیره$/i }).click();
    await expect(page.getByText(/حلقه|cycle/i)).toBeVisible({ timeout: 10_000 });
  });

  test("MSP import: preview and complete import", async ({ page }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/wbs`);
    await expect(
      page.getByRole("heading", { name: /ساختار شکست کار|WBS/i }).first(),
    ).toBeVisible({ timeout: 20_000 });
    await expectAppLoaded(page);

    await page.getByTestId("msp-import-btn").click();
    await expect(
      page.getByRole("heading", { name: /بارگذاری برنامه زمان‌بندی/i }),
    ).toBeVisible();

    const fixturePath = path.join(FIXTURES_DIR, "sample-msp.xml");
    await page.locator('input[type="file"]').setInputFiles(fixturePath);
    await expect(page.getByText(/sample-msp\.xml/i)).toBeVisible();

    const previewResponse = page.waitForResponse(
      (r) => r.url().includes("/import/msp/preview/") && r.request().method() === "POST",
      { timeout: 30_000 },
    );
    await page.getByRole("button", { name: /پیش‌نمایش/i }).click();
    const preview = await previewResponse;
    expect(preview.ok(), `preview status ${preview.status()}`).toBeTruthy();

    await expect(page.getByText(/نحوه وارد کردن/i)).toBeVisible({ timeout: 15_000 });
    await page.getByRole("button", { name: /وارد کردن/i }).click();

    await expect(page.getByText(/وارد کردن با موفقیت انجام شد/i)).toBeVisible({
      timeout: 60_000,
    });
    await page.getByRole("button", { name: /مشاهده WBS/i }).click();
    await expect(page.getByTestId("wbs-row-1")).toBeVisible({ timeout: 15_000 });
  });
});
