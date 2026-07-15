/**
 * FLOW: Project List & Create
 * MODULE: Project Foundation
 * ROLES: admin, project_manager, viewer
 * DECISION TREE:
 *  - List projects
 *    - Has projects -> render list
 *    - No projects -> empty state
 *  - Create project
 *    - Valid data -> submit -> redirect to project detail/list
 *    - Missing data -> validation error
 *    - Unauthorized -> permission denied
 *
 * BRANCHES TESTED: RTL layout validation, project list loads, create project form renders
 * BRANCHES DEFERRED: Valid project creation, validation errors
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

  test("create project route renders and has mandatory inputs", async ({ page }) => {
    await page.goto("/projects/new");
    await expect(page.getByRole("heading", { name: /ایجاد پروژه|پروژه جدید/i }).first()).toBeVisible({
      timeout: 15_000,
    });
    // Just verifying the form renders without actually submitting
    await expect(page.locator('input[value=""]').nth(1)).toBeVisible(); // Using nth or generic since shadcn labels don't always link accessibility properly if id is missing
  });
});
