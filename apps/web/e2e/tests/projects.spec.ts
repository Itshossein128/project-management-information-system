/**
 * FLOW: Project List & Create
 * MODULE: Project Foundation
 * ROLES: admin, project_manager, viewer
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Project Foundation", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("RTL layout is applied to HTML element", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  });

  test("projects list page loads and shows heading", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByRole("heading", { name: /پروژه|Projects/i }).first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/home redirects to project list", async ({ page }) => {
    await page.goto("/home");
    await expect(page).toHaveURL(/\/projects\/?$/);
  });

  test("create project route renders and has mandatory inputs", async ({ page }) => {
    await page.goto("/projects/new");
    await expect(page.getByRole("heading", { name: /ایجاد پروژه|پروژه جدید/i }).first()).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByRole("button", { name: "بعدی" })).toBeDisabled();
  });

  test("wizard step 1 requires mandatory fields before continuing", async ({ page }) => {
    await page.goto("/projects/new");
    await page.getByLabel("نام پروژه *").fill("E2E Test Project");
    await page.getByLabel("کد پروژه *").fill("e2e-test");
    await page.getByLabel("کارفرما *").fill("Test Employer");
    await expect(page.getByRole("button", { name: "بعدی" })).toBeEnabled();
    await page.getByRole("button", { name: "بعدی" }).click();
    await expect(page.getByLabel("تاریخ شروع *")).toBeVisible();
    await expect(page.getByRole("button", { name: "بعدی" })).toBeDisabled();
  });

  test("wizard creates project and redirects to overview", async ({ page }) => {
    const code = `e2e-${Date.now()}`;
    await page.goto("/projects/new");
    await page.getByLabel("نام پروژه *").fill(`E2E ${code}`);
    await page.getByLabel("کد پروژه *").fill(code);
    await page.getByLabel("کارفرما *").fill("E2E Employer");
    await page.getByRole("button", { name: "بعدی" }).click();
    await page.locator("#input-start_date").click();
    await page.locator(".rmdp-day:not(.rmdp-disabled)").first().click();
    await page.getByRole("button", { name: "بعدی" }).click();
    await page.getByRole("button", { name: "ایجاد پروژه" }).click();
    await expect(page).toHaveURL(new RegExp(`/projects/[0-9a-f-]+/overview`), {
      timeout: 20_000,
    });
  });
});
