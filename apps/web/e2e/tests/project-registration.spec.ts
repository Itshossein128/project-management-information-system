/**
 * FLOW: Spec 03 project registration — CR UI, draft settings, wizard FR-PRJ-001
 * MODULE: Project Foundation
 * ROLES: admin
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { activateProjectViaApi, createProjectViaApi } from "../helpers/project";

test.describe("Project registration — Spec 03", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("create wizard exposes FR-PRJ-001 fields and persists them", async ({ page }) => {
    const code = `wiz-${Date.now()}`;
    await page.goto("/projects/new");
    await expect(page.getByTestId("wizard-currency")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("wizard-owning-unit")).toBeVisible();
    await expect(page.getByTestId("wizard-contract-number")).toBeVisible();
    await expect(page.getByTestId("wizard-project-manager")).toBeVisible();

    await page.getByLabel("نام پروژه *").fill(`Wizard ${code}`);
    await page.getByLabel("کد پروژه *").fill(code);
    await page.getByLabel("کارفرما *").fill("Wizard Employer");
    await page.getByTestId("wizard-contract-number").fill(`CN-${code}`);
    await page.getByTestId("wizard-currency").selectOption("IRT");

    await page.getByRole("button", { name: "بعدی" }).click();
    await expect(page.locator("#input-start_date")).toBeVisible({ timeout: 10_000 });
    await page.locator("#input-start_date").click();
    await page.locator(".rmdp-day:not(.rmdp-disabled)").first().click();
    await expect(page.getByRole("button", { name: "بعدی" })).toBeEnabled({
      timeout: 5_000,
    });
    await page.getByRole("button", { name: "بعدی" }).click();
    const createResp = page.waitForResponse(
      (r) =>
        r.url().includes("/api/v1/projects/") &&
        r.request().method() === "POST" &&
        !r.url().includes("change-requests"),
      { timeout: 20_000 },
    );
    await page.getByRole("button", { name: "ایجاد پروژه" }).click();
    const resp = await createResp;
    expect(resp.ok(), `create project failed: ${resp.status()} ${await resp.text()}`).toBeTruthy();
    await expect(page).toHaveURL(new RegExp(`/projects/[0-9a-f-]+/overview`), {
      timeout: 20_000,
    });

    const projectId = page.url().match(/\/projects\/([0-9a-f-]+)/i)?.[1];
    expect(projectId).toBeTruthy();
    const res = await page.request.get(`http://127.0.0.1:8000/api/v1/projects/${projectId}/`, {
      headers: {
        Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem("auth_access_token"))}`,
      },
    });
    expect(res.ok()).toBeTruthy();
    const body = (await res.json()) as {
      currency?: string;
      contract_number?: string;
    };
    expect(body.currency).toBe("IRT");
    expect(body.contract_number).toBe(`CN-${code}`);
  });

  test("draft settings can save purpose, scope, amount, dates, contract_number", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    await page.goto(`${base}/settings`);
    await expect(page.getByTestId("settings-purpose")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("settings-scope")).toBeVisible();
    await expect(page.getByTestId("settings-contract-number")).toBeVisible();
    await expect(page.getByTestId("settings-contract-amount")).toBeVisible();

    await page.getByTestId("settings-purpose").fill("E2E purpose text");
    await page.getByTestId("settings-scope").fill("E2E scope text");
    await page.getByTestId("settings-contract-number").fill("DRAFT-CN-1");
    await page.getByTestId("settings-contract-amount").fill("2500000");
    await page.getByRole("button", { name: /ذخیره|Save/i }).first().click();
    await expect(page.getByText(/ذخیره|saved|تغییرات/i).first()).toBeVisible({
      timeout: 10_000,
    });

    await page.goto(`${base}/overview`);
    await expect(page.getByTestId("overview-purpose")).toContainText("E2E purpose text", {
      timeout: 15_000,
    });
    await expect(page.getByTestId("overview-scope")).toContainText("E2E scope text");
  });

  test("active settings protect employer; CR create→submit→approve updates it", async ({
    page,
  }) => {
    const base = await createProjectViaApi(page);
    await activateProjectViaApi(page, base);

    await page.goto(`${base}/settings`);
    await expect(page.locator("#input-employer")).toBeDisabled({ timeout: 15_000 });
    await expect(page.getByTestId("project-change-request-panel")).toBeVisible();

    const newEmployer = `CR Employer ${Date.now()}`;
    await page.getByTestId("cr-reason").fill("Correct employer legal name for contract package");
    await page.getByTestId("cr-field-employer").fill(newEmployer);
    await page.getByTestId("cr-create-btn").click();
    await expect(page.getByTestId("cr-submit-btn")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("cr-submit-btn").click();
    await expect(page.getByTestId("cr-approve-btn")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("cr-approve-btn").click();

    await expect
      .poll(async () => {
        const res = await page.request.get(
          `http://127.0.0.1:8000/api/v1/projects/${base.split("/").pop()}/`,
          {
            headers: {
              Authorization: `Bearer ${await page.evaluate(() =>
                localStorage.getItem("auth_access_token"),
              )}`,
            },
          },
        );
        const body = (await res.json()) as { employer?: string };
        return body.employer;
      })
      .toBe(newEmployer);

    await page.reload();
    await expect(page.locator("#input-employer")).toHaveValue(newEmployer);
  });
});
